// Milestone 1: thin fetch wrappers around the Flask API. No trace/hint/test
// endpoints yet -- see docs/development-roadmap.md for what's next.

const API_BASE = "http://127.0.0.1:5001/api";

export async function fetchLesson(day) {
  const res = await fetch(`${API_BASE}/lessons/${day}`);
  if (!res.ok) {
    throw new Error(`Failed to load lesson ${day}: ${res.status}`);
  }
  return res.json();
}

export async function runCode(code) {
  const res = await fetch(`${API_BASE}/run`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ code }),
  });
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.error || `Run failed: ${res.status}`);
  }
  return res.json();
}
