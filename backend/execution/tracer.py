"""
Phase 2: the trace visualizer's backend half. Runs the user's own
submitted code inside the sandbox with sys.settrace installed, and
returns a flat list of steps -- line executed, local variables at that
instant, call/return events, and call depth (which recursion depth falls
out of for free). See docs/architecture.md's "The trace visualizer"
section for the design rationale.

Honest limitation, stated here and surfaced in the API response: this
traces arbitrary Python reasonably well for typical DSA-style code
(loops, recursion, simple objects), but it is NOT a general debugger --
deeply nested C-extension calls, threads, and pathological code (huge
loops, deep recursion) are capped rather than fully captured. See
MAX_STEPS below and docs/decisions.md.

Core design principle: Traceviz traces what the learner's code ACTUALLY
does, bugs included -- it is not a canned animation of a correct
algorithm. That means the trace must stay useful when the submitted code
is wrong, not just when it's correct. Concretely, `status` in the return
value distinguishes five outcomes a learner can hit:
  - "completed"      ran to the end without error. Might still be a wrong
                      answer -- that's the grading endpoint's job to say,
                      not the tracer's; the trace itself is just faithful.
  - "runtime_error"   the submission raised an exception mid-execution
                      (IndexError, TypeError, etc). `steps` holds every
                      step captured before the crash, and `error` holds
                      the exception type/message/line, so the learner can
                      see exactly what their code did up to the failure.
  - "truncated"       hit MAX_STEPS (almost always an infinite loop/
                      unbounded recursion). `steps` holds the first
                      MAX_STEPS captured, so the learner can see the
                      pattern that's looping, not just a blank timeout.
  - "syntax_error"    the code didn't compile at all -- no execution, no
                      steps, `error` holds the parse error and line.
  - "crashed"         a lower-level failure outside the above (sandbox
                      process killed by wall-clock timeout before the
                      trace payload could be printed, or output the
                      parent process couldn't parse). Rare in practice --
                      MAX_STEPS catches almost all infinite loops well
                      before the wall-clock timeout fires -- but a single
                      pathologically slow line within the step budget can
                      still hit it. `steps` is empty here, which is the
                      one case this tracer cannot show partial progress
                      for.
"""
import json
import textwrap

from execution.sandbox import run_code

MAX_STEPS = 2000
# Named (not just a bare "8" default in the signature below) so callers that
# need to reason about it -- e.g. app.py clamping a caller-supplied timeout
# for the live-preview panel so it can only ever be LOWERED, never raised --
# have a single source of truth instead of a second hardcoded "8".
DEFAULT_TIMEOUT_SECONDS = 8

_TRACER_HARNESS = textwrap.dedent('''
    import sys, json as __tv_json, types as __tv_types, traceback as __tv_traceback, collections as __tv_collections

    __tv_steps = []
    __tv_depth = [0]
    __tv_truncated = [False]
    __tv_error = [None]
    __tv_filename = "<submission>"

    class __TVStepLimitExceeded(Exception):
        pass

    def __tv_safe_value(v, depth=0, seen=None):
        if seen is None:
            seen = set()
        if v is None or isinstance(v, (bool, int, float, str)):
            return v
        if isinstance(v, (list, tuple, __tv_collections.deque)):
            # deque specifically matters here: it's the standard type for a
            # queue in this curriculum (BFS frontiers, sliding-window-
            # maximum's monotonic deque, implement-queue-using-stacks-style
            # problems) and, unlike list/tuple, has no __dict__ -- without
            # this branch it would fall through to a bare repr() string
            # below and be unusable to the queue/BFS visualizers.
            if depth > 4:
                return f"<{{type(v).__name__}} len={{len(v)}}>"
            return [__tv_safe_value(x, depth + 1, seen) for x in list(v)[:200]]
        if isinstance(v, dict):
            if depth > 4:
                return f"<dict len={{len(v)}}>"
            return {{str(k): __tv_safe_value(val, depth + 1, seen) for k, val in list(v.items())[:200]}}
        if isinstance(v, set):
            return [__tv_safe_value(x, depth + 1, seen) for x in list(v)[:200]]
        if isinstance(v, (__tv_types.ModuleType, __tv_types.FunctionType, __tv_types.BuiltinFunctionType,
                          __tv_types.MethodType, type)):
            # Modules/functions/classes: never expand their __dict__ (a module's
            # namespace can be enormous and recursive) -- a short repr is what a
            # learner actually wants to see here anyway.
            return repr(v)[:200]
        if hasattr(v, "__dict__"):
            oid = id(v)
            if oid in seen:
                return {{"__type__": type(v).__name__, "__id__": oid, "__circular__": True}}
            if depth > 8:
                return {{"__type__": type(v).__name__, "__id__": oid, "__truncated__": True}}
            try:
                # __id__ is a per-process object identity (Python's id()), not a
                # value -- it lets the frontend recognize when two different
                # local variables (e.g. "prev" and "curr") point at the SAME
                # underlying node, so linked-list/tree/graph visualizers can
                # merge them into one shared diagram instead of drawing
                # duplicate disconnected copies. It's harmless noise to the
                # generic locals table and specifically consumed by the
                # specialized node-graph visualizers.
                return {{"__type__": type(v).__name__, "__id__": oid,
                        **{{k: __tv_safe_value(val, depth + 1, seen | {{oid}})
                           for k, val in vars(v).items()}}}}
            except Exception:
                return repr(v)[:200]
        return repr(v)[:200]

    __tv_skip_frames = set()
    __tv_exception_frames = set()

    def __tv_tracer(frame, event, arg):
        if len(__tv_steps) >= {max_steps}:
            __tv_truncated[0] = True
            sys.settrace(None)
            # Raising here (rather than just returning None) unwinds exec()
            # immediately instead of letting an infinite loop keep running
            # untraced in the background until the sandbox's wall-clock
            # timeout eventually kills the whole process -- which would
            # silently throw away every step already captured. Raising
            # from inside the trace function itself propagates exactly as
            # if the exception occurred at the currently-executing line of
            # the traced code (verified via a standalone sys.settrace
            # reproduction), so the steps collected so far survive intact.
            raise __TVStepLimitExceeded()
        if frame.f_code.co_filename != __tv_filename:
            return __tv_tracer
        # A `class Foo:` block executes as its own frame (CPython runs the
        # class body to build its namespace) -- co_name is the class name,
        # not a function a learner wrote to be called. Every linked-list/
        # tree problem's starter code defines Node/TreeNode at the top, so
        # without this filter every single trace would open with noisy
        # "call/line steps inside Node" before anything the learner
        # actually wrote starts running. Detect it via CO_OPTIMIZED
        # (bit 0x0001 of co_flags): real functions use fast locals and
        # have this flag set; class bodies (like module-level code) use a
        # plain namespace dict and don't -- excluding "<module>" itself
        # (which also lacks the flag, but whose steps we DO want to keep)
        # isolates class bodies specifically.
        if event == "call" and frame.f_code.co_name != "<module>" and not (frame.f_code.co_flags & 0x0001):
            __tv_skip_frames.add(id(frame))
            return __tv_tracer
        if id(frame) in __tv_skip_frames:
            if event == "return":
                __tv_skip_frames.discard(id(frame))
            return __tv_tracer
        if event == "call":
            __tv_depth[0] += 1
            __tv_steps.append({{
                "event": "call", "line": frame.f_lineno,
                "function": frame.f_code.co_name, "call_depth": __tv_depth[0],
                "locals": {{}},
            }})
        elif event == "line":
            locs = {{k: __tv_safe_value(v) for k, v in frame.f_locals.items()
                     if not k.startswith("__tv_") and not (k.startswith("__") and k.endswith("__"))}}
            __tv_steps.append({{
                "event": "line", "line": frame.f_lineno,
                "function": frame.f_code.co_name, "call_depth": __tv_depth[0],
                "locals": locs,
            }})
        elif event == "exception":
            # An exception is propagating OUT of this frame. Python still
            # sends a "return" event right after this (with arg=None) as
            # the frame unwinds -- that's not a real return, and recording
            # it as one would misleadingly show every function on the call
            # stack as having "returned None" right as the program crashed.
            # Mark this frame so the return branch below can tell the
            # difference and skip the fake step.
            __tv_exception_frames.add(id(frame))
        elif event == "return":
            if id(frame) in __tv_exception_frames:
                __tv_exception_frames.discard(id(frame))
            else:
                __tv_steps.append({{
                    "event": "return", "line": frame.f_lineno,
                    "function": frame.f_code.co_name, "call_depth": __tv_depth[0],
                    "return_value": __tv_safe_value(arg),
                }})
            __tv_depth[0] = max(0, __tv_depth[0] - 1)
        return __tv_tracer

    try:
        __tv_code_obj = compile({user_code!r}, __tv_filename, "exec")
    except SyntaxError as __tv_se:
        __tv_code_obj = None
        __tv_error[0] = {{"kind": "syntax_error", "type": "SyntaxError",
                          "message": str(__tv_se), "line": __tv_se.lineno}}

    if __tv_code_obj is not None:
        sys.settrace(__tv_tracer)
        try:
            exec(__tv_code_obj, {{"__name__": "__main__"}})
        except __TVStepLimitExceeded:
            pass  # truncated -- already flagged via __tv_truncated, steps preserved
        except Exception as __tv_exc:
            # A genuine bug in the learner's own code (wrong array logic,
            # a broken linked-list pointer, an off-by-one index, etc) --
            # NOT a tracer failure. Capture what/where and fall through to
            # print whatever steps were captured before the crash, so the
            # frontend can show execution right up to the failure point.
            __tv_tb_entries = __tv_traceback.extract_tb(__tv_exc.__traceback__)
            __tv_submission_frames = [e for e in __tv_tb_entries if e.filename == __tv_filename]
            __tv_crash_line = (__tv_submission_frames[-1].lineno if __tv_submission_frames
                                else (__tv_tb_entries[-1].lineno if __tv_tb_entries else None))
            __tv_error[0] = {{"kind": "runtime_error", "type": type(__tv_exc).__name__,
                              "message": str(__tv_exc), "line": __tv_crash_line}}
        finally:
            sys.settrace(None)

    print("__TRACEVIZ_TRACE_START__")
    print(__tv_json.dumps({{"steps": __tv_steps, "truncated": __tv_truncated[0], "error": __tv_error[0]}}))
    print("__TRACEVIZ_TRACE_END__")
''')


def trace_code(user_code: str, timeout: int = DEFAULT_TIMEOUT_SECONDS, stdin: str | None = None) -> dict:
    # `stdin` is forwarded as-is to the sandboxed subprocess running the
    # harness below -- the harness just execs the learner's code in-process
    # (see _TRACER_HARNESS), so input()/sys.stdin calls inside the traced
    # code read from the SAME real stdin pipe run_code() connects for
    # ordinary (non-traced) execution. No harness changes needed for this:
    # stdin is a subprocess-level pipe, orthogonal to the sys.settrace
    # instrumentation already wrapping the exec() call.
    harness = _TRACER_HARNESS.format(max_steps=MAX_STEPS, user_code=user_code)
    exec_result = run_code(harness, timeout=timeout, stdin=stdin)
    stdout = exec_result["stdout"]

    if "__TRACEVIZ_TRACE_START__" in stdout and "__TRACEVIZ_TRACE_END__" in stdout:
        payload = stdout.split("__TRACEVIZ_TRACE_START__")[1].split("__TRACEVIZ_TRACE_END__")[0].strip()
        try:
            data = json.loads(payload)
            error = data.get("error")
            truncated = data["truncated"]
            # See the module docstring for what each status means. Order
            # matters: a syntax error means zero steps ever ran; a runtime
            # error takes priority over "truncated" since it's a more
            # specific/actionable outcome (though the two are mutually
            # exclusive in practice -- you can't both hit MAX_STEPS and
            # raise on the very next line).
            if error and error.get("kind") == "syntax_error":
                status = "syntax_error"
            elif error and error.get("kind") == "runtime_error":
                status = "runtime_error"
            elif truncated:
                status = "truncated"
            else:
                status = "completed"
            return {
                "steps": data["steps"],
                "truncated": truncated,
                "error": error,
                "status": status,
                "stderr": exec_result["stderr"],
                "crashed": False,
                "limitations": (
                    "Traces only frames belonging to your submitted code (not library "
                    "internals). Values are captured by snapshot at each step, deeply "
                    f"nested objects are truncated past 4 levels, and tracing stops "
                    f"after {MAX_STEPS} steps to keep this responsive -- if your code "
                    "hits that limit it's almost always an infinite loop or unbounded "
                    "recursion, and the steps captured up to that point are shown below."
                ),
            }
        except (json.JSONDecodeError, KeyError):
            pass

    # The harness itself never got to print its markers -- e.g. the sandbox's
    # wall-clock timeout killed the process while still inside a single slow
    # line (rare: MAX_STEPS normally catches infinite loops first), or the
    # process was killed some other way. No partial steps are recoverable
    # in this specific case -- see the module docstring's "crashed" status.
    return {
        "steps": [], "truncated": False, "error": None, "status": "crashed",
        "stderr": exec_result["stderr"],
        "crashed": True, "timed_out": exec_result.get("timed_out", False),
        "limitations": "Execution did not complete (crashed or timed out) -- see stderr.",
    }
