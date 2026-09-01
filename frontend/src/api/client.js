// Thin fetch wrappers around the Flask API. One function per endpoint,
// all sharing the same error-handling shape (throw with the server's own
// error message when available).

const API_BASE = "http://127.0.0.1:5001/api";

async function get(path) {
  const res = await fetch(`${API_BASE}${path}`);
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.error || `${path} failed: ${res.status}`);
  }
  return res.json();
}

async function send(method, path, body) {
  const res = await fetch(`${API_BASE}${path}`, {
    method,
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body ?? {}),
  });
  if (!res.ok) {
    const errBody = await res.json().catch(() => ({}));
    throw new Error(errBody.error || `${path} failed: ${res.status}`);
  }
  return res.json();
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

// ---- attempts / progress ------------------------------------------------
export const logAttempt = (attempt) => send("POST", "/attempts", attempt);
export const fetchProgress = () => get("/progress");

// ---- plain run / trace (scratchpad + trace visualizer) -----------------
export const runCode = (code) => send("POST", "/run", { code });
export const traceCode = (code) => send("POST", "/trace", { code });
