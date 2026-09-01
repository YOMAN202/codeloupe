# Problem Roadmap

## Problem schema

Each problem in the database is one record with the following fields:

- `id`, `title`
- `topic` (e.g. "arrays", "hashing", "trees") and `pattern` (e.g. "two-pointer", "sliding-window", "BFS") — topic is the curriculum block, pattern is the reusable technique, since the same pattern often spans multiple topics
- `difficulty` (Easy / Medium / Hard, LeetCode-relative where the problem has a direct LeetCode analog)
- `description`, `examples` (input/output pairs), `constraints`
- `expected_complexity` (target time/space — used to check your empirical benchmark against a reasonable bar, not to grade you against a single "correct" answer)
- `hints` (the 3-rung ladder: conceptual, directional, pseudocode — see `learning-philosophy.md`)
- `common_mistakes` (seeds the AST-analyzer's pattern-matching for that specific problem)
- `brute_force_approach`, `optimal_approach` (short text descriptions, used in post-solve review, not shown up front)
- `test_cases` (curated edge cases) plus a `generator` spec (how to produce randomized stress-test inputs, and what brute-force reference function to compare against, per `PART 7` of your brief)
- `related_problems` (ids), `prerequisites` (ids or topic names — used to decide what's unlocked when)
- `curriculum_day` (which day in `45-day-curriculum.md` this problem belongs to)

## Starter problem set (curated, not exhaustive)

The full per-day list already lives in `45-day-curriculum.md` (field 6 of every day) — this section is the aggregate view plus counts, so the database's initial seed size is concrete rather than open-ended, per your instruction to start curated and expand later.

| Block | Days | Topics | Approx. problem count |
|---|---|---|---|
| 1 | 1-7 | Python fundamentals, first array/hash drills | ~25 drills (not LeetCode-style) + 3 problems |
| 2 | 8-16 | Arrays, strings, hashing, two pointers, sliding window | ~24 problems |
| 3 | 17-24 | Sorting, binary search, recursion, backtracking intro | ~17 problems (+ implementation exercises) |
| 4 | 25-32 | Linked lists, stacks, queues, trees | ~18 problems |
| 5 | 33-38 | Heaps, graphs, BFS/DFS, Dijkstra | ~12 problems |
| 6 | 39-42 | Intro DP (1D and 2D) | ~7 problems |
| 7 | 43-45 | Revision + mock interviews | 6-8 revision problems + 3 mock-interview problems |

Total starter bank: roughly **90-95 problems**, each hand-selected for the specific pattern that day teaches (not scraped in bulk), which matches "start with a curated set rather than hundreds" directly. Every problem above is either a well-known LeetCode-style problem (used under its usual name so you can cross-reference outside explanations if you want a second source) or, for the handful of implementation-exercise "problems" (e.g. "implement merge sort"), a self-contained spec since there's no single canonical LeetCode entry for "write the algorithm itself."

## Expansion plan (after the core system works)

Expansion happens in two triggered ways, not on a fixed schedule: (1) topic-driven — once Milestone 3 (problem system) is stable and you've moved past the first few curriculum blocks, each topic's pool grows from ~3 curated problems to ~6-10, giving room for the spaced-repetition system to pull a *different* problem on a topic's revision date instead of literally re-serving the same one every time; (2) weakness-driven — once the tracker (see below) has real data on your recurring mistakes, additional problems get added specifically targeting whatever pattern you're weakest in, rather than expanding breadth uniformly. Bulk-importing a large public problem set is explicitly out of scope for the 45 days (see `decisions.md`) — quality and curriculum-fit matter more than volume for a beginner on a deadline.

## Spaced revision scheduling (implementation of `PART 10`)

Each `(problem, attempt)` record stores enough to drive an adaptive schedule: whether the solve was independent or hint-assisted (per `learning-philosophy.md`'s permanent tagging), how many hints were used, and whether any stress test initially failed. The default schedule is the simple fixed ladder — first exposure → next day → 3 days → 7 days → 14 days — but the *interval* used between rungs adapts to performance: an independent, no-hints, first-try solve moves through the ladder at the stated pace or slightly slower (revision demand is genuinely lower), while a solve that took 2+ hints or multiple failed stress tests compresses the ladder (e.g., next day → 2 days → 4 days → 7 days) since the evidence says the concept hasn't stuck yet. This adaptive logic is intentionally simple (a small multiplier on the base intervals driven by hint count) rather than a full spaced-repetition algorithm like SM-2 — accuracy here matters less than the basic signal being right, and a more elaborate scheduler would be effort spent on the tool instead of on DSA.

## Dashboard data this feeds (per `PART 9`)

Every field above rolls up into the progress dashboard: total problems attempted/solved, independent-solve count and rate, current daily streak, top weak topics (by mistake frequency and hint usage) and top strong topics (by independent-solve rate), problems currently due for revision, average time-to-solve by topic, overall hint-usage rate, and topics considered "mastered" (defined as: 2+ independent solves in that topic with no revision currently overdue). Deliberately excluded, per your "do not gamify excessively" instruction: streak-based rewards/badges, point scores, leaderboards, or any mechanic whose purpose is engagement rather than information. The dashboard's job is to answer "where am I actually weak," not to make you feel good about usage.

## Actual implementation (Phase 1 pivot, post-subscription-deadline)

The section above was written before any code existed, as a planning target. What actually shipped is a **deliberately smaller, fully-verified 32-problem bank** rather than the ~90-95 originally sketched — see the reasoning below, and `decisions.md`'s note on this same tradeoff.

**Reference framework.** Problem selection was cross-checked against NeetCode 150 (pattern selection -- which techniques are actually asked in interviews) and Striver's DSA sheet / Take U Forward (topic sequencing -- what foundational order those patterns are normally taught in), with LeetCode's canonical problem pages used as an external reference point per problem (`canonical_reference` field, e.g. `"LeetCode 1: Two Sum"`). No problem statement was copied verbatim from any of these -- every description, constraint list, and hint in the database is original phrasing written for this curriculum. The goal was explicitly a **curated, deduplicated** set achievable in 45 days, not a merge of every entry from every list (which would mean hundreds of overlapping problems).

**Interview-priority taxonomy.** Every problem carries `interview_priority` (`Core` / `Important` / `Optional`), `estimated_solve_minutes`, and `progression_stage` (`core` / `variation`). Core = a problem you should recognize the instant a similar one shows up in an internship OA or phone screen (Two Sum, Valid Parentheses, Reverse Linked List, Binary Search, Merge Two Sorted Lists, Max Depth of Binary Tree, Group Anagrams, Climbing Stairs, and similar). Important = high-frequency but slightly more specialized. Optional = foundational/pedagogical (e.g. implementing bubble sort by hand) but rarely the actual interview question itself.

**Difficulty distribution is Easy/Medium only, by design.** Every one of the 32 seeded problems is Easy or Medium -- no Hard problems are part of the core 45-day path, matching the explicit instruction to prioritize internship/entry-level readiness over Hard-problem breadth. (Hard problems remain a reasonable post-Day-45 extension, listed in `decisions.md`'s deferred section, not something silently missing.)

**Progression shape.** The requested ladder -- concept → beginner exercise → Easy → Easy pattern-practice → Medium → Medium variation → revision -- is realized across the system rather than as 6 separate problem rows per pattern (that would mean ~90 problems at full rigor, which didn't fit the remaining build time honestly -- see the tradeoff note below):
- **Concept** = the day's lesson theory (`concept_markdown`, `why_it_matters`).
- **Beginner exercise** = the day's `exercises_markdown` (lightweight, non-graded implementation drills -- present for every day, most fully fleshed out for Days 1-7's Python fundamentals).
- **Easy → Medium, same pattern** = realized as an explicit pair of DIFFERENT curated problems for the highest-frequency patterns, both fully test-graded:
  - two-pointer: `two-sum-sorted` (Easy) → `max-area-container` (Medium)
  - sliding-window: `max-sum-subarray-k` (Easy) → `longest-unique-substring` (Medium)
  - binary-search: `binary-search` (Easy) → `search-rotated-sorted` (Medium)
  - recursion/backtracking: `factorial-recursive` (Easy) → `subsets` (Medium)
  - hashing: `two-sum` (Easy) → `group-anagrams` (Medium)
  - linked-lists: `merge-two-sorted-lists` (Easy) → `linked-list-cycle-detection` (Easy) → `reverse-linked-list` (Easy) -- three Easy-tier problems building the same pointer-manipulation muscle before anything harder is needed at this level
  - trees: `max-depth-binary-tree` (Easy) → `binary-tree-level-order` (Medium)
  - DP: `climbing-stairs` (Easy) → `coin-change` (Medium) → `unique-paths` (Medium)
  - sorting: `bubble-sort`/`insertion-sort` (Easy, foundational) → `merge-sort`/`quicksort` (Medium, divide-and-conquer)
- **Revision** = the existing adaptive spaced-repetition system (unchanged from the section above) -- a problem already solved comes back at 1/3/7/14-day intervals, compressed if hint-assisted.
- Each individual problem ALSO internally carries a brute-force-then-optimal progression (`brute_force_approach` explained, then `optimal_approach` -- the 3-rung hint ladder walks a learner from one to the other), so even a single-problem pattern isn't just "here's the answer."

**Known, disclosed gap: two patterns are thinner than the rest.** Heaps has exactly one problem (`kth-largest-stream`, Easy) with no Medium follow-up. Graphs has three Medium problems (`number-of-islands`, `max-area-of-island`, `network-delay-time`) but no dedicated Easy warm-up. Both are real gaps, not oversights papered over -- closing them properly (a verified Easy heap problem, a verified Easy graph traversal problem) is a reasonable next addition and is listed in `decisions.md`.

**Stress testing / brute-force comparison (Phase 4, `has_stress_test`/`stress_test_generator` columns) is schema-ready but not populated** for any of the 32 problems yet -- every row currently has `has_stress_test=0`. This is an honest placeholder for a real, not-yet-built feature, not a silently-broken one: the columns exist so it can be added per-problem without a schema migration, but no stress-test generator functions have been written. See `decisions.md`.

**A genuine bug this curation work caught:** the original auto-verified test-case pipeline (`init_db.py`) called each problem's reference solution directly on its stored `test_inputs`. For "in-place mutation" style problems (e.g. `remove-duplicates-sorted`, which mutates its input array as part of the correct algorithm), this silently corrupted the *stored* input before it was written to the database -- the expected output was computed correctly against the original array, but the array itself got overwritten in memory before being serialized, so the seeded test case ended up comparing the right answer against the wrong (mutated) input. Running every problem's own reference solution back through the live API as a verification pass caught this immediately (`remove-duplicates-sorted` failed its own seeded test). Fixed by deep-copying each test input before calling the reference solution (`copy.deepcopy`, see `_compute_expected_outputs` in `init_db.py`) -- worth recording here because it's exactly the kind of subtle correctness bug the "auto-verify against a reference solution" design was meant to prevent in the first place, and it still slipped through until end-to-end testing against the real API (not just unit-testing the seeding logic in isolation) exercised it.

## Non-linear curriculum navigation

The 45-day sequence is a **recommended path, not a locked course**. Every lesson (`lessons` table) has an independent status in a new `lesson_progress` table: `not_started`, `in_progress`, `completed`, `skipped`, or `known` (the last for "I already know this, don't make me redo it"). None of these gate access -- `GET /api/lessons/<day>` works for any day regardless of what came before, and `PUT /api/lessons/<day>/progress` can set any day to any status at any time.

Recommended background for an advanced topic is shown, never enforced: each lesson's block (e.g. "Linked Lists, Stacks, Queues, Trees") maps to a coarse, block-level prerequisite graph (`logic/curriculum_graph.py`) -- e.g. that block recommends "Sorting, Binary Search, Recursion" as background, which itself recommends "Arrays, Strings, Hashing." `GET /api/lessons/<day>` returns a `recommended_prerequisites` list showing how much of each prerequisite block is already done (e.g. "7/9 days done") so the UI can display it as a gentle nudge, not a locked door. This is intentionally block-level rather than a hand-authored 45-node dependency graph -- the real pedagogical structure (trees/graphs need recursion, DP needs recursion, everything needs Python fundamentals) is captured without the cost of precisely justifying 45 individual edges for a recommendation that's advisory either way.

`GET /api/progress` additionally reports `lesson_status_counts`, `recommended_next_lesson` (the lowest-numbered `not_started` day -- the default "keep going in order" suggestion), `resume_lesson` (the most-recently-updated `in_progress` lesson -- "pick up where you left off," distinct from the recommended-next suggestion), and a full `lessons_overview` for rendering a curriculum map with each day's status at a glance.
