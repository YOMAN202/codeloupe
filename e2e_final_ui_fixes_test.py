"""
Browser verification for the three "final UI/curriculum fixes" in this
change (base commit 8af8fd7):

  1. Curriculum sidebar active state on /lessons/:day + "Back to
     Curriculum" link on the Day lesson page (App.jsx's extraActivePaths /
     useLocation-based NavItem; LessonDetail.jsx's .lesson-back-link).
  2. Clicking "Day N+1 ->" auto-completes the CURRENT day via the existing
     lesson-progress API, without auto-completing on mere page load and
     without cascading to skipped days on a direct jump
     (LessonDetail.jsx's goToDay).
  3. Problem Bank column alignment -- header and every row share one fixed
     grid-template-columns (App.css's --problem-grid-columns), so columns
     never drift row-to-row regardless of content length.

Run standalone against the live dev server + Flask API:
    python3 e2e_final_ui_fixes_test.py
"""
import sys
import threading
import time
from playwright.sync_api import sync_playwright

BASE = "http://127.0.0.1:5173/#"
console_errors = []
failures = []


def check(label, cond, extra=None):
    status = "PASS" if cond else "FAIL"
    print(f"[{status}] {label}" + (f" -- {extra}" if extra and not cond else ""))
    if not cond:
        failures.append(label)


def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path="/opt/pw-browsers/chromium")

        # ==================================================================
        # 1. Sidebar active state + Back to Curriculum
        # ==================================================================
        page = browser.new_page(viewport={"width": 1440, "height": 900})
        page.on("console", lambda msg: console_errors.append(msg.text) if msg.type == "error" else None)
        page.on("pageerror", lambda exc: console_errors.append(str(exc)))

        curriculum_link = page.locator('.sidebar-nav a[aria-label="Curriculum"]')
        learn_link = page.locator('.sidebar-nav a[aria-label="Learn"]')

        # Baseline: /curriculum itself highlights Curriculum, not Learn.
        page.goto(f"{BASE}/curriculum", wait_until="networkidle")
        page.wait_for_selector(".lesson-grid", timeout=10000)
        check("On /curriculum: Curriculum nav item is active", "active" in curriculum_link.get_attribute("class"))
        check("On /curriculum: Learn nav item is NOT active", "active" not in learn_link.get_attribute("class"))

        # Direct navigation (not a client-side click) to a day lesson page --
        # exercises the route-aware (not click-origin-aware) requirement.
        page.goto(f"{BASE}/lessons/5", wait_until="networkidle")
        page.wait_for_selector(".lesson-detail-title", timeout=10000)
        check(
            "Direct nav to /lessons/5: Curriculum nav item is active",
            "active" in curriculum_link.get_attribute("class"),
        )
        check(
            "Direct nav to /lessons/5: Learn nav item is still NOT active",
            "active" not in learn_link.get_attribute("class"),
        )

        # A hard refresh on a day page must not depend on navigation history.
        page.reload(wait_until="networkidle")
        page.wait_for_selector(".lesson-detail-title", timeout=10000)
        check(
            "After hard refresh on /lessons/5: Curriculum nav item is still active",
            "active" in curriculum_link.get_attribute("class"),
        )

        back_link = page.locator(".lesson-back-link")
        check("Day page shows a 'Back to Curriculum' link", back_link.count() == 1)
        check("Back link text reads 'Back to Curriculum'", "Back to Curriculum" in back_link.inner_text())
        check("Back link points at /curriculum", back_link.get_attribute("href").endswith("/curriculum"))
        back_link.click()
        page.wait_for_selector(".lesson-grid", timeout=10000)
        check("Clicking 'Back to Curriculum' lands on the Curriculum page", "/curriculum" in page.url)

        # Prev/next controls must still exist alongside the back link.
        page.goto(f"{BASE}/lessons/5", wait_until="networkidle")
        page.wait_for_selector(".lesson-detail-title", timeout=10000)
        nav_buttons = page.locator(".lesson-nav-buttons button")
        check("Prev/next day controls still present (2 buttons)", nav_buttons.count() == 2)
        check("Prev button still reads 'Day 4'", "Day 4" in nav_buttons.nth(0).inner_text())
        check("Next button still reads 'Day 6'", "Day 6" in nav_buttons.nth(1).inner_text())

        # ==================================================================
        # 2. Day N -> Day N+1 auto-completes Day N (existing progress API)
        # ==================================================================
        page.goto(f"{BASE}/lessons/1", wait_until="networkidle")
        page.wait_for_selector(".lesson-detail-title", timeout=10000)
        check(
            "Opening Day 1 does NOT auto-mark it completed",
            "status-not_started" in (page.locator(".status-badge, [class*='status-']").first.get_attribute("class") or "")
            or page.locator(".chip-active").count() == 0,
        )
        # More precise: read the status badge text directly.
        badge_text = page.locator(".lesson-detail-title .badge").inner_text().strip().lower()
        check("Day 1 status badge reads 'not started' before navigating away", badge_text == "not started", badge_text)

        # goToDay awaits the status-write API call before navigating (a
        # deliberate best-effort ordering -- see LessonDetail.jsx), so the
        # URL change lags the click by one network round trip; wait for the
        # URL itself rather than a selector already satisfied by the
        # current (pre-navigation) page.
        page.locator(".lesson-nav-buttons button").nth(1).click()
        page.wait_for_url(lambda url: url.endswith("/lessons/2"), timeout=10000)
        page.wait_for_selector(".lesson-detail-title", timeout=10000)
        check("Clicking 'Day 2 ->' navigates to Day 2", "/lessons/2" in page.url)

        page.goto(f"{BASE}/lessons/1", wait_until="networkidle")
        page.wait_for_selector(".lesson-detail-title", timeout=10000)
        badge_text = page.locator(".lesson-detail-title .badge").inner_text().strip().lower()
        check("Day 1 is now 'completed' after navigating forward via Day 2 ->", badge_text == "completed", badge_text)

        page.reload(wait_until="networkidle")
        page.wait_for_selector(".lesson-detail-title", timeout=10000)
        badge_text = page.locator(".lesson-detail-title .badge").inner_text().strip().lower()
        check("Day 1 'completed' status PERSISTS after a full page refresh", badge_text == "completed", badge_text)

        # Curriculum card reflects it.
        page.goto(f"{BASE}/curriculum", wait_until="networkidle")
        page.wait_for_selector(".lesson-grid", timeout=10000)
        day1_card = page.locator('.lesson-card:has(.day-number:text-is("Day 1"))')
        check("Curriculum card for Day 1 shows status-completed class", "status-completed" in day1_card.get_attribute("class"))

        # Dashboard reflects it (lesson_status_counts includes it in "completed").
        page.goto(f"{BASE}/", wait_until="networkidle")
        page.wait_for_selector(".stat-grid", timeout=10000)
        check("Dashboard loaded after Day 1 completion (no console/page error state)", page.locator(".error").count() == 0)

        # Manually-set statuses (known/skipped) must never be silently
        # overwritten by simply moving on to the next day.
        page.goto(f"{BASE}/lessons/10", wait_until="networkidle")
        page.wait_for_selector(".lesson-detail-title", timeout=10000)
        page.locator(".status-controls").get_by_role("button", name="Mark skipped").click()
        page.wait_for_timeout(300)
        badge_text = page.locator(".lesson-detail-title .badge").inner_text().strip().lower()
        check("Day 10 manually marked 'skipped'", badge_text == "skipped", badge_text)
        page.locator(".lesson-nav-buttons button").nth(1).click()
        page.wait_for_url(lambda url: url.endswith("/lessons/11"), timeout=10000)
        page.goto(f"{BASE}/lessons/10", wait_until="networkidle")
        page.wait_for_selector(".lesson-detail-title", timeout=10000)
        badge_text = page.locator(".lesson-detail-title .badge").inner_text().strip().lower()
        check(
            "Day 10's manual 'skipped' status is NOT overwritten by clicking Day 11 ->",
            badge_text == "skipped",
            badge_text,
        )

        # Direct jump to a later day from Curriculum overview must not
        # cascade-complete the days skipped over.
        page.goto(f"{BASE}/lessons/30", wait_until="networkidle")
        page.wait_for_selector(".lesson-detail-title", timeout=10000)
        page.goto(f"{BASE}/lessons/25", wait_until="networkidle")
        page.wait_for_selector(".lesson-detail-title", timeout=10000)
        badge_text = page.locator(".lesson-detail-title .badge").inner_text().strip().lower()
        check(
            "Directly jumping to Day 25 does not auto-mark it completed",
            badge_text == "not started",
            badge_text,
        )

        # ==================================================================
        # 3. Problem Bank column alignment
        # ==================================================================
        for width in (1440, 1024):
            page.set_viewport_size({"width": width, "height": 900})
            page.goto(f"{BASE}/problems", wait_until="networkidle")
            page.wait_for_selector(".problem-list-row", timeout=10000)

            header = page.locator(".problem-list-header").first
            rows = page.locator(".problem-list-row")
            row_count = rows.count()
            check(f"[{width}px] Problem Bank renders rows", row_count > 5, row_count)

            header_cols = header.evaluate("el => getComputedStyle(el).gridTemplateColumns")
            mismatches = []
            sample = min(row_count, 40)
            for i in range(sample):
                row_cols = rows.nth(i).evaluate("el => getComputedStyle(el).gridTemplateColumns")
                if row_cols != header_cols:
                    mismatches.append(i)
            check(
                f"[{width}px] every sampled row's grid-template-columns exactly matches the header's",
                len(mismatches) == 0,
                f"{len(mismatches)}/{sample} rows differ (e.g. row {mismatches[0]})" if mismatches else None,
            )

            # Column boundaries (left edge of each of the 6 cells) must line
            # up across rows and the header -- the actual visual alignment
            # check, not just the CSS property string.
            def col_lefts(locator):
                return locator.evaluate(
                    "el => Array.from(el.children).map(c => c.getBoundingClientRect().left)"
                )

            header_lefts = col_lefts(header)
            drift_rows = []
            for i in range(sample):
                lefts = col_lefts(rows.nth(i))
                if any(abs(a - b) > 1 for a, b in zip(lefts, header_lefts)):
                    drift_rows.append(i)
            check(
                f"[{width}px] all 6 column left-edges align with the header across sampled rows",
                len(drift_rows) == 0,
                f"drift in rows {drift_rows[:5]}" if drift_rows else None,
            )

            # Page itself must never overflow horizontally -- the table
            # scrolls internally if needed, not the whole page.
            page_overflow = page.evaluate("document.documentElement.scrollWidth - document.documentElement.clientWidth")
            check(f"[{width}px] page itself is not wider than the viewport", page_overflow <= 1, page_overflow)

            # Difficulty/Priority badge text must not change column position:
            # compare the Difficulty column's left edge across an Easy row
            # and a Complex row.
            difficulty_lefts = set()
            for i in range(sample):
                lefts = col_lefts(rows.nth(i))
                difficulty_lefts.add(round(lefts[3], 1))
            check(
                f"[{width}px] Difficulty column left-edge is identical across all sampled rows regardless of badge text",
                len(difficulty_lefts) == 1,
                difficulty_lefts,
            )

            # Est. time stays in a consistent, right-aligned column.
            time_rights = set()
            for i in range(sample):
                el = rows.nth(i).locator(".problem-list-row-time")
                box = el.bounding_box()
                time_rights.add(round(box["x"] + box["width"], 0))
            check(
                f"[{width}px] Est. time right edge is consistent across sampled rows",
                len(time_rights) <= 2,  # allow 1px rounding jitter across rows
                time_rights,
            )

        # A "variation" row's secondary text must stay under the title, in
        # the title column (not drift into Topic).
        variation_row = page.locator(".problem-list-row:has(.problem-list-row-meta)").first
        check("At least one 'variation' row is present in the Problem Bank", variation_row.count() >= 1)
        if variation_row.count() >= 1:
            title_box = variation_row.locator(".problem-list-row-title").bounding_box()
            meta_box = variation_row.locator(".problem-list-row-meta").bounding_box()
            check(
                "'variation' meta text's left edge matches its row's title column left edge",
                abs(title_box["x"] - meta_box["x"]) <= 1,
            )

        # Both sort modes reuse the same ProblemList/CSS -- confirm the fix
        # holds under Difficulty sort too.
        page.set_viewport_size({"width": 1440, "height": 900})
        page.select_option("#problem-sort-select", "difficulty")
        page.wait_for_timeout(300)
        rows = page.locator(".problem-list-row")
        header = page.locator(".problem-list-header").first
        header_cols = header.evaluate("el => getComputedStyle(el).gridTemplateColumns")
        sample = min(rows.count(), 20)
        mismatches = [i for i in range(sample) if rows.nth(i).evaluate("el => getComputedStyle(el).gridTemplateColumns") != header_cols]
        check("Difficulty sort mode: rows still match header's grid-template-columns", len(mismatches) == 0, mismatches)

        check("No console/page errors across the full flow", len(console_errors) == 0, console_errors[:5])

        browser.close()


def run_completion_reliability_checks():
    """
    Focused checks on the goToDay(1) completion-write flow under a slow or
    failing lesson-progress API -- a real network round trip (unmocked)
    completes in well under the delays used here, so these specifically
    exercise the reliability requirements a happy-path run can't reach:
    the button must never look dead while the write is in flight, a rapid
    double-click must not fire the write twice or queue duplicate
    navigations, and a failed write must never falsely mark the day
    completed.
    """
    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path="/opt/pw-browsers/chromium")

        # ---- slow API: in-flight feedback + double-click guard ----------
        page = browser.new_page(viewport={"width": 1440, "height": 900})
        page.on("console", lambda msg: console_errors.append(msg.text) if msg.type == "error" else None)
        page.on("pageerror", lambda exc: console_errors.append(str(exc)))

        put_calls = []

        def slow_route(route):
            if route.request.method == "PUT" and "/progress" in route.request.url:
                put_calls.append(route.request.url)
                # Delay via a background thread rather than blocking here --
                # a blocking sleep in the handler itself would stall
                # Playwright's own dispatcher thread and make every other
                # call in this script (clicks, evaluate, ...) appear to
                # hang too, which isn't what a slow backend actually does.
                def delayed_continue():
                    time.sleep(1.0)
                    try:
                        route.continue_()
                    except Exception:
                        pass
                threading.Thread(target=delayed_continue, daemon=True).start()
            else:
                route.continue_()

        page.route("**/api/**", slow_route)
        page.goto(f"{BASE}/lessons/1", wait_until="networkidle")
        page.wait_for_selector(".lesson-detail-title", timeout=10000)

        next_btn = page.locator(".lesson-nav-buttons button").nth(1)
        # Two real, synchronous click() dispatches in the same tick -- the
        # actual pathological double-click race (faster than a React
        # re-render), not just two Playwright-paced clicks a disabled
        # attribute alone could already stop.
        page.evaluate("""
            () => {
              const btn = document.querySelectorAll('.lesson-nav-buttons button')[1];
              btn.click();
              btn.click();
            }
        """)
        page.wait_for_timeout(200)
        check(
            "Next-day button shows in-flight feedback while the completion write is pending",
            next_btn.inner_text().strip() == "Saving...",
            next_btn.inner_text(),
        )
        check("Next-day button is disabled while the completion write is pending", next_btn.is_disabled())
        check(
            "A synchronous double-click during the pending write fires only ONE completion request",
            len(put_calls) == 1,
            len(put_calls),
        )

        # Poll directly rather than wait_for_url -- confirmed equivalent
        # and more robust against this test's own background-thread route
        # delay than Playwright's built-in navigation waiter.
        navigated = False
        for _ in range(30):
            page.wait_for_timeout(200)
            if page.evaluate("location.href").endswith("/lessons/2"):
                navigated = True
                break
        check("Navigation to Day 2 completes once the delayed write resolves (button never stayed dead)", navigated)

        page.goto(f"{BASE}/lessons/1", wait_until="networkidle")
        page.wait_for_selector(".lesson-detail-title", timeout=10000)
        badge_text = page.locator(".lesson-detail-title .badge").inner_text().strip().lower()
        check("Day 1 is correctly completed once the (eventually slow) write succeeds", badge_text == "completed", badge_text)
        page.close()

        # ---- failing API: no false completion, navigation still works ---
        page2 = browser.new_page(viewport={"width": 1440, "height": 900})

        def failing_route(route):
            if route.request.method == "PUT" and "/progress" in route.request.url:
                route.fulfill(status=500, body="simulated failure")
            else:
                route.continue_()

        page2.route("**/api/**", failing_route)
        page2.goto(f"{BASE}/lessons/3", wait_until="networkidle")
        page2.wait_for_selector(".lesson-detail-title", timeout=10000)
        page2.locator(".lesson-nav-buttons button").nth(1).click()

        navigated = False
        for _ in range(20):
            page2.wait_for_timeout(150)
            if page2.evaluate("location.href").endswith("/lessons/4"):
                navigated = True
                break
        check("A failed completion write does not trap the learner -- navigation still proceeds", navigated)
        page2.close()

        # Re-check WITHOUT the failing mock -- confirms the failure was
        # never silently written through some other path.
        page3 = browser.new_page(viewport={"width": 1440, "height": 900})
        page3.goto(f"{BASE}/lessons/3", wait_until="networkidle")
        page3.wait_for_selector(".lesson-detail-title", timeout=10000)
        badge_text = page3.locator(".lesson-detail-title .badge").inner_text().strip().lower()
        check("Day 3 is NOT falsely marked completed after its completion write failed", badge_text == "not started", badge_text)
        page3.close()

        browser.close()


if __name__ == "__main__":
    run()
    run_completion_reliability_checks()
    print()
    if failures:
        print(f"{len(failures)} CHECK(S) FAILED:")
        for f in failures:
            print(f"  - {f}")
        sys.exit(1)
    print("ALL FINAL UI/CURRICULUM-FIX CHECKS PASSED")
