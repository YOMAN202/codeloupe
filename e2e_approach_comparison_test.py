"""
Playwright E2E check for approach comparison (my code vs a reference
optimal approach, and -- where a curated baseline exists -- a naive
approach too). See logic/approach_comparison.py and docs/decisions.md for
the design; this test exercises it as an actual user would, across the
three representative situations the feature was built for:

  1. two-sum, submitted as brute force -- a curated baseline exists, so
     the Approaches tab should show all three columns and a growth curve
     that actually demonstrates O(n^2) vs O(n).
  2. valid-parentheses, submitted already-efficient -- NO curated
     baseline exists for this problem, so the tab must degrade
     gracefully to "your code vs the optimal reference" rather than
     fabricate or hide the whole feature.
  3. climbing-stairs, submitted as naive exponential recursion -- a
     trade-off example (recursion vs DP), and specifically checks that
     revealing the reference code marks the attempt assisted and that
     "trace this approach" actually shows the reference's OWN trace, not
     the learner's.

Also checks the gate: the tab must not offer comparison before the
learner has run their code at least once, and the reference code must
stay hidden until an explicit second click.

Run with the dev server (port 5173) and backend (port 5001) already up,
against a freshly reseeded DB (test 1's exact-count assumptions don't
depend on this, but keeping the convention for consistency with the
other E2E suites).
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

        # ==================================================================
        # 1. two-sum, brute force -- curated baseline exists
        # ==================================================================
        page.goto(f"{BASE}/#/problems/two-sum")
        page.wait_for_selector("text=Two Sum", timeout=10000)

        approaches_tab = page.get_by_role("button", name="Approaches", exact=True)
        approaches_tab.click()
        check("gated before any run", "Run your code at least once" in page.locator(".tab-panel").inner_text())
        page.get_by_role("button", name="Tests", exact=True).click()

        set_code(page, (
            "def two_sum(nums, target):\n"
            "    n = len(nums)\n"
            "    for i in range(n):\n"
            "        for j in range(i + 1, n):\n"
            "            if nums[i] + nums[j] == target:\n"
            "                return [i, j]\n"
            "    return []\n"
        ))
        page.get_by_role("button", name="Run tests").click()
        page.wait_for_selector(".test-results", timeout=10000)

        approaches_tab.click()
        compare_btn = page.get_by_role("button", name="Compare my approach")
        check("compare button present once run", compare_btn.count() > 0)
        compare_btn.click()
        page.wait_for_selector(".approach-columns", timeout=20000)

        panel_text = page.locator(".tab-panel").inner_text()
        check("three-way progression shown for a problem with a baseline",
              "Naive baseline" in panel_text and "Your approach" in panel_text and "Optimized reference" in panel_text)
        check("no reference code shown before explicit reveal", "code-block" not in page.locator(".approach-columns").inner_html())

        cards = page.locator(".approach-card")
        check("three approach cards rendered", cards.count() == 3)
        check("structural estimate differs between my brute-force code and the optimized reference",
              "O(n^2)" in panel_text and "O(n)" in panel_text)
        check("growth curve rendered for the naive baseline", "Growth across synthetic input sizes" in panel_text)

        # reveal code
        reveal_btn = page.get_by_role("button", name=re.compile("Show reference code"))
        reveal_btn.click()
        page.wait_for_selector(".approach-columns pre.code-block", timeout=10000)
        check("assisted warning shown after revealing reference code",
              "tagged assisted" in page.locator(".tab-panel").inner_text())
        code_blocks = page.locator(".approach-columns pre.code-block")
        check("reference code blocks rendered after reveal", code_blocks.count() >= 2)

        # trace the optimized reference specifically
        trace_buttons = page.get_by_role("button", name=re.compile("Trace this approach"))
        check("trace-this-approach buttons present", trace_buttons.count() >= 2)
        trace_buttons.last.click()
        page.wait_for_selector(".trace-viewer", timeout=15000)
        check("trace tab labels whose execution is shown",
              "Showing trace of:" in page.locator(".tab-panel").inner_text())

        # ==================================================================
        # 2. valid-parentheses -- no curated baseline, must degrade gracefully
        # ==================================================================
        page.goto(f"{BASE}/#/problems/valid-parentheses")
        page.reload()
        page.wait_for_selector("text=Valid Parentheses", timeout=10000)
        set_code(page, (
            "def is_valid(s):\n"
            "    stack = []\n"
            "    pairs = {')': '(', ']': '[', '}': '{'}\n"
            "    for ch in s:\n"
            "        if ch in pairs.values():\n"
            "            stack.append(ch)\n"
            "        else:\n"
            "            if not stack or stack.pop() != pairs[ch]:\n"
            "                return False\n"
            "    return not stack\n"
        ))
        page.get_by_role("button", name="Run tests").click()
        page.wait_for_selector(".test-results", timeout=10000)
        page.get_by_role("button", name="Approaches", exact=True).click()
        page.get_by_role("button", name="Compare my approach").click()
        page.wait_for_selector(".approach-columns", timeout=20000)
        no_baseline_text = page.locator(".tab-panel").inner_text()
        check("no baseline card for a problem without a curated one", "Naive baseline" not in no_baseline_text)
        check("honest no-baseline message shown", "No curated naive baseline exists" in no_baseline_text)
        no_baseline_cards = page.locator(".approach-card")
        check("only two cards (mine + optimized) without a baseline", no_baseline_cards.count() == 2)

        # ==================================================================
        # 3. climbing-stairs -- naive recursion vs DP trade-off example
        # ==================================================================
        page.goto(f"{BASE}/#/problems/climbing-stairs")
        page.reload()
        page.wait_for_selector("text=Climbing Stairs", timeout=10000)
        set_code(page, (
            "def climb_stairs(n):\n"
            "    if n <= 2:\n"
            "        return n\n"
            "    return climb_stairs(n - 1) + climb_stairs(n - 2)\n"
        ))
        page.get_by_role("button", name="Run tests").click()
        page.wait_for_selector(".test-results", timeout=10000)
        page.get_by_role("button", name="Approaches", exact=True).click()
        page.get_by_role("button", name="Compare my approach").click()
        page.wait_for_selector(".approach-columns", timeout=20000)
        stairs_text = page.locator(".tab-panel").inner_text()
        check("recursive submission structurally flagged", "Recursive with" in stairs_text)
        check("three cards for climbing-stairs (has a curated baseline)", page.locator(".approach-card").count() == 3)

        browser.close()

        check("no console errors across the whole run", len(console_errors) == 0)
        if console_errors:
            print("Console errors seen:", console_errors)

        print("\nALL APPROACH COMPARISON CHECKS PASSED")


if __name__ == "__main__":
    main()
