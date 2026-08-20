# Traceviz

A Python-first, DSA learning environment built alongside a 45-day placement-prep curriculum. You write real solutions, run them in a sandboxed backend, and (from Milestone 2 onward) watch your own code execute step by step. Full project rationale, the day-by-day curriculum, and every architecture/scope decision are documented in [`docs/`](docs/) — start with `docs/decisions.md` if you want the honest version of what this is and isn't.

## Status: Milestone 1

Working right now: a lesson view backed by SQLite, a Monaco code editor, and a "Run" button that executes your code in a sandboxed subprocess (timeout + memory/CPU limits) and shows raw stdout/stderr. No trace visualization, hints, stress testing, complexity analysis, or dashboards yet — those are later milestones, built one at a time, just ahead of the curriculum days that need them. See `docs/development-roadmap.md` for the full milestone plan.

## Running it locally

Requires Python 3.11+ and Node 18+.

**Backend:**
```bash
cd backend
pip install -r requirements.txt
python3 app.py
```
Starts on `http://127.0.0.1:5001`, initializing `db/traceviz.db` on first run.

**Frontend** (in a second terminal):
```bash
cd frontend
npm install
npm run dev
```
Starts on `http://127.0.0.1:5173`.

Open the frontend URL — you should see Day 1's lesson on the left and a working code editor on the right.

## Why Monaco is bundled locally, not loaded from a CDN

`@monaco-editor/react` defaults to fetching Monaco from `cdn.jsdelivr.net` at runtime. That's a reasonable default for most apps, but it's a bad fit here on two counts: it silently fails in any network-restricted environment (which is exactly how this was first built and tested), and — more importantly — a tool meant to be used offline on your own machine for 45 days shouldn't depend on a CDN being reachable every time you open it. `frontend/src/monacoSetup.js` points the editor at the `monaco-editor` package installed via npm instead, with the editor's web worker wired up through Vite's native `?worker` import. See the comments in that file for the exact (slightly unintuitive) import path required by `monaco-editor`'s package `exports` map.

## Project layout

See `docs/architecture.md` for the full target folder structure and the reasoning behind each piece.
