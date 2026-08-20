# Architecture

## Tech stack

**Backend:** Python 3.11+, Flask serving a small JSON API. Python is used for everything server-side — the execution sandbox, the trace recorder, the AST analyzer, the complexity estimator, the test-case generator — partly because Flask is already available in this environment with zero setup, and partly because reading/maintaining the backend's own Python is incidental extra exposure to real, working Python for you.

**Frontend:** React via Vite (not Next.js — a single-user local tool doesn't need server-side rendering or file-based routing, and Vite's dev server starts in under a second, which matters for a tool you'll reopen dozens of times over 45 days). Monaco Editor (VS Code's editor component) for the code editor — mature, handles Python syntax highlighting well, npm-installable. Visualizations are hand-built with SVG driven by React state for anything needing smooth step-scrubbing (the trace visualizer, sorting animations, tree/graph rendering); D3 is pulled in only if a specific visualization (e.g. force-directed graph layout) genuinely needs it, not by default.

**Database:** SQLite via Python's built-in `sqlite3` module. Zero setup, a single portable file, trivially inspectable, and perfectly sized for one user's data across 45 days.

**Execution sandbox:** `subprocess` running your submitted code with a hard timeout, `resource.setrlimit` (Linux) capping memory and CPU, a fresh temporary working directory per run, and no network access granted to the sandboxed process. This is a personal-tool threat model (don't let a stray `while True:` hang the app), not a multi-tenant public-service threat model — deliberately, since building actual sandbox-escape-hardened infrastructure would be a multi-week distraction from DSA with zero learning payoff (see `decisions.md`).

**Why not Streamlit for the core app:** Streamlit's rerun-the-whole-script execution model is awkward for smooth, stateful interactions like dragging a timeline scrubber and watching a linked-list pointer animate — every interaction re-runs the script top to bottom, which fights against exactly the kind of UI the trace visualizer needs. Streamlit remains a reasonable candidate later, in isolation, if the analytics dashboard specifically becomes annoying to build in React — but the default is one consistent React frontend.

## The trace visualizer (core technical feature)

This is the piece the whole project exists to build well, so it gets a full design pass here rather than being folded into a generic "features" list.

**Recording a trace.** When you submit code, the backend runs it in the sandbox with `sys.settrace` installed. On every line event, the tracer captures: the line number executed, a snapshot of local variables (name → value, with lists/dicts captured by value at that instant, not by reference, so later mutations don't retroactively corrupt earlier frames), the current function name and call depth (recursion depth falls out of this naturally), and, on `call`/`return` events specifically, the arguments passed in and the value returned. The result is a flat list of "steps," each a JSON object like:

```
{ "step": 12, "line": 7, "event": "line", "locals": {"i": 1, "max_val": 7, "arr": [4,7,2,9]}, "call_depth": 0 }
```

This list is the entire contract between backend and frontend — the frontend never re-derives program state, it only ever renders whatever step index it's currently displaying, which is what makes PLAY/PAUSE/STEP FORWARD/STEP BACK/TIMELINE SCRUBBING/RESET all trivial to implement (they're all just "change the current index into an already-computed array"). Rewinding isn't re-execution, it's just looking at an earlier already-recorded snapshot.

**Rendering a trace.** The frontend is a two-pane layout: your code on the left with the currently-executing line highlighted (mapped directly from `step.line`), and a data-structure visualization on the right that's driven by `step.locals`. The specific visualization component shown depends on which data structures are present in the current topic (array boxes for lists, a linked node diagram when a `Node`/`.next` pattern is detected, a call-stack panel when `call_depth` is nonzero, etc.) — this mapping is intentionally simple pattern-matching (Milestone 2 builds exactly one of these, the array visualizer, end to end; more are added topic-by-topic per `development-roadmap.md`), not a general "visualize any Python value" engine, which would be a much bigger and lower-value undertaking.

**Why this matters pedagogically, restated once here since it drives every design choice above:** because the trace is recorded from your actual submitted code, not a canned reference implementation, what you see is your own bug, live — an off-by-one shows up as the visualization doing the wrong thing at a specific, inspectable step, which is a fundamentally different (and better) debugging experience than reading a stack trace or a printed value.

## Sandbox execution flow

1. Your code is written to a temp file inside a fresh temp directory.
2. It's wrapped with the tracer setup and a call to your target function using the test/example input.
3. Run via `subprocess.run([...], timeout=N, cwd=tempdir)`, with `resource.setrlimit(RLIMIT_AS, ...)` and `RLIMIT_CPU` set in a `preexec_fn` (Linux) to cap memory and CPU time.
4. Stdout is captured for the trace JSON (or a structured error if the code raised an exception or hit the timeout — a timeout or crash is itself useful feedback, shown to you plainly rather than swallowed).
5. The temp directory is deleted after the run regardless of outcome.

This same sandbox is reused for plain "run my code and show output," for stress-testing against generated inputs, and for benchmarking — it's one execution primitive with different callers, not three separate systems.

## Complexity estimation

Two independent signals, shown side by side, explicitly framed as estimates (see `decisions.md` for the exact language used and why):

- **Structural (AST-based):** walk the parsed AST counting loop nesting depth, detecting recursive calls and estimating branching factor, flagging known-cost patterns (e.g., `x in some_list` inside a loop is a red flag; `x in some_set`/`some_dict` is not). This gives a quick, cheap first guess.
- **Empirical (benchmark-based):** run your submitted function across increasing input sizes (e.g., n = 100, 1000, 10000, 100000, generated automatically for the problem's input shape), record wall-clock time (`timeit`) and peak memory (`tracemalloc`), and fit the resulting curve against candidate growth shapes (O(1), O(log n), O(n), O(n log n), O(n²), O(2ⁿ)) via simple regression on log-log scale, picking the best fit.

Where the two disagree, that disagreement is surfaced to you as a prompt to think, not silently resolved — see `learning-philosophy.md`'s point that this is a *teaching* signal, not a grading oracle.

## Folder structure (target shape — created incrementally per milestone, not all at once)

```
traceviz/
  docs/                    # this documentation set
  backend/
    app.py                 # Flask app entrypoint / API routes
    execution/
      sandbox.py           # subprocess + resource-limit runner
      tracer.py            # sys.settrace-based step recorder
      stress_test.py       # random/edge-case generation + brute-force comparison
      benchmark.py         # timeit/tracemalloc empirical complexity runner
    analysis/
      ast_analyzer.py      # structural complexity + hint-relevant pattern detection
      complexity.py        # combines structural + empirical into an estimate
    problems/
      schema.py            # Problem dataclass/schema
      data/                # curated problem JSON/YAML files, one per problem
    db/
      schema.sql           # SQLite schema
      models.py            # thin data-access layer
    tests/                 # backend unit tests
  frontend/
    src/
      components/
        Editor/            # Monaco wrapper
        TraceVisualizer/   # play/pause/step/scrub UI + per-topic renderers
        Dashboard/         # progress analytics views
        LessonView/         # teaching-loop UI (concept -> example -> ... )
      pages/
      api/                 # fetch wrappers around the Flask API
    tests/
  README.md
```

## Milestone build order (high-level — full detail with stop-and-test criteria lives in `development-roadmap.md`)

M1: project skeleton, navigation, basic lesson view, code editor, plain code execution + output display (no trace, no visualization yet). M2: trace recorder + array visualizer, wired to real Day 8-16 lessons. M3: problem system + hints + stress testing + progress tracking. M4 onward: one additional visualizer family per curriculum block (recursion tree, linked list, tree/heap, graph, DP table), built just ahead of the days that need it, plus the dashboard and mock-interview mode near the end. Each milestone ships something you actually use before the next one starts.
