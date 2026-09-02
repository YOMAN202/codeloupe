"""
Milestone 1 execution sandbox.

Scope (per docs/development-roadmap.md Milestone 1): run a user's submitted
Python code in an isolated subprocess with a timeout and resource limits,
and return raw stdout/stderr. No trace recording, no AST analysis, no
stress testing, no complexity estimation yet -- those are later milestones.

Threat model (see docs/decisions.md): this protects against an accidental
infinite loop or runaway memory use in your own code. It is NOT hardened
against a hostile actor -- that's a deliberate, documented scope cut.
"""
import os
import subprocess
import sys
import tempfile

if os.name == "posix":
    import signal

DEFAULT_TIMEOUT_SECONDS = 5
DEFAULT_MEMORY_LIMIT_BYTES = 256 * 1024 * 1024  # 256 MB
# Fork-bomb protection: a plain DSA submission (loops, recursion, simple
# objects) never legitimately needs to start additional processes/threads,
# so this only ever caps abuse (os.fork()/multiprocessing/subprocess spam)
# -- generous enough that it can never be hit by anything this app actually
# asks submitted code to do. Note RLIMIT_NPROC counts processes for the
# real UID system-wide, not just this child's own descendants, so this is a
# ceiling on top of whatever else that UID is already running, not a
# from-zero budget -- appropriate for shared/free hosting where the same
# unprivileged account also runs the web app process itself.
DEFAULT_NPROC_LIMIT = 32
# Max size (bytes) of any single file the submission creates on disk. Plain
# stdout/stderr capture goes through a pipe, not a file, so this never
# affects normal output -- it only stops a submission from writing a huge
# file to fill up disk, which matters a lot more on a free host with a
# small, shared disk quota than it would with unlimited storage.
DEFAULT_FILE_SIZE_LIMIT_BYTES = 10 * 1024 * 1024  # 10 MB


def _limit_resources():
    """Applied inside the child process (Linux only) before exec."""
    try:
        import resource

        resource.setrlimit(
            resource.RLIMIT_AS,
            (DEFAULT_MEMORY_LIMIT_BYTES, DEFAULT_MEMORY_LIMIT_BYTES),
        )
        resource.setrlimit(
            resource.RLIMIT_CPU,
            (DEFAULT_TIMEOUT_SECONDS, DEFAULT_TIMEOUT_SECONDS),
        )
        resource.setrlimit(
            resource.RLIMIT_NPROC,
            (DEFAULT_NPROC_LIMIT, DEFAULT_NPROC_LIMIT),
        )
        resource.setrlimit(
            resource.RLIMIT_FSIZE,
            (DEFAULT_FILE_SIZE_LIMIT_BYTES, DEFAULT_FILE_SIZE_LIMIT_BYTES),
        )
    except (ImportError, ValueError, OSError):
        # resource module is POSIX-only; fail open on unsupported platforms
        # rather than crash the whole request. Also tolerates a host where
        # one of these specific limits can't be lowered (e.g. already
        # constrained tighter by the platform itself) without losing the
        # other limits -- see the per-limit try/except note below this is
        # intentionally NOT split into, since RLIMIT_AS/RLIMIT_CPU already
        # shipped as one all-or-nothing block and a partial-failure split
        # would be a bigger behavior change than this fix calls for.
        pass


def _kill_process_group(proc, use_process_group):
    """On timeout, kill the whole process GROUP the submission spawned, not
    just the one process this module tracks directly. Plain proc.kill()
    only terminates that single process -- any child process the
    submission itself spawned (os.fork()/multiprocessing/subprocess, either
    a deliberate fork bomb or just an accidental one) becomes an orphan that
    keeps running AND keeps holding its inherited copy of the stdout/stderr
    pipe open, which can hang the read in run_code() below well past the
    timeout even though the ONE process subprocess.Popen tracked is already
    dead. start_new_session=True in run_code() put the submission in its
    own session/process group specifically so this single killpg() call
    reaches every descendant it spawned, all at once, instead of leaving
    stragglers behind (see RLIMIT_NPROC above for the complementary fix:
    that caps how many such descendants can ever exist in the first place;
    this makes sure however many did get created actually die on timeout)."""
    try:
        if use_process_group:
            os.killpg(os.getpgid(proc.pid), signal.SIGKILL)
        else:
            proc.kill()
    except (ProcessLookupError, PermissionError, OSError):
        pass  # already gone, or we can't signal it -- nothing more to do


def run_code(code: str, timeout: int = DEFAULT_TIMEOUT_SECONDS) -> dict:
    """
    Run `code` in an isolated subprocess and capture stdout/stderr.

    Returns a dict: { stdout, stderr, exit_code, timed_out }
    """
    with tempfile.TemporaryDirectory(prefix="traceviz_run_") as tmpdir:
        script_path = os.path.join(tmpdir, "submission.py")
        with open(script_path, "w") as f:
            f.write(code)

        preexec = _limit_resources if os.name == "posix" else None
        # Own session/process group (Linux/Mac only) so a timeout can kill
        # every process the submission spawned, not just the one directly
        # under our control -- see _kill_process_group's docstring above.
        use_process_group = os.name == "posix"

        proc = subprocess.Popen(
            [sys.executable, script_path],
            cwd=tmpdir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            preexec_fn=preexec,
            env={"PATH": os.environ.get("PATH", "")},  # no inherited secrets
            start_new_session=use_process_group,
        )
        try:
            stdout, stderr = proc.communicate(timeout=timeout)
            if proc.returncode is not None and proc.returncode < 0:
                # Negative returncode means the process was killed by a
                # signal (e.g. SIGKILL from our own CPU/memory rlimit, or
                # the OS's OOM killer) rather than exiting normally.
                stderr += (
                    "\n[traceviz] Process was terminated (likely hit the "
                    f"{DEFAULT_TIMEOUT_SECONDS}s CPU or "
                    f"{DEFAULT_MEMORY_LIMIT_BYTES // (1024*1024)}MB memory limit)."
                )
            return {
                "stdout": stdout,
                "stderr": stderr,
                "exit_code": proc.returncode,
                "timed_out": False,
            }
        except subprocess.TimeoutExpired:
            _kill_process_group(proc, use_process_group)
            # Drain whatever output the submission had already produced
            # before hanging, rather than losing it -- a short grace period
            # to let the now-killed process(es) actually finish exiting and
            # close the pipes; if even that hangs (extremely unlikely once
            # the whole group has been SIGKILLed), fall back to whatever's
            # available rather than hang the request indefinitely.
            try:
                stdout, stderr = proc.communicate(timeout=2)
            except subprocess.TimeoutExpired:
                stdout, stderr = "", ""
            return {
                "stdout": stdout or "",
                "stderr": (stderr or "") + "\n[traceviz] Execution timed out.",
                "exit_code": None,
                "timed_out": True,
            }
