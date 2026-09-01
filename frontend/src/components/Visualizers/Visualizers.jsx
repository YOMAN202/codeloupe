import "./visualizers.css";
import { collectNodeGraph } from "./nodeGraph";
import { colorForName, detectPrimaryView, isPrimitiveList, isNumericList, isBoolOrNumericList, isGridOfNumbers, isDisplayableString } from "./detect";

// Codeloupe's core promise, restated for every view in this file: render
// what the learner's OWN code actually did at this exact step -- correct
// or not -- never a canned animation of the "right" algorithm. Every
// component here reads straight from the captured trace snapshot; none
// of them know what the "correct" answer looks like.

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

function diffIndices(prevArr, currArr) {
  if (!Array.isArray(prevArr) || !Array.isArray(currArr)) return new Set();
  const changed = new Set();
  const len = Math.max(prevArr.length, currArr.length);
  for (let i = 0; i < len; i++) {
    if (prevArr[i] !== currArr[i]) changed.add(i);
  }
  return changed;
}

/* ============================== 1. ARRAYS / STRINGS / POINTERS / SLIDING WINDOW ============================== */

export function ArrayPointerView({ locals, topic, pattern }) {
  const sequences = Object.entries(locals).filter(([, v]) => isPrimitiveList(v) || isDisplayableString(v));
  if (sequences.length === 0) return null;

  const intVars = Object.entries(locals).filter(([, v]) => Number.isInteger(v));
  const windowEligible = topic === "sliding-window" || topic === "two-pointer" || /window|two.pointer/.test(pattern || "");

  return (
    <div className="viz-block">
      <Caption>
        Your array/string state right now, with any integer variable that's currently a valid index
        shown as a labeled pointer underneath it{windowEligible ? " — the shaded band shows the span between your outermost pointers, i.e. the current window." : "."}
      </Caption>
      {sequences.map(([name, raw]) => {
        const isStr = typeof raw === "string";
        const arr = isStr ? raw.split("") : raw;
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
                  <div key={i} className={`seq-box ${inWindow ? "seq-box-in-window" : ""}`}>
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

export function LinkedListView({ graph }) {
  const { nodes, roots } = graph;
  if (nodes.size === 0) return null;

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
        follow each node's real <code>.next</code>.
      </Caption>
      <div className="ll-chain">
        {chain.map((id, i) => {
          const node = nodes.get(id);
          const pointers = pointersAt(id);
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
              <div className="ll-node">{String(primaryField(node))}</div>
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
                  <div className="ll-node ll-node-orphan">{String(primaryField(node))}</div>
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
                    {k}=<code>{JSON.stringify(v)}</code>
                  </span>
                ))}
              </div>
            )}
            {frame.justReturned !== undefined && (
              <div className="call-frame-return">returning &rarr; <code>{JSON.stringify(frame.justReturned)}</code></div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}

/* ============================== 4. TREES ============================== */

export function TreeView({ graph }) {
  const { nodes, roots } = graph;
  if (nodes.size === 0) return null;
  const rootEntry = roots.find((r) => r.id != null);
  if (!rootEntry) return null;

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
        show which variable is currently pointing at which node.
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
                <div className="tree-node">{String(primaryField(node))}</div>
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

export function StackQueueView({ locals, mode }) {
  const entries = Object.entries(locals).filter(([, v]) => isPrimitiveList(v));
  if (entries.length === 0) return null;
  return (
    <div className="viz-block">
      <Caption>
        {mode === "stack"
          ? "Rendered as a stack — the last element is the top, exactly what .pop() would remove next."
          : "Rendered as a queue — the first element is the front, exactly what would be dequeued next."}
      </Caption>
      {entries.map(([name, arr]) => (
        <div key={name} className={`sq-view sq-${mode}`}>
          <div className="seq-label">{name}</div>
          <div className={mode === "stack" ? "sq-stack" : "sq-queue"}>
            {(mode === "stack" ? [...arr].reverse() : arr).map((val, i) => {
              const isEdge = mode === "stack" ? i === 0 : i === 0 || i === arr.length - 1;
              const edgeLabel =
                mode === "stack" && i === 0 ? "top" : mode === "queue" && i === 0 ? "front" : mode === "queue" && i === arr.length - 1 ? "back" : null;
              return (
                <div key={i} className={`sq-cell ${isEdge ? "sq-cell-edge" : ""}`}>
                  {edgeLabel && <div className="sq-cell-label">{edgeLabel}</div>}
                  <div className="sq-cell-value">{String(val)}</div>
                </div>
              );
            })}
            {arr.length === 0 && <span className="muted small">(empty)</span>}
          </div>
        </div>
      ))}
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

export function GridGraphView({ locals }) {
  const entries = Object.entries(locals).filter(([, v]) => isGridOfNumbers(v));
  if (entries.length === 0) return null;
  // A pair of int locals (row, col) is common in grid-DFS/BFS problems --
  // show it as a highlighted cursor cell when it's a valid position.
  const intPairs = Object.entries(locals).filter(([, v]) => Number.isInteger(v));
  return (
    <div className="viz-block">
      <Caption>
        Your grid's actual current values. If your code tracks a current (row, col) position, it's
        outlined below.
      </Caption>
      {entries.map(([name, grid]) => {
        const rowVar = intPairs.find(([n]) => /^(r|row|i)$/i.test(n));
        const colVar = intPairs.find(([n]) => /^(c|col|j)$/i.test(n));
        return (
          <div key={name} className="grid-view">
            <div className="seq-label">{name}</div>
            <div className="grid-rows">
              {grid.map((row, r) => (
                <div key={r} className="grid-row">
                  {row.map((cell, c) => {
                    const isCursor = rowVar && colVar && rowVar[1] === r && colVar[1] === c;
                    const truthy =
                      cell === 1 ||
                      cell === true ||
                      (typeof cell === "string" && cell !== "0" && cell !== "" && cell.toLowerCase() !== "false");
                    return (
                      <div
                        key={c}
                        className={`grid-cell ${truthy ? "grid-cell-on" : "grid-cell-off"} ${isCursor ? "grid-cell-cursor" : ""}`}
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

export function GraphNodeView({ graph }) {
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
  return (
    <div className="viz-block">
      <Caption>
        Every node your code currently references and its real neighbor connections. Colored tags
        show which variable points at which node.
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
              <div className="graph-node">{String(primaryField(node))}</div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

/* ============================== 8. HEAPS ============================== */

export function HeapView({ locals }) {
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
        reflects the array's actual current order, heap-valid or not.
      </Caption>
      {entries.map(([name, arr]) => {
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
                    <div className="tree-node heap-node">{label(v)}</div>
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

export function DPTableView({ locals, steps, index }) {
  const entries = Object.entries(locals).filter(([, v]) => isBoolOrNumericList(v) || isGridOfNumbers(v));
  if (entries.length === 0) return null;
  return (
    <div className="viz-block">
      <Caption>
        Your DP table's real values right now. The cell(s) that changed since the last time this
        table appeared in the trace are highlighted — that's the subproblem your code just solved.
      </Caption>
      {entries.map(([name, table]) => {
        const prev = findPreviousValue(steps, index, name);
        const is2D = Array.isArray(table[0]);
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
                      {row.map((cell, c) => (
                        <div key={c} className={`dp-cell ${changed.has(c) ? "dp-cell-changed" : ""}`}>
                          {typeof cell === "boolean" ? (cell ? "T" : "F") : cell}
                        </div>
                      ))}
                    </div>
                  );
                })}
              </div>
            ) : (
              <div className="grid-row">
                {table.map((cell, i) => {
                  const changed = diffIndices(prev, table).has(i);
                  return (
                    <div key={i} className={`dp-cell ${changed ? "dp-cell-changed" : ""}`}>
                      {typeof cell === "boolean" ? (cell ? "T" : "F") : cell}
                    </div>
                  );
                })}
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
  if (primary === "tree") primaryPanel = <TreeView graph={graph} />;
  else if (primary === "list") primaryPanel = <LinkedListView graph={graph} />;
  else if (primary === "graph") primaryPanel = <GraphNodeView graph={graph} />;
  else if (primary === "dp") primaryPanel = <DPTableView locals={locals} steps={steps} index={index} />;
  else if (primary === "heap") primaryPanel = <HeapView locals={locals} />;
  else if (primary === "sorting") primaryPanel = <SortingView locals={locals} steps={steps} index={index} />;
  else if (primary === "grid-graph") primaryPanel = <GridGraphView locals={locals} />;
  else if (primary === "stack" || primary === "queue") primaryPanel = <StackQueueView locals={locals} mode={primary} />;
  else if (primary === "array") primaryPanel = <ArrayPointerView locals={locals} topic={topic} pattern={pattern} />;

  const showCallStack = hasRecursion(steps);

  if (!primaryPanel && !showCallStack) return null;

  return (
    <div className="viz-panels">
      {primaryPanel}
      {showCallStack && <CallStackView steps={steps} index={index} />}
    </div>
  );
}
