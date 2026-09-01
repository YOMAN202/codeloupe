import { useEffect, useRef, useState } from "react";
import SpecializedVisualization from "../Visualizers/Visualizers";
import { diffLocals } from "../../utils/compare";

// Renders a captured execution trace (see backend/execution/tracer.py) as a
// step-through debugger: current line, locals, call depth, play/pause/
// step/scrub, PLUS a data-structure-aware visualization of the actual
// execution state (see ../Visualizers/Visualizers.jsx) -- an array/string
// view with pointer and sliding-window highlighting, a real linked-list
// node-and-arrow diagram, a live recursive call stack, a tree diagram, a
// stack/queue view, sorting bars, a grid/graph view, a heap tree, or a DP
// table -- whichever the current step's actual locals and the problem's
// topic best match. The generic locals table below always stays visible
// too, as the guaranteed fallback for anything a specialized view doesn't
// (or can't) cover -- see docs/decisions.md's "Phase 3" section.

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

// Predict -> Run -> Compare: an optional, off-by-default learning mode.
// The learner writes a free-text prediction of what the NEXT step will
// do (no attempt to auto-grade free text -- that would be an unreliable
// claim), then reveals a plain structural diff of what actually changed
// so they can judge for themselves. Fully self-contained: it only reads
// the already-fetched steps array and never affects normal stepping.
function PredictPanel({ steps, index }) {
  const [guess, setGuess] = useState("");
  const [revealed, setRevealed] = useState(false);

  useEffect(() => {
    setGuess("");
    setRevealed(false);
  }, [index]);

  const nextStep = steps[index + 1];
  if (!nextStep) {
    return (
      <div className="predict-panel">
        <p className="viz-caption">This is the last captured step — nothing further to predict.</p>
      </div>
    );
  }
  const changes = diffLocals(steps[index].locals, nextStep.locals);

  return (
    <div className="predict-panel">
      <p className="viz-caption">
        Before stepping forward: what do you think happens next — which variable, pointer, or value
        changes? Write a quick guess, then reveal to compare against what your code actually did.
      </p>
      <textarea
        className="predict-input"
        rows={2}
        placeholder="e.g. left will move to index 3, or nothing changes yet..."
        value={guess}
        onChange={(e) => setGuess(e.target.value)}
        disabled={revealed}
      />
      {!revealed ? (
        <button className="chip" onClick={() => setRevealed(true)}>
          Reveal what actually happens next
        </button>
      ) : (
        <div className="predict-reveal">
          <p className="muted small">
            <strong>Your prediction:</strong> {guess.trim() || "(left blank)"}
          </p>
          <p className="muted small">
            <strong>What actually happened</strong> — next is a <code>{nextStep.event}</code> at line{" "}
            {nextStep.line}
            {nextStep.function ? <> in <code>{nextStep.function}</code></> : null}:
          </p>
          {changes.length === 0 ? (
            <p className="muted small">No local variables changed at that step.</p>
          ) : (
            <ul className="predict-diff">
              {changes.map((c) => (
                <li key={c.name}>
                  <code>{c.name}</code>: {c.isNew ? <em>new</em> : JSON.stringify(c.before)} &rarr;{" "}
                  {JSON.stringify(c.after)}
                </li>
              ))}
            </ul>
          )}
          <button className="chip chip-small" onClick={() => setRevealed(false)}>
            Predict again
          </button>
        </div>
      )}
    </div>
  );
}

export default function TraceViewer({ trace, problem, focusEnd }) {
  const [index, setIndex] = useState(0);
  const [playing, setPlaying] = useState(false);
  const [predictMode, setPredictMode] = useState(false);
  const intervalRef = useRef(null);

  const steps = trace?.steps || [];

  useEffect(() => {
    setIndex(focusEnd && steps.length > 0 ? steps.length - 1 : 0);
    setPlaying(false);
    // eslint-disable-next-line react-hooks/exhaustive-deps
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
        <button
          className={`chip ${predictMode ? "chip-active" : ""}`}
          onClick={() => setPredictMode((p) => !p)}
          title="Optional: guess what happens next before revealing it"
        >
          &#128302; Predict mode {predictMode ? "on" : "off"}
        </button>
      </div>

      {predictMode && <PredictPanel steps={steps} index={index} />}

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

      <SpecializedVisualization problem={problem} steps={steps} index={index} />

      <p className="muted small">{trace.limitations}</p>
    </div>
  );
}
