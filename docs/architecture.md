# Architecture

This document describes the system as it actually exists, not as originally planned (see `docs/development-roadmap.md` for the historical milestone plan, and `docs/decisions.md` for the reasoning behind individual choices along the way). Where something is a real limitation rather than a missing feature, it's stated plainly rather than hidden.

## System overview

Codeloupe is two independent processes talking over HTTP:

```
┌─────────────────────┐        JSON over HTTP        ┌──────────────────────┐
│  Frontend (Vite/React) │ ───────────────────────────▶ │  Backend (Flask)      │
│  http://127.0.0.1:5173 │ ◀─────────────────────────── │  http://127.0.0.1:5001 │
└─────────────────────┘                               └──────────┬───────────┘
                                                                   │
                                                          sqlite3 (stdlib)
                                                                   │
                                                          ┌────────▼────────┐
                                                          │ backend/db/     │
                                                          │ traceviz.db     │
                                                          └─────────────────┘
```

There's no ORM, no message queue, no external service dependency, and no required environment variable — the backend reads `PORT`/`FLASK_DEBUG` and the frontend reads `VITE_API_BASE`, all with working defaults, so a fresh clone runs with nothing to configure. This is a deliberate choice: the project is meant to be cloned and run by one person on their own machine, not deployed as a multi-tenant service, so the architecture stays proportional to that.

## Frontend architecture

React 19 + Vite 5, plain `fetch`-based API client (`frontend/src/api/client.js`), React Router in **hash mode** (`HashRouter`, not `BrowserRouter`) specifically so a page refresh or a direct link to `/#/learn/two-pointers` works without any server-side SPA-fallback routing — important for a project meant to run locally with the simplest possible serving setup.

Structure, under `frontend/src/`:
- `pages/` — one folder per route: `Dashboard`, `Learn` (concept-lesson hub) + `ConceptLesson` (single lesson), `CurriculumMap` + `LessonDetail` (the 45-day sequence), `ProblemBrowser` + `ProblemWorkspace` (the problem list and the solve/test/trace/compare workspace), `MistakeJournal`, `Scratchpad`.
- `components/` — shared UI: `Editor` (Monaco wrapper), `TraceViewer` (the real trace stepper, driven by live `/api/.../trace` output), `ConceptWalkthrough` (the lesson-side stepper, driven by hand-authored example frames — see "Two steppers, one visual language" below), `Visualizers` (the topic-specific rendering components both steppers share), `Checkpoint` (inline lesson quiz widgets), `Badges`, `MultilineText`.
- `monacoSetup.js` — Monaco is bundled from the npm package and wired through Vite's native `?worker` import, not fetched from a CDN at runtime. That's deliberate: a tool meant to be used offline for weeks shouldn't depend on a CDN being reachable every time it's opened.

**Production build:** `npm run build` outputs a fully static site to `frontend/dist/` (~16 MB, plain HTML/CSS/JS, no server-side rendering). The Flask backend does not currently serve this directory — see "Deployment" below for how the two are meant to be composed in production.

## Backend / API architecture

A single Flask application (`backend/app.py`, one file, no blueprints) fronting SQLite. Route groups, by prefix:

| Prefix | Covers |
|---|---|
| `/api/lessons` | The 45-day curriculum sequence and per-day progress |
| `/api/problems` | Problem listing/detail, running/testing code (`/run`, `/run-custom`), hints, tracing, complexity estimate, approach comparison, per-problem attempt history |
| `/api/attempts` | Logging a submission (this is also where mistake classification happens, synchronously, on a failed attempt) |
| `/api/mistakes` | The mistake journal and reviewing/confirming a classifier suggestion |
| `/api/concepts` | The concept-lesson hub: listing, detail, marking progress |
| `/api/progress` | The dashboard's aggregate view: solve stats, streak, topic/pattern weaknesses and strengths, curriculum and concept-lesson status counts, revision-due list |
| `/api/practice-session` | The "Today's session" recommender |
| `/api/run`, `/api/trace` | Free-standing code execution/tracing, independent of any curated problem (used by the Scratchpad) |

Business logic that isn't pure routing lives in `backend/logic/`: `analysis.py` (complexity estimation, code-aware hints), `approach_comparison.py`, `curriculum_graph.py` (prerequisite computation), `mistakes.py` (classification), `pattern_families.py` (the topic/pattern normalization layer, and the lookup that links a mistake or a weak pattern back to a concept lesson), `practice_session.py`, `revision.py` (spaced-repetition scheduling). Execution itself lives in `backend/execution/`: `sandbox.py` (subprocess isolation), `test_runner.py`, `tracer.py`.

## Database structure

SQLite, twelve tables, no migrations framework — the schema (`backend/db/schema.sql`) is applied fresh by `backend/db/init_db.py`, which also seeds all content from the `backend/db/seed_*.py` files. Re-running it is safe and idempotent; there's no separate "migrate an existing db" path, which is appropriate for a single-user local SQLite file but wouldn't be for a shared production database.

- `lessons`, `lesson_progress` — the 45-day curriculum sequence and per-day status
- `problems`, `test_cases`, `hints` — the curated problem bank
- `attempts` — every logged submission (code, pass/fail, hints used, time taken)
- `mistakes` — one row per failed attempt, classified (or honestly left unclassified) by category
- `revision_schedule` — spaced-repetition due dates, one row per problem once attempted
- `concept_lessons`, `concept_checkpoints`, `concept_practice_exercises`, `concept_lesson_progress` — the Learn-hub teaching system

`concept_lessons` links to `problems` and to `mistakes`/weak-pattern data by **computed string match** (`topic`, and optionally `pattern_family`), not a foreign key or join table — see `pattern_families.py`'s `concept_lesson_for_family` and `app.py`'s `_related_problems_for_concept`. This is deliberate: it means the link never goes stale as new problems or lessons are added, at the cost of being a string-equality match rather than an explicit relation. A mismatch fails safe (no lesson shown) rather than guessing.

## Code execution / sandbox design

`backend/execution/sandbox.py` runs submitted code in an isolated subprocess with a wall-clock timeout (5s) and a memory cap (256 MB, via `RLIMIT_AS` on Linux). This is enough to contain an accidental infinite loop or runaway allocation in a learner's own code — it is explicitly **not** hardened against a hostile actor (no seccomp, no container boundary, no network isolation beyond what the subprocess already lacks). That threat model is correct for "one person running their own code on their own machine" and would need real sandboxing (a container, gVisor, a proper seccomp profile) before ever accepting untrusted code from strangers.

## Trace generation pipeline

`backend/execution/tracer.py` runs the submission again, this time inside the sandbox with `sys.settrace` installed, and returns a flat list of steps: line executed, local variables at that instant (JSON-serializable, deeply-nested values truncated past 4 levels), call/return events, and call depth. This is the project's central differentiator, so it's worth being precise about what it actually does and doesn't do:

- It traces the **learner's own submitted code**, not a reference solution — a buggy submission produces a trace of the bug actually happening (wrong values, an early/late return, an exception mid-loop), not a generic failure message. `status` in the trace response distinguishes several real outcomes (ran to completion, raised an exception, hit the step cap, timed out) so the frontend can render each honestly instead of collapsing them into one "trace unavailable" state.
- It is capped at a fixed number of steps (`MAX_STEPS` in `tracer.py`) — deeply nested C-extension calls, threads, and pathological code (huge loops, very deep recursion) are captured up to that cap and then stopped, not fully captured. This is stated in the API response itself, not just in this document.
- It is **not a general-purpose debugger**. It's built for typical DSA-style code (loops, recursion, simple data structures) and traced with that scope in mind.

## Visualization adapter architecture

Trace steps are just `{line, locals, event, call_depth}` — turning that into a picture is the job of the components in `frontend/src/components/Visualizers/`. Two things share this rendering layer:

1. **Real traces** (`TraceViewer.jsx`) — `detect.js`'s `detectPrimaryView(problem, locals, graphKind)` inspects the current frame's locals (and, for node-based problems, a `graphKind` computed from the actual node structure) and picks a view: `ArrayPointerView`, `LinkedListView`, `TreeView`, `HeapView`, `GridGraphView`, `GraphNodeView`, or `DPTableView`.
2. **Concept-lesson walkthroughs** (`ConceptWalkthrough.jsx`) — hand-authored example frames (`backend/db/seed_concepts.py`), verified by actual execution when they're written, stepped through with the same controls and rendered with the **same visualizer components**. This is deliberate: a learner sees one consistent visual language whether they're following a curated example or tracing their own code. `ConceptWalkthrough.jsx` is a simpler stepper than `TraceViewer.jsx` on purpose (no play/predict-mode, no live event/depth reporting) — there's no real execution behind it, so it never pretends to be the real trace system.

Most visualizers take `locals` directly (`HeapView`, `GridGraphView`). Three need a normalized graph shape (`{nodes: Map(id -> {fields, fieldRefs|neighborIds}), roots: [{name, id}]}`) built by small adapter functions — `LinkedListView`/`TreeView` from live trace output via `nodeGraph.js`, and the equivalent hand-authored shape in `ConceptWalkthrough.jsx` for lesson frames. `DPTableView` is the one exception that needs more than the current frame: its cell-level "just changed" highlighting looks backward through the full step history to find a value's previous state.

## Lesson / content architecture

Two content systems that intentionally stay separate rather than being merged into one:

- **The 45-day curriculum** (`lessons` table, seeded from `backend/db/seed_lessons.py`) — a fixed day-by-day sequence with its own progress tracking, driving "resume" and "recommended next" on the dashboard.
- **Concept lessons** (`concept_lessons` + related tables, seeded from `backend/db/seed_concepts.py`) — 28 topic/pattern lessons in the Learn hub, each with what/why/recognize/intuition sections, a verified interactive walkthrough, inline checkpoints, and a practice exercise, with its own independent progress tracking (`concept_lesson_progress`).

They're linked by topic/pattern-family string match (see "Database structure" above), not merged, because they answer different questions — "where am I in the 45-day plan" vs. "how well do I know this specific pattern" — and folding one into the other's progress count would misrepresent both. The dashboard surfaces both counts side by side for exactly this reason.

## Mistake classification design

`backend/logic/mistakes.py` classifies a failed attempt into one of a fixed set of ten DSA mistake categories (off-by-one, missed edge case, incorrect base case, etc.) using only evidence already available at attempt-log time — which test case failed, whether it crashed, what kind of exception — never a second execution or trace call. The classifier is deliberately conservative: an automatic classification is always tagged `likely_issue`, never a higher confidence tier, and a case with no confident rule match is left `unclassified` rather than forced into the nearest category. A learner can later confirm a suggestion (`user_confirmed`) or pick their own category, including for an unclassified entry (`manually_selected`) — once a human has answered, the heuristic is never re-run over it.

## Revision / recommendation logic

Two related but distinct pieces:

- **Spaced revision** (`backend/logic/revision.py`) — a straightforward due-date schedule per problem, advanced based on how the last attempt went.
- **"Today's session"** (`backend/logic/practice_session.py`) — a small, fully-explained recommender, not a scored ranking model. It reads signals that already exist elsewhere (the revision schedule, mistake-journal categories bucketed by pattern family via `pattern_families.py`, plain topic-weakness counts) and offers up to five items: a due revision, a problem tied to a recurring mistake, an occasional related-lesson revisit (only when the mistake maps to a lesson the learner hasn't already completed), a problem in a weak pattern/topic, and a new Core-tier problem. Every item carries a plain-language `reason` string built from the same data a person could see themselves elsewhere in the app — there's no hidden scoring, and nothing here is a required path; every lesson, topic, and problem stays reachable through normal navigation regardless of what's recommended.

## Approach comparison methodology

`backend/logic/approach_comparison.py` estimates a *structural* complexity for the learner's own submitted code (loop nesting depth, recursion shape) from the trace step count on representative inputs — not a proven asymptotic bound, and the API response says so. Where a problem has a curated brute-force baseline, the comparison shows it alongside an optimized reference so the learner can see *why* one approach is better on their own problem's inputs; where no baseline is curated, the response degrades honestly (`has_baseline: false`) rather than fabricating one.

## Deployment

Codeloupe currently ships as two dev servers, which is the right shape for its actual use case (one person, one machine, `npm run dev` + `python3 app.py`). For deploying it somewhere more permanent, the recommended shape — nothing here is built yet, this is guidance, not infrastructure the project imposes on you:

- **Backend:** run `backend/app.py` behind a production WSGI server (e.g. `gunicorn`), not Flask's own dev server. It needs no database server (SQLite file) and no environment variables beyond the already-optional `PORT`.
- **Frontend:** `npm run build` produces a static site (`frontend/dist/`) that can be served by any static host or CDN, or placed behind the same reverse proxy as the backend. Point it at the backend via `VITE_API_BASE` at build time if the two aren't on the same origin.
- **Sandbox caveat:** if this is ever exposed to untrusted users rather than run locally by its owner, the execution sandbox described above needs to be hardened first (real container isolation, not just a subprocess with resource limits) — this is a genuine gap, not an oversight to gloss over.

## Known limitations

Stated plainly rather than buried: the sandbox trusts the code it runs (single-user threat model only); the complexity estimator is a structural teaching aid, not a certifier; the trace visualizer's renderers cover the specific data shapes the curriculum uses, not arbitrary Python objects; traces are capped at a fixed step count; the problem bank and lesson set are curated and intentionally not exhaustive; there's no production static-file-serving wired up yet (see "Deployment" above — this is a documented gap, not a hidden one). See `docs/decisions.md` for the full, dated log of every scope decision behind these.
