# Codeloupe: 41-Problem Expansion — Final Report

**Status: implementation and verification complete. Nothing has been committed or pushed — per your instruction, this is on disk in the working tree only, awaiting your review.**

---

## 1. Original problem count

109

## 2. Number of new problems added

41

## 3. Final problem count

150 (verified live: `init_db.py` seeds exactly 150 rows, 627 auto-verified test cases, from a fresh DB)

## 4. Complete category × difficulty coverage matrix

Pulled directly from the seeded database (not the plan doc) as the authoritative source. Every one of the 16 topics — including the new `greedy` topic — has at least one problem at every difficulty, including Complex.

| Topic | Easy | Medium | Hard | Complex |
|---|---|---|---|---|
| arrays | 5 | 9 | 2 | 1 |
| binary-search | 2 | 4 | 1 | 1 |
| dynamic-programming | 2 | 9 | 1 | 1 |
| graphs | 1 | 8 | 1 | 1 |
| **greedy** (new topic) | 1 | 3 | 1 | 1 |
| hashing | 2 | 4 | 1 | 1 |
| heaps | 2 | 6 | 2 | 1 |
| linked-lists | 5 | 2 | 1 | 1 |
| queues | 2 | 2 | 1 | 1 |
| recursion | 1 | 6 | 1 | 1 |
| sliding-window | 1 | 5 | 1 | 1 |
| sorting | 2 | 2 | 1 | 1 |
| stacks | 1 | 4 | 1 | 1 |
| strings | 3 | 4 | 1 | 1 |
| trees | 4 | 5 | 2 | 1 |
| two-pointer | 2 | 6 | 1 | 1 |
| **Totals** | **36** | **79** | **19** | **16** |

## 5. Every new problem

All 41, as seeded (slug / title / topic / difficulty / day / path tier / visualization). None of the 41 got a specific curriculum day — see item 12 for the reasoning — so "day" is blank for all; only the promoted `jump-game` (item 6) carries a day. Visualization is the shape the existing `detect.js`/`Visualizers.jsx` dispatcher renders for that problem's actual runtime locals — no new visualizer component was needed for any of them.

| Slug | Title | Topic | Difficulty | Tier | Visualization |
|---|---|---|---|---|---|
| lru-cache | LRU Cache | hashing | Hard | advanced | Array/sequence (scripted design ops) |
| reverse-nodes-k-group | Reverse Nodes in k-Group | linked-lists | Hard | advanced | Linked list |
| shortest-subarray-sum-at-least-k | Shortest Subarray with Sum at Least K | queues | Hard | advanced | Array + monotonic deque |
| count-smaller-after-self | Count of Smaller Numbers After Self | sorting | Hard | advanced | Array (merge-sort trace) |
| largest-rectangle-histogram | Largest Rectangle in Histogram | stacks | Hard | advanced | Array + stack |
| basic-calculator | Basic Calculator | strings | Hard | advanced | String + stack |
| smallest-range-k-lists | Smallest Range Covering Elements from K Lists | two-pointer | Hard | advanced | Heap over k lists |
| trapping-rain-water-ii | Trapping Rain Water II | arrays | Complex | advanced | Grid + heap |
| split-array-largest-sum | Split Array Largest Sum | binary-search | Complex | advanced | Array (binary search over answer) |
| regular-expression-matching | Regular Expression Matching | dynamic-programming | Complex | advanced | 2D DP table |
| alien-dictionary | Alien Dictionary | graphs | Complex | advanced | Graph (topological order) |
| substring-concat-all-words | Substring with Concatenation of All Words | hashing | Complex | advanced | String/array sliding window |
| ipo-maximize-capital | IPO | heaps | Complex | advanced | Heap |
| lfu-cache | LFU Cache | linked-lists | Complex | advanced | Array/sequence (scripted design ops) |
| constrained-subsequence-sum | Constrained Subsequence Sum | queues | Complex | advanced | Array + monotonic deque / DP |
| word-break-ii | Word Break II | recursion | Complex | advanced | String (backtracking) |
| sliding-window-median | Sliding Window Median | sliding-window | Complex | advanced | Array + heap |
| maximum-gap | Maximum Gap | sorting | Complex | advanced | Array (bucket sort) |
| maximal-rectangle | Maximal Rectangle | stacks | Complex | advanced | Grid + stack (per-row histogram) |
| text-justification | Text Justification | strings | Complex | advanced | String/array |
| binary-tree-cameras | Binary Tree Cameras | trees | Complex | advanced | Tree |
| minimum-window-subsequence | Minimum Window Subsequence | two-pointer | Complex | advanced | String, two pointers |
| assign-cookies | Assign Cookies | greedy | Easy | extended | Array (two-pointer greedy) |
| jump-game-ii | Jump Game II | greedy | Medium | extended | Array (pointer) |
| candy | Candy | greedy | Hard | advanced | Array |
| course-schedule-iii | Course Schedule III | greedy | Complex | advanced | Heap |
| longest-increasing-subsequence | Longest Increasing Subsequence | dynamic-programming | Medium | extended | DP / array (patience sort) |
| non-overlapping-intervals | Non-overlapping Intervals | arrays | Medium | extended | Array (intervals) |
| gas-station | Gas Station | greedy | Medium | extended | Array (pointer) |
| partition-labels | Partition Labels | greedy | Medium | extended | Array/hashing |
| word-search | Word Search | recursion | Medium | extended | Grid (backtracking) |
| rotate-image | Rotate Image | arrays | Medium | extended | Grid |
| spiral-matrix | Spiral Matrix | arrays | Medium | extended | Grid |
| kth-smallest-sorted-matrix | Kth Smallest Element in a Sorted Matrix | heaps | Medium | extended | Grid + heap |
| course-schedule-ii | Course Schedule II | graphs | Medium | extended | Graph |
| next-permutation | Next Permutation | arrays | Medium | extended | Array |
| decode-ways | Decode Ways | dynamic-programming | Medium | extended | 1D DP |
| remove-k-digits | Remove K Digits | stacks | Medium | extended | String + stack |
| bst-iterator | Binary Search Tree Iterator | trees | Medium | extended | Tree (BST) + scripted design ops |
| reorganize-string | Reorganize String | heaps | Medium | extended | Heap + string |
| meeting-rooms-ii | Meeting Rooms II | heaps | Medium | extended | Heap (intervals) |

## 6. Existing problems promoted/reclassified

- **`jump-game`**: Extended → **Core**, assigned **Day 8**, budget raised to **240 min** (Day 8 previously 210). Confirmed live: Day 8's problem list now shows Remove Duplicates from Sorted Array, Jump Game, and Merge Intervals.

No other existing problem was moved, reclassified, or deleted. No ambiguous misclassifications were found in the original 109 during the audit that needed reporting.

## 7. New Greedy problems

The `greedy` topic is new. 6 problems now carry `topic='greedy'`, covering all four difficulties:

- **assign-cookies** (Easy)
- **jump-game-ii**, **gas-station**, **partition-labels** (Medium)
- **candy** (Hard)
- **course-schedule-iii** (Complex)

Plus a new **Greedy concept lesson** (`greedy`, "Greedy: local choices, global answers") teaching what greedy is, local-vs-global choice, recognition signals, the exchange-argument intuition, greedy vs. brute force/DP, and common patterns — with 3 checkpoints and 1 practice exercise (`min_platforms`). It auto-links to the 6 topic='greedy' problems above; see item 11 for how it also references the 4 pre-existing greedy-flavored problems that keep their original topics.

## 8. New Complex problems

Complex is a genuine 4th difficulty rung (Easy → Medium → Hard → Complex everywhere), spread across 15 topics — never a Hard problem renamed, never obscure competitive-programming trivia:

trapping-rain-water-ii, split-array-largest-sum, regular-expression-matching, alien-dictionary, substring-concat-all-words, ipo-maximize-capital, lfu-cache, constrained-subsequence-sum, word-break-ii, sliding-window-median, maximum-gap, maximal-rectangle, text-justification, binary-tree-cameras, minimum-window-subsequence, course-schedule-iii — **16 total** (the plan called for a mandatory 15; course-schedule-iii is the Greedy topic's Complex entry, counted separately in item 7 and here since it satisfies both requirements at once).

## 9. Files changed

**Modified:**
- `backend/db/schema.sql` — `difficulty` column comment updated to mention Complex
- `backend/db/seed_problems.py` — jump-game promoted; imports and appends the 41 new problems; new asserts (no dup slugs, count == 150)
- `backend/db/seed_concepts.py` — new Greedy concept lesson, checkpoints, practice exercise
- `backend/db/seed_lessons.py` — Day 8 budget change; Days 44–45 rewritten (drop nonexistent "Mock Interview Mode" references); Days 46–50 added; asserts updated to 50 lessons
- `backend/logic/pattern_families.py` — new Greedy rule
- `backend/test_endpoints.py` — counts updated (150 problems, 50 lessons, tier totals); new difficulty-validity check; new full coverage-matrix assertion
- `frontend/src/App.css` — Complex difficulty tokens/badge color; Problem Bank sort-select style; Scratchpad context-banner styles (kept outside the Split-mode-critical `.scratchpad-columns` scope)
- `frontend/src/App.jsx` — nav tagline → "Your Python DSA companion"
- `frontend/src/components/Badges/Badges.jsx` — "Core 45-Day Path" → "Core 50-Day Path"
- `frontend/src/pages/ConceptLesson/ConceptLesson.jsx` — practice-exercise Scratchpad link now carries concept/exercise context
- `frontend/src/pages/CurriculumMap/CurriculumMap.jsx` — intro copy: 50-day, Python-only
- `frontend/src/pages/Dashboard/Dashboard.jsx` — copy updates (50 days, Hard/Complex); **real bug fix**: hardcoded `pct(count, 45)` denominator replaced with a dynamically computed lesson total
- `frontend/src/pages/LessonDetail/LessonDetail.jsx` — Scratchpad link carries lesson context; **real bug fix**: day-nav cap `>= 45` → `>= 50`
- `frontend/src/pages/ProblemBrowser/ProblemBrowser.jsx` — new Curriculum Order / Difficulty sort dropdown; copy updates
- `frontend/src/pages/Scratchpad/Scratchpad.jsx` — new context banner + guarded starter-code prefill for the Try-in-Scratchpad handoff

**New:**
- `backend/db/seed_problems_expansion.py` — all 41 new problems
- `deliverables/EXPANSION_PLAN.md` — working plan (audit + full problem table)
- `deliverables/FINAL_REPORT.md` — this report

**Not changed (deliberately):** `backend/app.py` (no functional change needed), `Learn.jsx`, `ProblemWorkspace.jsx` — see item 12.

## 10. Tests run and results

- **Seeding**: `python3 db/init_db.py` on a fresh DB → *"Initialized: 50 lessons, 150 problems, 627 test cases (auto-verified against reference solutions), 29 concept lessons."* All 627 test cases (including every one of the 41 new problems') are verified against their own reference solutions at seed time — this is a hard gate, not a spot check.
- **Backend endpoint suite**: `python3 test_endpoints.py` against a freshly reseeded DB → **ALL CHECKS PASSED** (~60 checks: all pre-existing Run/Trace/stdin/attempts/progress checks, plus the new 150-problem count, 50-lesson count, difficulty-validity, and full coverage-matrix assertions). Note: this suite performs real writes (attempts, lesson status) as part of testing, so it is not safely rerunnable without a reseed between runs — confirmed by re-running it a second time against the same DB and seeing 2 expected, state-related (not code) failures, then reseeding and getting a clean pass again.
- **Live API spot-checks**: 17 of the 41 new problems' reference solutions submitted via `POST /api/problems/<slug>/run` → all returned `all_passed: true`. `GET /api/concepts/greedy` → correct title, 6 related problems, 3 checkpoints, 1 practice exercise with the exact field shape the Scratchpad handoff expects. `GET /api/concepts` → 29 total.
- **Frontend build**: `npm run build` → succeeds cleanly, zero errors (run 4 times across the session).
- **Browser verification (Playwright, this pass)**:
  - Problem Bank "Sort:" dropdown: Curriculum Order (default) and Difficulty both render correctly; Difficulty mode groups into Easy/Medium/Hard/Complex sections in that order, purely presentational (confirmed no DB writes triggered).
  - Complex difficulty badge renders with a distinct magenta (`rgb(194,64,158)`), clearly separated from Easy (green), Medium (orange), Hard (red).
  - Try-in-Scratchpad from a **lesson** (Day 8): banner correctly shows "From Day 8: Array patterns I ... — that day's problems: Remove Duplicates from Sorted Array, Jump Game, Merge Intervals"; no code prefill (correct — a day can have multiple problems, so this path is banner-only by design).
  - Try-in-Scratchpad from a **concept exercise** (Greedy → `min_platforms`): banner correct; starter code guarded-prefilled into the editor on a fresh/untouched Scratchpad.
  - **Guard verified**: typed custom code into the Scratchpad, then re-navigated to the same concept-exercise link — the editor content was unchanged (byte-for-byte identical before/after), confirming the prefill never overwrites existing work.
  - Split-screen and Stacked layouts both still render and toggle correctly.
  - 5 new problem workspace pages spot-checked in the browser (lru-cache, binary-tree-cameras, lfu-cache, reverse-nodes-k-group, kth-smallest-sorted-matrix) — all render with **zero console/page errors**.

## 11. Architectural issues discovered

1. `_related_problems_for_concept()` in `backend/app.py` matches on exact `topic` equality, so a concept lesson can only auto-link to problems sharing its own topic value. The new Greedy concept lesson therefore cannot auto-link to `max-area-container`, `jump-game` itself, `boats-to-save-people`, or `task-scheduler` — 4 pre-existing problems that reason greedily but deliberately keep their original topics (arrays/two-pointer/stacks etc.) rather than being reassigned. Worked around by naming those 4 in the lesson's prose (`recognize_markdown`) instead of a DB relationship — no schema change, per scope. Flagging in case you'd rather widen that matching logic later.
2. `test_runner.py`'s `comparison_mode` has no "any one valid answer accepted" mode, which several classic problems genuinely need (topological sort, "any valid rearrangement"). Worked around by constructing test cases with a forced-unique correct answer (e.g. `alien-dictionary`'s tests use a straight letter chain) rather than building new comparison infrastructure — out of scope per your spec, but a real gap if a wider set of "multiple valid answers" problems gets added later.
3. `test_endpoints.py` is not idempotent — see item 10. Worth knowing before it's rerun manually or wired into CI without a reseed step in between.
4. `docs/45-day-curriculum.md` (691 lines, internal reference doc) still describes the old 109-problem/45-day state and was not rewritten — see item 12.

## 12. Decisions that still require your approval

1. **`docs/45-day-curriculum.md` was not updated.** It's an internal reference doc, not runtime/user-facing, so I treated rewriting it as out of scope for this pass and left it stale rather than guess at a rewrite you didn't ask for. Say the word and I'll bring it in line with the new 150/50/Greedy/Complex state.
2. **`Learn.jsx` and `ProblemWorkspace.jsx` were left untouched** for the Python-only messaging audit — neither page had a natural generic-subtitle spot where adding "Python" wouldn't read as forced. Flagging as a judgment call rather than a confirmed decision.
3. **None of the 41 new problems were placed on a specific curriculum day** (all are Extended or Advanced tier, day=NULL) — only the pre-existing `jump-game` slug was promoted to Core/Day 8. This was deliberate, to avoid disturbing the carefully-paced Days 1–42 sequence, but it's a real choice: if you'd rather see some of the new Hard/Complex problems woven into specific days instead of left as open Extended/Advanced pool items, that's a different design and I held off making that call unilaterally.
4. **Days 46–50 content** (Weak-area revision, Advanced/Complex practice, Mock interview 4, Full-length final interview simulation, Final review) is built entirely from existing Problem Workspace/hints/solutions/attempts/progress functionality, as instructed — no new "mode" was built. Worth a read-through on your side since this is new curriculum prose, not just data.

---

**Nothing has been committed or pushed.** All changes above are sitting in the working tree at `/home/claude/traceviz`, ready for `git add`/`git commit` once you've reviewed this and given the go-ahead.
