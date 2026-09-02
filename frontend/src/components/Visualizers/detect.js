// Pure (no-JSX) detection helpers shared by the visualizer dispatcher.
// Kept separate from rendering so the "what should we show" decision is
// easy to read and easy to test in isolation.

// Deliberately excludes teal and amber -- those two are reserved
// site-wide for brand/action and current-inspection-focus respectively
// (see App.css's token comment). A pointer variable landing on either by
// hash-chance would wrongly read as "this is the thing to look at" or
// "this is a button". Everything here is a qualitative, non-brand hue.
const PALETTE = ["#5fb0e6", "#d688e8", "#8a7bff", "#4fd8a0", "#ff8a9e", "#e2924a", "#7ee08a", "#7ec8ff"];

export function colorForName(name) {
  let hash = 0;
  for (let i = 0; i < name.length; i++) hash = (hash * 31 + name.charCodeAt(i)) >>> 0;
  return PALETTE[hash % PALETTE.length];
}

export function isPrimitiveList(v) {
  return (
    Array.isArray(v) &&
    v.length > 0 &&
    v.length <= 200 &&
    v.every((x) => typeof x === "number" || typeof x === "string" || typeof x === "boolean")
  );
}

export function isNumericList(v) {
  return Array.isArray(v) && v.length > 0 && v.length <= 200 && v.every((x) => typeof x === "number");
}

export function isBoolOrNumericList(v) {
  return (
    Array.isArray(v) &&
    v.length > 0 &&
    v.length <= 300 &&
    v.every((x) => typeof x === "number" || typeof x === "boolean")
  );
}

// Grid cells in the curated problem bank aren't always numbers -- e.g.
// number-of-islands' test data represents "1"/"0" as strings, and other
// grid problems use short char markers ("W"/"O" for water/ocean). Any row
// of short scalar values (number, boolean, or a string up to 3 chars) is
// treated as a grid row.
export function isGridOfNumbers(v) {
  return (
    Array.isArray(v) &&
    v.length > 0 &&
    v.length <= 60 &&
    v.every(
      (row) =>
        Array.isArray(row) &&
        row.length > 0 &&
        row.length <= 60 &&
        row.every((x) => typeof x === "number" || typeof x === "boolean" || (typeof x === "string" && x.length <= 3))
    )
  );
}

export function hasDPArray(locals) {
  // DP tables specifically are numeric/boolean, never char grids -- keep
  // this narrower than the general grid detector above so a char-grid
  // problem never gets misdetected as a DP table.
  return Object.values(locals).some((v) => isBoolOrNumericList(v) || isNumericOrBoolGrid(v));
}

function isNumericOrBoolGrid(v) {
  return (
    Array.isArray(v) &&
    v.length > 0 &&
    v.length <= 60 &&
    v.every((row) => Array.isArray(row) && row.length > 0 && row.length <= 60 && row.every((x) => typeof x === "number" || typeof x === "boolean"))
  );
}

export function hasNumericOrTupleList(locals) {
  return Object.values(locals).some(
    (v) =>
      isNumericList(v) ||
      (Array.isArray(v) && v.length > 0 && v.length <= 100 && v.every((x) => Array.isArray(x) || typeof x === "number"))
  );
}

export function hasNumericList(locals) {
  return Object.values(locals).some(isNumericList);
}

export function hasGridLocal(locals) {
  return Object.values(locals).some(isGridOfNumbers);
}

export function hasSequenceList(locals) {
  return Object.values(locals).some(isPrimitiveList);
}

// backend/execution/tracer.py falls back to a bare repr() string for
// values it doesn't otherwise know how to serialize -- functions,
// modules, classes ("<function two_sum at 0x7f...>"). Those are real
// strings but not meaningful "sequences" to a learner, so they're
// excluded from sequence detection everywhere below.
export function isDisplayableString(v) {
  return typeof v === "string" && v.length > 0 && v.length <= 200 && !/^<.*>$/.test(v);
}

export function hasStringOrList(locals) {
  return Object.values(locals).some((v) => isPrimitiveList(v) || isDisplayableString(v));
}

// Which integer locals are plausibly array/string INDICES vs ordinary
// numeric values (a target being searched for, a running count/sum,
// a distance, a price...). The tracer only gives us a name and a value
// per step -- no static analysis of how a variable is actually used in
// the source -- so this is unavoidably a name-based heuristic, same as
// the grid view's row/col detection just below in Visualizers.jsx. Kept
// deliberately conservative and allow-list-based (default: NOT a
// pointer) rather than "anything in bounds counts": a false negative
// (a real pointer variable with an unusual name doesn't get a tag) is
// far less misleading than a false positive (an ordinary value like
// `target` or `count` gets drawn as if it were navigating the array).
//
// The base names below were checked against this app's own curated
// reference solutions (backend/db/seed_problems.py) across two-pointer,
// binary-search, sliding-window, and array/sorting problems, rather than
// guessed -- e.g. `k` was deliberately EXCLUDED after checking: every
// `k` in this codebase's reference solutions is a slice boundary or
// problem parameter (e.g. "rotate by k"), never an index a value is
// compared against, so allow-listing it would reintroduce exactly this
// bug for "k-th largest" style problems. Same reasoning excluded `curr`/
// `prev` (used for rolling DP totals, not array positions, in this
// corpus) and generic single letters like `n`, `m`, `x`.
const POINTER_BASE_NAMES = new Set([
  "i", "j", "l", "r",
  "left", "right", "lo", "hi", "low", "high",
  "mid", "middle", "slow", "fast",
  "read", "write", "start", "end",
  "idx", "index", "pos", "ptr", "cursor",
  "front", "back", "top", "bottom",
]);

// Strips a trailing numeric suffix so paired pointers like `left1`/`left2`
// or `l1`/`r2` (seen in this app's own multi-pointer problems) still
// match their base name.
export function isLikelyPointerName(name) {
  if (typeof name !== "string") return false;
  const base = name.toLowerCase().replace(/\d+$/, "");
  return POINTER_BASE_NAMES.has(base);
}

// One primary structural view per step, chosen by (in priority order):
// an actual node-graph shape found in the data itself (tree/linked-list/
// graph -- these are unambiguous regardless of problem metadata), then
// the problem's own topic combined with a matching data shape, then a
// generic array/string/pointer view as the catch-all. Returns null when
// nothing visualizable is present (the plain locals table still covers
// that step either way).
export function detectPrimaryView(problem, locals, graphKind) {
  if (graphKind === "tree") return "tree";
  if (graphKind === "list") return "list";
  if (graphKind === "graph") return "graph";
  const topic = problem?.topic;
  if (topic === "dynamic-programming" && hasDPArray(locals)) return "dp";
  if (topic === "heaps" && hasNumericOrTupleList(locals)) return "heap";
  if (topic === "sorting" && hasNumericList(locals)) return "sorting";
  if (topic === "graphs" && hasGridLocal(locals)) return "grid-graph";
  if ((topic === "stacks" || topic === "queues") && hasSequenceList(locals)) return topic === "stacks" ? "stack" : "queue";
  if (hasStringOrList(locals)) return "array";
  return null;
}
