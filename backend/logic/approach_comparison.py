"""
Approach comparison: "my code" vs this problem's optimal reference
solution, and -- for a curated subset of problems where a genuinely
distinct, worse-complexity baseline exists and is pedagogically useful --
a brute-force reference too.

Deliberately NOT built for every problem. optimal_reference is populated
for all 109 (it's the same code already used to compute expected test
outputs at seed time, see init_db.py), so "my code vs the optimal
reference" is always available. brute_force_reference is only populated
for problems where a real, distinct-complexity, technically valid
baseline exists and is worth seeing (13 problems as of this writing --
see docs/decisions.md for the list and reasoning). Comparison against a
baseline, including the growth-curve benchmark, is simply omitted when
brute_force_reference is NULL rather than fabricated.

Reuses, rather than duplicates, three pieces of infrastructure that
already exist elsewhere:
  - logic/analysis.py's structural_estimate() for the AST-based heuristic
    -- same function, same caveat language, no second implementation.
  - execution/sandbox.py's run_code() for actually running candidate code,
    the same isolated subprocess used by every other execution path.
  - execution/tracer.py's trace_code() for the operation-count signal
    (steps executed is read straight off a real trace) and, from the
    frontend, for "trace this approach" once its code has been revealed --
    that reuses the existing /api/problems/<slug>/trace endpoint verbatim,
    no new tracing code needed at all.

Every number this module returns is labeled with where it came from:
  - structural            AST-shape heuristic, no code ever runs. Can be
                           wrong (see analysis.py's own caveat text).
  - empirical_existing_tests   Real wall-clock time + peak memory, but
                           only at whatever input sizes this problem's own
                           seeded test cases happen to use.
  - growth_curve           Real wall-clock time + peak memory on
                           SYNTHETICALLY GENERATED inputs at a few
                           hand-picked sizes. Real measurements, not a
                           fitted curve or a big-O proof -- a run that
                           times out at some size is reported as exactly
                           that, not silently dropped.
  - operation_count        A real count of executed trace steps for ONE
                           representative input -- not an estimate, but
                           specific to that one input's size.
Nothing here claims a formally verified asymptotic bound. See
docs/decisions.md for the full design writeup.
"""
import json
import re

from execution.sandbox import run_code
from execution.tracer import trace_code
from logic.analysis import structural_estimate

EXISTING_TESTS_TIMEOUT = 5
GROWTH_CURVE_TIMEOUT = 3
TRACE_STEP_CAP_NOTE = (
    "Reached the trace step cap before finishing -- the real operation count for this input "
    "is higher than shown."
)


def _fn_name(function_signature):
    match = re.match(r"\s*def\s+(\w+)\s*\(", function_signature or "")
    return match.group(1) if match else None


def _run_benchmark_harness(code, harness_tail, timeout):
    """Runs `code` followed by `harness_tail` (which must print exactly one
    JSON object between the two markers) in the sandbox. Returns the
    parsed dict, or a dict with an "error" key if the run crashed, timed
    out, or produced nothing parseable -- callers turn that into an
    honest per-candidate/per-size gap rather than letting one bad run take
    the whole comparison down."""
    full = code.rstrip() + "\n\n" + harness_tail
    result = run_code(full, timeout=timeout)
    stdout = result["stdout"]
    if "__TV_BENCH_START__" in stdout and "__TV_BENCH_END__" in stdout:
        payload = stdout.split("__TV_BENCH_START__")[1].split("__TV_BENCH_END__")[0].strip()
        try:
            return json.loads(payload)
        except json.JSONDecodeError:
            pass
    return {
        "error": True,
        "timed_out": result.get("timed_out", False),
        "stderr": (result.get("stderr") or "")[-500:],
    }


def empirical_on_existing_cases(code, function_signature, test_cases):
    """Times + measures peak memory for each of this problem's own seeded
    test cases (same inputs the Complexity tab already times, this just
    also captures memory). One sandboxed call covers every case."""
    fn_name = _fn_name(function_signature)
    if fn_name is None or not test_cases:
        return {"points": [], "note": "No test cases available to time against."}

    harness = (
        "import time, json as __tv_json, resource as __tv_resource\n"
        f"__tv_cases = {test_cases!r}\n"
        "__tv_points = []\n"
        "for __tv_case in __tv_cases:\n"
        "    __tv_start = time.perf_counter()\n"
        f"    {fn_name}(*__tv_case['args'])\n"
        "    __tv_elapsed = time.perf_counter() - __tv_start\n"
        "    __tv_size = len(__tv_case['args'][0]) if __tv_case['args'] and hasattr(__tv_case['args'][0], '__len__') else None\n"
        "    __tv_points.append({'input_size': __tv_size, 'seconds': __tv_elapsed,\n"
        "                         'peak_kb': __tv_resource.getrusage(__tv_resource.RUSAGE_SELF).ru_maxrss})\n"
        "print('__TV_BENCH_START__')\n"
        "print(__tv_json.dumps({'points': __tv_points}))\n"
        "print('__TV_BENCH_END__')\n"
    )
    out = _run_benchmark_harness(code, harness, EXISTING_TESTS_TIMEOUT)
    if out.get("error"):
        return {
            "points": [],
            "note": "Could not measure timing -- this code may crash or hang on one of the test cases.",
        }
    out["note"] = (
        "Wall-clock time and peak memory on this problem's own test cases -- real "
        "measurements, but only at whatever sizes those cases happen to use, not a "
        "growth-curve fit. See growth_curve for that."
    )
    return out


def growth_curve(code, function_signature, generator_source, sizes):
    """Times + measures peak memory against synthetically generated input
    at each size in `sizes`. One sandboxed call per size, so a size that
    times out doesn't take the others down with it."""
    fn_name = _fn_name(function_signature)
    points = []
    for n in sizes:
        harness = (
            "import time, json as __tv_json, resource as __tv_resource\n"
            f"{generator_source}\n"
            f"__tv_args = generate({n})\n"
            "__tv_start = time.perf_counter()\n"
            f"{fn_name}(*__tv_args)\n"
            "__tv_elapsed = time.perf_counter() - __tv_start\n"
            "print('__TV_BENCH_START__')\n"
            "print(__tv_json.dumps({'n': " + repr(n) + ", 'seconds': __tv_elapsed,\n"
            "    'peak_kb': __tv_resource.getrusage(__tv_resource.RUSAGE_SELF).ru_maxrss}))\n"
            "print('__TV_BENCH_END__')\n"
        )
        out = _run_benchmark_harness(code, harness, GROWTH_CURVE_TIMEOUT)
        if out.get("error"):
            points.append({"n": n, "seconds": None, "peak_kb": None, "timed_out": out.get("timed_out", False)})
        else:
            points.append(out)
    return {
        "points": points,
        "note": (
            f"Timed on synthetically generated input at n = {sizes} -- real measurements, not "
            "a fitted curve. A candidate that times out at a given size is shown as exactly "
            "that (it became impractical there), not a fabricated number."
        ),
    }


def operation_count(code, function_signature, sample_args):
    """Number of trace steps executed for ONE representative input --
    reuses the tracer verbatim rather than building separate
    instrumentation. Specific to that one input's size, not a general
    count."""
    fn_name = _fn_name(function_signature)
    if fn_name is None:
        return {"count": None, "note": "Could not determine the function name to trace."}
    augmented = code.rstrip() + f"\n\n{fn_name}(*{sample_args!r})\n"
    result = trace_code(augmented)
    if result["status"] == "crashed":
        return {"count": None, "note": "Could not trace this code to count operations."}
    return {
        "count": len(result["steps"]),
        "truncated": result["status"] == "truncated",
        "note": (
            TRACE_STEP_CAP_NOTE
            if result["status"] == "truncated"
            else "Number of executed trace steps for this one input -- a real count, not an "
                 "estimate, but specific to this input's size."
        ),
    }


def compare_candidate(code, function_signature, test_cases, sample_args, growth_generator=None, growth_sizes=None):
    """Bundles structural + empirical(existing tests) + operation count,
    and growth-curve timing when a generator is supplied, for ONE
    candidate's code."""
    fn_name = _fn_name(function_signature)
    structural = structural_estimate(code, fn_name) if fn_name else {"error": "Could not determine function name"}
    result = {
        "structural": structural,
        "empirical_existing_tests": empirical_on_existing_cases(code, function_signature, test_cases),
        "operation_count": operation_count(code, function_signature, sample_args),
    }
    if growth_generator and growth_sizes:
        result["growth_curve"] = growth_curve(code, function_signature, growth_generator, growth_sizes)
    else:
        result["growth_curve"] = None
    return result
