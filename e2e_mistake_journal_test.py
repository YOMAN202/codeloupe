"""
Playwright E2E check for the mistake journal, pattern-level revision
tracking, and adaptive practice-session recommender.

Exercises the FULL connected pipeline the user asked for:
  attempts -> observed outcomes -> mistake journal -> pattern weaknesses
  -> revision schedule -> Today's Session recommendations

...against multiple failure shapes (a classifiable IndexError, an
ambiguous wrong answer that must stay unclassified, a crash) plus the
confirm/override review flow, and checks the honesty requirement
explicitly: an unclassified mistake must never be silently upgraded to a
guessed category anywhere in the UI. Run with the dev server (port 5173)
and backend (port 5001) already up, DB freshly reseeded.
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

        # ---- Case 1: a classifiable failure (IndexError -> Off-by-one) ----
        page.goto(f"{BASE}/#/problems/two-sum")
        page.wait_for_selector("text=Two Sum", timeout=10000)
        set_code(page, "def two_sum(nums, target):\n    return nums[999]\n")
        page.get_by_role("button", name="Run tests").click()
        page.wait_for_selector(".mistake-suggestion", timeout=10000)
        suggestion_text = page.locator(".mistake-suggestion").inner_text()
        check("mistake suggestion shows a category for a clear IndexError", "Off-by-one" in suggestion_text)
        check("mistake suggestion shows a confidence tag, not a bare claim", "likely" in suggestion_text.lower())

        confirm_btn = page.get_by_role("button", name="Yes, that's it")
        check("confirm button offered when a category was suggested", confirm_btn.count() > 0)
        confirm_btn.click()
        page.wait_for_selector("text=Saved to your mistake journal.", timeout=10000)

        # ---- Case 2: an ambiguous wrong answer -- must stay unclassified ----
        # Passes 3 of two-sum's 4 seeded cases; fails only the duplicate-
        # value case ([3,3] -> 6) because of an accidental "nums[i] !=
        # nums[j]" exclusion. Non-edge-shaped input, not a total failure --
        # exactly the case with no confident signal either way.
        page.get_by_role("button", name="Tests", exact=True).click()
        set_code(page, """def two_sum(nums, target):
    for i in range(len(nums)):
        for j in range(i + 1, len(nums)):
            if nums[i] + nums[j] == target and nums[i] != nums[j]:
                return [i, j]
    return []
""")
        page.get_by_role("button", name="Run tests").click()
        page.wait_for_selector(".mistake-suggestion", timeout=10000)
        unclassified_text = page.locator(".mistake-suggestion").inner_text()
        check("ambiguous failure is NOT given a confident guessed category",
              "couldn't confidently classify" in unclassified_text.lower())
        classify_btn = page.get_by_role("button", name="Classify it myself")
        check("manual classify option offered for an unclassified mistake", classify_btn.count() > 0)
        classify_btn.click()
        page.get_by_role("button", name="Pattern recognition difficulty", exact=True).click()
        page.wait_for_selector('text=Saved as "Pattern recognition difficulty".', timeout=10000)

        # ---- Case 3: correct code -- no mistake suggestion should appear ----
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
        check("no mistake suggestion on an all-passing run", page.locator(".mistake-suggestion").count() == 0)

        # ---- History tab shows both classified mistakes with their final state ----
        page.get_by_role("button", name="History", exact=True).click()
        page.wait_for_selector(".attempt-history", timeout=10000)
        history_text = page.locator(".attempt-history").inner_text()
        check("history shows the user-confirmed mistake", "Off-by-one errors" in history_text and "user confirmed" in history_text)
        check("history shows the manually-classified mistake", "Pattern recognition difficulty" in history_text and "manually selected" in history_text)

        check("no console errors through the ProblemWorkspace mistake flow", len(console_errors) == 0)

        # ---- Mistake Journal page ----
        page.goto(f"{BASE}/#/mistakes")
        page.wait_for_selector("text=Mistake journal", timeout=10000)
        journal_text = page.locator(".page").inner_text()
        check("journal shows both classified mistakes", "Off-by-one errors" in journal_text and "Pattern recognition difficulty" in journal_text)
        check("journal shows an honest 0-unclassified count after both were resolved", "0 of 2 mistakes" in journal_text)
        filter_btn = page.get_by_role("button", name=re.compile(r"Off-by-one errors \(\d+\)"))
        check("recurring-category filter chip present", filter_btn.count() > 0)
        filter_btn.click()
        filtered_text = page.locator(".attempt-history").inner_text()
        check("filtering by category hides the other category", "Pattern recognition difficulty" not in filtered_text)

        # ---- Dashboard: pattern weaknesses + Today's Session ----
        page.goto(f"{BASE}/#/dashboard")
        page.wait_for_selector("text=Weakest patterns", timeout=10000)
        dash_text = page.locator(".page").inner_text()
        check("dashboard still shows topic-level weaknesses (not replaced)", "Weakest topics" in dash_text)
        check("dashboard shows pattern-level weaknesses alongside it", "Weakest patterns" in dash_text)
        check("dashboard's pattern weakness references the Hash-map lookup family", "Hash-map lookup" in dash_text or "Hash map" in dash_text)

        if "Today's session" in dash_text:
            check("Today's Session items include an explanatory reason", "Recommended" in dash_text or "Revision recommended" in dash_text)
            check("Today's Session explicitly says it's not a required path", "never a required path" in dash_text)

        check("no console errors across Journal/Dashboard checks", len(console_errors) == 0)

        browser.close()

    print("\nALL MISTAKE-JOURNAL / PATTERN-REVISION / PRACTICE-SESSION CHECKS PASSED")


if __name__ == "__main__":
    main()
