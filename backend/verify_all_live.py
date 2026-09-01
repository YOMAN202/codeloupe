"""
Comprehensive live-API verification: for every seeded problem, submit its
OWN reference_solution source through the real /api/problems/<slug>/run
endpoint (the actual sandboxed grading path a learner's submission goes
through) and confirm every test case passes. This is the check that
previously caught two real bugs (json.dumps vs repr for bool/None test
values, and in-place-mutation corrupting seeded inputs) -- neither of
which would have been caught by unit-testing the seed logic alone.
"""
import sys
import requests

BASE = "http://127.0.0.1:5001"

r = requests.get(f"{BASE}/api/problems")
problems = r.json()
print(f"Verifying {len(problems)} problems against the live grading API...")

failures = []
for p in problems:
    slug = p["slug"]
    detail = requests.get(f"{BASE}/api/problems/{slug}").json()
    ref_source = requests.get(f"{BASE}/api/problems/{slug}/solution").json()["solution_code"]
    run_result = requests.post(f"{BASE}/api/problems/{slug}/run", json={"code": ref_source}).json()
    if run_result.get("crashed"):
        failures.append((slug, "CRASHED", run_result.get("stderr", "")[:300]))
        continue
    results = run_result.get("results", [])
    failed_cases = [res for res in results if not res["passed"]]
    if failed_cases:
        failures.append((slug, f"{len(failed_cases)}/{len(results)} cases failed", failed_cases[0]))
    elif not results:
        failures.append((slug, "NO TEST CASES RETURNED", ""))

print(f"\n{len(problems) - len(failures)}/{len(problems)} problems: reference solution passes all its own seeded tests via the live API.")
if failures:
    print(f"\n{len(failures)} FAILURES:")
    for slug, reason, detail in failures:
        print(f"  - {slug}: {reason}")
        print(f"      {detail}")
    sys.exit(1)
else:
    print(f"ALL {len(problems)} REFERENCE SOLUTIONS VERIFIED VIA LIVE GRADING API.")
