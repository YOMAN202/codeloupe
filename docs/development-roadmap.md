# Development Roadmap

This roadmap builds Traceviz vertically — every milestone ships something you actually use, in order, timed to land just ahead of the curriculum day that needs it. Nothing here is built speculatively ahead of need. If a milestone would land later than the curriculum day that wants it, the curriculum day proceeds anyway using pen-and-paper / a plain `.py` file (see `learning-philosophy.md`'s "usable even before the app exists" point) — the study schedule never waits on the build.

## Milestone 1 — Skeleton (target: ready before or during Days 1-7)

**Builds:** project structure (`backend/`, `frontend/`, per `architecture.md`), a minimal Flask API with one working route, a minimal React app with basic navigation, SQLite initialized with an empty schema, a basic lesson-display view (renders a lesson's concept/example text — no interactivity yet beyond reading), Monaco code editor embedded and wired to a "Run" button, submitted code executed via the sandbox (subprocess + timeout, no trace recording yet), and raw stdout/stderr displayed back to you.

**Stop-and-test criterion:** you can open the app, read a Day 1-style lesson, write a small script in the editor (e.g., the Day 1 exercises), click Run, and see correct output — or a clear error if your code is wrong. No visualization, no hints, no progress tracking yet. If this loop doesn't work end to end, nothing later matters.

**Then STOP.** Confirm this milestone is genuinely useful before adding anything else.

## Milestone 2 — First trace + array visualizer (target: ready by Day 8)

**Builds:** the `sys.settrace`-based step recorder (`backend/execution/tracer.py`), the trace JSON contract described in `architecture.md`, and the first visualizer — array boxes with index labels, current-line highlighting, and PLAY/PAUSE/STEP FORWARD/STEP BACK/SCRUB/RESET controls. Wired specifically to Day 8-16 lessons (array/string/hashing problems), since those are the simplest data shapes to visualize well.

**Stop-and-test criterion:** you can submit your own Day 8-era solution (e.g., your Two Sum attempt), and the trace visualizer correctly shows the array, the current line, and variable values updating step by step as *your* code runs — including showing a bug clearly if your code has one. This is the core resume-worthy feature; it needs to genuinely work well before anything else gets built on top of it.

**Then STOP.**

## Milestone 3 — Problem system, hints, testing, tracking (target: ready by ~Day 11-12, when hashing/Two-Sum-style problems start needing structured hints)

**Builds:** the problem database (schema + first ~25-30 seeded problems covering Blocks 1-2, per `problem-roadmap.md`), the 3-rung hint ladder with independent/assisted solve tagging, the AST analyzer for directional hints and mistake-pattern detection, the stress-test system (generated random inputs + brute-force comparison, first-failing-input reporting per `PART 7`), and SQLite-backed progress tracking (attempts, hints used, time taken, solved status).

**Stop-and-test criterion:** you can open a real problem from the database, attempt it, get a conceptual hint without seeing code, have a stress test catch a genuine bug in your solution and show you the first failing input, eventually solve it, and see it correctly logged as independent or assisted in the database.

**Then STOP.**

## Milestone 4 — Complexity estimation + benchmarking (target: ready by Day 15-17, as sliding window/sorting start making complexity comparisons concrete)

**Builds:** the AST-based structural estimator, the empirical benchmark runner (`timeit` + `tracemalloc` across increasing input sizes with curve-fitting), and the UI that asks you to estimate complexity *before* revealing either analysis, per `PART 8`.

**Stop-and-test criterion:** after solving a problem, you're prompted for your own time/space complexity estimate, then shown the structural and empirical estimates side by side, with disagreements flagged as a discussion prompt rather than silently resolved.

**Then STOP.**

## Milestone 5 — Topic-specific visualizers, one per block (ongoing, Days 17 through 42)

**Builds, one at a time, just ahead of need:** sorting animations (Day 17-20), recursion-tree/call-stack view (Day 23, reusing the trace recorder's `call_depth` field), linked-list node/pointer diagrams (Day 25), stack/queue push-pop/enqueue-dequeue visuals (Day 28-29), tree traversal + BST + level-order visuals (Day 30-32), heap bubble-up/down visuals (Day 33), graph adjacency/BFS/DFS/Dijkstra visuals (Day 35-38), and DP table-filling visuals, 1D and 2D only (Day 39-42).

**Stop-and-test criterion per visualizer:** each one is checked against your own real submitted code for that day's problems before the next visualizer is started — no visualizer gets built two topics ahead of where you currently are.

## Milestone 6 — Dashboard + spaced revision + mock interview mode (target: ready by ~Day 30-32, per your spec that mock-interview mode unlocks "by approximately day 30")

**Builds:** the analytics dashboard (per `problem-roadmap.md`'s dashboard section), the adaptive spaced-revision scheduler, and mock-interview mode (timer, no-hints, problem-only view, post-submission review covering correctness/complexity/clarity/edge cases/pattern recognition, per `PART 11`).

**Stop-and-test criterion:** the dashboard's numbers are checked by hand against a few known attempts to confirm they're computed correctly (this is exactly the kind of thing worth writing a real backend test for, per `PART 15`'s "tests" requirement); one full mock interview is run start to finish before Day 30 arrives, so it's not being debugged live during actual mock-interview practice.

## The 20% rule, operationally

Priority order, repeated here because every scoping call in this roadmap defers to it: (1) learning Python, (2) learning DSA, (3) solving problems independently, (4) the project reinforcing that learning, (5) project/resume polish. Concretely: at the end of each day, if building or debugging Traceviz took more than roughly 45-50 minutes out of a ~3.5-4 hour session, that's the 20% line — the next day's build work gets simplified or deferred, not the study plan. A milestone slipping by a few days because study time didn't allow more build time is expected and fine; a curriculum day getting cut short because the app needed fixing is the failure mode this rule exists to prevent.

## Commit conventions

Meaningful, `feat:`/`fix:`/`docs:`/`test:`-prefixed commits at the level of a completed capability, not a save-point — matching how the milestones above are scoped. Examples: `feat: add sys.settrace-based execution tracer`, `feat: add array trace visualizer with step controls`, `feat: add problem database schema and Block 1-2 seed data`, `feat: add 3-rung hint ladder with independent-solve tracking`, `feat: add stress-test generator with brute-force comparison`, `feat: add structural + empirical complexity estimator`, `feat: add linked-list pointer visualizer`, `feat: add progress dashboard`, `fix: correct off-by-one in sliding-window boundary trace capture`, `docs: add architecture decision record for sandbox execution model`. Each milestone in this document should correspond to roughly 3-8 commits, not one giant commit and not dozens of tiny ones.
