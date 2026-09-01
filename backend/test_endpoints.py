"""
Manual end-to-end smoke test for every Phase 1/2/4 API endpoint, run
against the live dev server + freshly seeded DB. Not a pytest suite --
a throwaway verification script per the "test end-to-end before moving
on" development rule. Prints PASS/FAIL per check; exits nonzero on any
failure.
"""
import sys
import requests

BASE = "http://127.0.0.1:5001"
failures = []


def check(label, cond, extra=None):
    status = "PASS" if cond else "FAIL"
    print(f"[{status}] {label}" + (f" -- {extra}" if extra and not cond else ""))
    if not cond:
        failures.append(label)


# ---- health --------------------------------------------------------------
r = requests.get(f"{BASE}/api/health")
check("GET /api/health -> 200", r.status_code == 200, r.text)

# ---- lessons --------------------------------------------------------------
r = requests.get(f"{BASE}/api/lessons")
check("GET /api/lessons -> 200, 45 lessons", r.status_code == 200 and len(r.json()) == 45, r.text[:300])

r = requests.get(f"{BASE}/api/lessons/1")
d = r.json()
check("GET /api/lessons/1 -> has title/exercises/problems", r.status_code == 200 and "title" in d and "exercises_markdown" in d and "problems" in d, d)

r = requests.get(f"{BASE}/api/lessons/8")
d = r.json()
check("GET /api/lessons/8 -> has >=1 linked problem (Two Sum day)", r.status_code == 200 and len(d.get("problems", [])) >= 1, d)

r = requests.get(f"{BASE}/api/lessons/999")
check("GET /api/lessons/999 -> 404", r.status_code == 404)

# ---- problems ---------------------------------------------------------
r = requests.get(f"{BASE}/api/problems")
problems = r.json()
check("GET /api/problems -> 200, 76 problems (32 original + 38 expansion + 6 advanced)",
      r.status_code == 200 and len(problems) == 76, len(problems))
check("  every problem has interview_priority in Core/Important/Optional",
      all(p.get("interview_priority") in ("Core", "Important", "Optional") for p in problems),
      {p["slug"] for p in problems if p.get("interview_priority") not in ("Core", "Important", "Optional")})
check("  every problem has estimated_solve_minutes set", all(p.get("estimated_solve_minutes") for p in problems),
      [p["slug"] for p in problems if not p.get("estimated_solve_minutes")])
check("  every problem has a valid path_tier",
      all(p.get("path_tier") in ("core", "extended", "advanced") for p in problems),
      {p["slug"] for p in problems if p.get("path_tier") not in ("core", "extended", "advanced")})
check("  core-tier problems all have a day assigned",
      all(p["day"] is not None for p in problems if p["path_tier"] == "core"),
      [p["slug"] for p in problems if p["path_tier"] == "core" and p["day"] is None])
check("  extended/advanced-tier problems have no day assigned",
      all(p["day"] is None for p in problems if p["path_tier"] in ("extended", "advanced")),
      [p["slug"] for p in problems if p["path_tier"] in ("extended", "advanced") and p["day"] is not None])
check("  no Hard problems outside the advanced tier (Hard must stay strictly optional)",
      all(p["path_tier"] == "advanced" for p in problems if p["difficulty"] == "Hard"),
      [p["slug"] for p in problems if p["difficulty"] == "Hard" and p["path_tier"] != "advanced"])
r = requests.get(f"{BASE}/api/problems?path_tier=advanced")
advanced_problems = r.json()
check("GET /api/problems?path_tier=advanced -> filters to exactly the 6 Hard challenges",
      r.status_code == 200 and len(advanced_problems) == 6 and all(p["difficulty"] == "Hard" for p in advanced_problems),
      len(advanced_problems))

r = requests.get(f"{BASE}/api/problems/group-anagrams")
ga = r.json()
check("GET group-anagrams -> canonical_reference present, comparison_mode set",
      r.status_code == 200 and "LeetCode" in ga.get("canonical_reference", "") and ga.get("comparison_mode") == "unordered_list_of_sorted_lists",
      ga)

correct_group_anagrams = 'def group_anagrams(strs):\n    groups = {}\n    for s in strs:\n        key = "".join(sorted(s))\n        groups.setdefault(key, []).append(s)\n    return list(groups.values())\n'
r = requests.post(f"{BASE}/api/problems/group-anagrams/run", json={"code": correct_group_anagrams})
result = r.json()
check("POST run group-anagrams (order-independent grading) -> all_passed True", r.status_code == 200 and result.get("all_passed") is True, result)

# ---- non-linear lesson navigation ------------------------------------
r = requests.get(f"{BASE}/api/lessons/30")
lesson30 = r.json()
check("GET /api/lessons/30 -> status defaults to not_started", r.status_code == 200 and lesson30.get("status") == "not_started", lesson30)
check("  has recommended_prerequisites with block/days_done/days_total/satisfied",
      len(lesson30.get("recommended_prerequisites", [])) > 0 and
      all(k in lesson30["recommended_prerequisites"][0] for k in ("block", "days_done", "days_total", "satisfied")),
      lesson30.get("recommended_prerequisites"))

r = requests.put(f"{BASE}/api/lessons/30/progress", json={"status": "in_progress"})
check("PUT lessons/30/progress in_progress -> 200, started_at set", r.status_code == 200 and r.json().get("started_at"), r.json())

r = requests.get(f"{BASE}/api/lessons/30")
check("  lesson 30 now reflects in_progress status", r.json().get("status") == "in_progress", r.json())

r = requests.put(f"{BASE}/api/lessons/8/progress", json={"status": "completed"})
check("PUT lessons/8/progress completed -> 200", r.status_code == 200, r.text)

r = requests.put(f"{BASE}/api/lessons/1/progress", json={"status": "known"})
check("PUT lessons/1/progress known (skip-ahead use case) -> 200", r.status_code == 200, r.text)

r = requests.put(f"{BASE}/api/lessons/5/progress", json={"status": "not-a-real-status"})
check("PUT invalid status -> 400", r.status_code == 400)

r = requests.put(f"{BASE}/api/lessons/9999/progress", json={"status": "completed"})
check("PUT progress for nonexistent day -> 404", r.status_code == 404)

r = requests.get(f"{BASE}/api/progress")
prog2 = r.json()
check("GET /api/progress -> lesson_status_counts reflects updates (>=1 completed, >=1 known, >=1 in_progress)",
      prog2.get("lesson_status_counts", {}).get("completed", 0) >= 1 and
      prog2.get("lesson_status_counts", {}).get("known", 0) >= 1 and
      prog2.get("lesson_status_counts", {}).get("in_progress", 0) >= 1,
      prog2.get("lesson_status_counts"))
check("  resume_lesson points at day 30 (the in_progress one)",
      prog2.get("resume_lesson", {}).get("day") == 30, prog2.get("resume_lesson"))
check("  recommended_next_lesson is the lowest not_started day (day 2, since day 1 was marked known)",
      prog2.get("recommended_next_lesson", {}).get("day") == 2, prog2.get("recommended_next_lesson"))
check("  lessons_overview has all 45 lessons with status", len(prog2.get("lessons_overview", [])) == 45,
      len(prog2.get("lessons_overview", [])))

r = requests.get(f"{BASE}/api/problems?day=8")
check("GET /api/problems?day=8 -> filters correctly", r.status_code == 200 and all(p["day"] == 8 for p in r.json()), r.json())

slug = "two-sum"
r = requests.get(f"{BASE}/api/problems/{slug}")
problem = r.json()
check(f"GET /api/problems/{slug} -> has function_signature/starter_code/visible_test_cases",
      r.status_code == 200 and "function_signature" in problem and len(problem.get("visible_test_cases", [])) > 0,
      problem)

r = requests.get(f"{BASE}/api/problems/does-not-exist")
check("GET /api/problems/does-not-exist -> 404", r.status_code == 404)

# ---- hints ----------------------------------------------------------------
for rung in (1, 2, 3):
    r = requests.get(f"{BASE}/api/problems/{slug}/hints/{rung}")
    check(f"GET /api/problems/{slug}/hints/{rung} -> 200, has content", r.status_code == 200 and len(r.json().get("content", "")) > 0, r.text)

r = requests.get(f"{BASE}/api/problems/{slug}/hints/4")
check("GET hints/4 (invalid rung) -> 400", r.status_code == 400)

# ---- solution ---------------------------------------------------------
r = requests.get(f"{BASE}/api/problems/{slug}/solution")
sol = r.json()
check(f"GET /api/problems/{slug}/solution -> has solution_code", r.status_code == 200 and "def " in sol.get("solution_code", ""), sol)

# ---- run (correct submission) ------------------------------------------
correct_two_sum = """
def two_sum(nums, target):
    seen = {}
    for i, n in enumerate(nums):
        if target - n in seen:
            return [seen[target - n], i]
        seen[n] = i
    return []
"""
r = requests.post(f"{BASE}/api/problems/{slug}/run", json={"code": correct_two_sum})
result = r.json()
check("POST run correct two-sum -> all_passed True", r.status_code == 200 and result.get("all_passed") is True, result)

# ---- run (wrong submission) --------------------------------------------
wrong_two_sum = "def two_sum(nums, target):\n    return [0, 0]\n"
r = requests.post(f"{BASE}/api/problems/{slug}/run", json={"code": wrong_two_sum})
result = r.json()
check("POST run wrong two-sum -> all_passed False, some failures", r.status_code == 200 and result.get("all_passed") is False and any(not x["passed"] for x in result["results"]), result)

# ---- run (crashing submission) -----------------------------------------
crashing = "def two_sum(nums, target):\n    return 1 / 0\n"
r = requests.post(f"{BASE}/api/problems/{slug}/run", json={"code": crashing})
result = r.json()
check("POST run crashing two-sum -> errors reported per-case, all_passed False",
      r.status_code == 200 and result.get("all_passed") is False and all(x.get("error") for x in result["results"]), result)

# ---- unordered_list comparison mode (top-k-frequent) -------------------
r = requests.get(f"{BASE}/api/problems/top-k-frequent")
tk = r.json()
check("GET top-k-frequent -> comparison_mode unordered_list", r.status_code == 200 and tk.get("comparison_mode") == "unordered_list", tk)

# ---- hint-from-code (AST) ----------------------------------------------
nested_loop_code = """
def two_sum(nums, target):
    for i in range(len(nums)):
        for j in range(len(nums)):
            if i != j and nums[i] + nums[j] == target:
                return [i, j]
    return []
"""
r = requests.post(f"{BASE}/api/problems/{slug}/hint-from-code", json={"code": nested_loop_code})
hc = r.json()
check("POST hint-from-code (O(n^2) brute force) -> mentions nested loops", r.status_code == 200 and "nested" in hc.get("hint", "").lower(), hc)

# ---- complexity-estimate ------------------------------------------------
r = requests.post(f"{BASE}/api/problems/{slug}/complexity-estimate", json={"code": correct_two_sum})
ce = r.json()
check("POST complexity-estimate -> has structural + empirical", r.status_code == 200 and "structural" in ce and "empirical" in ce, ce)
check("  structural analysis correctly reads O(n) for hashmap two-sum",
      "O(n)" in ce.get("structural", {}).get("structural_time_estimate", ""), ce.get("structural"))

r = requests.post(f"{BASE}/api/problems/{slug}/complexity-estimate", json={"code": nested_loop_code})
ce2 = r.json()
check("  structural analysis correctly reads O(n^2) for brute force nested loops",
      "n^2" in ce2.get("structural", {}).get("structural_time_estimate", ""), ce2.get("structural"))

# ---- attempts + revision scheduling -------------------------------------
r = requests.post(f"{BASE}/api/attempts", json={
    "slug": slug, "submitted_code": correct_two_sum, "passed": True,
    "hints_used": 0, "max_hint_rung_seen": 0, "solution_revealed": False,
    "time_taken_seconds": 120,
})
att = r.json()
check("POST /api/attempts (independent pass) -> is_independent True, next_due_date set",
      r.status_code == 200 and att.get("is_independent") is True and att.get("next_due_date"), att)

r = requests.post(f"{BASE}/api/attempts", json={
    "slug": "valid-parentheses", "submitted_code": "def is_valid(s): return True",
    "passed": True, "hints_used": 2, "max_hint_rung_seen": 2, "solution_revealed": False,
    "time_taken_seconds": 400,
})
att2 = r.json()
check("POST /api/attempts (assisted pass) -> is_independent False, result assisted",
      r.status_code == 200 and att2.get("is_independent") is False and att2.get("result") == "assisted", att2)

# ---- progress dashboard ---------------------------------------------------
r = requests.get(f"{BASE}/api/progress")
prog = r.json()
check("GET /api/progress -> 200, reflects logged attempts",
      r.status_code == 200 and prog.get("total_problems_attempted") == 2 and prog.get("independent_solves") == 1,
      prog)
check("  progress includes weak/strong topics + revision queue keys",
      all(k in prog for k in ("top_weaknesses", "top_strengths", "problems_due_for_revision", "current_streak_days")),
      prog)

# ---- trace (Phase 2) -------------------------------------------------
trace_code_sample = """
def factorial(n):
    if n <= 1:
        return 1
    return n * factorial(n - 1)

print(factorial(4))
"""
r = requests.post(f"{BASE}/api/trace", json={"code": trace_code_sample})
tr = r.json()
check("POST /api/trace -> not crashed, has steps", r.status_code == 200 and tr.get("crashed") is False and len(tr.get("steps", [])) > 0, tr if tr.get("crashed") else {"n_steps": len(tr.get("steps", []))})
check("  trace captures recursive call_depth increasing", any(s.get("call_depth", 0) >= 4 for s in tr.get("steps", [])), [s["call_depth"] for s in tr.get("steps", []) if s["event"] == "call"])
check("  trace captures return events with return_value", any(s["event"] == "return" and s.get("return_value") is not None for s in tr.get("steps", [])), None)

# ---- plain run (Milestone 1 endpoint still works) ----------------------
r = requests.post(f"{BASE}/api/run", json={"code": "print('hello traceviz')"})
check("POST /api/run -> 200, stdout has output", r.status_code == 200 and "hello traceviz" in r.json().get("stdout", ""), r.json())

print()
if failures:
    print(f"{len(failures)} FAILURE(S):")
    for f in failures:
        print(f"  - {f}")
    sys.exit(1)
else:
    print("ALL CHECKS PASSED")
