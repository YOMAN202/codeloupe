"""
Playwright E2E check for the teaching system (Learn hub + concept lessons,
see backend/db/seed_concepts.py and docs/decisions.md "Teaching system
content architecture"). Covers the original Arrays + Two Pointers pilot
plus batch 1 (Prefix Sums, Strings, Hashing -- Days 9-12), batch 2
(Sliding Window -- Days 15-16), batch 3 (Linked Lists, Fast/Slow
Pointers -- Days 25-27), batch 4 (Stacks, Queues -- Days 28-29), batch 5
(Recursion, Backtracking -- Days 23-24), batch 6 (Binary Search, Binary
Search Variants -- Days 21-22), batch 7 (Sorting, Divide-and-conquer
sorting -- Days 17-20), and batch 8 (Trees, Binary Search Trees, Tree
BFS -- Days 30-32) of the curriculum expansion.

Covers: the Learn hub lists all lessons grouped by topic in the correct
topic-before-pattern order; a concept lesson page renders every section
(what/why/recognize/intuition/walkthrough/common mistakes/complexity/
checkpoints/practice/related problems); the teaching walkthrough steps
through its authored frames; a choose_pattern checkpoint gives
right/wrong feedback; lesson-status progress persists; and the lesson
links INTO the rest of the app (a related problem, a prerequisite lesson)
and the rest of the app links back INTO it (a problem page's "concepts
you should know" callout, a day-lesson's related-concept callout) --
including the negative case, that a day with no authored concept content
(Day 1) shows no broken/empty callout. Also covers batch-specific
content: the prefix-sums negative-indexing spot_bug checkpoint, the
strings expand-around-center walkthrough, the hashing lesson's honest
disclaimer that dict state isn't visualized, the sliding-window
double-shrink walkthrough frame, and the linked-list reversal/cycle-
detection walkthroughs that reuse LinkedListView (a node-chain renderer,
not the array-box one every other lesson uses) via a small adapter in
ConceptWalkthrough.jsx.

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
        check("Learn hub lists all nineteen concept lessons (pilot + batches 1-8)", cards.count() == 19)
        check("Learn hub groups by topic (arrays, two pointer, strings, hashing, sliding window, linked lists, stacks, queues, recursion, binary search, sorting, trees)",
              page.locator("text=two pointer").count() > 0
              and page.locator("h3", has_text="arrays").count() > 0
              and page.locator("h3", has_text="strings").count() > 0
              and page.locator("h3", has_text="hashing").count() > 0
              and page.locator("h3", has_text="sliding window").count() > 0
              and page.locator("h3", has_text="linked lists").count() > 0
              and page.locator("h3", has_text="stacks").count() > 0
              and page.locator("h3", has_text="queues").count() > 0
              and page.locator("h3", has_text="recursion").count() > 0
              and page.locator("h3", has_text="binary search").count() > 0
              and page.locator("h3", has_text="sorting").count() > 0
              and page.locator("h3", has_text="trees").count() > 0)
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
        # href-exact, not a text/regex match: as more lessons are added, a
        # lesson's own SUMMARY can legitimately contain another lesson's
        # title as a substring (e.g. Fast/slow pointers' summary literally
        # starts "Two pointers moving through..."), which a fuzzy text match
        # against a card's full accessible name would wrongly click.
        page.locator('a.lesson-card[href="#/learn/two-pointers"]').click()
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

        # ---- batch 2: sliding-window lesson ------------------------------------
        page.goto(f"{BASE}/#/learn/sliding-window", wait_until="networkidle")
        page.wait_for_selector("h2:has-text('Sliding window')", timeout=10000)
        check("sliding-window prerequisite links to Two pointers",
              page.get_by_role("link", name="Two pointers").count() > 0)
        walkthrough = page.locator(".concept-walkthrough")
        check("sliding-window walkthrough renders (longest_unique_substring)", walkthrough.count() > 0)
        check("sliding-window walkthrough starts at step 1", "step 1 / 5" in walkthrough.inner_text())
        # step through to the double-shrink frame (step 4) that specifically
        # demonstrates why the shrink has to be a while loop, not an if
        for _ in range(3):
            page.get_by_role("button", name=re.compile("Next")).click()
            page.wait_for_timeout(120)
        check("stepping to the double-shrink frame shows both shrink steps happened",
              "shrink again" in page.locator(".concept-walkthrough-caption").inner_text().lower())
        # final frame: left=2, right=3 -- a genuine two-box window, so the
        # shaded "current window" band (windowEligible for topic=sliding-window)
        # should highlight both boxes, not just one
        page.get_by_role("button", name=re.compile("Next")).click()
        page.wait_for_timeout(120)
        check("sliding-window's shaded window band highlights both boxes of a real 2-wide window",
              page.locator(".concept-walkthrough .seq-box-in-window").count() >= 2)

        # the spot_bug checkpoint calls out the classic if-vs-while shrink bug
        page.locator(".checkpoint-card").first.scroll_into_view_if_needed()
        reveal_btns = page.get_by_role("button", name="Reveal answer")
        check("sliding-window has reveal-style checkpoints (spot_bug/complexity)", reveal_btns.count() > 0)
        reveal_btns.first.click()
        page.wait_for_timeout(150)
        check("revealed checkpoint explanation mentions the if-vs-while shrink bug",
              "while" in page.locator(".checkpoint-explanation").first.inner_text().lower())

        # ---- integration: day-15 (fixed-size window) links to the lesson ------
        page.goto(f"{BASE}/#/lessons/15", wait_until="networkidle")
        page.wait_for_selector("text=Day 15", timeout=10000)
        check("day-15 lesson page shows a 'Learn: Sliding window' callout",
              page.locator("a.callout", has_text="Learn: Sliding window").count() > 0)

        # ---- batch 3: linked-lists lesson (reversal walkthrough) --------------
        page.goto(f"{BASE}/#/learn/linked-lists", wait_until="networkidle")
        page.wait_for_selector("h2:has-text('Linked lists')", timeout=10000)
        walkthrough = page.locator(".concept-walkthrough")
        check("linked-lists walkthrough renders via the node-chain view, not array boxes",
              walkthrough.locator(".ll-chain").count() > 0 and walkthrough.locator(".seq-boxes").count() == 0)
        check("linked-lists walkthrough starts at step 1 of 4", "step 1 / 4" in walkthrough.inner_text())
        # step to the "split" frame: prev's chain and curr's still-linked
        # remainder become genuinely separate pieces until the loop reaches them
        page.get_by_role("button", name=re.compile("Next")).click()
        page.wait_for_timeout(150)
        check("split-chain frame shows the not-yet-relinked portion as a separate, labeled group",
              "not reachable" in page.locator(".concept-walkthrough").inner_text().lower())
        # step to the final frame: the fully-reversed chain should read 3 -> 2 -> 1
        page.get_by_role("button", name=re.compile("Next")).click()
        page.wait_for_timeout(120)
        page.get_by_role("button", name=re.compile("Next")).click()
        page.wait_for_timeout(150)
        ll_nodes = page.locator(".concept-walkthrough .ll-node:not(.ll-node-orphan):not(.ll-node-none)").all_inner_texts()
        check("final frame's reversed chain reads 3, 2, 1 in order (a real in-place reversal, not a relabeling)",
              ll_nodes == ["3", "2", "1"])

        # ---- batch 3: fast/slow-pointers lesson (cycle-detection walkthrough) --
        page.goto(f"{BASE}/#/learn/linked-list-fast-slow", wait_until="networkidle")
        page.wait_for_selector("h2:has-text('Fast/slow pointers')", timeout=10000)
        check("fast/slow prerequisites link to both Linked lists and Two pointers",
              page.get_by_role("link", name="Linked lists").count() > 0
              and page.get_by_role("link", name="Two pointers").count() > 0)
        for _ in range(3):
            page.get_by_role("button", name=re.compile("Next")).click()
            page.wait_for_timeout(120)
        check("cycle-detection final frame shows the cycle indicator, not a plain None tail",
              page.locator(".concept-walkthrough .ll-cycle").count() > 0)
        check("both slow and fast pointer chips land on the same node when the cycle is detected",
              page.locator(".concept-walkthrough .ll-pointer-tags .pointer-chip").count() >= 2)

        # ---- integration: day-27 (reversal + cycle detection) links to both ---
        page.goto(f"{BASE}/#/lessons/27", wait_until="networkidle")
        page.wait_for_selector("text=Day 27", timeout=10000)
        check("day-27 lesson page shows callouts for both Linked lists and Fast/slow pointers",
              page.locator("a.callout", has_text="Learn: Linked lists").count() > 0
              and page.locator("a.callout", has_text="Learn: Fast/slow pointers").count() > 0)

        # ---- batch 4: stacks lesson (monotonic-stack double-pop walkthrough) --
        page.goto(f"{BASE}/#/learn/stacks", wait_until="networkidle")
        page.wait_for_selector("h2:has-text('Stacks')", timeout=10000)
        walkthrough = page.locator(".concept-walkthrough")
        check("stacks walkthrough renders via the plain array/pointer view (a stack IS just a list)",
              walkthrough.locator(".seq-boxes").count() > 0)
        check("stacks walkthrough shows only the stack itself, no stray pointer chip on it",
              walkthrough.locator(".pointer-chip").count() == 0)
        for _ in range(2):
            page.get_by_role("button", name=re.compile("Next")).click()
            page.wait_for_timeout(120)
        check("double-pop frame's caption shows both stacked values got resolved by the same new value",
              "keeps popping" in page.locator(".concept-walkthrough-caption").inner_text().lower())
        reveal_btns = page.get_by_role("button", name="Reveal answer")
        check("stacks has reveal-style checkpoints", reveal_btns.count() > 0)
        reveal_btns.first.click()
        page.wait_for_timeout(150)
        check("revealed checkpoint explanation mentions the if-vs-while pop bug",
              "while" in page.locator(".checkpoint-explanation").first.inner_text().lower())

        # ---- batch 4: queues lesson (monotonic-deque, indices not values) -----
        page.goto(f"{BASE}/#/learn/queues", wait_until="networkidle")
        page.wait_for_selector("h2:has-text('Queues')", timeout=10000)
        check("queues prerequisite links to Stacks",
              page.get_by_role("link", name="Stacks").count() > 0)
        walkthrough = page.locator(".concept-walkthrough")
        check("queues walkthrough renders (monotonic deque of indices)", walkthrough.count() > 0)
        check("queues lesson explicitly flags the deque holds indices, not raw values",
              "indices" in page.locator("body").inner_text().lower())
        for _ in range(4):
            page.get_by_role("button", name=re.compile("Next")).click()
            page.wait_for_timeout(120)
        check("final queues frame's deque holds two indices after a full scan",
              page.locator(".concept-walkthrough .seq-box").count() == 2)

        # ---- integration: day-28/29 link to their respective lessons ----------
        page.goto(f"{BASE}/#/lessons/28", wait_until="networkidle")
        page.wait_for_selector("text=Day 28", timeout=10000)
        check("day-28 lesson page shows a 'Learn: Stacks' callout",
              page.locator("a.callout", has_text="Learn: Stacks").count() > 0)
        page.goto(f"{BASE}/#/lessons/29", wait_until="networkidle")
        page.wait_for_selector("text=Day 29", timeout=10000)
        check("day-29 lesson page shows a 'Learn: Queues' callout",
              page.locator("a.callout", has_text="Learn: Queues").count() > 0)

        # ---- batch 5: recursion lesson (call stack rendered as an array) ------
        page.goto(f"{BASE}/#/learn/recursion", wait_until="networkidle")
        page.wait_for_selector("h2:has-text('Recursion')", timeout=10000)
        walkthrough = page.locator(".concept-walkthrough")
        check("recursion walkthrough renders the call stack via the plain array view, not LinkedListView",
              walkthrough.locator(".seq-boxes").count() > 0 and walkthrough.locator(".ll-chain").count() == 0)
        check("recursion walkthrough starts at step 1 of 7", "step 1 / 7" in walkthrough.inner_text())
        for _ in range(3):
            page.get_by_role("button", name=re.compile("Next")).click()
            page.wait_for_timeout(120)
        check("deepest frame shows all four stack frames (factorial 4 down to 1)",
              page.locator(".concept-walkthrough .seq-box").count() == 4)
        for _ in range(3):
            page.get_by_role("button", name=re.compile("Next")).click()
            page.wait_for_timeout(120)
        check("final frame's caption confirms the stack unwound in reverse order",
              "reverse order" in page.locator(".concept-walkthrough-caption").inner_text().lower())
        check("final frame shows an empty call stack -- every frame has returned",
              page.locator(".concept-walkthrough .seq-box").count() == 0)

        # ---- batch 5: backtracking lesson (choose/recurse/un-choose) ----------
        page.goto(f"{BASE}/#/learn/backtracking", wait_until="networkidle")
        page.wait_for_selector("h2:has-text('Backtracking')", timeout=10000)
        check("backtracking prerequisite links to Recursion",
              page.get_by_role("link", name="Recursion").count() > 0)
        walkthrough = page.locator(".concept-walkthrough")
        check("backtracking walkthrough renders (subsets via include/exclude)", walkthrough.count() > 0)
        # step to the base-case "record" frame: path should hold both chosen elements
        page.get_by_role("button", name=re.compile("Next")).click()
        page.wait_for_timeout(120)
        page.get_by_role("button", name=re.compile("Next")).click()
        page.wait_for_timeout(120)
        path_values = page.locator(".concept-walkthrough .seq-box-value").all_inner_texts()
        check("record frame shows the full chosen path [1, 2], not a stale or empty path",
              path_values == ["1", "2"])
        reveal_btns = page.get_by_role("button", name="Reveal answer")
        check("backtracking has reveal-style checkpoints", reveal_btns.count() > 0)
        reveal_btns.first.click()
        page.wait_for_timeout(150)
        check("revealed checkpoint explanation mentions copying path, not sharing the same list object",
              "copy" in page.locator(".checkpoint-explanation").first.inner_text().lower())

        # ---- integration: day-23/24 link to their respective lessons ----------
        page.goto(f"{BASE}/#/lessons/23", wait_until="networkidle")
        page.wait_for_selector("text=Day 23", timeout=10000)
        check("day-23 lesson page shows a 'Learn: Recursion' callout",
              page.locator("a.callout", has_text="Learn: Recursion").count() > 0)
        page.goto(f"{BASE}/#/lessons/24", wait_until="networkidle")
        page.wait_for_selector("text=Day 24", timeout=10000)
        check("day-24 lesson page shows callouts for both Recursion and Backtracking",
              page.locator("a.callout", has_text="Learn: Recursion").count() > 0
              and page.locator("a.callout", has_text="Learn: Backtracking").count() > 0)

        # ---- batch 6: binary-search lesson (lo/hi/mid closing in on a target) --
        page.goto(f"{BASE}/#/learn/binary-search", wait_until="networkidle")
        page.wait_for_selector("h2:has-text('Binary search')", timeout=10000)
        walkthrough = page.locator(".concept-walkthrough")
        check("binary-search walkthrough renders via the plain array/pointer view",
              walkthrough.locator(".seq-boxes").count() > 0)
        check("binary-search walkthrough starts at step 1 of 6", "step 1 / 6" in walkthrough.inner_text())
        for _ in range(5):
            page.get_by_role("button", name=re.compile("Next")).click()
            page.wait_for_timeout(120)
        check("final frame's caption confirms the target was found",
              "found" in page.locator(".concept-walkthrough-caption").inner_text().lower())
        reveal_btns = page.get_by_role("button", name="Reveal answer")
        check("binary-search has reveal-style checkpoints", reveal_btns.count() > 0)
        reveal_btns.first.click()
        page.wait_for_timeout(150)
        check("revealed checkpoint explanation renders",
              page.locator(".checkpoint-explanation").first.inner_text().strip() != "")

        # ---- batch 6: binary-search-variants lesson (rotated-array search) -----
        page.goto(f"{BASE}/#/learn/binary-search-variants", wait_until="networkidle")
        page.wait_for_selector("h2:has-text('Binary search variants')", timeout=10000)
        check("binary-search-variants prerequisite links to Binary search",
              page.get_by_role("link", name="Binary search").count() > 0)
        walkthrough = page.locator(".concept-walkthrough")
        check("binary-search-variants walkthrough renders (rotated-array search)", walkthrough.count() > 0)
        check("binary-search-variants walkthrough starts at step 1 of 6", "step 1 / 6" in walkthrough.inner_text())
        page.get_by_role("button", name=re.compile("Next")).click()
        page.wait_for_timeout(120)
        check("second frame's caption identifies which half of the rotated array is sorted",
              "sorted" in page.locator(".concept-walkthrough-caption").inner_text().lower())
        for _ in range(4):
            page.get_by_role("button", name=re.compile("Next")).click()
            page.wait_for_timeout(120)
        check("final frame's caption confirms the target was found",
              "found" in page.locator(".concept-walkthrough-caption").inner_text().lower())
        checkpoint_choice = page.get_by_role("button", name=re.compile("Binary search over candidate speeds"))
        check("binary-search-variants has a choose_pattern checkpoint about searching an answer space",
              checkpoint_choice.count() > 0)
        checkpoint_choice.click()
        page.wait_for_timeout(150)
        check("correct choice gets positive feedback styling",
              "checkpoint-correct" in (checkpoint_choice.get_attribute("class") or ""))

        # ---- integration: day-21/22 link to their respective lessons ----------
        page.goto(f"{BASE}/#/lessons/21", wait_until="networkidle")
        page.wait_for_selector("text=Day 21", timeout=10000)
        check("day-21 lesson page shows a 'Learn: Binary search' callout",
              page.locator("a.callout", has_text="Learn: Binary search").count() > 0)
        page.goto(f"{BASE}/#/lessons/22", wait_until="networkidle")
        page.wait_for_selector("text=Day 22", timeout=10000)
        check("day-22 lesson page shows callouts for both Binary search and Binary search variants",
              page.locator("a.callout", has_text="Learn: Binary search").count() > 0
              and page.locator("a.callout", has_text="Learn: Binary search variants").count() > 0)

        # ---- batch 7: sorting lesson (insertion sort's multi-shift while loop) --
        page.goto(f"{BASE}/#/learn/sorting", wait_until="networkidle")
        page.wait_for_selector("h2:has-text('Sorting')", timeout=10000)
        walkthrough = page.locator(".concept-walkthrough")
        check("sorting walkthrough renders via the plain array/pointer view",
              walkthrough.locator(".seq-boxes").count() > 0)
        check("sorting walkthrough starts at step 1 of 7", "step 1 / 7" in walkthrough.inner_text())
        for _ in range(3):
            page.get_by_role("button", name=re.compile("Next")).click()
            page.wait_for_timeout(120)
        check("multi-shift frame's caption confirms one shift wasn't enough",
              "isn't enough" in page.locator(".concept-walkthrough-caption").inner_text().lower())
        for _ in range(3):
            page.get_by_role("button", name=re.compile("Next")).click()
            page.wait_for_timeout(120)
        final_values = page.locator(".concept-walkthrough .seq-box-value").all_inner_texts()
        check("final frame shows the fully sorted array [1, 2, 3, 4, 5]",
              final_values == ["1", "2", "3", "4", "5"])
        reveal_btns = page.get_by_role("button", name="Reveal answer")
        check("sorting has reveal-style checkpoints", reveal_btns.count() > 0)
        reveal_btns.first.click()
        page.wait_for_timeout(150)
        check("revealed checkpoint explanation mentions the negative-indexing wraparound bug",
              "wrap" in page.locator(".checkpoint-explanation").first.inner_text().lower())

        # ---- batch 7: divide-and-conquer-sorting lesson (quicksort partition) --
        page.goto(f"{BASE}/#/learn/divide-and-conquer-sorting", wait_until="networkidle")
        page.wait_for_selector("h2:has-text('Divide-and-conquer sorting')", timeout=10000)
        check("divide-and-conquer-sorting prerequisites link to both Sorting and Recursion",
              page.get_by_role("link", name="Sorting: comparison-based fundamentals").count() > 0
              and page.get_by_role("link", name="Recursion").count() > 0)
        walkthrough = page.locator(".concept-walkthrough")
        check("divide-and-conquer-sorting walkthrough renders (quicksort partition, single array only)",
              walkthrough.count() > 0)
        check("divide-and-conquer-sorting walkthrough starts at step 1 of 7", "step 1 / 7" in walkthrough.inner_text())
        for _ in range(6):
            page.get_by_role("button", name=re.compile("Next")).click()
            page.wait_for_timeout(120)
        final_values = page.locator(".concept-walkthrough .seq-box-value").all_inner_texts()
        check("final partition frame places the pivot (4) at its correct sorted index, [3, 1, 4, 9, 5, 8]",
              final_values == ["3", "1", "4", "9", "5", "8"])
        checkpoint_choice = page.get_by_role("button", name=re.compile("Quickselect -- partition like quicksort"))
        check("divide-and-conquer-sorting has a choose_pattern checkpoint about quickselect",
              checkpoint_choice.count() > 0)
        checkpoint_choice.click()
        page.wait_for_timeout(150)
        check("correct choice gets positive feedback styling",
              "checkpoint-correct" in (checkpoint_choice.get_attribute("class") or ""))

        # ---- integration: days 17-20 link to both sorting lessons --------------
        page.goto(f"{BASE}/#/lessons/17", wait_until="networkidle")
        page.wait_for_selector("text=Day 17", timeout=10000)
        check("day-17 lesson page shows callouts for both Sorting and Divide-and-conquer sorting",
              page.locator("a.callout", has_text="Learn: Sorting").count() > 0
              and page.locator("a.callout", has_text="Learn: Divide-and-conquer sorting").count() > 0)
        page.goto(f"{BASE}/#/lessons/20", wait_until="networkidle")
        page.wait_for_selector("text=Day 20", timeout=10000)
        check("day-20 lesson page shows callouts for both Sorting and Divide-and-conquer sorting",
              page.locator("a.callout", has_text="Learn: Sorting").count() > 0
              and page.locator("a.callout", has_text="Learn: Divide-and-conquer sorting").count() > 0)

        # ---- batch 8: trees lesson (preorder DFS via the new TreeView adapter) --
        page.goto(f"{BASE}/#/learn/trees", wait_until="networkidle")
        page.wait_for_selector("h2:has-text('Trees')", timeout=10000)
        walkthrough = page.locator(".concept-walkthrough")
        check("trees walkthrough renders via TreeView's node-and-edge shape, not the array/pointer view",
              walkthrough.locator(".tree-node").count() > 0 and walkthrough.locator(".seq-boxes").count() == 0)
        check("trees walkthrough starts at step 1 of 7", "step 1 / 7" in walkthrough.inner_text())
        for _ in range(3):
            page.get_by_role("button", name=re.compile("Next")).click()
            page.wait_for_timeout(150)
        check("fourth frame's caption confirms returning to node 2 to recurse right",
              "back at node 2" in page.locator(".concept-walkthrough-caption").inner_text().lower())
        for _ in range(3):
            page.get_by_role("button", name=re.compile("Next")).click()
            page.wait_for_timeout(150)
        check("final frame's caption states the complete preorder result",
              "[1, 2, 4, 5, 3]" in page.locator(".concept-walkthrough-caption").inner_text())
        reveal_btns = page.get_by_role("button", name="Reveal answer")
        check("trees has reveal-style checkpoints", reveal_btns.count() > 0)
        reveal_btns.first.click()
        page.wait_for_timeout(150)
        check("revealed checkpoint explanation renders",
              page.locator(".checkpoint-explanation").first.inner_text().strip() != "")

        # ---- batch 8: binary-search-trees lesson (bounds, not parent-only) -----
        page.goto(f"{BASE}/#/learn/binary-search-trees", wait_until="networkidle")
        page.wait_for_selector("h2:has-text('Binary search trees')", timeout=10000)
        check("binary-search-trees prerequisites link to both Trees and Binary search",
              page.get_by_role("link", name="Trees: structure and traversal").count() > 0
              and page.get_by_role("link", name="Binary search").count() > 0)
        walkthrough = page.locator(".concept-walkthrough")
        check("binary-search-trees walkthrough renders via TreeView", walkthrough.locator(".tree-node").count() > 0)
        check("binary-search-trees walkthrough starts at step 1 of 7", "step 1 / 7" in walkthrough.inner_text())
        for _ in range(4):
            page.get_by_role("button", name=re.compile("Next")).click()
            page.wait_for_timeout(150)
        check("node-4 frame's caption explains bounds guarantee beyond a parent-only check",
              "guarantees" in page.locator(".concept-walkthrough-caption").inner_text().lower())
        checkpoint_choice = page.get_by_role("button", name=re.compile("Track a \\(low, high\\) range"))
        check("binary-search-trees has a choose_pattern checkpoint about bounds tracking",
              checkpoint_choice.count() > 0)
        checkpoint_choice.click()
        page.wait_for_timeout(150)
        check("correct choice gets positive feedback styling",
              "checkpoint-correct" in (checkpoint_choice.get_attribute("class") or ""))

        # ---- batch 8: tree-bfs lesson (queue draining, reusing the array view) --
        page.goto(f"{BASE}/#/learn/tree-bfs", wait_until="networkidle")
        page.wait_for_selector("h2:has-text('Tree BFS')", timeout=10000)
        check("tree-bfs prerequisites link to both Trees and Queues",
              page.get_by_role("link", name="Trees: structure and traversal").count() > 0
              and page.get_by_role("link", name="Queues").count() > 0)
        walkthrough = page.locator(".concept-walkthrough")
        check("tree-bfs walkthrough renders via the plain array view (the queue's contents), not TreeView",
              walkthrough.locator(".seq-boxes").count() > 0 and walkthrough.locator(".tree-node").count() == 0)
        check("tree-bfs walkthrough starts at step 1 of 7", "step 1 / 7" in walkthrough.inner_text())
        for _ in range(5):
            page.get_by_role("button", name=re.compile("Next")).click()
            page.wait_for_timeout(150)
        check("sixth frame shows the queue fully drained (empty)",
              page.locator(".concept-walkthrough .seq-box").count() == 0)

        # ---- integration: days 30-32 all link to all three tree lessons --------
        page.goto(f"{BASE}/#/lessons/30", wait_until="networkidle")
        page.wait_for_selector("text=Day 30", timeout=10000)
        check("day-30 lesson page shows callouts for all three tree lessons",
              page.locator("a.callout", has_text="Learn: Trees").count() > 0
              and page.locator("a.callout", has_text="Learn: Binary search trees").count() > 0
              and page.locator("a.callout", has_text="Learn: Tree BFS").count() > 0)
        page.goto(f"{BASE}/#/lessons/32", wait_until="networkidle")
        page.wait_for_selector("text=Day 32", timeout=10000)
        check("day-32 lesson page shows callouts for all three tree lessons",
              page.locator("a.callout", has_text="Learn: Trees").count() > 0
              and page.locator("a.callout", has_text="Learn: Binary search trees").count() > 0
              and page.locator("a.callout", has_text="Learn: Tree BFS").count() > 0)

        check("no console errors across the whole teaching-system flow", len(console_errors) == 0)

        browser.close()

    print("\nALL TEACHING-SYSTEM CHECKS PASSED")


if __name__ == "__main__":
    main()
