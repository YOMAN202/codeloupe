import { useEffect, useState } from "react";
import LessonView from "./components/LessonView/LessonView";
import CodeEditor from "./components/Editor/CodeEditor";
import { fetchLesson, runCode } from "./api/client";
import "./App.css";

const DEFAULT_CODE = "# Write your Python code here, then click Run.\n";

function App() {
  const [lesson, setLesson] = useState(null);
  const [lessonLoading, setLessonLoading] = useState(true);
  const [lessonError, setLessonError] = useState(null);

  const [code, setCode] = useState(DEFAULT_CODE);
  const [output, setOutput] = useState(null);
  const [running, setRunning] = useState(false);
  const [runError, setRunError] = useState(null);

  useEffect(() => {
    fetchLesson(1)
      .then(setLesson)
      .catch((e) => setLessonError(e.message))
      .finally(() => setLessonLoading(false));
  }, []);

  async function handleRun() {
    setRunning(true);
    setRunError(null);
    setOutput(null);
    try {
      const result = await runCode(code);
      setOutput(result);
    } catch (e) {
      setRunError(e.message);
    } finally {
      setRunning(false);
    }
  }

  return (
    <div className="app-shell">
      <header>
        <h1>Traceviz</h1>
        <p className="muted">Milestone 1 — lesson view, editor, sandboxed run</p>
      </header>

      <main className="two-pane">
        <div className="pane lesson-pane">
          <LessonView lesson={lesson} loading={lessonLoading} error={lessonError} />
        </div>

        <div className="pane editor-pane">
          <CodeEditor value={code} onChange={setCode} />
          <button className="run-button" onClick={handleRun} disabled={running}>
            {running ? "Running..." : "Run"}
          </button>

          <div className="output-panel">
            <h3>Output</h3>
            {runError && <pre className="error">{runError}</pre>}
            {output && (
              <>
                {output.timed_out && (
                  <p className="warning">Execution timed out.</p>
                )}
                <pre className="stdout">{output.stdout || "(no stdout)"}</pre>
                {output.stderr && <pre className="stderr">{output.stderr}</pre>}
                <p className="muted">exit code: {String(output.exit_code)}</p>
              </>
            )}
            {!output && !runError && <p className="muted">(run your code to see output)</p>}
          </div>
        </div>
      </main>
    </div>
  );
}

export default App;
