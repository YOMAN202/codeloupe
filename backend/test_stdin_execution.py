"""
Standalone tests for stdin support in execution/sandbox.py and
execution/tracer.py -- added so ordinary `input()` / `sys.stdin.readline()`
/ `sys.stdin.read()` code works in both Run and Trace, instead of every
program that reads input immediately failing with EOFError (stdin was
never connected to the subprocess before this).

Pure-function level (calls run_code()/trace_code() directly, no server) --
fast, and covers the 12 specific cases from the stdin/sys audit:
  1. Basic stdin (single input())
  2. Multiline stdin (multiple lines available)
  3. Multiple input() calls consuming successive lines
  4. Empty stdin + input() -> honest EOFError, not a hang or crash
  5. `import sys; input = sys.stdin.readline` boilerplate -- Run
  6. Same boilerplate -- Trace
  7. Multiline stdin during Trace
  8. Dangerous imports (os) still rejected regardless of stdin (safety_check,
     not run_code/trace_code -- exercised here at the AST-filter level for
     completeness; the live end-to-end version is in test_endpoints.py)
  9. Existing problem test-case execution (test_runner.py) is untouched --
     NOT exercised here (different module entirely, no stdin concept) --
     see verify_all_live.py / test_endpoints.py's problem-run checks for
     that coverage; noted explicitly per "flag anything not tested here."
 10. All existing tests still passing -- meta-requirement, satisfied by
     running test_safety_check.py / test_endpoints.py / this file together,
     not a single case in this file.
 11. Trailing-newline / no-trailing-newline stdin both work
 12. Larger multi-value stdin (many lines) works

Run directly: `python3 test_stdin_execution.py` from backend/.
"""
import sys

sys.path.insert(0, ".")
from execution.sandbox import run_code
from execution.tracer import trace_code
from execution.safety_check import find_safety_violation

FAILURES = []


def check(label, condition, detail=""):
    status = "PASS" if condition else "FAIL"
    print(f"[{status}] {label}" + (f" -- {detail}" if detail else ""))
    if not condition:
        FAILURES.append(label)


print("=== 1. Basic stdin ===")
r = run_code("n = int(input())\nprint(n * 2)", stdin="21\n")
check("single input() reads the given line", r["stdout"].strip() == "42", r)

print("\n=== 2. Multiline stdin ===")
r = run_code("a = input()\nb = input()\nprint(a, b)", stdin="hello\nworld\n")
check("two input() calls read two separate lines in order", r["stdout"].strip() == "hello world", r)

print("\n=== 3. Multiple input() calls (3+) ===")
r = run_code(
    "vals = [input() for _ in range(3)]\nprint(','.join(vals))",
    stdin="1\n2\n3\n",
)
check("three sequential input() calls via list comprehension", r["stdout"].strip() == "1,2,3", r)

print("\n=== 4. Empty stdin -> honest EOFError, not a hang ===")
r = run_code("n = input()\nprint(n)", stdin="")
check("no stdin provided + input() -> process exits non-zero", r["exit_code"] not in (0, None), r)
check("stderr names EOFError specifically (not silently manufactured input)", "EOFError" in r["stderr"], r["stderr"])
check("run_code does not report a timeout for this (fails fast, doesn't hang)", r["timed_out"] is False, r)

r_none = run_code("n = input()\nprint(n)")  # stdin left at its default (None)
check("stdin=None (default, e.g. from any caller that doesn't pass one) behaves identically to stdin=''",
      r_none["stderr"].find("EOFError") != -1 and r_none["timed_out"] is False, r_none)

print("\n=== 5. `import sys; input = sys.stdin.readline` boilerplate -- Run ===")
boilerplate = "import sys\ninput = sys.stdin.readline\nn = int(input())\nprint(n + 1)"
assert find_safety_violation(boilerplate) is None, "boilerplate must pass the safety filter first"
r = run_code(boilerplate, stdin="10\n")
check("sys.stdin.readline boilerplate runs and reads stdin correctly", r["stdout"].strip() == "11", r)

print("\n=== 6. Same boilerplate -- Trace ===")
t = trace_code(boilerplate, stdin="10\n")
check("trace_code completes (not crashed/runtime_error) with the boilerplate", t["status"] == "completed", t)
check("trace captured at least one step", len(t.get("steps", [])) > 0, t)

print("\n=== 7. Multiline stdin during Trace ===")
t = trace_code("a = input()\nb = input()\nprint(a + b)", stdin="foo\nbar\n")
check("trace with two input() calls completes", t["status"] == "completed", t)
check("trace's own stdout capture (via stderr/steps) shows no crash", t.get("error") is None, t)

print("\n=== 8. Dangerous imports still rejected regardless of stdin ===")
check("import os is still rejected by the safety filter",
      find_safety_violation("import os\nos.listdir('.')") is not None, "")
check("sys.modules os-bypass is still rejected", find_safety_violation("import sys\nsys.modules['os']") is not None, "")
check("bare `import sys` with no dangerous attribute access is now ALLOWED",
      find_safety_violation("import sys\nprint(sys.argv)") is None, "")

print("\n=== 9. Problem test-case execution (test_runner.py) ===")
print("[SKIPPED HERE -- not this module's concern] run_against_tests() calls fn(*args) "
      "directly and has no stdin parameter by design; unchanged by this work. "
      "See test_endpoints.py's /api/problems/<slug>/run checks and verify_all_live.py "
      "for that coverage instead.")

print("\n=== 11. Trailing-newline / no-trailing-newline stdin ===")
r = run_code("n = int(input())\nprint(n)", stdin="7\n")
check("stdin WITH trailing newline works", r["stdout"].strip() == "7", r)
r = run_code("n = int(input())\nprint(n)", stdin="7")
check("stdin WITHOUT trailing newline also works (input() still gets the line)", r["stdout"].strip() == "7", r)

print("\n=== 12. Larger multi-value stdin ===")
lines = "\n".join(str(i) for i in range(1, 51)) + "\n"
r = run_code("total = 0\nfor _ in range(50):\n    total += int(input())\nprint(total)", stdin=lines)
check("50 sequential input() calls sum correctly", r["stdout"].strip() == str(sum(range(1, 51))), r)

print("\n=== extra: code that never reads input() ignores unused stdin harmlessly ===")
r = run_code("print('no input needed')", stdin="this is never read\n")
check("unused stdin does not affect a program that never calls input()",
      r["stdout"].strip() == "no input needed" and r["exit_code"] == 0, r)

print("\n=== extra: sys.stdin.read() (whole-input form, not just readline) ===")
r = run_code("import sys\ndata = sys.stdin.read()\nprint(len(data.splitlines()))", stdin="a\nb\nc\n")
check("sys.stdin.read() sees the full multiline input", r["stdout"].strip() == "3", r)

print()
if FAILURES:
    print(f"{len(FAILURES)} FAILURE(S):")
    for f in FAILURES:
        print(" -", f)
    sys.exit(1)
else:
    print("ALL STDIN/EXECUTION TESTS PASSED")
