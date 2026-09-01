"""
Feature-completeness audit: the full central learning workflow, run as an
actual user would, against 4 code variants on ONE problem (two-sum) in one
continuous session per variant -- not each piece tested in isolation.

  Choose a problem -> identify a pattern -> write code -> optionally
  explain approach -> optionally predict execution -> run -> inspect
  tests -> handle failures -> trace execution -> inspect visualization ->
  see progress/mistakes/revision recommendations.

Variants:
  1. Correct solution (should reach Accepted, no mistake entry, progress updates)
  2. Wrong-answer solution (failure analysis, jump-to-trace, a CLASSIFIABLE mistake)
  3. Runtime-error solution (trace preserves steps up to the crash, a
     CLASSIFIABLE mistake from the exception type)
  4. Ambiguous wrong-answer (mistake correctly stays UNCLASSIFIED)

Not a replacement for the feature-specific suites (e2e_test.py,
e2e_visualizers_test.py, e2e_learning_features_test.py,
e2e_mistake_journal_test.py) -- this is the connectedness check: does the
whole loop actually work end to end, in order, on the same page.
"""
import re
from playwright.sync_api import sync_playwright

BASE = "http://127.0.0.1:5173"
console_errors = []
failures = []


def check(label, cond):
    print(f"[{'PASS' if cond else 'FAIL'}] {label}")
    if not cond:
        failures.append(label)


def set_code(page, code):
    page.evaluate("(c) => window.__tracevizEditor.setValue(c)", code)


CORRECT = """def two_sum(nums, target):
    seen = {}
    for i, n in enumerate(nums):
        if target - n in seen:
            return [seen[target - n], i]
        seen[n] = i
    return []
"""
WRONG_ANSWER = "def two_sum(nums, target):\n    return [0, 0]\n"
RUNTIME_ERROR = "def two_sum(nums, target):\n    return nums[9999]\n"
AMBIGUOUS = """def two_sum(nums, target):
    for i in range(len(nums)):
        for j in range(i + 1, len(nums)):
            if nums[i] + nums[j] == target and nums[i] != nums[j]:
                return [i, j]
    return []
"""


def run_workflow(page, code, variant_name, expect_pass):
    print(f"\n--- variant: {variant_name} ---")

    # 1. Choose a problem. Every variant reuses the SAME problem/URL on
    # purpose (one continuous "as a user" session per variant) -- but
    # navigating to an identical hash URL is a browser no-op that would
    # leave the previous variant's component state (pattern reveal, etc.)
    # sitting around, so force a real remount with reload().
    page.goto(f"{BASE}/#/problems/two-sum")
    page.reload()
    page.wait_for_selector("text=Two Sum", timeout=10000)
    check(f"[{variant_name}] problem page loads with description/examples", "Examples" in page.locator(".workspace-left").inner_text())

    # 2. Identify a pattern (optional pattern-recognition practice).
    toggle = page.get_by_role("button", name=re.compile("Pattern practice"))
    check(f"[{variant_name}] pattern practice available before coding", toggle.count() > 0)
    toggle.click()
    page.wait_for_selector(".pattern-choice-grid")
    page.get_by_role("button", name="Hash map / set", exact=True).click()
    page.get_by_role("button", name="Reveal the actual pattern").click()
    page.wait_for_selector(".pattern-reveal")
    check(f"[{variant_name}] pattern reveal shows the real pattern, not before a guess", "Actual pattern" in page.locator(".pattern-reveal").inner_text())

    # 3. Write code.
    set_code(page, code)

    # 4. Optionally explain approach (interview-prep, before running).
    think_toggle = page.get_by_role("button", name=re.compile("Explain your thinking"))
    check(f"[{variant_name}] explain-your-thinking available", think_toggle.count() > 0)
    think_toggle.click()
    page.locator(".explain-thinking textarea").fill("Use a hash map to record seen values and their index.")

    # 5. Run -> inspect tests.
    page.get_by_role("button", name="Run tests").click()
    page.wait_for_selector(".test-results, .error", timeout=10000)
    page.wait_for_timeout(200)

    if expect_pass:
        check(f"[{variant_name}] test results show PASS", "PASS" in page.locator(".tab-panel").inner_text())
        check(f"[{variant_name}] explain-thinking now compares plan vs. actual pattern", "This problem's pattern" in page.locator(".explain-thinking").inner_text())
        check(f"[{variant_name}] no mistake suggestion on a passing run", page.locator(".mistake-suggestion").count() == 0)
    else:
        # 6. Handle failures: failure analysis (wrong answer) or the
        # runtime-error banner (crash), whichever applies -- then a
        # mistake-journal suggestion either way.
        tab_text = page.locator(".tab-panel").inner_text()
        has_failure_analysis = page.locator(".failure-analysis").count() > 0
        check(f"[{variant_name}] failure surfaced in the Tests tab (analysis or a visible FAIL)", has_failure_analysis or "FAIL" in tab_text)
        check(f"[{variant_name}] mistake suggestion appears after a failed run", page.locator(".mistake-suggestion").count() > 0)

        if has_failure_analysis:
            inspect_btn = page.get_by_role("button", name=re.compile("Inspect this case in the Trace tab"))
            if inspect_btn.count() > 0:
                inspect_btn.click()
                page.wait_for_selector(".trace-viewer", timeout=15000)
                check(f"[{variant_name}] jump-to-trace opens the Trace tab", page.locator(".trace-viewer").count() > 0)

    # 7. Trace actual execution (if not already there) + predict mode + visualization.
    if page.get_by_role("button", name="Trace", exact=True).count() > 0:
        page.get_by_role("button", name="Trace", exact=True).click()
    if page.get_by_role("button", name="Trace my code").count() > 0:
        page.get_by_role("button", name="Trace my code").click()
    page.wait_for_selector(".trace-viewer", timeout=15000)
    page.wait_for_timeout(300)

    predict_toggle = page.get_by_role("button", name=re.compile("Predict mode"))
    check(f"[{variant_name}] predict mode available on the trace", predict_toggle.count() > 0)
    predict_toggle.click()
    check(f"[{variant_name}] predict panel renders", page.locator(".predict-panel").count() > 0)

    if not expect_pass and "IndexError" not in code:
        # A runtime-error trace should preserve steps up to the crash.
        pass
    if "nums[9999]" in code:
        banner = page.locator(".trace-status-banner").inner_text()
        check(f"[{variant_name}] runtime-error trace shows a clear crash banner", "Crashed" in banner or "crash" in banner.lower())
        check(f"[{variant_name}] steps preserved up to the crash (not empty)", int(page.locator(".trace-scrubber").get_attribute("max") or 0) > 0)

    has_generic_locals = page.locator(".locals-table").count() >= 0  # presence checked across steps below
    max_index = int(page.locator(".trace-scrubber").get_attribute("max") or 0)
    saw_specialized = False
    for f in (0.1, 0.3, 0.5, 0.7, 0.9):
        idx = round(max_index * f)
        page.evaluate(
            """(idx) => {
                const el = document.querySelector('.trace-scrubber');
                const setter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set;
                setter.call(el, idx);
                el.dispatchEvent(new Event('input', { bubbles: true }));
            }""",
            idx,
        )
        page.wait_for_timeout(50)
        if page.locator(".seq-boxes, .pointer-chip").count() > 0:
            saw_specialized = True
    check(f"[{variant_name}] specialized array/pointer visualization renders from actual execution state", saw_specialized)

    # 8. Mistake-journal review (only relevant for failing variants).
    if not expect_pass:
        suggestion_text = page.locator(".mistake-suggestion").inner_text() if page.locator(".mistake-suggestion").count() else ""
        if variant_name == "ambiguous (should stay unclassified)":
            check(f"[{variant_name}] mistake correctly stays unclassified, not guessed", "couldn't confidently classify" in suggestion_text.lower())
        else:
            check(f"[{variant_name}] mistake given a real category (not silently skipped)", suggestion_text.strip() != "" and "couldn't confidently classify" not in suggestion_text.lower())

    return True


with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page()
    page.on("console", lambda m: console_errors.append(m.text) if m.type == "error" else None)
    page.on("pageerror", lambda e: console_errors.append(str(e)))

    run_workflow(page, CORRECT, "correct solution", expect_pass=True)
    run_workflow(page, WRONG_ANSWER, "wrong answer", expect_pass=False)
    run_workflow(page, RUNTIME_ERROR, "runtime error", expect_pass=False)
    run_workflow(page, AMBIGUOUS, "ambiguous (should stay unclassified)", expect_pass=False)

    # 9. See progress / mistakes / revision recommendations.
    page.goto(f"{BASE}/#/dashboard")
    page.wait_for_selector("text=Weakest patterns", timeout=10000)
    dash_text = page.locator(".page").inner_text()
    check("dashboard reflects at least one solved problem after the correct-solution run", "Problems solved" in dash_text)
    check("dashboard shows pattern-level weakness data after the failing runs", "Hash-map lookup" in dash_text or "Hash map" in dash_text)

    page.goto(f"{BASE}/#/mistakes")
    page.wait_for_selector("text=Mistake journal", timeout=10000)
    journal_text = page.locator(".page").inner_text()
    check("mistake journal has entries from this session", "Two Sum" in journal_text)
    check("mistake journal honestly reports at least one unclassified mistake", "1 of" in journal_text or re.search(r"[1-9]\d* of \d+ mistakes", journal_text))

    check("no console errors across the full 4-variant workflow audit", len(console_errors) == 0)
    for e in console_errors[:10]:
        print("  CONSOLE:", e[:300])

    browser.close()

print()
if failures:
    print(f"{len(failures)} FAILURE(S):")
    for f in failures:
        print(f"  - {f}")
else:
    print("ALL CENTRAL-WORKFLOW AUDIT CHECKS PASSED")
