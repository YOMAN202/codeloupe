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
