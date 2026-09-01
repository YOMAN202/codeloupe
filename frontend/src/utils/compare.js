// Small, honest, structural comparison helpers -- used by the failure-
// analysis panel to describe HOW an actual result differs from the
// expected one. Deliberately does not attempt to diagnose WHY (that
// would be an unreliable claim); it only states structural facts the
// learner can verify themselves.

export function describeMismatch(expected, actual) {
  if (actual === undefined) return "Your function didn't return a value here (or an error stopped it first).";
  if (Array.isArray(expected) && Array.isArray(actual)) {
    if (expected.length !== actual.length) {
      return `Expected a list of length ${expected.length}, got length ${actual.length}.`;
    }
    const diffIndices = [];
    for (let i = 0; i < expected.length; i++) {
      if (JSON.stringify(expected[i]) !== JSON.stringify(actual[i])) diffIndices.push(i);
    }
    if (diffIndices.length === 0) return "Same length and same values -- likely an element ordering difference or a type mismatch (e.g. string vs number).";
    if (diffIndices.length <= 3) {
      return `Values differ at index ${diffIndices.join(", ")}: expected ${diffIndices
        .map((i) => JSON.stringify(expected[i]))
        .join(", ")}, got ${diffIndices.map((i) => JSON.stringify(actual[i])).join(", ")}.`;
    }
    return `Values differ at ${diffIndices.length} of ${expected.length} positions.`;
  }
  if (typeof expected === "number" && typeof actual === "number") {
    return `Expected ${expected}, got ${actual} (off by ${Math.abs(expected - actual)}).`;
  }
  if (typeof expected !== typeof actual) {
    return `Expected a ${typeof expected} (${JSON.stringify(expected)}), got a ${typeof actual} (${JSON.stringify(actual)}) -- a type mismatch is often the actual bug.`;
  }
  return `Expected ${JSON.stringify(expected)}, got ${JSON.stringify(actual)}.`;
}

// Diffs two "locals" snapshots (plain objects from a trace step) for the
// Predict -> Compare panel. Structural only -- no interpretation.
export function diffLocals(before, after) {
  const changes = [];
  const keys = new Set([...Object.keys(before || {}), ...Object.keys(after || {})]);
  for (const k of keys) {
    const a = JSON.stringify(before ? before[k] : undefined);
    const b = JSON.stringify(after ? after[k] : undefined);
    if (a !== b) {
      changes.push({
        name: k,
        before: before ? before[k] : undefined,
        after: after ? after[k] : undefined,
        isNew: !(before && k in before),
      });
    }
  }
  return changes;
}
