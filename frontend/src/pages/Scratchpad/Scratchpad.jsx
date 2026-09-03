import { useEffect, useRef, useState } from "react";
import CodeEditor from "../../components/Editor/CodeEditor";
import TraceViewer from "../../components/TraceViewer/TraceViewer";
import StdinInput from "../../components/StdinInput/StdinInput";
import { runCode, traceCode } from "../../api/client";

const DEFAULT_CODE = "# Free scratchpad -- try exercises here, or trace any snippet.\n";

export default function Scratchpad() {
  const [code, setCode] = useState(DEFAULT_CODE);
  const [stdin, setStdin] = useState("");
  const [output, setOutput] = useState(null);
  const [running, setRunning] = useState(false);
  const [error, setError] = useState(null);
  const [trace, setTrace] = useState(null);
  const [tracing, setTracing] = useState(false);
  const [tab, setTab] = useState("run");
  // "stacked" (editor above, output/trace below -- the existing layout) is
  // the default per the requested UX: split screen is an opt-in choice,
  // never something a first-time visitor is dropped into.
  const [viewMode, setViewMode] = useState("stacked");

  // Run and Trace intentionally read the SAME `stdin` state -- one Input
  // box feeds whichever action the learner clicks, so a program that reads
  // input() sees identical input whether you Run it or step through it in
  // Trace. Switching the Output/Trace tab never touches this state, so
  // stdin survives that switch too (nothing to lose).
  async function handleRun() {
    setRunning(true);
    setError(null);
    setOutput(null);
    try {
      setOutput(await runCode(code, stdin));
    } catch (e) {
      setError(e.message);
    } finally {
      setRunning(false);
    }
  }

  async function handleTrace() {
    setTracing(true);
    setError(null);
    setTrace(null);
    try {
      setTrace(await traceCode(code, stdin));
    } catch (e) {
      setError(e.message);
    } finally {
      setTracing(false);
    }
  }

  // "Jump to Trace" (the bottom ribbon's arrow): switches to the Trace tab
  // AND scrolls it into view, accounting for the fixed ribbon's own height
  // via traceSection's scroll-margin-bottom (see App.css) so the
  // destination doesn't land half-hidden behind the ribbon. traceScrollToken
  // is bumped on every click of that one control -- and nothing else -- so
  // the effect below re-fires on repeat clicks even when `tab` was already
  // "trace" (where a tab-keyed effect wouldn't retrigger). Same pattern as
  // ProblemWorkspace's "Open in full Trace" scroll handoff.
  const traceSectionRef = useRef(null);
  const [traceScrollToken, setTraceScrollToken] = useState(0);

  function jumpToTrace() {
    setTab("trace");
    setTraceScrollToken((n) => n + 1);
  }

  const skippedInitialScrollRef = useRef(false);
  useEffect(() => {
    if (!skippedInitialScrollRef.current) {
      skippedInitialScrollRef.current = true;
      return;
    }
    const reduceMotion = window.matchMedia?.("(prefers-reduced-motion: reduce)").matches;
    traceSectionRef.current?.scrollIntoView({ behavior: reduceMotion ? "auto" : "smooth", block: "start" });
  }, [traceScrollToken]);

  return (
    <div className="page workspace-page scratchpad-page">
      <div className="page-header">
        <h2>Scratchpad &amp; Trace</h2>
        <p className="muted">
          Free-form Python. Run it directly, or step through its execution line by line.
        </p>
      </div>

      <div className="scratchpad-toolbar" role="group" aria-label="Layout">
        <span className="scratchpad-toolbar-label">Layout:</span>
        <button
          type="button"
          className={`chip ${viewMode === "stacked" ? "chip-active" : ""}`}
          onClick={() => setViewMode("stacked")}
          aria-pressed={viewMode === "stacked"}
        >
          Stacked
        </button>
        <button
          type="button"
          className={`chip ${viewMode === "split" ? "chip-active" : ""}`}
          onClick={() => setViewMode("split")}
          aria-pressed={viewMode === "split"}
        >
          Split screen
        </button>
      </div>

      <div className={`scratchpad-columns ${viewMode === "split" ? "scratchpad-columns-split" : "scratchpad-columns-stacked"}`}>
        <div className="scratchpad-editor-column">
          <CodeEditor value={code} onChange={setCode} />
          <StdinInput value={stdin} onChange={setStdin} />
        </div>

        <div className="scratchpad-trace-column" ref={traceSectionRef}>
          <div className="tab-row">
            <button className={`chip ${tab === "run" ? "chip-active" : ""}`} onClick={() => setTab("run")}>
              Output
            </button>
            <button className={`chip ${tab === "trace" ? "chip-active" : ""}`} onClick={() => setTab("trace")}>
              Trace
            </button>
          </div>

          {tab === "run" && (
            <div className="output-panel">
              {error && <pre className="error">{error}</pre>}
              {output && (
                <>
                  {output.timed_out && <p className="warning">Execution timed out.</p>}
                  <pre className="stdout">{output.stdout || "(no stdout)"}</pre>
                  {output.stderr && <pre className="stderr">{output.stderr}</pre>}
                  <p className="muted">exit code: {String(output.exit_code)}</p>
                </>
              )}
              {!output && !error && <p className="muted">(run your code to see output)</p>}
            </div>
          )}

          {tab === "trace" && <TraceViewer trace={trace} />}
        </div>
      </div>

      {/* Fixed bottom action ribbon: Run + Trace (the same handlers/state as
          before -- this replaces the old inline Run/Trace button row rather
          than duplicating it alongside a second copy) plus a jump-to-trace
          arrow. Stays reachable while scrolling; see .scratchpad-page's
          padding-bottom (App.css) for how the page reserves room so this
          never covers the last bit of real content. */}
      <div className="scratchpad-ribbon">
        <div className="scratchpad-ribbon-inner">
          <div className="scratchpad-ribbon-actions">
            <button className="run-button" onClick={handleRun} disabled={running}>
              {running ? "Running..." : "Run"}
            </button>
            <button className="run-button" onClick={handleTrace} disabled={tracing}>
              {tracing ? "Tracing..." : "Trace"}
            </button>
          </div>
          <button
            type="button"
            className="scratchpad-jump-btn"
            onClick={jumpToTrace}
            title="Jump to the Trace section"
          >
            Trace section
            <span className="scratchpad-jump-arrow" aria-hidden="true">↓</span>
          </button>
        </div>
      </div>
    </div>
  );
}
