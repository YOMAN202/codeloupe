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
"""
import json
import textwrap

from execution.sandbox import run_code

MAX_STEPS = 2000

_TRACER_HARNESS = textwrap.dedent('''
    import sys, json as __tv_json, types as __tv_types

    __tv_steps = []
    __tv_depth = [0]
    __tv_truncated = [False]
    __tv_filename = "<submission>"

    def __tv_safe_value(v, depth=0, seen=None):
        if seen is None:
            seen = set()
        if v is None or isinstance(v, (bool, int, float, str)):
            return v
        if isinstance(v, (list, tuple)):
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
                return f"<{{type(v).__name__}} (circular ref)>"
            try:
                return {{"__type__": type(v).__name__,
                        **{{k: __tv_safe_value(val, depth + 1, seen | {{oid}})
                           for k, val in vars(v).items()}}}}
            except Exception:
                return repr(v)[:200]
        return repr(v)[:200]

    __tv_skip_frames = set()

    def __tv_tracer(frame, event, arg):
        if len(__tv_steps) >= {max_steps}:
            __tv_truncated[0] = True
            sys.settrace(None)
            return None
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
        elif event == "return":
            __tv_steps.append({{
                "event": "return", "line": frame.f_lineno,
                "function": frame.f_code.co_name, "call_depth": __tv_depth[0],
                "return_value": __tv_safe_value(arg),
            }})
            __tv_depth[0] = max(0, __tv_depth[0] - 1)
        return __tv_tracer

    __tv_code_obj = compile({user_code!r}, __tv_filename, "exec")
    sys.settrace(__tv_tracer)
    try:
        exec(__tv_code_obj, {{"__name__": "__main__"}})
    finally:
        sys.settrace(None)

    print("__TRACEVIZ_TRACE_START__")
    print(__tv_json.dumps({{"steps": __tv_steps, "truncated": __tv_truncated[0]}}))
    print("__TRACEVIZ_TRACE_END__")
''')


def trace_code(user_code: str, timeout: int = 8) -> dict:
    harness = _TRACER_HARNESS.format(max_steps=MAX_STEPS, user_code=user_code)
    exec_result = run_code(harness, timeout=timeout)
    stdout = exec_result["stdout"]

    if "__TRACEVIZ_TRACE_START__" in stdout and "__TRACEVIZ_TRACE_END__" in stdout:
        payload = stdout.split("__TRACEVIZ_TRACE_START__")[1].split("__TRACEVIZ_TRACE_END__")[0].strip()
        try:
            data = json.loads(payload)
            return {
                "steps": data["steps"],
                "truncated": data["truncated"],
                "stderr": exec_result["stderr"],
                "crashed": False,
                "limitations": (
                    "Traces only frames belonging to your submitted code (not library "
                    "internals). Values are captured by snapshot at each step, deeply "
                    f"nested objects are truncated past 4 levels, and tracing stops "
                    f"after {MAX_STEPS} steps to keep this responsive."
                ),
            }
        except (json.JSONDecodeError, KeyError):
            pass

    return {
        "steps": [], "truncated": False, "stderr": exec_result["stderr"],
        "crashed": True, "timed_out": exec_result.get("timed_out", False),
        "limitations": "Execution did not complete (crashed or timed out) -- see stderr.",
    }
