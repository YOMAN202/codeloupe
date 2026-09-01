import { useState } from "react";
import CodeEditor from "../../components/Editor/CodeEditor";
import TraceViewer from "../../components/TraceViewer/TraceViewer";
import { runCode, traceCode } from "../../api/client";

const DEFAULT_CODE = "# Free scratchpad -- try exercises here, or trace any snippet.\n";

export default function Scratchpad() {
  const [code, setCode] = useState(DEFAULT_CODE);
  const [output, setOutput] = useState(null);
  const [running, setRunning] = useState(false);
  const [error, setError] = useState(null);
  const [trace, setTrace] = useState(null);
  const [tracing, setTracing] = useState(false);
  const [tab, setTab] = useState("run");

  async function handleRun() {
    setRunning(true);
    setError(null);
    setOutput(null);
    try {
      setOutput(await runCode(code));
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
      setTrace(await traceCode(code));
    } catch (e) {
      setError(e.message);
    } finally {
      setTracing(false);
    }
  }

  return (
    <div className="page workspace-page">
      <div className="page-header">
        <h2>Scratchpad &amp; Trace</h2>
        <p className="muted">
          Free-form Python. Run it directly, or step through its execution line by line.
        </p>
      </div>

      <CodeEditor value={code} onChange={setCode} />
      <div className="tab-row">
        <button className="run-button" onClick={handleRun} disabled={running}>
          {running ? "Running..." : "Run"}
        </button>
        <button className="run-button" onClick={handleTrace} disabled={tracing}>
          {tracing ? "Tracing..." : "Trace"}
        </button>
      </div>

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
  );
}
