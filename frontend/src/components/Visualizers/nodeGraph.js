// Shared helper for the linked-list / tree / graph visualizers.
//
// backend/execution/tracer.py serializes any custom Python object (Node,
// TreeNode, GNode, ...) as a plain JSON dict: {"__type__": "Node",
// "__id__": <python id()>, ...its own fields...}. Two different local
// variables that point at the SAME underlying object (e.g. "prev" and
// "curr" both referencing the same node) get serialized independently --
// they are two separate JSON trees -- but they share the same "__id__".
//
// This module walks every top-level local, follows the object fields
// recursively, and de-duplicates by "__id__" into one shared node/edge
// graph. That's what turns "5 separate, partially-overlapping tree
// diagrams" into "one diagram with 5 labeled arrows pointing into it" --
// which is what actually helps a learner see what their pointers are
// doing.

export function isNodeShape(v) {
  return (
    v !== null &&
    typeof v === "object" &&
    !Array.isArray(v) &&
    typeof v.__type__ === "string" &&
    typeof v.__id__ !== "undefined"
  );
}

function nodeKind(v) {
  if ("left" in v || "right" in v) return "tree";
  if (Array.isArray(v.neighbors)) return "graph";
  if ("next" in v) return "list";
  return "generic";
}

// Walks every (name, value) local pair; returns:
//   { nodes: Map(id -> {id, type, kind, fields, fieldRefs}),
//     roots: [{name, id}],   -- top-level local variable -> node id
//     kind: "tree" | "list" | "graph" | null }
// `fields` holds primitive (displayable) fields only (val, value, key, ...).
// `fieldRefs` maps a pointer-field name (next/left/right) -> child node id
// (or null). For graph nodes, `neighborIds` holds the list of neighbor ids.
export function collectNodeGraph(locals) {
  const nodes = new Map();
  const roots = [];
  let dominantKind = null;

  function visit(v, depth) {
    if (!isNodeShape(v) || depth > 500) return v.__id__ ?? null;
    const id = v.__id__;
    if (nodes.has(id)) return id;
    const kind = nodeKind(v);
    if (!dominantKind || kind !== "generic") dominantKind = dominantKind || kind;
    const fields = {};
    const fieldRefs = {};
    let neighborIds = null;
    for (const [k, val] of Object.entries(v)) {
      if (k === "__type__" || k === "__id__" || k === "__circular__" || k === "__truncated__") continue;
      if (k === "neighbors" && Array.isArray(val)) {
        neighborIds = val.map((n) => visit(n, depth + 1)).filter((x) => x !== null);
        continue;
      }
      if (isNodeShape(val)) {
        fieldRefs[k] = visit(val, depth + 1);
      } else if (val === null && (k === "next" || k === "left" || k === "right")) {
        fieldRefs[k] = null;
      } else if (Array.isArray(val)) {
        // e.g. a node whose field is a plain list of primitives -- show it
        // as a field value, not a pointer.
        fields[k] = val;
      } else {
        fields[k] = val;
      }
    }
    nodes.set(id, { id, type: v.__type__, kind, fields, fieldRefs, neighborIds });
    return id;
  }

  for (const [name, value] of Object.entries(locals || {})) {
    if (isNodeShape(value)) {
      const id = visit(value, 0);
      roots.push({ name, id });
    } else if (Array.isArray(value) && value.length > 0 && value.length <= 40 && value.every(isNodeShape)) {
      // e.g. a list of tree/graph nodes (BFS queue of nodes, adjacency list root list)
      value.forEach((v, i) => {
        const id = visit(v, 0);
        roots.push({ name: `${name}[${i}]`, id });
      });
    } else if (value === null) {
      // A local that's currently None but named like a pointer (e.g. `prev
      // = None` before the loop starts) -- still worth surfacing as a root
      // pointing at nothing, so the learner sees the pointer exists.
      roots.push({ name, id: null });
    }
  }

  return { nodes, roots, kind: dominantKind };
}
