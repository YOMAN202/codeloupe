import "./visualizers.css";
import { collectNodeGraph } from "./nodeGraph";
import { colorForName, detectPrimaryView, isPrimitiveList, isNumericList, isBoolOrNumericList, isGridOfNumbers, isDisplayableString, isLikelyPointerName } from "./detect";
import { formatValue } from "../../utils/format";

// Codeloupe's core promise, restated for every view in this file: render
// what the learner's OWN code actually did at this exact step -- correct
// or not -- never a canned animation of the "right" algorithm. Every
// component here reads straight from the captured trace snapshot; none
// of them know what the "correct" answer looks like.
//
// Visual-clarity conventions (see visualizers.css's own top-of-file
// comment for the full color rule): amber stays reserved for "the direct
// result of / focus of the CURRENT step" everywhere below -- a written
// array cell, a node whose fields just changed, the node a plain pointer
// currently references, a just-pushed stack cell. Anything "worth noting
// but not the current step's focus" (a BFS/DFS node in the frontier, a
// node your code pointed at a few steps ago, a grid cell visited earlier)
// gets a quieter tint built from an existing secondary token instead, so
// it never competes with amber for attention. Pointer "movement" is shown
// for free by giving `.pointer-chip` a brief mount animation (see the
// CSS) -- since every chip is keyed by variable name inside whichever
// node/box it currently occupies, React itself unmounts+remounts it
// whenever a pointer moves, so the animation plays exactly when and only
// when a pointer's position actually changed, with no extra diffing.

function Caption({ children }) {
  return <p className="viz-caption">{children}</p>;
}

// ---- shared: search backward through the trace for the previous value
// of a named local, so views can highlight "what just changed" (a swap
// during sorting, a newly-written DP cell, ...). Best-effort heuristic,
// not a formal data-flow analysis -- good enough for a learning aid.
function findPreviousValue(steps, index, name) {
  const start = Math.max(0, index - 300);
  for (let i = index - 1; i >= start; i--) {
    const locals = steps[i].locals;
    if (locals && Object.prototype.hasOwnProperty.call(locals, name)) return locals[name];
  }
  return undefined;
}

// Array/object element equality, not just `===`. Every trace step is its
// own fresh JSON.parse, so two structurally-identical values (a heap's
// (distance, node) tuple, a locals entry that's itself a small list) are
// never the same object reference even when nothing actually changed --
// `===` alone would flag them as "changed" on literally every step.
// Primitives short-circuit on the `===` check first, so this stays just
// as cheap as a plain `!==` for the number/string/boolean case every
// caller other than HeapView actually uses.
function valuesEqual(a, b) {
  if (a === b) return true;
  if (Array.isArray(a) && Array.isArray(b)) return formatValue(a) === formatValue(b);
  return false;
}

function diffIndices(prevArr, currArr) {
  if (!Array.isArray(prevArr) || !Array.isArray(currArr)) return new Set();
  const changed = new Set();
  const len = Math.max(prevArr.length, currArr.length);
  for (let i = 0; i < len; i++) {
    if (!valuesEqual(prevArr[i], currArr[i])) changed.add(i);
  }
  return changed;
}

// ---- shared: node-graph diffing (linked lists / trees / graphs) --------
// Mirrors findPreviousValue's heuristic above, but for the id-keyed
// node/edge graph collectNodeGraph builds from locals, so these views can
// highlight "which node did my code just touch" the same way array/DP/
// sorting views highlight "which index changed" -- reusing real object
// identity (__id__ from tracer.py) rather than guessing from position.

// The most recent step with real per-line locals before `index` -- "call"
// steps always carry empty locals and "return" steps carry none at all
// (see tracer.py), so this has to skip past those, the same way
// findPreviousValue skips past steps that don't mention a given name.
function mostRecentLineIndex(steps, index, maxBack = 300) {
  const start = Math.max(0, index - maxBack);
  for (let i = index - 1; i >= start; i--) {
    if (steps[i].event === "line") return i;
  }
  return -1;
}

function previousGraph(steps, index) {
  const i = mostRecentLineIndex(steps, index);
  return i >= 0 ? collectNodeGraph(steps[i].locals) : null;
}

// Node ids whose fields/refs differ from the same id's fields one step
// ago ("changed"), plus ids that didn't exist a step ago at all ("new").
// Comparing by id -- real object identity -- is what makes this reliable
// even when a node gets reached via a different variable name than
// before (e.g. "prev" now points at what "curr" pointed at last step).
function graphDiff(prevGraph, currGraph) {
  const changed = new Set();
  const isNew = new Set();
  if (!prevGraph) return { changed, isNew };
  for (const [id, node] of currGraph.nodes) {
    const prevNode = prevGraph.nodes.get(id);
    if (!prevNode) {
      isNew.add(id);
      continue;
    }
    const refKeys = new Set([...Object.keys(node.fieldRefs), ...Object.keys(prevNode.fieldRefs)]);
    const refsDiffer = [...refKeys].some((k) => (node.fieldRefs[k] ?? null) !== (prevNode.fieldRefs[k] ?? null));
    const fieldKeys = new Set([...Object.keys(node.fields), ...Object.keys(prevNode.fields)]);
    const fieldsDiffer = [...fieldKeys].some((k) => formatValue(node.fields[k]) !== formatValue(prevNode.fields[k]));
    const neighborsDiffer = formatValue(node.neighborIds) !== formatValue(prevNode.neighborIds);
    if (refsDiffer || fieldsDiffer || neighborsDiffer) changed.add(id);
  }
  return { changed, isNew };
}

// Best-effort "recently referenced" trail: walks backward from `index`
// (bounded, same spirit as findPreviousValue) recording how many steps
// ago each node id was pointed at by a plain, single-variable root --
// i.e. actually dereferenced by name, not just sitting in an unexamined
// queue/list. This is NOT a claim about true traversal order -- just
// "your code looked at this recently" -- so older hits fade rather than
// staying permanently marked, and it never overrides the current step's
// amber focus.
function recencyMap(steps, index, window = 30) {
  const map = new Map();
  const start = Math.max(0, index - window);
  for (let i = index - 1; i >= start; i--) {
    const s = steps[i];
    if (s.event !== "line") continue;
    const g = collectNodeGraph(s.locals);
    for (const r of g.roots) {
      if (r.id != null && !r.name.includes("[") && !map.has(r.id)) map.set(r.id, index - i);
    }
  }
  return map;
}

// Classifies one node id into a quiet-highlight tier once it's already
// been excluded from the amber "current/changed" treatment -- "strong"
// covers both "in the frontier right now" (a BFS/DFS queue local,
// expanded into indexed roots by collectNodeGraph itself -- see its own
// comment) and "referenced within the last ~8 steps"; "faint" covers the
// rest of the recency window. Kept to two tiers deliberately -- enough to
// read as "fading", not enough to turn into a confusing gradient.
function quietTier(id, frontierIds, recency) {
  if (frontierIds.has(id)) return "strong";
  if (recency.has(id)) return recency.get(id) <= 8 ? "strong" : "faint";
  return null;
}

/* ============================== 1. ARRAYS / STRINGS / POINTERS / SLIDING WINDOW ============================== */

export function ArrayPointerView({ locals, topic, pattern, steps, index }) {
  const sequences = Object.entries(locals).filter(([, v]) => isPrimitiveList(v) || isDisplayableString(v));
  if (sequences.length === 0) return null;

  // Only integer locals whose NAME looks like an index/pointer (left,
  // right, mid, i, j, ...) are ever drawn as pointers -- see
  // isLikelyPointerName in detect.js for exactly which names qualify and
  // why. Being in-bounds is necessary but not sufficient: an ordinary
  // value like `target` or `count` can easily fall inside [0, len) by
  // coincidence (e.g. searching for 0 in a 7-element array) without
  // being a position the code is tracking at all.
  const intVars = Object.entries(locals).filter(([name, v]) => Number.isInteger(v) && isLikelyPointerName(name));
  const windowEligible = topic === "sliding-window" || topic === "two-pointer" || /window|two.pointer/.test(pattern || "");

  return (
    <div className="viz-block">
      <Caption>
        Your array/string state right now, with index-like variables (left/right, lo/hi, mid, i/j,
        slow/fast, and similar) shown as a labeled pointer underneath the position they currently
        point to{windowEligible ? " — the shaded band shows the span between your outermost pointers, i.e. the current window." : "."}{" "}
        Amber marks a value your code just wrote at this exact step.
      </Caption>
      {sequences.map(([name, raw]) => {
        const isStr = typeof raw === "string";
        const arr = isStr ? raw.split("") : raw;
        const prevRaw = findPreviousValue(steps, index, name);
        const prevArr = prevRaw == null ? undefined : typeof prevRaw === "string" ? prevRaw.split("") : prevRaw;
        const changed = diffIndices(prevArr, arr);
        const pointers = intVars.filter(([, v]) => v >= 0 && v < arr.length);
        const windowRange =
          windowEligible && pointers.length >= 2
            ? [Math.min(...pointers.map(([, v]) => v)), Math.max(...pointers.map(([, v]) => v))]
            : null;
        return (
          <div key={name} className="seq-row">
            <div className="seq-label">
              {name} {isStr && <span className="viz-type-tag">str</span>}
            </div>
            <div className="seq-boxes">
              {arr.map((val, i) => {
                const inWindow = windowRange && i >= windowRange[0] && i <= windowRange[1];
                const here = pointers.filter(([, v]) => v === i);
                return (
                  <div
                    key={i}
                    className={`seq-box ${inWindow ? "seq-box-in-window" : ""} ${changed.has(i) ? "seq-box-changed" : ""}`}
                  >
                    {here.length > 0 && (
                      <div className="seq-box-pointer-tags">
                        {here.map(([pname]) => (
                          <span key={pname} className="pointer-chip" style={{ background: colorForName(pname) }}>
                            {pname}
                          </span>
                        ))}
                      </div>
                    )}
                    <div className="seq-box-value">{isStr ? val : String(val)}</div>
                    <div className="seq-box-index">{i}</div>
                  </div>
                );
              })}
            </div>
          </div>
        );
      })}
    </div>
  );
}

/* ============================== 2. LINKED LISTS ============================== */

export function LinkedListView({ graph, steps, index }) {
  const { nodes, roots } = graph;
  if (nodes.size === 0) return null;

  const { changed, isNew } = graphDiff(previousGraph(steps, index), graph);

  // Build a display chain by following .next from whichever root looks
  // most like a starting point ("head" if present, else the first root
  // with a non-null id), then append any nodes never reached that way
  // (e.g. a node a buggy submission detached from the chain entirely --
  // exactly the kind of bug this view exists to surface).
  const namedRoot = roots.find((r) => /head/i.test(r.name) && r.id != null) || roots.find((r) => r.id != null);
  const chain = [];
  const visited = new Set();
  let cursor = namedRoot ? namedRoot.id : null;
  let cycleAt = null;
  while (cursor != null && chain.length < 60) {
    if (visited.has(cursor)) {
      cycleAt = cursor;
      break;
    }
    visited.add(cursor);
    chain.push(cursor);
    const node = nodes.get(cursor);
    cursor = node ? node.fieldRefs.next ?? null : null;
  }
  const orphans = [...nodes.keys()].filter((id) => !visited.has(id));

  function pointersAt(id) {
    return roots.filter((r) => r.id === id);
  }
  function primaryField(node) {
    const keys = Object.keys(node.fields);
    const key = keys.find((k) => k === "val" || k === "value") || keys[0];
    return key ? node.fields[key] : "";
  }

  return (
    <div className="viz-block">
      <Caption>
        Each box is one node your code is actually pointing at right now (matched by real object
        identity, not just value) — labeled tags show which of your variables point where. Arrows
        follow each node's real <code>.next</code>. Amber marks a node whose fields or{" "}
        <code>.next</code> your code just changed.
      </Caption>
      <div className="ll-chain">
        {chain.map((id, i) => {
          const node = nodes.get(id);
          const pointers = pointersAt(id);
          const isChanged = changed.has(id) || isNew.has(id);
          return (
            <div className="ll-node-wrap" key={id}>
              {pointers.length > 0 && (
                <div className="ll-pointer-tags">
                  {pointers.map((p) => (
                    <span key={p.name} className="pointer-chip" style={{ background: colorForName(p.name) }}>
                      {p.name}
                    </span>
                  ))}
                </div>
              )}
              <div className={`ll-node ${isChanged ? "ll-node-changed" : ""}`}>{String(primaryField(node))}</div>
              {i < chain.length - 1 ? (
                <span className="ll-arrow">&rarr;</span>
              ) : cycleAt != null ? (
                <span className="ll-arrow ll-cycle">&#8635; back to an earlier node (cycle!)</span>
              ) : (
                <span className="ll-arrow ll-null">&rarr; None</span>
              )}
            </div>
          );
        })}
        {roots.filter((r) => r.id === null).map((r) => (
          <div className="ll-node-wrap" key={r.name}>
            <div className="ll-pointer-tags">
              <span className="pointer-chip" style={{ background: colorForName(r.name) }}>
                {r.name}
              </span>
            </div>
            <div className="ll-node ll-node-none">None</div>
          </div>
        ))}
      </div>
      {cycleAt != null && (
        <p className="viz-warning">
          A node's <code>.next</code> points back into a node already visited — your list has become
          a cycle. That's very often the bug itself (e.g. forgetting to set a node's <code>.next</code>{" "}
          to <code>None</code>), not a rendering issue.
        </p>
      )}
      {orphans.length > 0 && (
        <>
          <p className="viz-caption">
            Also currently referenced, but not reachable by following <code>.next</code> from{" "}
            {namedRoot ? <code>{namedRoot.name}</code> : "your chain"} — worth checking whether that's
            expected:
          </p>
          <div className="ll-chain">
            {orphans.map((id) => {
              const node = nodes.get(id);
              const pointers = pointersAt(id);
              const isChanged = changed.has(id) || isNew.has(id);
              return (
                <div className="ll-node-wrap" key={id}>
                  {pointers.length > 0 && (
                    <div className="ll-pointer-tags">
                      {pointers.map((p) => (
                        <span key={p.name} className="pointer-chip" style={{ background: colorForName(p.name) }}>
                          {p.name}
                        </span>
                      ))}
                    </div>
                  )}
                  <div className={`ll-node ll-node-orphan ${isChanged ? "ll-node-changed" : ""}`}>
                    {String(primaryField(node))}
                  </div>
                </div>
              );
            })}
          </div>
        </>
      )}
    </div>
  );
}

/* ============================== 3. RECURSION / CALL STACK ============================== */

function buildCallStack(steps, index) {
  const stack = [];
  for (let i = 0; i <= index; i++) {
    const s = steps[i];
    if (s.event === "call") {
      stack.push({ function: s.function, callDepth: s.call_depth, locals: {}, line: s.line, justReturned: undefined, key: `${i}` });
    } else if (s.event === "line") {
      const frame = stack[stack.length - 1];
      if (frame) {
        frame.locals = s.locals;
        frame.line = s.line;
      }
    } else if (s.event === "return") {
      const frame = stack.pop();
      if (i === index && frame) {
        frame.justReturned = s.return_value;
        stack.push(frame);
      }
    }
  }
  return stack;
}

export function CallStackView({ steps, index }) {
  const stack = buildCallStack(steps, index);
  if (stack.length === 0) return null;
  const visual = [...stack].reverse(); // deepest/most-recent call on top, like a real stack
  return (
    <div className="viz-block">
      <Caption>
        Your actual recursive call stack at this exact step — one card per still-active call, deepest
        call on top. This is real, not simulated: it's built from the call/return events your code
        actually produced.
      </Caption>
      <div className="call-stack">
        {visual.map((frame, i) => (
          <div key={frame.key} className={`call-frame ${i === 0 ? "call-frame-top" : ""}`}>
            <div className="call-frame-header">
              <span className="call-frame-fn">{frame.function}()</span>
              <span className="muted small">depth {frame.callDepth} &middot; line {frame.line}</span>
            </div>
            {Object.keys(frame.locals || {}).length > 0 && (
              <div className="call-frame-locals">
                {Object.entries(frame.locals).map(([k, v]) => (
                  <span key={k} className="call-frame-local">
                    {k}=<code>{formatValue(v)}</code>
                  </span>
                ))}
              </div>
            )}
            {frame.justReturned !== undefined && (
              <div className="call-frame-return">returning &rarr; <code>{formatValue(frame.justReturned)}</code></div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}

/* ============================== 4. TREES ============================== */

export function TreeView({ graph, steps, index }) {
  const { nodes, roots } = graph;
  if (nodes.size === 0) return null;
  const rootEntry = roots.find((r) => r.id != null);
  if (!rootEntry) return null;

  const { changed, isNew } = graphDiff(previousGraph(steps, index), graph);
  const recency = recencyMap(steps, index);
  const currentIds = new Set(roots.filter((r) => r.id != null && !r.name.includes("[")).map((r) => r.id));
  const frontierIds = new Set(roots.filter((r) => r.id != null && r.name.includes("[")).map((r) => r.id));

  const positions = new Map();
  const edges = [];
  let counter = 0;
  let maxDepth = 0;
  const visiting = new Set();
  let cycleDetected = false;

  function assign(id, depth) {
    if (id == null || positions.has(id) || depth > 30) return;
    if (visiting.has(id)) {
      cycleDetected = true;
      return;
    }
    visiting.add(id);
    const node = nodes.get(id);
    if (!node) {
      visiting.delete(id);
      return;
    }
    if (node.fieldRefs.left != null) {
      edges.push([id, node.fieldRefs.left]);
      assign(node.fieldRefs.left, depth + 1);
    }
    positions.set(id, { x: counter++, y: depth });
    maxDepth = Math.max(maxDepth, depth);
    if (node.fieldRefs.right != null) {
      edges.push([id, node.fieldRefs.right]);
      assign(node.fieldRefs.right, depth + 1);
    }
    visiting.delete(id);
  }
  assign(rootEntry.id, 0);

  const CELL_W = 56;
  const CELL_H = 68;
  const width = Math.max(1, counter) * CELL_W;
  const height = (maxDepth + 1) * CELL_H;

  function pointersAt(id) {
    return roots.filter((r) => r.id === id);
  }
  function primaryField(node) {
    const keys = Object.keys(node.fields);
    const key = keys.find((k) => k === "val" || k === "value") || keys[0];
    return key ? node.fields[key] : "";
  }

  return (
    <div className="viz-block">
      <Caption>
        Your tree's real shape and values right now, laid out left-to-right in-order. Colored tags
        show which variable is currently pointing at which node — amber is the node your code just
        changed or is directly pointing at this step; a fainter ring means your code referenced that
        node recently or it's sitting in a traversal queue right now.
      </Caption>
      <div className="tree-scroll">
        <div className="tree-canvas" style={{ width, height: height + 40 }}>
          <svg className="tree-edges" width={width} height={height + 40}>
            {edges.map(([from, to], i) => {
              const a = positions.get(from);
              const b = positions.get(to);
              if (!a || !b) return null;
              return (
                <line
                  key={i}
                  x1={a.x * CELL_W + CELL_W / 2}
                  y1={a.y * CELL_H + 34}
                  x2={b.x * CELL_W + CELL_W / 2}
                  y2={b.y * CELL_H + 34}
                  stroke="#7a8492"
                  strokeWidth="2"
                />
              );
            })}
          </svg>
          {[...positions.entries()].map(([id, pos]) => {
            const node = nodes.get(id);
            const pointers = pointersAt(id);
            const isFocus = changed.has(id) || isNew.has(id) || currentIds.has(id);
            const tier = isFocus ? null : quietTier(id, frontierIds, recency);
            const nodeClass = isFocus
              ? "tree-node-changed"
              : tier === "strong"
              ? "tree-node-quiet-strong"
              : tier === "faint"
              ? "tree-node-quiet-faint"
              : "";
            return (
              <div
                key={id}
                className="tree-node-wrap"
                style={{ left: pos.x * CELL_W, top: pos.y * CELL_H }}
              >
                {pointers.length > 0 && (
                  <div className="tree-pointer-tags">
                    {pointers.map((p) => (
                      <span key={p.name} className="pointer-chip" style={{ background: colorForName(p.name) }}>
                        {p.name}
                      </span>
                    ))}
                  </div>
                )}
                <div className={`tree-node ${nodeClass}`}>{String(primaryField(node))}</div>
              </div>
            );
          })}
        </div>
      </div>
      {cycleDetected && (
        <p className="viz-warning">
          Following left/right pointers looped back on itself — this tree currently has a cycle,
          which is essentially always a bug rather than a valid tree shape.
        </p>
      )}
    </div>
  );
}

/* ============================== 5. STACKS / QUEUES ============================== */

export function StackQueueView({ locals, mode, steps, index }) {
  const entries = Object.entries(locals).filter(([, v]) => isPrimitiveList(v));
  if (entries.length === 0) return null;
  return (
    <div className="viz-block">
      <Caption>
        {mode === "stack"
          ? "Rendered as a stack — the last element is the top, exactly what .pop() would remove next."
          : "Rendered as a queue — the first element is the front, exactly what would be dequeued next."}{" "}
        Amber marks whatever changed here since this collection last appeared in the trace — your
        most recent push/enqueue.
      </Caption>
      {entries.map(([name, arr]) => {
        const prev = findPreviousValue(steps, index, name);
        const changed = diffIndices(prev, arr);
        const display = mode === "stack" ? [...arr].reverse() : arr;
        return (
          <div key={name} className={`sq-view sq-${mode}`}>
            <div className="seq-label">{name}</div>
            <div className={mode === "stack" ? "sq-stack" : "sq-queue"}>
              {display.map((val, i) => {
                const originalIndex = mode === "stack" ? arr.length - 1 - i : i;
                const isEdge = mode === "stack" ? i === 0 : i === 0 || i === arr.length - 1;
                const edgeLabel =
                  mode === "stack" && i === 0 ? "top" : mode === "queue" && i === 0 ? "front" : mode === "queue" && i === arr.length - 1 ? "back" : null;
                return (
                  <div
                    key={originalIndex}
                    className={`sq-cell ${isEdge ? "sq-cell-edge" : ""} ${changed.has(originalIndex) ? "sq-cell-changed" : ""}`}
                  >
                    {edgeLabel && <div className="sq-cell-label">{edgeLabel}</div>}
                    <div className="sq-cell-value">{String(val)}</div>
                  </div>
                );
              })}
              {arr.length === 0 && <span className="muted small">(empty)</span>}
            </div>
          </div>
        );
      })}
    </div>
  );
}

/* ============================== 6. SORTING ============================== */

export function SortingView({ locals, steps, index }) {
  const entries = Object.entries(locals).filter(([, v]) => isNumericList(v));
  if (entries.length === 0) return null;
  return (
    <div className="viz-block">
      <Caption>
        Bar height is each element's value. Highlighted bars changed value since the last time this
        array appeared in the trace — i.e. a swap or write your code just made.
      </Caption>
      {entries.map(([name, arr]) => {
        const prev = findPreviousValue(steps, index, name);
        const changed = diffIndices(prev, arr);
        const max = Math.max(...arr.map((v) => Math.abs(v)), 1);
        return (
          <div key={name} className="sort-row">
            <div className="seq-label">{name}</div>
            <div className="sort-bars">
              {arr.map((v, i) => (
                <div key={i} className={`sort-bar-wrap ${changed.has(i) ? "sort-bar-changed" : ""}`}>
                  <div
                    className="sort-bar"
                    style={{ height: `${Math.max(6, (Math.abs(v) / max) * 90)}px` }}
                    title={String(v)}
                  />
                  <div className="sort-bar-value">{v}</div>
                </div>
              ))}
            </div>
          </div>
        );
      })}
    </div>
  );
}

/* ============================== 7. GRAPHS (grid + node) ============================== */

// Real trace data, preferred over any heuristic when it's present: a
// local literally named visited/seen/explored, shaped either like this
// grid (a same-size boolean/number grid) or like a list of [row, col]
// pairs.
function explicitVisitedCells(locals, grid) {
  const rows = grid.length;
  const cols = grid[0]?.length ?? 0;
  for (const [name, v] of Object.entries(locals)) {
    if (!/^(visited|seen|explored)$/i.test(name)) continue;
    if (Array.isArray(v) && v.length === rows && v.every((row) => Array.isArray(row) && row.length === cols)) {
      const set = new Set();
      v.forEach((row, r) => row.forEach((cell, c) => {
        if (cell === true || cell === 1) set.add(`${r},${c}`);
      }));
      return set;
    }
    if (Array.isArray(v) && v.length > 0 && v.every((p) => Array.isArray(p) && p.length === 2 && p.every(Number.isInteger))) {
      return new Set(v.map(([r, c]) => `${r},${c}`));
    }
  }
  return null;
}

// Fallback when there's no explicit visited/seen local: cells that have
// ever differed from this grid's very first captured value, up through
// the current step. Covers the common "mark visited by mutating the grid
// in place" pattern (flood fill, number of islands, rotting oranges)
// without needing a dedicated visited structure. Best-effort, same spirit
// as findPreviousValue -- not a claim about exactly when each cell changed.
function everChangedCells(steps, index, name) {
  const set = new Set();
  let initial;
  for (let i = 0; i <= index; i++) {
    const locals = steps[i].locals;
    if (locals && Object.prototype.hasOwnProperty.call(locals, name)) {
      initial = locals[name];
      break;
    }
  }
  const current = steps[index].locals?.[name];
  if (!Array.isArray(initial) || !Array.isArray(current)) return set;
  current.forEach((row, r) => {
    const initRow = Array.isArray(initial[r]) ? initial[r] : [];
    row.forEach((cell, c) => {
      if (initRow[c] !== cell) set.add(`${r},${c}`);
    });
  });
  return set;
}

// A queue/stack/frontier-named local holding [row, col] pairs, within
// this grid's bounds -- real local data, but only discoverable by common
// naming since nothing in the trace structurally marks "this is the
// frontier" the way object identity marks node pointers.
function frontierCells(locals, grid) {
  const rows = grid.length;
  const cols = grid[0]?.length ?? 0;
  const inBounds = (r, c) => Number.isInteger(r) && Number.isInteger(c) && r >= 0 && r < rows && c >= 0 && c < cols;
  for (const [name, v] of Object.entries(locals)) {
    if (!/^(queue|q|dq|deque|frontier|stack|to_visit|pending|next_level)$/i.test(name)) continue;
    if (
      Array.isArray(v) &&
      v.length > 0 &&
      v.length <= rows * cols &&
      v.every((p) => Array.isArray(p) && p.length === 2 && inBounds(p[0], p[1]))
    ) {
      return new Set(v.map(([r, c]) => `${r},${c}`));
    }
  }
  return new Set();
}

export function GridGraphView({ locals, steps, index }) {
  const entries = Object.entries(locals).filter(([, v]) => isGridOfNumbers(v));
  if (entries.length === 0) return null;
  // A pair of int locals (row, col) is common in grid-DFS/BFS problems --
  // show it as a highlighted cursor cell when it's a valid position.
  const intPairs = Object.entries(locals).filter(([, v]) => Number.isInteger(v));
  return (
    <div className="viz-block">
      <Caption>
        Your grid's actual current values. The current (row, col) position your code is tracking is
        outlined in amber; cells your code has already visited are shaded, and cells sitting in a
        traversal queue (when one exists in your code) are marked with a dashed border.
      </Caption>
      {entries.map(([name, grid]) => {
        const rowVar = intPairs.find(([n]) => /^(r|row|i)$/i.test(n));
        const colVar = intPairs.find(([n]) => /^(c|col|j)$/i.test(n));
        const visited = explicitVisitedCells(locals, grid) ?? everChangedCells(steps, index, name);
        const frontier = frontierCells(locals, grid);
        return (
          <div key={name} className="grid-view">
            <div className="seq-label">{name}</div>
            <div className="grid-rows">
              {grid.map((row, r) => (
                <div key={r} className="grid-row">
                  {row.map((cell, c) => {
                    const isCursor = rowVar && colVar && rowVar[1] === r && colVar[1] === c;
                    const key = `${r},${c}`;
                    const isVisited = visited.has(key);
                    const isFrontier = frontier.has(key);
                    const truthy =
                      cell === 1 ||
                      cell === true ||
                      (typeof cell === "string" && cell !== "0" && cell !== "" && cell.toLowerCase() !== "false");
                    return (
                      <div
                        key={c}
                        className={`grid-cell ${truthy ? "grid-cell-on" : "grid-cell-off"} ${isVisited ? "grid-cell-visited" : ""} ${isFrontier ? "grid-cell-frontier" : ""} ${isCursor ? "grid-cell-cursor" : ""}`}
                        title={String(cell)}
                      >
                        {String(cell)}
                      </div>
                    );
                  })}
                </div>
              ))}
            </div>
          </div>
        );
      })}
    </div>
  );
}

export function GraphNodeView({ graph, steps, index }) {
  const { nodes, roots } = graph;
  if (nodes.size === 0) return null;
  const ids = [...nodes.keys()];
  const R = 120;
  const CX = 150;
  const CY = 150;
  const positions = new Map();
  ids.forEach((id, i) => {
    const angle = (2 * Math.PI * i) / ids.length;
    positions.set(id, { x: CX + R * Math.cos(angle), y: CY + R * Math.sin(angle) });
  });
  const edgeSet = new Set();
  const edges = [];
  ids.forEach((id) => {
    const node = nodes.get(id);
    (node.neighborIds || []).forEach((nid) => {
      const key = [id, nid].sort().join("-");
      if (!edgeSet.has(key) && positions.has(nid)) {
        edgeSet.add(key);
        edges.push([id, nid]);
      }
    });
  });
  function pointersAt(id) {
    return roots.filter((r) => r.id === id);
  }
  function primaryField(node) {
    const keys = Object.keys(node.fields);
    const key = keys.find((k) => k === "val" || k === "value") || keys[0];
    return key ? node.fields[key] : "";
  }

  const { changed, isNew } = graphDiff(previousGraph(steps, index), graph);
  const recency = recencyMap(steps, index);
  const currentIds = new Set(roots.filter((r) => r.id != null && !r.name.includes("[")).map((r) => r.id));
  const frontierIds = new Set(roots.filter((r) => r.id != null && r.name.includes("[")).map((r) => r.id));

  return (
    <div className="viz-block">
      <Caption>
        Every node your code currently references and its real neighbor connections. Colored tags
        show which variable points at which node — amber is the node your code just changed or is
        directly pointing at this step; a fainter ring means it's in a traversal queue right now or
        was referenced a few steps ago.
      </Caption>
      <div className="graph-canvas">
        <svg width={300} height={300} className="graph-edges">
          {edges.map(([a, b], i) => {
            const pa = positions.get(a);
            const pb = positions.get(b);
            return <line key={i} x1={pa.x} y1={pa.y} x2={pb.x} y2={pb.y} stroke="#7a8492" strokeWidth="2" />;
          })}
        </svg>
        {ids.map((id) => {
          const pos = positions.get(id);
          const node = nodes.get(id);
          const pointers = pointersAt(id);
          const isFocus = changed.has(id) || isNew.has(id) || currentIds.has(id);
          const tier = isFocus ? null : quietTier(id, frontierIds, recency);
          const nodeClass = isFocus
            ? "graph-node-changed"
            : tier === "strong"
            ? "graph-node-quiet-strong"
            : tier === "faint"
            ? "graph-node-quiet-faint"
            : "";
          return (
            <div key={id} className="graph-node-wrap" style={{ left: pos.x - 20, top: pos.y - 20 }}>
              {pointers.length > 0 && (
                <div className="graph-pointer-tags">
                  {pointers.map((p) => (
                    <span key={p.name} className="pointer-chip" style={{ background: colorForName(p.name) }}>
                      {p.name}
                    </span>
                  ))}
                </div>
              )}
              <div className={`graph-node ${nodeClass}`}>{String(primaryField(node))}</div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

/* ============================== 8. HEAPS ============================== */

export function HeapView({ locals, steps, index }) {
  const entries = Object.entries(locals).filter(
    ([, v]) => isNumericList(v) || (Array.isArray(v) && v.length > 0 && v.length <= 63 && v.every((x) => Array.isArray(x) || typeof x === "number"))
  );
  if (entries.length === 0) return null;

  function label(v) {
    if (Array.isArray(v)) return v.map((x) => (Array.isArray(x) ? `[${x.join(",")}]` : String(x))).join(", ");
    return String(v);
  }

  return (
    <div className="viz-block">
      <Caption>
        Your list rendered as a binary heap tree (index <code>i</code>'s children live at{" "}
        <code>2i+1</code>/<code>2i+2</code> — exactly how Python's <code>heapq</code> stores it). This
        reflects the array's actual current order, heap-valid or not. Amber marks a slot whose value
        changed since this array last appeared — a sift-up/down swap, push, or pop your code just
        made. <code>heapq</code>'s own comparisons happen inside library code this tracer doesn't
        capture, so individual "comparing these two" steps aren't available — only the resulting
        array state is.
      </Caption>
      {entries.map(([name, arr]) => {
        const prev = findPreviousValue(steps, index, name);
        const changed = diffIndices(prev, arr);
        const CELL_W = 64;
        const CELL_H = 60;
        const depthOf = (i) => Math.floor(Math.log2(i + 1));
        const maxDepth = depthOf(arr.length - 1);
        const width = Math.pow(2, maxDepth) * CELL_W + CELL_W;
        const positions = arr.map((_, i) => {
          const depth = depthOf(i);
          const firstInDepth = Math.pow(2, depth) - 1;
          const slot = i - firstInDepth;
          const slotsInDepth = Math.pow(2, depth);
          const x = ((slot + 0.5) / slotsInDepth) * width;
          return { x, y: depth * CELL_H };
        });
        return (
          <div key={name} className="heap-view">
            <div className="seq-label">{name}</div>
            <div className="tree-scroll">
              <div className="tree-canvas" style={{ width, height: (maxDepth + 1) * CELL_H + 30 }}>
                <svg className="tree-edges" width={width} height={(maxDepth + 1) * CELL_H + 30}>
                  {arr.map((_, i) => {
                    const left = 2 * i + 1;
                    const right = 2 * i + 2;
                    const p = positions[i];
                    const lines = [];
                    if (left < arr.length) {
                      const c = positions[left];
                      lines.push(<line key={`${i}-l`} x1={p.x} y1={p.y + 20} x2={c.x} y2={c.y + 20} stroke="#7a8492" strokeWidth="2" />);
                    }
                    if (right < arr.length) {
                      const c = positions[right];
                      lines.push(<line key={`${i}-r`} x1={p.x} y1={p.y + 20} x2={c.x} y2={c.y + 20} stroke="#7a8492" strokeWidth="2" />);
                    }
                    return lines;
                  })}
                </svg>
                {arr.map((v, i) => (
                  <div key={i} className="tree-node-wrap" style={{ left: positions[i].x - 24, top: positions[i].y }}>
                    <div className={`tree-node heap-node ${changed.has(i) ? "heap-node-changed" : ""}`}>{label(v)}</div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
}

/* ============================== 9. DYNAMIC PROGRAMMING TABLES ============================== */

// Every index/cell that has ever differed between two consecutive
// appearances of `name` up through `index` -- i.e. every subproblem
// that's actually been computed so far, as opposed to still sitting at
// its initialization value. Reuses diffIndices (the same helper the
// per-step "just changed" highlight uses) repeatedly across the table's
// whole history instead of a new comparison mechanism.
function everComputedCells(steps, index, name) {
  const result = new Set();
  let prevVal;
  let havePrev = false;
  for (let i = 0; i <= index; i++) {
    const locals = steps[i].locals;
    if (!locals || !Object.prototype.hasOwnProperty.call(locals, name)) continue;
    const val = locals[name];
    if (havePrev) {
      if (Array.isArray(val) && Array.isArray(val[0])) {
        val.forEach((row, r) => {
          const prevRow = Array.isArray(prevVal) ? prevVal[r] : undefined;
          diffIndices(prevRow, row).forEach((c) => result.add(`${r},${c}`));
        });
      } else {
        diffIndices(prevVal, val).forEach((i2) => result.add(`${i2}`));
      }
    }
    prevVal = val;
    havePrev = true;
  }
  return result;
}

function flattenNumeric(table) {
  const out = [];
  const walk = (v) => {
    if (Array.isArray(v)) v.forEach(walk);
    else if (typeof v === "number") out.push(v);
  };
  walk(table);
  return out;
}

// Secondary, subtle magnitude cue for numeric (non-boolean) tables only --
// reuses --sky's own literal RGB (see App.css's --sky token) at a capped,
// low alpha so it can scale continuously with value while never coming
// close to affecting the (unchanged) text contrast. Boolean tables never
// get this -- there's no meaningful magnitude to shade.
function magnitudeStyle(cell, maxAbs) {
  if (typeof cell !== "number" || maxAbs <= 0) return undefined;
  const alpha = Math.min(0.22, (Math.abs(cell) / maxAbs) * 0.22);
  return alpha > 0.02 ? { backgroundColor: `rgba(95, 176, 230, ${alpha.toFixed(2)})` } : undefined;
}

export function DPTableView({ locals, steps, index }) {
  const entries = Object.entries(locals).filter(([, v]) => isBoolOrNumericList(v) || isGridOfNumbers(v));
  if (entries.length === 0) return null;
  return (
    <div className="viz-block">
      <Caption>
        Your DP table's real values right now. Amber is the cell(s) that changed since the last time
        this table appeared in the trace — the subproblem your code just solved. Cells that haven't
        been computed yet (still at their initial value) are faded; a faint blue wash on already-
        computed numeric cells is a secondary hint of relative magnitude, not the main signal.
      </Caption>
      {entries.map(([name, table]) => {
        const prev = findPreviousValue(steps, index, name);
        const everComputed = everComputedCells(steps, index, name);
        const is2D = Array.isArray(table[0]);
        const isBool = typeof (is2D ? table[0]?.[0] : table[0]) === "boolean";
        const maxAbs = isBool ? 0 : Math.max(1, ...flattenNumeric(table).map(Math.abs));
        return (
          <div key={name} className="dp-view">
            <div className="seq-label">{name}</div>
            {is2D ? (
              <div className="grid-rows">
                {table.map((row, r) => {
                  const prevRow = Array.isArray(prev) ? prev[r] : undefined;
                  const changed = diffIndices(prevRow, row);
                  return (
                    <div key={r} className="grid-row">
                      {row.map((cell, c) => {
                        const isChanged = changed.has(c);
                        const isComputed = everComputed.has(`${r},${c}`) || isChanged;
                        const style = !isBool && !isChanged ? magnitudeStyle(cell, maxAbs) : undefined;
                        return (
                          <div
                            key={c}
                            className={`dp-cell ${isChanged ? "dp-cell-changed" : isComputed ? "" : "dp-cell-untouched"}`}
                            style={style}
                          >
                            {typeof cell === "boolean" ? (cell ? "T" : "F") : cell}
                          </div>
                        );
                      })}
                    </div>
                  );
                })}
              </div>
            ) : (
              <div className="grid-row">
                {(() => {
                  const changedSet = diffIndices(prev, table);
                  return table.map((cell, i) => {
                    const changed = changedSet.has(i);
                    const isComputed = everComputed.has(`${i}`) || changed;
                    const style = !isBool && !changed ? magnitudeStyle(cell, maxAbs) : undefined;
                    return (
                      <div
                        key={i}
                        className={`dp-cell ${changed ? "dp-cell-changed" : isComputed ? "" : "dp-cell-untouched"}`}
                        style={style}
                      >
                        {typeof cell === "boolean" ? (cell ? "T" : "F") : cell}
                      </div>
                    );
                  });
                })()}
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
}

// Real recursion (a function calling itself while an earlier call to that
// SAME function is still active on the stack) rather than just "this
// function got called more than once". Counting total call events per
// function name isn't enough -- e.g. building a 5-node linked list calls
// Node.__init__ five times, sequentially, with each call fully returning
// before the next starts; that's an ordinary loop, not recursion. What
// actually indicates recursion is a function name reappearing while it's
// still on the active call stack.
function hasRecursion(steps) {
  const activeStack = [];
  for (const s of steps) {
    if (s.event === "call") {
      if (activeStack.includes(s.function)) return true;
      activeStack.push(s.function);
    } else if (s.event === "return") {
      activeStack.pop();
    }
  }
  return false;
}

/* ============================== DISPATCHER ============================== */

export default function SpecializedVisualization({ problem, steps, index }) {
  const step = steps[index];
  if (!step) return null;
  const locals = step.locals || {};
  const topic = problem?.topic;
  const pattern = (problem?.pattern || "").toLowerCase();

  const graph = collectNodeGraph(locals);
  const primary = detectPrimaryView(problem, locals, graph.kind);

  let primaryPanel = null;
  if (primary === "tree") primaryPanel = <TreeView graph={graph} steps={steps} index={index} />;
  else if (primary === "list") primaryPanel = <LinkedListView graph={graph} steps={steps} index={index} />;
  else if (primary === "graph") primaryPanel = <GraphNodeView graph={graph} steps={steps} index={index} />;
  else if (primary === "dp") primaryPanel = <DPTableView locals={locals} steps={steps} index={index} />;
  else if (primary === "heap") primaryPanel = <HeapView locals={locals} steps={steps} index={index} />;
  else if (primary === "sorting") primaryPanel = <SortingView locals={locals} steps={steps} index={index} />;
  else if (primary === "grid-graph") primaryPanel = <GridGraphView locals={locals} steps={steps} index={index} />;
  else if (primary === "stack" || primary === "queue") primaryPanel = <StackQueueView locals={locals} mode={primary} steps={steps} index={index} />;
  else if (primary === "array") primaryPanel = <ArrayPointerView locals={locals} topic={topic} pattern={pattern} steps={steps} index={index} />;

  const showCallStack = hasRecursion(steps);

  if (!primaryPanel && !showCallStack) return null;

  return (
    <div className="viz-panels">
      {primaryPanel}
      {showCallStack && <CallStackView steps={steps} index={index} />}
    </div>
  );
}
