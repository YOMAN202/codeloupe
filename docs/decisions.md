# Technical Decisions and Tradeoffs

This document exists so the project can be shown on a resume/GitHub honestly — documenting what was deliberately cut and why is itself a signal of engineering maturity, and it's also just true: every decision below was made to protect the 45-day DSA-learning goal, not because of a technical limitation we couldn't work around.

## What we are explicitly not building, and why

**Auth, accounts, multi-user support, cloud deployment.** This is a single-user local tool for 45 days of personal study. Adding real authentication and a production deployment is legitimate work, but it has zero relationship to whether you learn recursion — it's real effort competing directly with study time for no learning payoff. If a public version is ever wanted, it's a clean, well-scoped follow-up project after Day 45, not a day-1 requirement.

**A hardened, multi-tenant-safe code execution sandbox.** The execution model (subprocess, timeout, resource limits, no network) is appropriate for "don't let my own typo hang the app," not for "defend against a hostile stranger's exploit." Building genuinely hostile-input-safe sandboxing (containerization, seccomp, gVisor-style isolation) is a deep, separate discipline that would consume real build time for a threat model that doesn't apply here — you're the only user, running your own code.

**A general-purpose "visualize any Python value" engine.** The trace visualizer renders specific, known data-structure shapes (arrays, linked-list nodes, call stacks, trees, graphs, DP tables) that are pattern-matched from `step.locals`, not a universal object visualizer. A fully general version is a much harder and more open-ended engineering problem, and the curated version covers 100% of what the curriculum actually needs.

**A from-scratch Python interpreter or custom execution engine.** `sys.settrace` plus subprocess isolation does everything the tracer needs. Writing a toy interpreter is a fun, legitimate project — just a different one, with essentially no DSA-learning content.

**Bulk-importing hundreds of problems.** The starter bank (~90-95 problems, see `problem-roadmap.md`) is hand-curated to match the curriculum's actual patterns. A bulk import would dilute quality and curriculum-fit for a beginner on a deadline, and volume was never the bottleneck — pattern coverage was.

**A high-fidelity conversational mock-interview AI.** Mock-interview mode (`PART 11`) is deliberately a focused, minimal-UI feature: timer, problem, editor, structured post-submission review. A fully conversational interviewer that asks natural follow-ups and reacts to hesitation is a much bigger product in its own right and risks becoming the interesting-to-build distraction the whole project is designed to avoid.

**Excessive gamification.** No points, badges, streak rewards, or leaderboards, per your explicit instruction. The dashboard's only job is showing you the truth about where you're weak.

**Advanced DSA topics beyond the 45-day scope** (segment/Fenwick trees, tries, union-find, Bellman-Ford/Floyd-Warshall/MST, bitmask/digit DP, advanced string algorithms). These are genuinely good topics — just not ones a placement-focused beginner needs inside 45 days, per the curriculum's stated priority of depth over breadth (see `45-day-curriculum.md`'s coverage summary).

## Honest framing of the complexity estimator

The estimator produces a **complexity estimate**, combining a structural (AST-based) signal and an empirical (benchmark-based) signal — never a mathematically authoritative Big-O determination. This distinction is enforced in the product's actual language, not just in this doc:

- Say: *"Implemented heuristic structural and empirical complexity estimation, combining AST-based static analysis with curve-fit runtime/memory benchmarking."*
- Never say: *"AI automatically determines Big-O"* or any phrasing implying the tool proves complexity rather than estimating it.

The limitations are real and worth stating plainly: the structural analyzer can be fooled by code whose real cost doesn't match its loop-nesting shape (e.g., an early-exit condition that changes measured complexity depending on input distribution, or a huge constant factor that looks like a different growth curve at small n); the empirical benchmark is only as good as the input sizes it's tested against and can misclassify a curve near the boundary between two growth shapes. The two signals are shown side by side specifically so that *you* reconcile them and justify your own answer — which is a more accurate simulation of what an interviewer actually asks for than a single "trust me" number would be.

## What's deferred to after Day 45

Anything in this list is a reasonable next step once placement-readiness is achieved, deliberately not attempted during the 45 days: authentication and a real deployment; a broader problem bank (hundreds of problems instead of ~90-95); the general-value visualizer; a more sophisticated spaced-repetition algorithm (e.g., full SM-2) instead of the simple adaptive ladder in `problem-roadmap.md`; a richer mock-interview experience; mobile support; multi-device sync.

## Milestone 1 build note: Monaco is bundled locally, not CDN-loaded

`@monaco-editor/react` defaults to fetching the Monaco editor from `cdn.jsdelivr.net` at runtime. During Milestone 1 this failed outright in the build/test environment (the CDN wasn't reachable), which forced a small, concrete implementation decision: bundle `monaco-editor` as a direct npm dependency and wire its web worker through Vite's native `?worker` import instead of the library's default loader. This isn't a compromise -- a locally-bundled editor is arguably the more correct choice anyway for a tool meant to run offline on your own machine for 45 days, so it's being kept even though the specific failure that surfaced it was environment-specific. Full detail and the exact (non-obvious) import path Monaco's package `exports` map requires is documented in `frontend/src/monacoSetup.js`.

## Known limitations, stated up front (for the eventual README)

The sandbox is appropriate for trusted, single-user code, not hostile input. The complexity estimator is a teaching aid, not a certifier. The trace visualizer's per-topic renderers cover the specific data shapes the curriculum uses, not arbitrary Python objects. The problem bank is curated and intentionally not comprehensive. None of these are things we didn't know how to build — they're things we chose not to build so that 45 days of build time didn't compete with 45 days of learning time.
