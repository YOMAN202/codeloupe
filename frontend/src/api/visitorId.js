// Anonymous per-visitor identifier for backend data isolation (see
// backend/app.py's get_visitor_id docstring). Generated once per browser
// profile/storage partition and persisted in localStorage -- this is NOT an
// account or login, there's no password and nothing ties it to a real
// identity. It exists purely so that when Codeloupe is reachable by more
// than one visitor (e.g. a public deployment, or just two people on the
// same machine), their attempts/mistakes/revision schedules/progress don't
// collide with each other.
//
// A private/incognito window has its own localStorage, completely separate
// from a normal window's, so it always gets its own freshly-generated id --
// that's what makes two incognito sessions' data provably independent, and
// is exactly what this feature is tested with.
const STORAGE_KEY = "codeloupe_visitor_id";

function generateVisitorId() {
  if (typeof crypto !== "undefined" && typeof crypto.randomUUID === "function") {
    return crypto.randomUUID();
  }
  // Fallback for browsers old enough not to have crypto.randomUUID --
  // still unique-enough-in-practice per browser profile, just not
  // cryptographically random.
  return `visitor-${Date.now()}-${Math.random().toString(16).slice(2)}`;
}

let cachedId = null;

// Returns this browser's visitor id, generating and persisting one on first
// call if none exists yet. Cached in-memory after the first read so a page
// full of near-simultaneous requests doesn't race on localStorage.
export function getVisitorId() {
  if (cachedId) return cachedId;
  try {
    let id = window.localStorage.getItem(STORAGE_KEY);
    if (!id) {
      id = generateVisitorId();
      window.localStorage.setItem(STORAGE_KEY, id);
    }
    cachedId = id;
    return id;
  } catch {
    // localStorage unavailable (disabled storage, some strict private-mode
    // configurations) -- fall back to an id that lives only for this page
    // load rather than breaking the app; progress just won't persist
    // across a reload in that situation.
    cachedId = generateVisitorId();
    return cachedId;
  }
}
