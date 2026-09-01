"""
Runs a student's submitted code against a problem's stored test cases,
inside the same sandbox used for plain execution (Milestone 1's
sandbox.py). The comparison logic (exact / unordered_list /
unordered_list_of_lists) lives here since it needs to run INSIDE the
sandboxed subprocess (the submission defines the function; we can't call
it from the parent process without re-implementing the whole sandbox).
"""
import json
import re

from execution.sandbox import run_code

_COMPARE_HELPERS = '''
def __traceviz_compare(actual, expected, mode):
    if mode == "float_close":
        # A handful of Hard/Advanced problems (e.g. Median of Two Sorted
        # Arrays) have a float answer that can legitimately be computed via
        # a different but mathematically-equivalent sequence of operations,
        # producing a tiny floating-point rounding difference from the
        # seeded reference solution's exact bit pattern. Exact "==" would
        # unfairly fail a correct submission in that case, so this mode
        # tolerates a very small epsilon instead.
        import math
        try:
            return math.isclose(actual, expected, rel_tol=1e-9, abs_tol=1e-9)
        except TypeError:
            return actual == expected
    if mode == "unordered_list":
        try:
            return sorted(actual) == sorted(expected)
        except TypeError:
            return sorted(actual, key=repr) == sorted(expected, key=repr)
    if mode == "unordered_list_of_lists":
        norm_a = sorted((list(x) for x in actual), key=lambda x: (len(x), repr(x)))
        norm_b = sorted((list(x) for x in expected), key=lambda x: (len(x), repr(x)))
        return norm_a == norm_b
    if mode == "unordered_list_of_sorted_lists":
        # Like unordered_list_of_lists, but also ignores element order WITHIN
        # each sublist -- for problems like Group Anagrams where neither the
        # group order nor the order of items inside a group is meaningful.
        try:
            norm_a = sorted((sorted(x) for x in actual), key=lambda x: (len(x), x))
            norm_b = sorted((sorted(x) for x in expected), key=lambda x: (len(x), x))
        except TypeError:
            norm_a = sorted((sorted(x, key=repr) for x in actual), key=lambda x: (len(x), repr(x)))
            norm_b = sorted((sorted(x, key=repr) for x in expected), key=lambda x: (len(x), repr(x)))
        return norm_a == norm_b
    return actual == expected
'''

_RUNNER_TEMPLATE = '''
import json as __traceviz_json

__traceviz_results = []
for __tv_i, __tv_case in enumerate(__TRACEVIZ_TEST_CASES__):
    __tv_args = __tv_case["args"]
    __tv_expected = __tv_case["expected"]
    try:
        __tv_actual = {fn_name}(*__tv_args)
        __tv_passed = __traceviz_compare(__tv_actual, __tv_expected, "{comparison_mode}")
        __traceviz_results.append({{
            "index": __tv_i, "passed": __tv_passed,
            "actual": __tv_actual, "expected": __tv_expected,
            "args": __tv_args, "error": None,
        }})
    except Exception as __tv_e:
        __traceviz_results.append({{
            "index": __tv_i, "passed": False,
            "actual": None, "expected": __tv_expected,
            "args": __tv_args, "error": f"{{type(__tv_e).__name__}}: {{__tv_e}}",
        }})

print("__TRACEVIZ_RESULTS_START__")
print(__traceviz_json.dumps(__traceviz_results))
print("__TRACEVIZ_RESULTS_END__")
'''


def _extract_function_name(function_signature: str) -> str:
    match = re.match(r"\s*def\s+(\w+)\s*\(", function_signature)
    if not match:
        raise ValueError(f"Could not parse function name from: {function_signature!r}")
    return match.group(1)


def run_against_tests(submitted_code: str, function_signature: str, test_cases: list,
                       comparison_mode: str = "exact", timeout: int = 8) -> dict:
    """
    test_cases: list of {"args": [...], "expected": ...}
    Returns: {"results": [...], "stdout": str, "stderr": str, "crashed": bool}
    """
    fn_name = _extract_function_name(function_signature)
    runner = _RUNNER_TEMPLATE.format(fn_name=fn_name, comparison_mode=comparison_mode)
    # Embed as a Python literal (repr), NOT json.dumps: JSON's true/false/null
    # aren't valid Python syntax, so any test case whose expected value is a
    # bool or None would silently crash the generated script with a
    # NameError -- this bit real problems (cycle detection returns
    # True/False, tree-gap inputs use None) the moment such a value showed
    # up. repr() always round-trips to valid, directly-executable Python.
    test_cases_literal = repr(test_cases)

    full_script = (
        submitted_code.rstrip() + "\n\n"
        + _COMPARE_HELPERS + "\n"
        + f"__TRACEVIZ_TEST_CASES__ = {test_cases_literal}\n"
        + runner
    )

    exec_result = run_code(full_script, timeout=timeout)

    stdout = exec_result["stdout"]
    if "__TRACEVIZ_RESULTS_START__" in stdout and "__TRACEVIZ_RESULTS_END__" in stdout:
        payload = stdout.split("__TRACEVIZ_RESULTS_START__")[1].split("__TRACEVIZ_RESULTS_END__")[0].strip()
        try:
            results = json.loads(payload)
            return {"results": results, "stdout": stdout, "stderr": exec_result["stderr"], "crashed": False}
        except json.JSONDecodeError:
            pass

    # Submission crashed before/during the harness (e.g. SyntaxError,
    # NameError from an undefined function, infinite loop timeout).
    return {"results": [], "stdout": stdout, "stderr": exec_result["stderr"], "crashed": True,
            "timed_out": exec_result.get("timed_out", False)}
