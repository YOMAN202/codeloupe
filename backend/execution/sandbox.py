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

DEFAULT_TIMEOUT_SECONDS = 5
DEFAULT_MEMORY_LIMIT_BYTES = 256 * 1024 * 1024  # 256 MB


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
    except (ImportError, ValueError, OSError):
        # resource module is POSIX-only; fail open on unsupported platforms
        # rather than crash the whole request.
        pass


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

        try:
            result = subprocess.run(
                [sys.executable, script_path],
                cwd=tmpdir,
                timeout=timeout,
                capture_output=True,
                text=True,
                preexec_fn=preexec,
                env={"PATH": os.environ.get("PATH", "")},  # no inherited secrets
            )
            stderr = result.stderr
            if result.returncode is not None and result.returncode < 0:
                # Negative returncode means the process was killed by a
                # signal (e.g. SIGKILL from our own CPU/memory rlimit, or
                # the OS's OOM killer) rather than exiting normally.
                stderr += (
                    "\n[traceviz] Process was terminated (likely hit the "
                    f"{DEFAULT_TIMEOUT_SECONDS}s CPU or "
                    f"{DEFAULT_MEMORY_LIMIT_BYTES // (1024*1024)}MB memory limit)."
                )
            return {
                "stdout": result.stdout,
                "stderr": stderr,
                "exit_code": result.returncode,
                "timed_out": False,
            }
        except subprocess.TimeoutExpired as e:
            return {
                "stdout": (e.stdout or ""),
                "stderr": (e.stderr or "") + "\n[traceviz] Execution timed out.",
                "exit_code": None,
                "timed_out": True,
            }
