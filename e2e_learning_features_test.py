"""
Playwright E2E check for the 3 learning features added this phase:
  1. Predict -> Run -> Compare (TraceViewer's optional predict mode)
  2. Better failure analysis (ProblemWorkspace's FailureAnalysis panel + jump-to-trace)
  3. Pattern-recognition practice (ProblemWorkspace's PatternPractice block)

Exercised against BOTH a correct and an intentionally wrong two-sum submission,
per the explicit requirement to test learning features against real success
and real failure, not just the happy path. Run with the dev server (port 5173)
and backend (port 5001) already up.
"""
import re
from playwright.sync_api import sync_playwright

BASE = "http://localhost:5173"
console_errors = []


def check(label, cond):
    print(f"[{'PASS' if cond else 'FAIL'}] {label}")
    assert cond, label


def set_code(page, code):
    page.evaluate("(c) => window.__tracevizEditor.setValue(c)", code)


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.on("console", lambda m: console_errors.append(m.text) if m.type == "error" else None)
        page.on("pageerror", lambda e: console_errors.append(str(e)))

        page.goto(f"{BASE}/#/problems/two-sum")
        page.wait_for_selector("text=Two Sum", timeout=10000)

        # ---- Pattern practice: collapsed by default, guess-then-reveal ----
        toggle = page.get_by_role("button", name=re.compile("Pattern practice"))
        check("pattern practice toggle present", toggle.count() > 0)
        toggle.click()
        page.wait_for_selector(".pattern-choice-grid")
        choices = page.locator(".pattern-choice")
        check("pattern choices rendered", choices.count() > 5)
        # answer not revealed before a guess is made
        reveal_btn = page.get_by_role("button", name="Reveal the actual pattern")
        check("reveal button disabled before a guess", reveal_btn.is_disabled())
        page.get_by_role("button", name="Hash map / set", exact=True).click()
        check("reveal button enabled after a guess", reveal_btn.is_enabled())
        reveal_btn.click()
        page.wait_for_selector(".pattern-reveal")
        check("actual pattern shown after reveal", page.locator(".pattern-reveal").inner_text().find("Actual pattern") != -1)

        # ---- WRONG submission: failure analysis + jump to trace ----
        set_code(page, "def two_sum(nums, target):\n    return []\n")
        page.get_by_role("button", name="Run tests").click()
        page.wait_for_selector(".failure-analysis", timeout=10000)
        fa_text = page.locator(".failure-analysis").inner_text()
        check("failure analysis shows first failing case", "First failing case" in fa_text)
        check("failure analysis shows expected/got", "Expected" in fa_text and "Got" in fa_text)
        check("failure analysis avoids overclaiming the bug", "the bug is" not in fa_text.lower())

        inspect_btn = page.get_by_role("button", name=re.compile("Inspect this case in the Trace tab"))
        check("inspect-in-trace button present", inspect_btn.count() > 0)
        inspect_btn.click()
        page.wait_for_selector(".trace-viewer", timeout=15000)
        check("jumped to Trace tab", page.locator(".trace-viewer").count() > 0)
        # focusEnd should land on the LAST captured step, not step 1
        step_label = page.locator(".muted:has-text('step ')").first.inner_text()
        m = re.search(r"step (\d+) / (\d+)", step_label)
        check("jump-to-trace lands on final step (focusEnd)", m and m.group(1) == m.group(2))

        # ---- Predict -> Run -> Compare mode ----
        predict_toggle = page.get_by_role("button", name=re.compile("Predict mode"))
        check("predict mode toggle present", predict_toggle.count() > 0)
        predict_toggle.click()
        page.wait_for_selector(".predict-panel")
        # step back so there IS a next step to predict
        back_btn = page.get_by_role("button", name=re.compile("Step back"))
        if back_btn.is_enabled():
            back_btn.click()
        textarea = page.locator(".predict-input")
        textarea.fill("i will move forward")
        reveal_predict = page.get_by_role("button", name="Reveal what actually happens next")
        reveal_predict.click()
        page.wait_for_selector(".predict-reveal")
        predict_text = page.locator(".predict-reveal").inner_text()
        check("predict reveal shows the actual next event", "What actually happened" in predict_text)

        # ---- CORRECT submission: failure analysis should NOT render ----
        page.get_by_role("button", name="Tests", exact=True).click()
        set_code(page, """def two_sum(nums, target):
    seen = {}
    for i, n in enumerate(nums):
        if target - n in seen:
            return [seen[target - n], i]
        seen[n] = i
    return []
""")
        page.get_by_role("button", name="Run tests").click()
        page.wait_for_selector("text=PASS", timeout=10000)
        check("failure analysis absent on all-passing run", page.locator(".failure-analysis").count() == 0)

        check("no console errors across the whole flow", len(console_errors) == 0)

        browser.close()

    print("\nALL LEARNING-FEATURE CHECKS PASSED")


if __name__ == "__main__":
    main()
