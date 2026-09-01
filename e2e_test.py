"""
Full end-to-end browser test of the complete learning workflow, run
against the live Vite dev server + Flask API. Covers the exact 11-step
flow requested: open app -> choose a day -> see recommended path but jump
freely -> learn the lesson -> do exercises/problems -> write & run code ->
see test results -> use hints -> trace execution -> see array
visualization -> record progress -> see the dashboard/revision queue.
"""
import sys
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
        page = browser.new_page()
        page.on("console", lambda msg: console_errors.append(msg.text) if msg.type == "error" else None)
        page.on("pageerror", lambda exc: console_errors.append(str(exc)))

        # 1. Open the app -> curriculum map
        page.goto(f"{BASE}/", wait_until="networkidle")
        page.wait_for_selector(".lesson-grid", timeout=10000)
        check("Curriculum map loads with lesson cards", page.locator(".lesson-card").count() > 0)
        check("Curriculum map shows all 7 blocks", page.locator(".block-section").count() == 7)

        # 2. Free navigation: jump directly to Day 27 (deep into the
        #    curriculum) without completing everything before it.
        page.goto(f"{BASE}/lessons/27", wait_until="networkidle")
        page.wait_for_selector(".lesson-detail-title", timeout=10000)
        check("Jumped directly to Day 27 lesson detail", "Day 27" in page.locator(".lesson-detail-title h2").inner_text())

        # Recommended prerequisites shown, not blocking
        check("Recommended prerequisites shown (informational)", page.locator(".prereq-box").count() > 0)
        check("Lesson content (concept) rendered", page.locator(".lesson-section").count() > 0)

        # 3. Mark lesson in_progress (non-linear status tracking)
        page.get_by_role("button", name="Mark in progress").click()
        try:
            # .badge has CSS text-transform: capitalize, so the rendered
            # text is "In Progress" -- compare case-insensitively.
            page.wait_for_function(
                "document.querySelector('.lesson-detail-title .badge')?.innerText.toLowerCase() === 'in progress'",
                timeout=5000,
            )
            badge_ok = True
        except Exception:
            badge_ok = False
        check("Status badge updates to in_progress", badge_ok,
              page.locator(".lesson-detail-title .badge").inner_text())

        # 4. Navigate to a linked practice problem from the lesson
        problem_links = page.locator(".problem-row")
        check("Lesson has linked practice problems", problem_links.count() > 0)
        first_problem_title = problem_links.first.inner_text()
        problem_links.first.click()
        page.wait_for_selector(".workspace-columns", timeout=10000)
        check("Navigated into problem workspace", page.locator(".workspace-left h2").count() > 0)

        # 5. Editor loaded with starter code (Monaco)
        page.wait_for_selector(".monaco-editor", timeout=15000)
        page.wait_for_timeout(1000)
        check("Monaco editor mounted in problem workspace", page.locator(".monaco-editor").count() > 0)

        # Write a correct solution for reverse-linked-list (the day-27 core
        # problem). Interact with the real editor DOM (not a window.monaco
        # global, which @monaco-editor/react doesn't expose) -- click in,
        # select all, replace. Use insert_text rather than .type(): Monaco's
        # autocomplete/snippet handling silently drops characters like '='
        # when characters are typed one at a time (documented gotcha).
        solution_code = """class Node:
    def __init__(self, val):
        self.val = val
        self.next = None

def build_list(values):
    head = None
    for v in reversed(values):
        node = Node(v)
        node.next = head
        head = node
    return head

def to_list(head):
    result = []
    while head:
        result.append(head.val)
        head = head.next
    return result

def reverse_list(values):
    head = build_list(values)
    prev = None
    curr = head
    while curr:
        nxt = curr.next
        curr.next = prev
        prev = curr
        curr = nxt
    return to_list(prev)
"""
        page.evaluate(
            "(code) => window.__tracevizEditor && window.__tracevizEditor.setValue(code)",
            solution_code,
        )
        page.wait_for_timeout(300)

        # 6/7. Run tests, see results
        page.get_by_role("button", name="Run tests").click()
        page.wait_for_selector(".test-results, .error", timeout=15000)
        page.wait_for_timeout(500)
        results_text = page.locator(".tab-panel").inner_text()
        check("Test results panel shows PASS results", "PASS" in results_text)
        check("Attempt feedback shown after run", page.locator(".success, .warning").count() > 0)

        # 8. Use progressive hints
        page.get_by_role("button", name="Hints").click()
        page.wait_for_timeout(200)
        page.get_by_role("button", name="Reveal hint 1").click()
        page.wait_for_timeout(500)
        check("Hint 1 content revealed", page.locator(".hint-text").count() > 0)

        # 9. Trace execution of own code
        page.get_by_role("button", name="Trace").click()
        page.wait_for_timeout(200)
        page.get_by_role("button", name="Trace my code").click()
        page.wait_for_selector(".trace-step-info", timeout=15000)
        page.wait_for_timeout(500)
        check("Trace viewer shows step info after tracing", page.locator(".trace-step-info").count() > 0)
        check("Trace step controls present (play/step/scrub)", page.locator(".trace-scrubber").count() > 0)

        # step forward through several steps -- some steps (e.g. a bare
        # "call" event) have empty locals by construction, so scan across
        # a handful of steps rather than asserting on one arbitrary point.
        step_btn = page.get_by_role("button", name="Step forward →")
        saw_locals_or_array = False
        for _ in range(10):
            panel_html = page.locator(".tab-panel").inner_html()
            if "locals-table" in panel_html or "array-view" in panel_html:
                saw_locals_or_array = True
                break
            if step_btn.is_enabled():
                step_btn.click()
                page.wait_for_timeout(100)
            else:
                break
        check("Stepping forward works without crashing the page", len(console_errors) == 0, console_errors)

        # 10. relevant visualization (array/linked-list view) where available
        check("Locals table or array view rendered somewhere during trace", saw_locals_or_array)

        # 11. Dashboard reflects the logged attempt
        page.goto(f"{BASE}/dashboard", wait_until="networkidle")
        page.wait_for_selector(".stat-grid", timeout=10000)
        page.wait_for_timeout(300)
        stat_values = page.locator(".stat-value").all_inner_texts()
        check("Dashboard shows at least 1 problem attempted", any(v not in ("0", "--") for v in stat_values), stat_values)

        # Curriculum map reflects the lesson status change + resume pointer
        page.goto(f"{BASE}/", wait_until="networkidle")
        page.wait_for_selector(".lesson-grid", timeout=10000)
        page.wait_for_timeout(300)
        check("Resume callout appears on curriculum map after marking a lesson in_progress",
              page.locator(".callout-resume").count() > 0)

        browser.close()


run()

print()
print(f"Console errors captured: {len(console_errors)}")
for e in console_errors[:20]:
    print("  -", e)

print()
if failures:
    print(f"{len(failures)} FAILURES:")
    for f in failures:
        print(" -", f)
    sys.exit(1)
else:
    print("ALL E2E CHECKS PASSED")
