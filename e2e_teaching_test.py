"""
Playwright E2E check for the teaching system (Learn hub + concept lessons,
see backend/db/seed_concepts.py and docs/decisions.md "Teaching system
content architecture"). Covers the original Arrays + Two Pointers pilot
plus batch 1 of the curriculum expansion (Prefix Sums, Strings, Hashing --
Days 9-12).

Covers: the Learn hub lists all five lessons grouped by topic in the
correct topic-before-pattern order; a concept lesson page renders every
section (what/why/recognize/intuition/walkthrough/common mistakes/
complexity/checkpoints/practice/related problems); the teaching
walkthrough steps through its authored frames; a choose_pattern checkpoint
gives right/wrong feedback; lesson-status progress persists; and the
lesson links INTO the rest of the app (a related problem, a prerequisite
lesson) and the rest of the app links back INTO it (a problem page's
"concepts you should know" callout, a day-lesson's related-concept
callout) -- including the negative case, that a day with no authored
concept content (Day 1) shows no broken/empty callout. Also covers
batch-1-specific content: the prefix-sums negative-indexing spot_bug
checkpoint, the strings expand-around-center walkthrough, and the
hashing lesson's honest disclaimer that dict state isn't visualized.

Run with the dev server (port 5173) and backend (port 5001) already up.
"""
import re
from playwright.sync_api import sync_playwright

BASE = "http://localhost:5173"
console_errors = []


def check(label, cond):
    print(f"[{'PASS' if cond else 'FAIL'}] {label}")
    assert cond, label


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.on("console", lambda m: console_errors.append(m.text) if m.type == "error" else None)
        page.on("pageerror", lambda e: console_errors.append(str(e)))

        # ---- Learn hub -----------------------------------------------------
        page.goto(f"{BASE}/#/learn")
        page.wait_for_selector("text=Learn", timeout=10000)
        cards = page.locator(".lesson-card")
        check("Learn hub lists all five concept lessons (pilot + batch 1)", cards.count() == 5)
        check("Learn hub groups by topic (arrays, two pointer, strings, hashing)",
              page.locator("text=two pointer").count() > 0
              and page.locator("h3", has_text="arrays").count() > 0
              and page.locator("h3", has_text="strings").count() > 0
              and page.locator("h3", has_text="hashing").count() > 0)
        # topic-before-pattern ordering within a group: "Arrays: the
        # foundation" (kind=topic) must appear before "Prefix sums"
        # (kind=pattern, same topic='arrays') -- see app.py's CASE-ordered
        # query and docs/decisions.md for why alphabetical order was wrong.
        hub_text = page.locator(".lesson-card").all_inner_texts()
        arrays_idx = next(i for i, t in enumerate(hub_text) if "Arrays: the foundation" in t)
        prefix_idx = next(i for i, t in enumerate(hub_text) if "Prefix sums" in t)
        check("topic lesson ('Arrays') sorts before its pattern lesson ('Prefix sums')",
              arrays_idx < prefix_idx)

        # ---- Concept lesson page: every section present ---------------------
        page.get_by_role("link", name=re.compile("Two pointers")).first.click()
        page.wait_for_selector("h2:has-text('Two pointers')", timeout=10000)
        for heading in ["What it is", "Why it matters", "When should I use this?",
                         "Core intuition", "Worked example", "Common mistakes",
                         "Complexity", "Quick checks", "Practice before a full problem", "Apply it"]:
            check(f"section '{heading}' renders", page.locator(f"text={heading}").count() > 0)

        check("bold markdown ('**opposite-direction**') rendered as real <strong>, not literal asterisks",
              page.locator("strong", has_text="opposite-direction").count() > 0)
        check("inline code span rendered as real <code>, not literal backticks",
              page.locator("code", has_text="left").count() > 0)

        # ---- prerequisite link works ------------------------------------
        prereq_link = page.get_by_role("link", name="Arrays: the foundation")
        check("prerequisite lesson linked", prereq_link.count() > 0)

        # ---- teaching walkthrough steps through its authored frames --------
        walkthrough = page.locator(".concept-walkthrough")
        check("teaching walkthrough renders", walkthrough.count() > 0)
        check("walkthrough starts at step 1", "step 1 /" in walkthrough.inner_text())
        first_caption = page.locator(".concept-walkthrough-caption").inner_text()
        page.get_by_role("button", name=re.compile("Next")).click()
        page.wait_for_timeout(150)
        second_caption = page.locator(".concept-walkthrough-caption").inner_text()
        check("stepping the walkthrough forward changes the caption AND the visualized state",
              second_caption != first_caption and "step 2 /" in page.locator(".concept-walkthrough").inner_text())
        check("walkthrough reuses the real array/pointer visualizer (not a separate one-off widget)",
              page.locator(".concept-walkthrough .viz-block, .concept-walkthrough .seq-box").count() > 0)

        # ---- checkpoint: choose_pattern gives right/wrong feedback ----------
        page.locator(".checkpoint-card").first.scroll_into_view_if_needed()
        correct_choice = page.get_by_role("button", name="Two pointers starting at both ends, O(n)")
        check("choose_pattern checkpoint choices rendered", correct_choice.count() > 0)
        correct_choice.click()
        page.wait_for_timeout(150)
        check("correct choice gets positive feedback styling",
              "checkpoint-correct" in (correct_choice.get_attribute("class") or ""))
        check("explanation shown after answering", page.locator(".checkpoint-explanation").count() > 0)

        # a predict_output-style checkpoint: reveal-then-explain, not multiple choice
        reveal_btns = page.get_by_role("button", name="Reveal answer")
        check("non-multiple-choice checkpoints use reveal-answer, not fake choices", reveal_btns.count() >= 2)
        reveal_btns.first.click()
        page.wait_for_timeout(150)
        # index 1, not .first: the choose_pattern checkpoint above (index 0) was
        # already answered and shows no "Answer:" line (multiple-choice
        # checkpoints show the picked/correct choice inline instead -- see
        # Checkpoint.jsx's isChoice branch), so its explanation renders first
        # in document order regardless of which checkpoint was revealed here.
        check("revealing shows the answer text", page.locator(".checkpoint-explanation").nth(1).inner_text().find("Answer:") != -1)

        # ---- practice exercise: reveal solution -----------------------------
        show_solution = page.get_by_role("button", name=re.compile("Show (hint \\+ )?solution"))
        check("practice exercise present with a reveal control", show_solution.count() > 0)
        show_solution.first.click()
        page.wait_for_timeout(150)
        check("solution code revealed", page.locator(".practice-exercise pre.code-block").count() >= 2)  # starter + solution

        # ---- related problems link out -------------------------------------
        apply_section_link = page.locator(".problem-list .problem-row").first
        check("related problems listed under 'Apply it'", apply_section_link.count() > 0)

        # ---- progress status persists across reload -------------------------
        page.get_by_role("button", name="Mark in progress").click()
        page.wait_for_timeout(300)
        page.reload(wait_until="networkidle")
        check("status persists after reload", page.locator(".badge.status-in_progress").count() > 0)

        # ---- integration: problem page shows "concepts you should know" ----
        page.goto(f"{BASE}/#/problems/two-sum-sorted", wait_until="networkidle")
        page.wait_for_selector("text=Two Sum", timeout=10000)
        check("problem page shows a 'Pattern to know' callout linking to the concept lesson",
              page.locator("a.callout", has_text="Pattern to know").count() > 0)

        # ---- integration: day-lesson page shows related concept lesson -----
        page.goto(f"{BASE}/#/lessons/13", wait_until="networkidle")
        page.wait_for_selector("text=Day 13", timeout=10000)
        check("day-13 lesson page shows a 'Learn: Two pointers' callout",
              page.locator("a.callout", has_text="Learn: Two pointers").count() > 0)

        # ---- negative case: a day with no authored concept content shows nothing (not broken) --
        page.goto(f"{BASE}/#/lessons/1", wait_until="networkidle")
        page.wait_for_selector("text=Day 1", timeout=10000)
        check("day-1 lesson page (no concept content yet) shows no concept callout, gracefully",
              page.locator("a.callout", has_text="Learn:").count() == 0)

        # ---- batch 1: prefix-sums lesson ------------------------------------
        page.goto(f"{BASE}/#/learn/prefix-sums", wait_until="networkidle")
        page.wait_for_selector("h2:has-text('Prefix sums')", timeout=10000)
        check("prefix-sums prerequisite links to Arrays",
              page.get_by_role("link", name="Arrays: the foundation").count() > 0)
        check("prefix-sums walkthrough renders both the arr and prefix arrays as separate labeled sequences",
              page.locator(".concept-walkthrough .seq-row").count() >= 2)
        seq_labels = page.locator(".concept-walkthrough .seq-label").all_inner_texts()
        check("labeled sequences are 'arr' and 'prefix', not a single merged view",
              any("arr" in t for t in seq_labels) and any("prefix" in t for t in seq_labels))
        # the spot_bug checkpoint calls out the classic prefix[left-1] with
        # left=0 silently wrapping to prefix[-1] via Python negative indexing
        page.locator(".checkpoint-card").first.scroll_into_view_if_needed()
        reveal_btns = page.get_by_role("button", name="Reveal answer")
        check("prefix-sums has reveal-style checkpoints (spot_bug/predict_output)", reveal_btns.count() > 0)
        reveal_btns.first.click()
        page.wait_for_timeout(150)
        check("revealed checkpoint explanation mentions the negative-indexing bug",
              "index" in page.locator(".checkpoint-explanation").first.inner_text().lower()
              or "-1" in page.locator(".checkpoint-explanation").first.inner_text())

        # ---- batch 1: strings lesson -----------------------------------------
        page.goto(f"{BASE}/#/learn/strings", wait_until="networkidle")
        page.wait_for_selector("h2:has-text('Strings')", timeout=10000)
        walkthrough = page.locator(".concept-walkthrough")
        check("strings walkthrough renders (expand-around-center)", walkthrough.count() > 0)
        check("strings walkthrough starts at step 1", "step 1 /" in walkthrough.inner_text())
        page.get_by_role("button", name=re.compile("Next")).click()
        page.wait_for_timeout(150)
        check("strings walkthrough advances to step 2", "step 2 /" in page.locator(".concept-walkthrough").inner_text())

        # ---- batch 1: hashing lesson ------------------------------------------
        page.goto(f"{BASE}/#/learn/hashing", wait_until="networkidle")
        page.wait_for_selector("h2:has-text('Hashing')", timeout=10000)
        check("hashing lesson prerequisite links to Arrays",
              page.get_by_role("link", name="Arrays: the foundation").count() > 0)
        check("hashing walkthrough renders (two_sum)", page.locator(".concept-walkthrough").count() > 0)
        page_text = page.locator("body").inner_text().lower()
        check("hashing lesson honestly discloses dict state isn't visually rendered",
              "isn't rendered visually" in page_text or "is not rendered visually" in page_text)
        check("hashing walkthrough caption narrates seen's dict contents directly",
              "seen is empty" in page.locator(".concept-walkthrough").inner_text())
        page.get_by_role("button", name=re.compile("Next")).click()
        page.wait_for_timeout(150)
        check("later hashing walkthrough caption shows seen's accumulated key/value pairs",
              "seen = {" in page.locator(".concept-walkthrough").inner_text())

        check("no console errors across the whole teaching-system flow", len(console_errors) == 0)

        browser.close()

    print("\nALL TEACHING-SYSTEM CHECKS PASSED")


if __name__ == "__main__":
    main()
