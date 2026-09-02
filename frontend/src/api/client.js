// Thin fetch wrappers around the Flask API. One function per endpoint,
// all sharing the same error-handling shape (throw with the server's own
// error message when available).

import { getVisitorId } from "./visitorId";

// Overridable via a VITE_API_BASE entry in frontend/.env(.local) for
// anyone running the backend on a different host/port -- the default
// (127.0.0.1:5001) is unchanged and matches backend/app.py's own default,
// so this is a no-op for the normal "everything on one machine" case.
const API_BASE = import.meta.env.VITE_API_BASE || "http://127.0.0.1:5001/api";

// ---- Infinity/NaN-safe JSON parsing -------------------------------------
// Python's own `json` module (used throughout backend/execution/tracer.py
// and app.py to serialize responses) allows `Infinity`, `-Infinity` and
// `NaN` as an extension to the JSON spec by default -- and a trace's
// `locals` legitimately contain these: `best = float("inf")` is a common,
// correct sentinel pattern (e.g. minimum-size-subarray-sum's reference
// solution). Those come across the wire as bare, UNQUOTED tokens
// (`Infinity`, not `"Infinity"`), which is not valid per strict JSON --
// the browser's native JSON.parse/res.json() throw a SyntaxError on them,
// which is exactly the bug this fixes.
//
// Rather than changing the backend's serialization (which would mean
// picking some other on-the-wire representation and updating tracer.py,
// AND would still need a frontend-side revival step to turn it back into a
// real number anyway), this parses the response text ourselves: swap the
// three bad tokens for quoted sentinel strings wherever they appear
// OUTSIDE of a string literal (so a value that happens to legitimately
// contain the text "Infinity" inside a real JSON string -- e.g. stderr
// output -- is left completely alone), parse normally, then walk the
// result turning the sentinels back into real `Infinity` / `-Infinity` /
// `NaN` JS numbers. A real `Infinity` is what everything downstream
// (isNumericList, Number.isInteger-based pointer detection, etc.) already
// expects a number to look like -- typeof Infinity === "number" is true,
// so no visualizer code needs to know this ever happened.
const NONFINITE_TOKEN_RE = /"(?:[^"\\]|\\.)*"|(-?Infinity|NaN)\b/g;
const NONFINITE_SENTINELS = {
  NaN: "__codeloupe_nan__",
  Infinity: "__codeloupe_posinf__",
  "-Infinity": "__codeloupe_neginf__",
};
const SENTINEL_TO_VALUE = {
  __codeloupe_nan__: NaN,
  __codeloupe_posinf__: Infinity,
  __codeloupe_neginf__: -Infinity,
};

function reviveNonFinite(value) {
  if (typeof value === "string" && Object.prototype.hasOwnProperty.call(SENTINEL_TO_VALUE, value)) {
    return SENTINEL_TO_VALUE[value];
  }
  if (Array.isArray(value)) return value.map(reviveNonFinite);
  if (value !== null && typeof value === "object") {
    const out = {};
    for (const k of Object.keys(value)) out[k] = reviveNonFinite(value[k]);
    return out;
  }
  return value;
}

// Parses a fetch Response as JSON, tolerating Python's non-standard bare
// Infinity/-Infinity/NaN tokens instead of throwing on them. Falls back to
// null for a genuinely empty body (e.g. a 204), same as callers already
// treated a bodyless response before this existed.
async function parseJsonResponse(res) {
  const text = await res.text();
  if (!text) return null;
  const sanitized = text.replace(NONFINITE_TOKEN_RE, (match, bad) =>
    bad === undefined ? match : `"${NONFINITE_SENTINELS[bad]}"`
  );
  return reviveNonFinite(JSON.parse(sanitized));
}

async function get(path) {
  const res = await fetch(`${API_BASE}${path}`, {
    // X-Visitor-Id scopes any per-visitor data this endpoint reads
    // (attempts/mistakes/revision schedule/progress/dashboard) to this
    // browser -- see backend/app.py's get_visitor_id. Harmless to send on
    // endpoints that don't use it (lessons/problems/concept content).
    headers: { "X-Visitor-Id": getVisitorId() },
  });
  if (!res.ok) {
    const body = await parseJsonResponse(res).catch(() => ({}));
    throw new Error(body?.error || `${path} failed: ${res.status}`);
  }
  return parseJsonResponse(res);
}

async function send(method, path, body) {
  const res = await fetch(`${API_BASE}${path}`, {
    method,
    headers: { "Content-Type": "application/json", "X-Visitor-Id": getVisitorId() },
    body: JSON.stringify(body ?? {}),
  });
  if (!res.ok) {
    const errBody = await parseJsonResponse(res).catch(() => ({}));
    throw new Error(errBody?.error || `${path} failed: ${res.status}`);
  }
  return parseJsonResponse(res);
}

// ---- lessons ---------------------------------------------------------
export const fetchLessons = () => get("/lessons");
export const fetchLesson = (day) => get(`/lessons/${day}`);
export const setLessonProgress = (day, status) =>
  send("PUT", `/lessons/${day}/progress`, { status });

// ---- problems ----------------------------------------------------------
export const fetchProblems = (params = {}) => {
  const qs = new URLSearchParams(params).toString();
  return get(`/problems${qs ? `?${qs}` : ""}`);
};
export const fetchProblem = (slug) => get(`/problems/${slug}`);
export const fetchHint = (slug, rung) => get(`/problems/${slug}/hints/${rung}`);
export const fetchHintFromCode = (slug, code) =>
  send("POST", `/problems/${slug}/hint-from-code`, { code });
export const fetchSolution = (slug) => get(`/problems/${slug}/solution`);
export const runProblem = (slug, code) => send("POST", `/problems/${slug}/run`, { code });
export const fetchComplexityEstimate = (slug, code) =>
  send("POST", `/problems/${slug}/complexity-estimate`, { code });
// Approach comparison: my code vs the optimal reference (always) and a
// brute-force baseline (only for problems that have one). revealCode=false
// (the default) returns every number but never the reference code itself --
// see app.py's approach_comparison docstring for the two-stage reveal.
export const fetchApproachComparison = (slug, code, revealCode = false) =>
  send("POST", `/problems/${slug}/approach-comparison`, { code, reveal_code: revealCode });
// Traces the learner's code AGAINST one of the problem's own test cases
// (appends a real call using that test case's args before tracing) -- see
// backend app.py's /api/problems/<slug>/trace docstring for why this is
// necessary: starter code is just a bare function definition, so tracing
// it raw would never actually run the function body at all.
// `opts.timeoutSeconds`, if given, asks the backend for a SHORTER execution
// budget than its own default (app.py clamps it -- a caller can only ever
// lower it, never raise it past the server's real limit). Used by the
// Problem Workspace's live preview panel so a background trace fired while
// the learner is still typing gives up fast on code that hangs, instead of
// tying up the single-worker dev server for the full default timeout on
// every debounce tick; the manual "Trace my code" button never passes this,
// so it keeps the full default budget.
export const traceProblem = (slug, code, testCaseIndex = 0, opts = {}) =>
  send("POST", `/problems/${slug}/trace`, {
    code,
    test_case_index: testCaseIndex,
    ...(opts.timeoutSeconds != null ? { timeout: opts.timeoutSeconds } : {}),
  });
// Custom test-case playground variant: trace the learner's OWN input
// instead of one of the problem's stored examples.
export const traceProblemCustom = (slug, code, args) =>
  send("POST", `/problems/${slug}/trace`, { code, custom_args: args });
// Runs the learner's code against one input THEY provide -- ungraded (no
// pass/fail, just the actual output or error). See app.py's run_custom.
export const runProblemCustom = (slug, code, args) =>
  send("POST", `/problems/${slug}/run-custom`, { code, args });

// ---- attempts / progress ------------------------------------------------
export const logAttempt = (attempt) => send("POST", "/attempts", attempt);
export const fetchProgress = () => get("/progress");
export const fetchAttempts = (slug) => get(`/problems/${slug}/attempts`);

// ---- manual revision ------------------------------------------------
// Reuses the same revision_schedule table the automatic ladder (above,
// via logAttempt) writes to -- these just let the learner opt a problem
// in/out directly. See app.py's add_manual_revision/remove_manual_revision.
export const fetchRevisionStatus = (slug) => get(`/problems/${slug}/revision`);
export const addToRevision = (slug) => send("POST", `/problems/${slug}/revision`);
export const removeFromRevision = (slug) => send("DELETE", `/problems/${slug}/revision`);

// ---- concepts (teaching system) -----------------------------------------
export const fetchConcepts = () => get("/concepts");
export const fetchConcept = (slug) => get(`/concepts/${slug}`);
export const setConceptProgress = (slug, status) =>
  send("PUT", `/concepts/${slug}/progress`, { status });

// ---- mistake journal / practice session ---------------------------------
export const updateMistake = (id, payload) => send("PUT", `/mistakes/${id}`, payload);
// Permanently removes exactly one mistake-journal entry (never the
// underlying attempt -- see app.py's delete_mistake docstring).
export const deleteMistake = (id) => send("DELETE", `/mistakes/${id}`);
export const fetchMistakeJournal = () => get("/mistakes/journal");
export const fetchPracticeSession = () => get("/practice-session");

// ---- plain run / trace (scratchpad + trace visualizer) -----------------
export const runCode = (code) => send("POST", "/run", { code });
export const traceCode = (code) => send("POST", "/trace", { code });
