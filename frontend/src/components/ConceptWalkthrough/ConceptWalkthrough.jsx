import { useState } from "react";
import { ArrayPointerView, LinkedListView, TreeView } from "../Visualizers/Visualizers";

// A teaching walkthrough steps through a hand-authored, VERIFIED-BY-HAND
// sequence of {caption, locals} frames (see backend/db/seed_concepts.py) --
// a controlled example chosen to demonstrate a concept clearly. It reuses
// the same presentation components the real trace-your-own-code system
// (TraceViewer.jsx) uses -- ArrayPointerView for array/string/pointer
// state, LinkedListView for node chains -- so a learner sees one
// consistent visual language everywhere in the app. That is where the
// reuse stops on purpose: this component never touches /api/.../trace or
// sys.settrace. Codeloupe's actual differentiator -- write your own code,
// run it, trace what IT actually did -- lives only in TraceViewer.jsx.
// This is clearly a separate, simpler stepper (no play/predict-mode, no
// event/line/depth -- there's no real execution here to report on) so the
// two are never visually confusable.

// LinkedListView expects a real trace's { nodes: Map(id -> {fields,
// fieldRefs}), roots: [{name, id}] } shape (built by nodeGraph.js from
// live sys.settrace output). Hand-authoring a Map is inconvenient, so
// linked-list lessons author frames.locals as the much simpler
// { nodes: [{id, val, next}], pointers: [[name, id], ...] } and this
// adapter builds the shape LinkedListView actually needs -- the same
// node-chain rendering (including its cycle/orphan handling) with no
// changes to the visualizer itself.
//
// pointers is a list of [name, id] PAIRS, not a plain {name: id} object --
// deliberately, since which pointer LinkedListView picks as the chain's
// starting point depends on root order (the first root with a non-null id,
// absent a "head"-named one -- see its own namedRoot logic), and Flask's
// JSON serializer sorts object keys alphabetically before this ever
// reaches the browser, silently discarding whatever order seed_concepts.py
// authored. Array element order survives that round-trip; object key
// order does not.
function buildLinkedListGraph(locals) {
  const nodes = new Map();
  (locals.nodes || []).forEach((n) => {
    nodes.set(n.id, { id: n.id, fields: { val: n.val }, fieldRefs: { next: n.next ?? null } });
  });
  const roots = (locals.pointers || []).map(([name, id]) => ({ name, id: id ?? null }));
  return { nodes, roots };
}

// TreeView expects the same { nodes: Map(id -> {fields, fieldRefs}), roots:
// [{name, id}] } shape as LinkedListView, just with fieldRefs.left/.right
// instead of .next -- so tree lessons author frames.locals in the parallel
// { nodes: [{id, val, left, right}], pointers: [[name, id], ...] } shape,
// and this adapter converts it the same way buildLinkedListGraph does.
//
// The SAME ordered-list-of-pairs reasoning applies here (see that
// function's comment): TreeView's assign() walk starts from
// `roots.find(r => r.id != null)`, i.e. the FIRST pointer in the list with
// a non-null id, and recursively lays out the WHOLE tree from there via
// left/right. So the tree's actual root must always be authored first in
// `pointers` -- any other pointer (e.g. a "node" chip tracking the current
// position during a traversal) is purely additive after that: TreeView
// renders it as a colored tag whenever its id lands on an already-placed
// node, without affecting which node anchors the layout.
function buildTreeGraph(locals) {
  const nodes = new Map();
  (locals.nodes || []).forEach((n) => {
    nodes.set(n.id, {
      id: n.id,
      fields: { val: n.val },
      fieldRefs: { left: n.left ?? null, right: n.right ?? null },
    });
  });
  const roots = (locals.pointers || []).map(([name, id]) => ({ name, id: id ?? null }));
  return { nodes, roots };
}

export default function ConceptWalkthrough({ frames, topic, pattern }) {
  const [index, setIndex] = useState(0);
  if (!frames || frames.length === 0) return null;
  const frame = frames[index];
  const isLinkedList = topic === "linked-lists" && frame.locals && Array.isArray(frame.locals.nodes);
  const isTree = topic === "trees" && frame.locals && Array.isArray(frame.locals.nodes);

  return (
    <div className="concept-walkthrough">
      <div className="trace-controls">
        <button className="chip" onClick={() => setIndex((i) => Math.max(0, i - 1))} disabled={index === 0}>
          &larr; Back
        </button>
        <button
          className="chip"
          onClick={() => setIndex((i) => Math.min(frames.length - 1, i + 1))}
          disabled={index >= frames.length - 1}
        >
          Next &rarr;
        </button>
        <span className="muted">
          step {index + 1} / {frames.length}
        </span>
      </div>

      <input
        type="range"
        min={0}
        max={frames.length - 1}
        value={index}
        onChange={(e) => setIndex(Number(e.target.value))}
        className="trace-scrubber"
        style={{ "--scrub-pct": `${frames.length > 1 ? (index / (frames.length - 1)) * 100 : 100}%` }}
        aria-label={`Walkthrough step ${index + 1} of ${frames.length}`}
      />

      <p className="concept-walkthrough-caption">{frame.caption}</p>
      {isLinkedList ? (
        <LinkedListView graph={buildLinkedListGraph(frame.locals)} />
      ) : isTree ? (
        <TreeView graph={buildTreeGraph(frame.locals)} />
      ) : (
        <ArrayPointerView locals={frame.locals} topic={topic} pattern={pattern} />
      )}
    </div>
  );
}
