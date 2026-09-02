// Small display helper: stringifies a trace/test value for on-screen
// display, correctly handling non-finite numbers (Infinity, -Infinity,
// NaN) that a real trace can legitimately contain -- e.g. a sentinel like
// `best = float("inf")` in a sliding-window solution. These arrive here as
// real JS numbers (see api/client.js's parseJsonResponse, which revives
// them from the wire), but plain JSON.stringify has no way to represent a
// non-finite number at all and silently turns every one of them into the
// text "null" -- which would show a learner "null" for a value that is
// very much not null. formatValue fixes that at every nesting depth (a
// bare Infinity, or one buried inside an array/object) while leaving
// every other value's formatting byte-for-byte identical to
// JSON.stringify.
//
// A first version of this returned `String(val)` (e.g. "Infinity") straight
// from the replacer -- but a replacer's return value is itself run back
// through JSON.stringify's normal string handling, so that just produced a
// QUOTED `"Infinity"` in the output, indistinguishable from an actual
// string value and not the "displayed clearly" bare number the sentinel is
// supposed to read as. Fixed the same way api/client.js's parser already
// swaps values across the JSON boundary in the other direction: replace
// each non-finite number with a unique quoted marker, then strip the
// quotes back off just those markers in the finished text.
const FMT_MARKER = { NaN: "__codeloupe_fmt_nan__", Infinity: "__codeloupe_fmt_posinf__", "-Infinity": "__codeloupe_fmt_neginf__" };
export function formatValue(v) {
  const json = JSON.stringify(v, (_key, val) => {
    if (typeof val !== "number" || Number.isFinite(val)) return val;
    return FMT_MARKER[Number.isNaN(val) ? "NaN" : val > 0 ? "Infinity" : "-Infinity"];
  });
  if (json === undefined) return json; // e.g. formatValue(undefined) -- preserve JSON.stringify's own behavior
  return json
    .replace(/"__codeloupe_fmt_nan__"/g, "NaN")
    .replace(/"__codeloupe_fmt_posinf__"/g, "Infinity")
    .replace(/"__codeloupe_fmt_neginf__"/g, "-Infinity");
}
