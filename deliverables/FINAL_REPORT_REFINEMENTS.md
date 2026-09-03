# Codeloupe: Architecture/Content Refinement Pass — Final Report

**Status: complete and validated. Nothing has been committed or pushed** — as instructed, this sits in the working tree, on top of the already-reviewed 150-problem/50-day expansion, awaiting your review.

This report covers the 6 refinements requested after your review of the first pass: curriculum integration of the 41 new problems, the stale curriculum doc, the Greedy cross-topic architectural gap, Python-only branding verification, a re-review of Days 46-50 (now 44-49; see below), and full validation.

---

## 1. Files changed (this round)

**Backend:**
- `backend/db/schema.sql` — new `problems.secondary_concept_slugs` column; updated comments on `problems.day` and `problems.path_tier` to reflect that a day may now be set on an `extended`/`advanced` problem without making it required.
- `backend/db/init_db.py` — seeds `secondary_concept_slugs` into the new column.
- `backend/db/seed_problems_expansion.py` — 22 of the 41 new problems gained a `day` (44-49); no other field touched.
- `backend/db/seed_problems.py` — `max-area-container`, `jump-game`, `boats-to-save-people`, `task-scheduler` each gained `secondary_concept_slugs="greedy"`.
- `backend/db/seed_concepts.py` — Greedy lesson's `recognize_markdown` reworded to reflect that the 4 cross-topic examples are now genuinely linked, not just narrated.
- `backend/db/seed_lessons.py` — Days 44-49's `exercises_markdown` each gained one sentence pointing at that day's curated practice-problem menu (rendered from the DB, not duplicated in prose).
- `backend/app.py` — `_related_problems_for_concept()` rewritten to also match on `secondary_concept_slugs` (see item 3).
- `backend/test_endpoints.py` — the stale "extended/advanced problems never have a day" check replaced with one that permits it specifically for the curated Days 44-49 picks.
- `e2e_test.py`, `e2e_teaching_test.py` — fixed hardcoded assertions that had gone stale since the *previous* expansion pass and had never actually been re-run until this pass's full regression run (see item 8 and item 9's "architectural issues").

**Docs:**
- `docs/45-day-curriculum.md` → renamed to `docs/50-day-curriculum.md` and substantially rewritten (see item 6).
- `README.md`, `docs/decisions.md`, `docs/problem-roadmap.md`, `docs/learning-philosophy.md`, `study-notes/days-01-07-study-guide.md`, and the three backend comments above — filename references updated to the new path; `README.md` additionally had its stale "45-day / 109 problems / 28 concept lessons" claims corrected to 50/150/29.

**Not changed:** any frontend file (no UI code changes were needed this round — the sidebar tagline was already exactly right, see item 4; Curriculum Order/Difficulty sort, Try in Scratchpad, and guarded prefill all needed no code changes, only re-verification).

---

## 2. New problems integrated into curriculum days, and why

22 of the 41 new problems (from the previous pass) now have a `day` set, all within **Days 44-49** — deliberately *not* Days 1-42. Reasoning: Days 1-42's problem placement was already carefully paced and validated; touching it risked exactly the "arbitrary reshuffling" you asked me to avoid, for low benefit (none of the 41 are a strong fit as *introductory* material for an early day — the ones that would fit topically, like the two new linked-list problems, are Hard/Complex and too advanced for an intro day). Days 43-50, by contrast, had **zero** day-linked problems despite their prose promising concrete revision/mock-interview/advanced practice — populating them is where the real, low-risk improvement was.

None of the 22 became `path_tier='core'` — they kept whatever tier they already had (`extended` or `advanced`). Setting `day` on a pool-tier problem is new behavior as of this pass (see item 3's schema note): it means "recommended for this day," not "required." This is why the Hard/Complex problems could land specifically on Day 47 (Advanced/Complex practice) and Day 49 (final simulation) without violating the pre-existing, deliberate convention that Hard/Complex problems are never part of the required Core Path.

| Day | Problems added | Why this day |
|---|---|---|
| 44 (Mock interviews 1&2) | Meeting Rooms II (Medium), Gas Station (Medium), LRU Cache (Hard) | Realistic single-session interview problems, one stretch option |
| 45 (Mixed-problem practice) | Rotate Image, Word Search, Remove K Digits, Course Schedule II (all Medium) | Deliberately mixed topics, matching the day's "recognize without a topic label" goal |
| 46 (Weak-area revision) | Decode Ways, BST Iterator, Non-overlapping Intervals (all Medium) | Fresh material across a few different topics, for whichever weak area a learner has |
| 47 (Advanced/Complex practice) | Trapping Rain Water II, Split Array Largest Sum, Regular Expression Matching, Alien Dictionary, Binary Tree Cameras (all Complex), Largest Rectangle in Histogram (Hard) | The flagship day for Hard/Complex exposure — 6 topics represented |
| 48 (Mock interview 4) | Candy (Hard), Basic Calculator (Hard) | Medium-Hard mock-interview pair |
| 49 (Final simulation) | Maximal Rectangle, Text Justification, Constrained Subsequence Sum, Course Schedule III (all Complex) | Capstone-level, 4 different topics for the two back-to-back slots |

Each day's `exercises_markdown` now explicitly points at "the practice problems listed below" as a curated menu, while still explicitly allowing substitution from the Problem Bank — so the day pages give concrete recommendations without becoming a rigid checklist.

## 3. Which problems remain pool-only

The other 19 of the 41 stay `day=NULL`, browsable any time via the Problem Bank, exactly as before: assign-cookies, jump-game-ii, partition-labels (Greedy — see item 5's note on why Greedy doesn't need day-anchoring), reverse-nodes-k-group, lfu-cache, shortest-subarray-sum-at-least-k, count-smaller-after-self, smallest-range-k-lists, substring-concat-all-words, ipo-maximize-capital, word-break-ii, sliding-window-median, maximum-gap, minimum-window-subsequence, longest-increasing-subsequence, spiral-matrix, kth-smallest-sorted-matrix, next-permutation, reorganize-string.

## 4. Greedy cross-topic linking — how it was implemented

New `problems.secondary_concept_slugs` column: a comma-separated list of `concept_lessons.slug` values, using the **exact same convention already established** by `related_problem_slugs` and `concept_lessons.prerequisite_slugs` elsewhere in this schema — no new join table, no parallel system. A problem's primary `topic` is untouched; this is purely additive.

`max-area-container`, `jump-game`, `boats-to-save-people`, and `task-scheduler` each got `secondary_concept_slugs="greedy"` — their primary topics (`two-pointer`, `arrays`, `two-pointer`, `heaps`) are unchanged. `app.py`'s `_related_problems_for_concept()` now matches a concept lesson's problems on **primary topic (as before) OR the concept's own slug appearing in a problem's `secondary_concept_slugs`** — so any future concept lesson can retroactively tag any existing problem as a secondary example, with zero lesson-side code changes and no hardcoded slug list anywhere in `seed_concepts.py`.

Verified live: `GET /api/concepts/greedy` now returns **10** related problems — the 6 dedicated `topic='greedy'` problems plus the 4 cross-topic ones, correctly sorted (core-tier first, matching the existing convention). The Greedy lesson's prose was lightly reworded to say these 4 are "listed below" rather than just narratively mentioned, since that's now literally true.

## 5. Sidebar branding — confirmed

The sidebar tagline directly under the `codeloupe` logo reads **exactly** `Your Python DSA companion` (this was already in place from the previous pass; re-verified this round, unchanged). Audited the rest of the frontend for any ambiguous or multi-language messaging (searches for "Java", "C++", "multi-language", "any language", "favorite language," etc. across every `.jsx`/`.js` file) — found none. No changes were needed beyond the audit itself.

## 6. What changed in the curriculum documentation

`docs/45-day-curriculum.md` renamed to **`docs/50-day-curriculum.md`**. Substantive changes:
- Header/pace updated to 50 days; a status note explains the rename and that Days 1-42 are content-identical to the original plan.
- A new **difficulty-labels clarification**: the doc's own relative "Beginner-Easy...Medium-Hard" narrative scale is now explicitly distinguished from the shipped product's real, fixed `problems.difficulty` field (Easy/Medium/Hard/Complex) — these were always two different things and the doc previously didn't say so.
- A new **Greedy note**: explains it's a cross-curriculum concept lesson, not a dedicated block, and names how it connects to both its own topic pool and the 4 secondary-tagged cross-topic problems.
- A new **"Canonical curriculum vs. the Problem Bank pool"** section: 150 total problems, 82 of them day-tied (60 required Core + 22 optional Days 44-49 recommendations), the rest pool-only — and explicitly states that a day being set never implies "required."
- **Block 7 fully rewritten**: was 3 days (43-45), now 8 (43-50), matching `seed_lessons.py` exactly, including each day's real curated problem menu from item 2, and explicitly stating there is no "Mock Interview Mode" feature (every mock interview is self-timed use of the existing Problem Workspace).
- Coverage summary and excluded-topics list updated for 50 days / Greedy / Complex.

Every other repo reference to the old filename (README, `docs/decisions.md`, `docs/problem-roadmap.md`, `docs/learning-philosophy.md`, `study-notes/`, 3 backend comments) was updated to point at the new path. `README.md`'s own stale headline claims ("45-day," "109 problems," "28 concept lessons") were corrected to 50/150/29 since those are current-state claims, not historical ones.

**Scope note:** `docs/decisions.md` and `docs/problem-roadmap.md` are written as historical decision logs/changelogs (e.g. "Second expansion: 76 → 109 problems") — I updated their links but left their historical narrative content as-is, since rewriting "what we decided at the time" to current numbers would misrepresent the history they're recording. Flagging this scope call for your approval in item 9.

## 7. What changed in Days 44-49 (was "46-50" in your message — the actual block is Days 43-50, and the day-linked content lives in 44-49)

Re-reviewed the prose against the new curated problem menus: it already correctly avoided claiming a "Mock Interview Mode" feature (that was fixed in the previous pass), so no correction was needed there. What changed this round is that each day's exercises now name a **concrete, curated menu** pulled from real DB rows instead of only a generic instruction — see the table in item 2. I did not hardcode the menu into the prose text; each day's `exercises_markdown` references "the practice problems listed below," which renders from the actual `day`-linked problems, so the prose can never drift out of sync with what's really in the database.

## 8. Validation results

Fresh reseed: **150 problems, 50 lessons (days 1-50), 627 test cases, 29 concept lessons.** No duplicate slugs. Every one of the 16 topics × 4 difficulties has at least one problem — full coverage, confirmed via direct DB query, not just the plan doc. Complex confirmed to never appear as a topic value (16 rows, all `difficulty='Complex'`, spread across 15 different topics). Greedy confirmed Easy(1)/Medium(3)/Hard(1)/Complex(1). `path_tier` totals unchanged from before this round (60 core / 55 extended / 35 advanced) — confirming the day-assignment work altered zero tier values, only added `day` to 22 rows (13 advanced + 9 extended), all within 44-49.

`GET /api/concepts/greedy` → 10 related problems (6 primary + 4 secondary), correctly sorted. Problem Bank Curriculum Order re-verified in a real browser: Meeting Rooms II, Non-overlapping Intervals, Candy, and Trapping Rain Water II all render under their correct tier section (Extended/Advanced respectively) — none reshuffled into Core. Difficulty sort still groups Easy/Medium/Hard/Complex correctly. Try in Scratchpad re-verified from Day 47 (banner correctly lists all 6 of that day's curated problems); guarded prefill logic untouched this round. `npm run build` succeeds cleanly.

**Full regression suite** (`run_all_tests.sh`, all 10 suites, each against a fresh reseed): backend smoke tests, live-grading verification, approach-comparison baselines, and all 7 Playwright E2E suites (core, central-workflow, learning-features, visualizers, mistake-journal, approach-comparison, teaching-system) — **10/10 passing, zero console errors** across every suite. This was the first time this full suite had actually been run since the *previous* expansion pass, and it caught 3 genuinely pre-existing stale assertions from that earlier work (not introduced this round): `e2e_test.py` still searched for the string "Core 45-Day Path" (the badge itself already correctly said "Core 50-Day Path"); `e2e_teaching_test.py` expected exactly 28 concept lessons (Greedy's addition had made it 29) and expected stale problem-counts on the Graphs/DP concept lessons (9 vs. actual 11, and three DP-family counts) after those topics gained new Hard/Complex problems in the earlier pass. All fixed and re-verified green.

## 9. Architectural issues / decisions that still need your approval

1. **`docs/decisions.md` and `docs/problem-roadmap.md` were not rewritten**, only their links fixed — see item 6's scope note. They're historical logs; a full-repo pass making every historical count "current" would blur decision history with present state. Say the word if you want them brought current anyway.
2. **The full regression suite (`run_all_tests.sh`) had apparently never been run after the previous 41-problem expansion** — the 3 stale assertions it caught this round (item 8) were real gaps that existed before this session touched anything. Worth knowing for future changes: `test_endpoints.py` alone is not the full regression signal: the 7 Playwright suites need a real run too.
3. Everything else from the first report's item 12 (the Learn.jsx/ProblemWorkspace.jsx Python-messaging judgment call) still stands as previously reported — nothing new to flag there.

---

**Nothing has been committed or pushed.** Fresh reseed leaves a clean, validated `traceviz.db`. Ready for your review before any commit.
