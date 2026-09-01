"""
Phase 4: AST-based hints and complexity ESTIMATION (never "detection" --
see docs/decisions.md on why that word choice matters). Two independent,
honestly-labeled signals:

1. Structural: parse the submission's AST, look at loop nesting depth and
   recursion shape. Cheap, fast, sometimes wrong (a loop with an early
   break can be much faster than its nesting suggests).
2. Empirical: actually time the submission against the test cases already
   on file for this problem. This is real measurement, not a fabricated
   number -- but it's timing at whatever sizes the test cases happen to
   use, not a full growth-curve fit across synthetic input sizes (that
   would need a per-problem input generator we don't have time to build
   for all 26 problems -- see docs/decisions.md's scope notes). It's
   still useful signal: if two O(n) test cases and one O(n^2)-shaped
   large case show a suspicious jump, that's worth noticing.
"""
import ast
import time

from execution.sandbox import run_code


def _find_function(tree: ast.AST, name: str):
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == name:
            return node
    return None


def _max_loop_nesting(node: ast.AST) -> int:
    def depth(n, current):
        best = current
        for child in ast.iter_child_nodes(n):
            child_depth = depth(child, current + 1) if isinstance(child, (ast.For, ast.While)) else depth(child, current)
            best = max(best, child_depth)
        return best
    return depth(node, 0)


def _calls_self(node: ast.FunctionDef) -> int:
    """Returns how many times the function calls itself lexically (a rough
    proxy for branching factor -- e.g. naive Fibonacci calls itself twice)."""
    count = 0
    for n in ast.walk(node):
        if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id == node.name:
            count += 1
    return count


def structural_estimate(code: str, function_name: str) -> dict:
    try:
        tree = ast.parse(code)
    except SyntaxError as e:
        return {"error": f"Could not parse code: {e}"}

    fn = _find_function(tree, function_name)
    if fn is None:
        return {"error": f"Could not find a function named '{function_name}' to analyze"}

    nesting = _max_loop_nesting(fn)
    self_calls = _calls_self(fn)

    if self_calls >= 2:
        time_estimate = f"Recursive with {self_calls} self-calls per invocation -- likely exponential (O(2^n)-ish) unless memoized"
    elif self_calls == 1:
        time_estimate = "Recursive with 1 self-call per invocation -- likely O(n) or O(log n) depending on how much the input shrinks each call; check the empirical timing"
    elif nesting == 0:
        time_estimate = "No loops or recursion detected -- likely O(1)"
    elif nesting == 1:
        time_estimate = "One loop level -- likely O(n)"
    elif nesting == 2:
        time_estimate = "Two nested loop levels -- likely O(n^2)"
    else:
        time_estimate = f"{nesting} nested loop levels -- likely O(n^{nesting})"

    return {
        "loop_nesting_depth": nesting,
        "self_recursive_calls": self_calls,
        "structural_time_estimate": time_estimate,
        "caveat": "Structural analysis is a heuristic based on code shape, not proof -- "
                  "an early return/break, short-circuiting, or input-dependent behavior "
                  "can make the real complexity better (or worse) than this suggests.",
    }


def empirical_timing(code: str, function_signature: str, test_cases: list) -> dict:
    """Times the submission against each existing test case's input. Not a
    growth-curve fit -- see module docstring."""
    import re
    match = re.match(r"\s*def\s+(\w+)\s*\(", function_signature)
    fn_name = match.group(1) if match else None
    if fn_name is None or not test_cases:
        return {"timings": [], "note": "No test cases available to time against."}

    timing_harness = code.rstrip() + "\n\n"
    timing_harness += "import time, json as __tv_json\n"
    timing_harness += f"__tv_cases = {test_cases!r}\n"
    timing_harness += "__tv_timings = []\n"
    timing_harness += "for __tv_case in __tv_cases:\n"
    timing_harness += "    __tv_start = time.perf_counter()\n"
    timing_harness += f"    {fn_name}(*__tv_case['args'])\n"
    timing_harness += "    __tv_timings.append({'input_size': len(__tv_case['args'][0]) if __tv_case['args'] and hasattr(__tv_case['args'][0], '__len__') else None, 'seconds': time.perf_counter() - __tv_start})\n"
    timing_harness += "print('__TRACEVIZ_TIMING_START__')\n"
    timing_harness += "print(__tv_json.dumps(__tv_timings))\n"
    timing_harness += "print('__TRACEVIZ_TIMING_END__')\n"

    result = run_code(timing_harness, timeout=10)
    stdout = result["stdout"]
    if "__TRACEVIZ_TIMING_START__" in stdout:
        import json
        payload = stdout.split("__TRACEVIZ_TIMING_START__")[1].split("__TRACEVIZ_TIMING_END__")[0].strip()
        try:
            timings = json.loads(payload)
            return {"timings": timings,
                    "note": "Wall-clock time on your existing test cases, not a synthetic growth-curve fit."}
        except Exception:
            pass
    return {"timings": [], "note": "Could not measure timing (submission may have crashed).", "stderr": result["stderr"]}


def estimate_complexity(code: str, function_signature: str, test_cases: list = None) -> dict:
    import re
    match = re.match(r"\s*def\s+(\w+)\s*\(", function_signature)
    fn_name = match.group(1) if match else ""
    structural = structural_estimate(code, fn_name)
    result = {"structural": structural}
    if test_cases:
        result["empirical"] = empirical_timing(code, function_signature, test_cases)
    return result


# ---------------------------------------------------------- AST-based hint --

def generate_hint_from_code(code: str, problem: dict) -> str:
    """A rung-2 style hint derived from what the learner ACTUALLY wrote,
    per learning-philosophy.md: 'points at where in your specific approach
    the gap is'. Deliberately simple pattern-matching, not a general code
    critic -- see docs/decisions.md."""
    try:
        tree = ast.parse(code)
    except SyntaxError as e:
        return f"Your code has a syntax error before I can analyze it: {e}"

    findings = []

    nesting = _max_loop_nesting(tree)
    if nesting >= 2 and problem.get("expected_time_complexity", "").startswith("O(n)") and "n^2" not in problem.get("expected_time_complexity", ""):
        findings.append(
            f"Your code has {nesting} nested loop levels, but this problem's target complexity is "
            f"{problem.get('expected_time_complexity')}. A nested loop checking 'have I seen this "
            f"combination before' is usually a sign a hashmap/set could replace the inner loop."
        )

    # `x in some_list` inside a loop, where some_list looks like a list built via [] literal or list(...)
    for node in ast.walk(tree):
        if isinstance(node, ast.Compare) and any(isinstance(op, ast.In) for op in node.ops):
            findings.append(
                "You're using `in` to check membership somewhere -- if that's checking against a "
                "list (not a set or dict), each check is O(n), which is often the hidden cost behind "
                "an accidentally-O(n^2) solution. A set gives O(1) average-case membership checks."
            )
            break

    if not any(isinstance(n, ast.Return) for n in ast.walk(tree)):
        findings.append(
            "I don't see a `return` statement anywhere in your function -- if you're using `print()` "
            "to show the answer, remember the automated tests need the value returned, not printed."
        )

    if not findings:
        return ("Nothing obviously off structurally. If tests are still failing, re-check your base "
                "cases and the specific edge cases listed for this problem.")
    return " ".join(findings)
