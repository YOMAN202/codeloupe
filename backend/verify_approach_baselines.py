"""
Verifies the curated brute-force baselines added for approach comparison
(see logic/approach_comparison.py, docs/decisions.md), the same way
verify_all_live.py already verifies every optimal reference_solution:
submit the ACTUAL stored source through the real live grading API and
confirm it passes every one of the problem's own seeded test cases.
Also sanity-checks each problem's growth_curve_generator actually runs
without crashing at every declared size, for both the optimal reference
and the brute-force baseline -- catching a broken generate(n) before a
learner ever hits it from the Approaches tab.
"""
import sys
import requests

BASE = "http://127.0.0.1:5001"

r = requests.get(f"{BASE}/api/problems")
all_problems = r.json()
curated = [p["slug"] for p in
           [requests.get(f"{BASE}/api/problems/{p['slug']}").json() for p in all_problems]
           if p.get("has_approach_baseline")]

print(f"Found {len(curated)} problems with a curated brute-force baseline: {curated}\n")

failures = []
for slug in curated:
    optimal_source = requests.get(f"{BASE}/api/problems/{slug}/solution").json()["solution_code"]

    compare = requests.post(
        f"{BASE}/api/problems/{slug}/approach-comparison",
        json={"code": optimal_source, "reveal_code": True},
    ).json()

    if not compare.get("has_baseline") or not compare.get("brute_force_baseline", {}).get("code"):
        failures.append((slug, "no brute_force_baseline code returned despite has_approach_baseline=1", ""))
        continue
    baseline_source = compare["brute_force_baseline"]["code"]

    # 1. The baseline must pass this problem's own seeded tests, via the
    #    SAME live grading endpoint a learner's own submission goes through.
    run_result = requests.post(f"{BASE}/api/problems/{slug}/run", json={"code": baseline_source}).json()
    if run_result.get("crashed"):
        failures.append((slug, "baseline CRASHED on seeded tests", run_result.get("stderr", "")[:300]))
        continue
    results = run_result.get("results", [])
    failed_cases = [res for res in results if not res["passed"]]
    if failed_cases:
        failures.append((slug, f"baseline failed {len(failed_cases)}/{len(results)} seeded cases", failed_cases[0]))
        continue
    if not results:
        failures.append((slug, "baseline: NO TEST CASES RETURNED", ""))
        continue

    # 2. Both candidates' growth-curve numbers must be real measurements at
    #    every declared size, not silent timeouts/crashes -- a broken
    #    generate(n) would show up here as every point being null.
    for label in ("optimal_reference", "brute_force_baseline"):
        points = compare[label]["growth_curve"]["points"]
        bad = [pt for pt in points if pt.get("seconds") is None]
        if bad:
            failures.append((slug, f"{label} growth_curve has {len(bad)}/{len(points)} unmeasured points", bad))

    print(f"  [OK] {slug}: baseline passes {len(results)}/{len(results)} seeded tests, "
          f"growth curve measured at all sizes for both candidates")

print(f"\n{len(curated) - len(failures)}/{len(curated)} baselines fully verified.")
if failures:
    print(f"\n{len(failures)} FAILURES:")
    for slug, reason, detail in failures:
        print(f"  - {slug}: {reason}")
        print(f"      {detail}")
    sys.exit(1)
else:
    print("ALL CURATED APPROACH-COMPARISON BASELINES VERIFIED VIA LIVE API.")
