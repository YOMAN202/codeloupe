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

**Known, disclosed gap (as of the original 32-problem cut): two patterns were thinner than the rest.** Heaps had exactly one problem with no Medium follow-up. Graphs had Medium problems but no dedicated Easy warm-up. Both were closed in the expansion documented in the next section.

## Expansion: 32 -> 76 problems, three explicit tiers (Core / Extended / Advanced)

Once Phase 1's end-to-end frontend was verified (see `decisions.md`'s "Non-linear curriculum navigation" and the E2E test suite), the problem bank was expanded from 32 to **76 problems**, organized by a new `path_tier` column (`'core'` | `'extended'` | `'advanced'`) rather than one flat list. Every new reference solution followed the same two-pass verification the original 32 did: standalone correctness checks before being written into `seed_problems.py`, then a live-API pass (`verify_all_live.py`) re-running every problem's own reference solution through the real grading endpoint after seeding.

**1. Total Core problems: 51** (`path_tier='core'`, each tied to a specific curriculum day 8-42). This is the required 45-day path -- completing it is the "job-ready" bar the dashboard's Core Path progress bar tracks against.

**2. Total Extended problems: 19** (`path_tier='extended'`, `day=NULL`). Optional Easy/Medium reinforcement, not required within 45 days, filterable via `GET /api/problems?path_tier=extended`.

Plus a third tier added on explicit request, sitting outside both: **Advanced Challenges: 6 Hard problems** (`path_tier='advanced'`, `day=NULL`) -- Trapping Rain Water, Median of Two Sorted Arrays, Merge k Sorted Lists, Serialize/Deserialize Binary Tree, Word Ladder, and Edit Distance. Curated one per topic area that was thinnest at the Hard tier, not added to pad the count. Strictly optional: never tied to a day, never counted in Core Path completion, and the dashboard/problem-browser UI is explicit that Easy/Medium mastery (Core + Extended) is the primary goal.

**3. Breakdown by topic (core / extended / advanced / total):**

| Topic | Core | Extended | Advanced | Total |
|---|---|---|---|---|
| arrays | 4 | 3 | 1 | 8 |
| binary-search | 3 | 2 | 1 | 6 |
| dynamic-programming | 5 | 3 | 1 | 9 |
| graphs | 6 | 1 | 1 | 8 |
| hashing | 4 | 1 | 0 | 5 |
| heaps | 4 | 0 | 1 | 5 |
| linked-lists | 4 | 2 | 0 | 6 |
| queues | 1 | 0 | 0 | 1 |
| recursion | 4 | 1 | 0 | 5 |
| sliding-window | 2 | 1 | 0 | 3 |
| sorting | 4 | 0 | 0 | 4 |
| stacks | 2 | 1 | 0 | 3 |
| strings | 1 | 0 | 0 | 1 |
| trees | 4 | 3 | 1 | 8 |
| two-pointer | 3 | 1 | 0 | 4 |

**4. Breakdown by difficulty (all 76):** Easy = 31, Medium = 39, Hard = 6 (all 6 Hard problems are `advanced`-tier and excluded from the required 51-problem Core Path -- 0 Hard problems appear in Core or Extended). Within Core + Extended (the 70 Easy/Medium problems), every topic above has at least one Easy AND one Medium entry except `queues` (1 Medium only) and `strings` (1 Easy only) -- both intentionally thin because most queue- and string-heavy interview patterns are categorized under `sliding-window`, `two-pointer`, and `arrays` instead (e.g. sliding-window and two-pointer problems are almost all string/array problems in practice); this is a categorization choice, disclosed here rather than left implicit.

**5. Remaining weak coverage areas, disclosed honestly:** `queues` and `strings` as standalone topic labels (see above -- not a real coverage gap once sliding-window/two-pointer/arrays are counted, but worth knowing if filtering the problem browser by topic specifically). No topic has zero Extended-tier reinforcement except `sorting`, `heaps`, and `queues`/`strings` -- a reasonable next addition if further expansion happens, but not blocking: every topic already has full Core-tier Easy-to-Medium progression.

**6. Trace/visualization support by topic:** every problem across all three tiers gets the generic trace viewer (step-through debugger with locals at each step) plus the auto-detected array/pointer view (any list-typed local rendered as indexed boxes, with matching int-typed locals shown as pointer tags) -- this already gives arrays, two-pointer, sliding-window, sorting, and binary-search a genuinely useful picture for free, and works identically whether the traced code is correct or buggy (see `decisions.md`'s section on tracing incorrect code). No topic has a bespoke, topic-aware visualizer yet (a dedicated linked-list node/pointer diagram, a real tree render, a graph node/edge diagram, a call-stack view for recursion, or a DP state table) -- that's the explicitly-deferred Phase 3 work, to be built progressively now that the problem bank and generic tracer are both verified end-to-end for correct AND incorrect code.

**Stress testing / brute-force comparison (Phase 4, `has_stress_test`/`stress_test_generator` columns) is schema-ready but not populated** for any of the 32 problems yet -- every row currently has `has_stress_test=0`. This is an honest placeholder for a real, not-yet-built feature, not a silently-broken one: the columns exist so it can be added per-problem without a schema migration, but no stress-test generator functions have been written. See `decisions.md`.

**A genuine bug this curation work caught:** the original auto-verified test-case pipeline (`init_db.py`) called each problem's reference solution directly on its stored `test_inputs`. For "in-place mutation" style problems (e.g. `remove-duplicates-sorted`, which mutates its input array as part of the correct algorithm), this silently corrupted the *stored* input before it was written to the database -- the expected output was computed correctly against the original array, but the array itself got overwritten in memory before being serialized, so the seeded test case ended up comparing the right answer against the wrong (mutated) input. Running every problem's own reference solution back through the live API as a verification pass caught this immediately (`remove-duplicates-sorted` failed its own seeded test). Fixed by deep-copying each test input before calling the reference solution (`copy.deepcopy`, see `_compute_expected_outputs` in `init_db.py`) -- worth recording here because it's exactly the kind of subtle correctness bug the "auto-verify against a reference solution" design was meant to prevent in the first place, and it still slipped through until end-to-end testing against the real API (not just unit-testing the seeding logic in isolation) exercised it.

## Second expansion: 76 -> 109 problems, closing the queues/strings/sliding-window/two-pointer gaps

Once the 76-problem, 3-tier bank was stable, it was expanded again to **109 problems**, this time specifically targeting the coverage gaps disclosed at the end of the previous expansion (`queues` and `strings` each had only 1 dedicated problem; `sliding-window` and `two-pointer` had thin Easy-to-Medium progressions) rather than expanding uniformly. 33 new problems were added: 28 Easy/Medium (8 Core, 20 Extended) and 5 curated Hard (Advanced).

**A mandatory deduplication review preceded writing any of the 33 into the seed file.** Before finalizing the candidate list, every planned new problem was cross-checked against the full existing 76-problem bank (not just within its own topic) for three failure modes: an outright duplicate, a duplicate under a different name, and a problem teaching essentially the same pattern with no meaningful variation. This caught two real issues that would otherwise have padded the bank without adding learning value:

- **`valid-anagram` was independently proposed as a new Easy strings problem, but it already existed** in the 76-problem bank (`strings`/`core`/Easy). Dropped from the new-problems list; the strings gap was closed instead with a genuinely new Easy anchor (`longest-common-prefix`) plus five Medium variations, keeping the existing `valid-anagram` as the topic's Easy concept-introduction problem rather than adding a second one.
- **`moving-average-from-data-stream` and `number-of-recent-calls` (Recent Counter) were both candidates for the queues gap**, and on inspection are mechanically near-identical (append to a deque, evict stale entries from the front, read the current size) with the only real difference being a fixed-count window versus a time-bounded window. Rather than include both, only `number-of-recent-calls` was kept -- it maps to a more distinctly valuable real-world pattern (time-windowed rate limiting) and its inclusion alongside `implement-queue-using-stacks` and `design-circular-queue` still gives the topic a real Easy-to-Medium spread without the redundant middle entry.

Every one of the 33 problems that survived the review earns its place on one of the six grounds the review used explicitly: introduces a new pattern/data-structure-design idea not covered elsewhere (`merge-intervals`, `min-stack`, `add-two-numbers`, `subarray-sum-equals-k`, `clone-graph`, `partition-equal-subset-sum`, `task-scheduler`); is a deliberate Easy-to-Medium progression step building on an existing problem (`insert-interval` after `merge-intervals`; `remove-duplicates-sorted-array-ii` after the original `remove-duplicates-sorted`; `subsets-ii` after `subsets`; `valid-palindrome-ii` after `valid-palindrome`; `permutation-in-string` and `fruit-into-two-baskets` as new sliding-window sub-patterns distinct from the existing three); is a meaningfully different constraint variant sharing a broad pattern (`sort-colors`'s 3-way partition vs. the existing 2-pointer problems; `boats-to-save-people`'s greedy pairing vs. `max-area-container`'s greedy expansion; `minimum-size-subarray-sum`'s minimize-length objective vs. the existing maximize-length sliding-window problems); reinforces a high-interview-frequency skill not otherwise represented (`kth-smallest-element-in-bst`'s in-order-traversal-for-rank, `search-a-2d-matrix`'s flattened-grid binary search); or is a natural Hard capstone of a pattern family already built up through Easy/Medium (`minimum-window-substring` after the Medium sliding-window problems; `first-missing-positive`, `n-queens`, `binary-tree-maximum-path-sum`, `find-median-from-data-stream`). Every surviving problem was standalone-verified before being written into `seed_problems.py`, then re-verified through the live grading API (`verify_all_live.py`) after seeding -- the same two-pass process both prior expansions used, with 109/109 reference solutions passing.

**Final tier breakdown:** Core 59 (was 51, +8), Extended 39 (was 19, +20), Advanced 11 (was 6, +5).

**Final difficulty breakdown:** Easy 35, Medium 63, Hard 11 (all 11 Hard problems remain strictly `advanced`-tier -- 0 Hard problems in Core or Extended, unchanged from before).

**Breakdown by topic (core / extended / advanced / total):**

| Topic | Core | Extended | Advanced | Total |
|---|---|---|---|---|
| arrays | 5 | 5 | 2 | 12 |
| binary-search | 3 | 3 | 1 | 7 |
| dynamic-programming | 5 | 4 | 1 | 10 |
| graphs | 6 | 2 | 1 | 9 |
| hashing | 5 | 1 | 0 | 6 |
| heaps | 4 | 1 | 2 | 7 |
| linked-lists | 5 | 2 | 0 | 7 |
| queues | 2 | 2 | 0 | 4 |
| recursion | 4 | 2 | 1 | 7 |
| sliding-window | 3 | 3 | 1 | 7 |
| sorting | 4 | 0 | 0 | 4 |
| stacks | 3 | 1 | 0 | 4 |
| strings | 2 | 5 | 0 | 7 |
| trees | 4 | 4 | 2 | 10 |
| two-pointer | 4 | 4 | 0 | 8 |

**Gap status:** `queues` went from 1 problem to 4 (Easy: `implement-queue-using-stacks`; Easy: `number-of-recent-calls`; Medium: `design-circular-queue`; Medium: the existing `sliding-window-maximum`). `strings` went from 1 to 7 (Easy: `valid-anagram`, `longest-common-prefix`, `implement-strstr`; Medium: `longest-palindromic-substring`, `palindromic-substrings`, `reverse-words-in-a-string`, `string-to-integer-atoi`). `sliding-window` went from 3 to 7 and `two-pointer` from 4 to 8, both now with a genuine Easy-to-Medium-to-variation spread instead of 1-2 Medium entries. Every topic in the bank now has at least one Easy AND one Medium entry within Core+Extended -- the queues/strings thinness disclosed at the end of the previous expansion is fully closed.

**Remaining intentional gaps, disclosed honestly:** `sorting` and `stacks` still have no Extended-tier reinforcement beyond their Core problems (4 Core / 0 Extended, and 3 Core / 1 Extended respectively) -- both already have solid Easy-to-Medium Core progressions, and no additional Easy/Medium problem in either topic cleared the deduplication bar (the natural next candidates -- e.g. a second monotonic-stack problem, or heapsort as a fifth sorting algorithm -- were considered and judged pattern-redundant with what's already covered, so they were left out rather than added to pad a count). `heaps` and `sliding-window` each have exactly 2 Hard/Advanced problems (a deliberate exception to the "roughly one Hard per area" default, since both had two genuinely distinct high-value Hard applications -- k-way merge and task-scheduling-adjacent greedy heap use for heaps; minimize-with-frequency-coverage and the underlying monotonic-deque-max problem for sliding-window/queues). No topic has more than 2 Advanced-tier problems, and several topics (`hashing`, `linked-lists`, `sorting`, `stacks`, `two-pointer`) deliberately have zero -- not every topic needs a Hard capstone to be complete, and forcing one everywhere was explicitly rejected per the "don't pad Hard problems to hit a quota" instruction.

## Non-linear curriculum navigation

The 45-day sequence is a **recommended path, not a locked course**. Every lesson (`lessons` table) has an independent status in a new `lesson_progress` table: `not_started`, `in_progress`, `completed`, `skipped`, or `known` (the last for "I already know this, don't make me redo it"). None of these gate access -- `GET /api/lessons/<day>` works for any day regardless of what came before, and `PUT /api/lessons/<day>/progress` can set any day to any status at any time.

Recommended background for an advanced topic is shown, never enforced: each lesson's block (e.g. "Linked Lists, Stacks, Queues, Trees") maps to a coarse, block-level prerequisite graph (`logic/curriculum_graph.py`) -- e.g. that block recommends "Sorting, Binary Search, Recursion" as background, which itself recommends "Arrays, Strings, Hashing." `GET /api/lessons/<day>` returns a `recommended_prerequisites` list showing how much of each prerequisite block is already done (e.g. "7/9 days done") so the UI can display it as a gentle nudge, not a locked door. This is intentionally block-level rather than a hand-authored 45-node dependency graph -- the real pedagogical structure (trees/graphs need recursion, DP needs recursion, everything needs Python fundamentals) is captured without the cost of precisely justifying 45 individual edges for a recommendation that's advisory either way.

`GET /api/progress` additionally reports `lesson_status_counts`, `recommended_next_lesson` (the lowest-numbered `not_started` day -- the default "keep going in order" suggestion), `resume_lesson` (the most-recently-updated `in_progress` lesson -- "pick up where you left off," distinct from the recommended-next suggestion), and a full `lessons_overview` for rendering a curriculum map with each day's status at a glance.
