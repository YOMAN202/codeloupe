import { useEffect, useRef, useState } from "react";

// Renders a captured execution trace (see backend/execution/tracer.py) as a
// step-through debugger: current line, locals, call depth, play/pause/
// step/scrub. Also auto-derives a generic "array view" -- any list-typed
// local rendered as a row of boxes, with any int-typed local whose value
// is a valid index into it shown as a pointer underneath. This isn't a
// bespoke per-pattern visualizer (see docs/decisions.md on Phase 3 scope)
// but it gives arrays/two-pointer/sliding-window a genuinely useful
// picture for free, since the underlying data is already captured.

function ArrayView(locals) {
  const arrays = Object.entries(locals).filter(
    ([, v]) => Array.isArray(v) && v.length > 0 && v.length <= 60 &&
      v.every((x) => typeof x === "number" || typeof x === "string" || typeof x === "boolean")
  );
  if (arrays.length === 0) return null;

  const intVars = Object.entries(locals).filter(([, v]) => Number.isInteger(v));

  return (
    <div className="array-view">
      {arrays.map(([name, arr]) => {
        const pointers = intVars.filter(([, v]) => v >= 0 && v < arr.length);
        return (
          <div key={name} className="array-view-row">
            <div className="array-view-label">{name}</div>
            <div className="array-view-boxes">
              {arr.map((val, i) => (
                <div key={i} className="array-box">
                  <div className="array-box-value">{String(val)}</div>
                  <div className="array-box-index">{i}</div>
                </div>
              ))}
            </div>
            {pointers.length > 0 && (
              <div className="array-view-pointers">
                {pointers.map(([pname, pval]) => (
                  <span key={pname} className="pointer-tag" style={{ "--idx": pval }}>
                    {pname}={pval}
                  </span>
                ))}
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
}

// Traceviz's core promise: this shows what YOUR code actually did, bugs
// included -- not a canned animation of the correct algorithm. That means
// staying useful across all 5 outcomes a submission can hit. See
// backend/execution/tracer.py's module docstring for the full breakdown;
// this banner is the frontend half of the same story.
const STATUS_BANNER = {
  completed: { tone: "success", label: "Ran to completion", detail: null },
  runtime_error: { tone: "error", label: "Crashed during execution", detail: null },
  truncated: { tone: "warning", label: "Step limit reached", detail: null },
  syntax_error: { tone: "error", label: "Code didn't run — syntax error", detail: null },
  crashed: { tone: "error", label: "Execution didn't complete", detail: null },
};

function TraceStatusBanner({ trace, onJumpToFailure, atFailure }) {
  const meta = STATUS_BANNER[trace.status] || STATUS_BANNER.crashed;
  return (
    <div className={`trace-status-banner trace-status-${meta.tone}`}>
      <span className="trace-status-label">{meta.label}</span>
      {trace.status === "runtime_error" && trace.error && (
        <>
          <span className="trace-status-error-detail">
            <code>{trace.error.type}</code>: {trace.error.message}
            {trace.error.line != null && <> (line {trace.error.line})</>}
          </span>
          {!atFailure && (
            <button className="chip chip-small" onClick={onJumpToFailure}>
              Jump to failure point &rarr;
            </button>
          )}
        </>
      )}
      {trace.status === "truncated" && (
        <span className="trace-status-error-detail">
          Your code was still running after {trace.steps.length} steps — almost always an
          infinite loop or recursion with no base case. Showing everything captured up to that
          point; step or scrub through to find where it stops making progress.
        </span>
      )}
      {trace.status === "syntax_error" && trace.error && (
        <span className="trace-status-error-detail">
          <code>{trace.error.type}</code>: {trace.error.message}
          {trace.error.line != null && <> (line {trace.error.line})</>} — fix this before Traceviz
          can trace anything, since Python can't even parse the code yet.
        </span>
      )}
    </div>
  );
}

export default function TraceViewer({ trace }) {
  const [index, setIndex] = useState(0);
  const [playing, setPlaying] = useState(false);
  const intervalRef = useRef(null);

  const steps = trace?.steps || [];

  useEffect(() => {
    setIndex(0);
    setPlaying(false);
  }, [trace]);

  useEffect(() => {
    if (playing && index < steps.length - 1) {
      intervalRef.current = setTimeout(() => setIndex((i) => i + 1), 500);
    } else {
      setPlaying(false);
    }
    return () => clearTimeout(intervalRef.current);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [playing, index, steps.length]);

  if (!trace) return null;

  // Hard crash before/without any parseable trace payload at all (rare --
  // usually a wall-clock timeout on a single pathologically slow line; see
  // tracer.py's docstring). No steps are recoverable here, unlike every
  // other failure mode below.
  if (trace.crashed || steps.length === 0) {
    return (
      <div className="trace-viewer">
        <TraceStatusBanner trace={{ ...trace, status: trace.status || "crashed" }} />
        {trace.status === "syntax_error" ? (
          <p className="muted">Nothing executed yet — there's no step-through to show until this parses.</p>
        ) : (
          <>
            <p className="muted">
              {trace.crashed
                ? "The sandbox couldn't finish running your code, so no execution steps were recoverable this time."
                : "No trace steps captured (code may not have executed any lines)."}
            </p>
            {trace.stderr && <pre className="error">{trace.stderr}</pre>}
          </>
        )}
      </div>
    );
  }

  const step = steps[index];
  const atFailure = index === steps.length - 1;

  return (
    <div className="trace-viewer">
      <TraceStatusBanner
        trace={trace}
        atFailure={atFailure}
        onJumpToFailure={() => {
          setPlaying(false);
          setIndex(steps.length - 1);
        }}
      />
      <div className="trace-controls">
        <button className="chip" onClick={() => setIndex(0)} disabled={index === 0}>
          &#8634; Reset
        </button>
        <button className="chip" onClick={() => setIndex((i) => Math.max(0, i - 1))} disabled={index === 0}>
          &larr; Step back
        </button>
        <button className="chip" onClick={() => setPlaying((p) => !p)} disabled={index >= steps.length - 1}>
          {playing ? "Pause" : "Play"}
        </button>
        <button
          className="chip"
          onClick={() => setIndex((i) => Math.min(steps.length - 1, i + 1))}
          disabled={index >= steps.length - 1}
        >
          Step forward &rarr;
        </button>
        <span className="muted">
          step {index + 1} / {steps.length}
        </span>
      </div>

      <input
        type="range"
        min={0}
        max={steps.length - 1}
        value={index}
        onChange={(e) => {
          setPlaying(false);
          setIndex(Number(e.target.value));
        }}
        className="trace-scrubber"
      />

      <div className={`trace-step-info ${atFailure && trace.status === "runtime_error" ? "trace-step-failure" : ""}`}>
        <span className={`trace-event trace-event-${step.event}`}>{step.event}</span>
        <span>
          line <strong>{step.line}</strong>
        </span>
        <span>
          in <strong>{step.function}</strong>
        </span>
        <span>call depth {"  ".repeat(0)}{"|".repeat(Math.min(step.call_depth, 15))} ({step.call_depth})</span>
        {atFailure && trace.status === "runtime_error" && (
          <span className="trace-failure-tag">&#9888; execution stopped here</span>
        )}
      </div>

      {step.event === "return" && (
        <p className="muted">
          returns: <code>{JSON.stringify(step.return_value)}</code>
        </p>
      )}

      {Object.keys(step.locals || {}).length > 0 && (
        <div className="locals-table">
          <strong>Local variables</strong>
          <table>
            <tbody>
              {Object.entries(step.locals).map(([k, v]) => (
                <tr key={k}>
                  <td className="locals-key">{k}</td>
                  <td className="locals-value">{JSON.stringify(v)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {ArrayView(step.locals || {})}

      <p className="muted small">{trace.limitations}</p>
    </div>
  );
}
