import { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import CodeEditor from "../../components/Editor/CodeEditor";
import TraceViewer from "../../components/TraceViewer/TraceViewer";
import { DifficultyBadge, PriorityBadge, TierBadge } from "../../components/Badges/Badges";
import MultilineText from "../../components/MultilineText/MultilineText";
import {
  fetchProblem,
  fetchHint,
  fetchHintFromCode,
  fetchSolution,
  runProblem,
  fetchComplexityEstimate,
  logAttempt,
  traceProblem,
} from "../../api/client";

const TABS = ["Tests", "Hints", "Trace", "Complexity"];

export default function ProblemWorkspace() {
  const { slug } = useParams();
  const [problem, setProblem] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const [code, setCode] = useState("");
  const [running, setRunning] = useState(false);
  const [runResult, setRunResult] = useState(null);

  const [tab, setTab] = useState("Tests");

  const [hintsShown, setHintsShown] = useState([]); // rungs revealed, e.g. [1, 2]
  const [codeHint, setCodeHint] = useState(null);
  const [loadingCodeHint, setLoadingCodeHint] = useState(false);
  const [solution, setSolution] = useState(null);
  const [solutionRevealed, setSolutionRevealed] = useState(false);

  const [complexity, setComplexity] = useState(null);
  const [loadingComplexity, setLoadingComplexity] = useState(false);

  const [trace, setTrace] = useState(null);
  const [tracing, setTracing] = useState(false);
  const [traceTestCaseIndex, setTraceTestCaseIndex] = useState(0);

  const [startedAt, setStartedAt] = useState(Date.now());
  const [attemptFeedback, setAttemptFeedback] = useState(null);

  useEffect(() => {
    setLoading(true);
    setRunResult(null);
    setHintsShown([]);
    setCodeHint(null);
    setSolution(null);
    setSolutionRevealed(false);
    setComplexity(null);
    setTrace(null);
    setTraceTestCaseIndex(0);
    setAttemptFeedback(null);
    setStartedAt(Date.now());
    setTab("Tests");
    fetchProblem(slug)
      .then((p) => {
        setProblem(p);
        setCode(p.starter_code || "");
      })
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, [slug]);

  async function handleRun() {
    setRunning(true);
    setRunResult(null);
    setAttemptFeedback(null);
    try {
      const result = await runProblem(slug, code);
      setRunResult(result);
      const timeTakenSeconds = Math.round((Date.now() - startedAt) / 1000);
      const attempt = await logAttempt({
        slug,
        submitted_code: code,
        passed: result.all_passed,
        hints_used: hintsShown.length,
        max_hint_rung_seen: hintsShown.length ? Math.max(...hintsShown) : 0,
        solution_revealed: solutionRevealed,
        time_taken_seconds: timeTakenSeconds,
      });
      setAttemptFeedback(attempt);
    } catch (e) {
      setError(e.message);
    } finally {
      setRunning(false);
    }
  }

  async function revealHint(rung) {
    if (hintsShown.includes(rung)) return;
    try {
      const h = await fetchHint(slug, rung);
      setHintsShown((prev) => [...prev, rung].sort());
      setCodeHint((prev) => ({ ...prev, [`static-${rung}`]: h.content }));
    } catch (e) {
      setError(e.message);
    }
  }

  async function requestCodeHint() {
    setLoadingCodeHint(true);
    try {
      const result = await fetchHintFromCode(slug, code);
      setCodeHint((prev) => ({ ...prev, fromCode: result.hint }));
    } catch (e) {
      setError(e.message);
    } finally {
      setLoadingCodeHint(false);
    }
  }

  async function revealSolution() {
    try {
      const s = await fetchSolution(slug);
      setSolution(s);
      setSolutionRevealed(true);
    } catch (e) {
      setError(e.message);
    }
  }

  async function runComplexity() {
    setLoadingComplexity(true);
    try {
      const result = await fetchComplexityEstimate(slug, code);
      setComplexity(result);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoadingComplexity(false);
    }
  }

  async function runTrace() {
    setTracing(true);
    setTrace(null);
    try {
      // Traces against a real test case (not the bare code as-typed) --
      // starter code is just a function signature with no call to it, so
      // without this the trace would never actually enter the function
      // body. See client.js's traceProblem / app.py's /trace docstring.
      const result = await traceProblem(slug, code, traceTestCaseIndex);
      setTrace(result);
    } catch (e) {
      setError(e.message);
    } finally {
      setTracing(false);
    }
  }

  if (loading) return <p className="muted">Loading problem...</p>;
  if (error) return <p className="error">{error}</p>;
  if (!problem) return null;

  return (
    <div className="page workspace-page">
      <div className="workspace-columns">
        <div className="workspace-left">
          <div className="page-header">
            <div className="lesson-detail-title">
              <h2>{problem.title}</h2>
              <TierBadge tier={problem.path_tier} />
              <DifficultyBadge difficulty={problem.difficulty} />
              <PriorityBadge priority={problem.interview_priority} />
            </div>
            <p className="muted">
              {problem.topic} &middot; {problem.pattern}
              {problem.canonical_reference && <> &middot; {problem.canonical_reference}</>}
            </p>
            {problem.day != null ? (
              <Link to={`/lessons/${problem.day}`} className="muted small">
                &larr; back to Day {problem.day}
              </Link>
            ) : (
              <Link to="/problems" className="muted small">
                &larr; back to problem bank
              </Link>
            )}
          </div>

          <MultilineText text={problem.description_markdown} />
          {problem.constraints_markdown && (
            <>
              <h4>Constraints</h4>
              <MultilineText text={problem.constraints_markdown} />
            </>
          )}
          {problem.visible_test_cases?.length > 0 && (
            <>
              <h4>Examples</h4>
              <ul>
                {problem.visible_test_cases.slice(0, 3).map((tc, i) => (
                  <li key={i}>
                    <code>{JSON.stringify(tc.args)}</code> &rarr;{" "}
                    <code>{JSON.stringify(tc.expected)}</code>
                  </li>
                ))}
              </ul>
            </>
          )}
          <p className="muted small">
            Target: {problem.expected_time_complexity} time, {problem.expected_space_complexity} space
          </p>
          {problem.edge_cases && (
            <>
              <h4>Edge cases to think about</h4>
              <MultilineText text={problem.edge_cases} />
            </>
          )}
        </div>

        <div className="workspace-right">
          <CodeEditor value={code} onChange={setCode} />
          <button className="run-button" onClick={handleRun} disabled={running}>
            {running ? "Running..." : "Run tests"}
          </button>

          {attemptFeedback && (
            <p className={attemptFeedback.is_independent ? "success" : "warning"}>
              {attemptFeedback.result === "failed"
                ? "Not passing yet -- keep going."
                : attemptFeedback.is_independent
                ? `Solved independently. Next review: ${attemptFeedback.next_due_date}.`
                : `Solved with help (hints/solution used). Next review: ${attemptFeedback.next_due_date}.`}
            </p>
          )}

          <div className="tab-row">
            {TABS.map((t) => (
              <button key={t} className={`chip ${tab === t ? "chip-active" : ""}`} onClick={() => setTab(t)}>
                {t}
              </button>
            ))}
          </div>

          <div className="tab-panel">
            {tab === "Tests" && (
              <div>
                {!runResult && <p className="muted">Run your code to see test results.</p>}
                {runResult?.crashed && (
                  <>
                    <p className="error">Your code crashed before producing results.</p>
                    <pre className="error">{runResult.stderr}</pre>
                  </>
                )}
                {runResult?.results?.length > 0 && (
                  <ul className="test-results">
                    {runResult.results.map((r) => (
                      <li key={r.index} className={r.passed ? "test-pass" : "test-fail"}>
                        <span>{r.passed ? "PASS" : "FAIL"}</span>
                        <code>input: {JSON.stringify(r.args)}</code>
                        {!r.passed && (
                          <>
                            <code>expected: {JSON.stringify(r.expected)}</code>
                            <code>got: {r.error ? r.error : JSON.stringify(r.actual)}</code>
                          </>
                        )}
                      </li>
                    ))}
                  </ul>
                )}
              </div>
            )}

            {tab === "Hints" && (
              <div>
                <p className="muted">
                  Try for real first. Each hint gets more specific -- rung 1 is conceptual, rung 3 is
                  near-pseudocode.
                </p>
                <div className="hint-buttons">
                  {[1, 2, 3].map((rung) => (
                    <button key={rung} className="chip" onClick={() => revealHint(rung)}>
                      {hintsShown.includes(rung) ? `Hint ${rung} shown` : `Reveal hint ${rung}`}
                    </button>
                  ))}
                  <button className="chip" onClick={requestCodeHint} disabled={loadingCodeHint}>
                    {loadingCodeHint ? "Analyzing..." : "Hint based on my code"}
                  </button>
                </div>
                {[1, 2, 3].map(
                  (rung) =>
                    hintsShown.includes(rung) && (
                      <p key={rung} className="hint-text">
                        <strong>Hint {rung}:</strong> {codeHint?.[`static-${rung}`]}
                      </p>
                    )
                )}
                {codeHint?.fromCode && (
                  <p className="hint-text">
                    <strong>About your code:</strong> {codeHint.fromCode}
                  </p>
                )}
                <hr />
                {!solutionRevealed ? (
                  <button className="chip chip-danger" onClick={revealSolution}>
                    Reveal full solution (last resort)
                  </button>
                ) : (
                  <div>
                    <p className="warning">
                      This attempt will be tagged assisted, not independent, per the spaced-revision
                      system.
                    </p>
                    <p>
                      <strong>Brute force:</strong> {solution.brute_force_approach}
                    </p>
                    <p>
                      <strong>Optimal:</strong> {solution.optimal_approach}
                    </p>
                    <pre className="code-block">{solution.solution_code}</pre>
                  </div>
                )}
              </div>
            )}

            {tab === "Trace" && (
              <div>
                {problem.visible_test_cases?.length > 1 && (
                  <label className="trace-testcase-picker">
                    Trace against:{" "}
                    <select
                      value={traceTestCaseIndex}
                      onChange={(e) => setTraceTestCaseIndex(Number(e.target.value))}
                    >
                      {problem.visible_test_cases.map((tc, i) => (
                        <option key={i} value={i}>
                          test case {i + 1}: {JSON.stringify(tc.args)}
                        </option>
                      ))}
                    </select>
                  </label>
                )}
                <button className="chip" onClick={runTrace} disabled={tracing}>
                  {tracing ? "Tracing..." : "Trace my code"}
                </button>
                {trace?.traced_test_case_args && (
                  <p className="muted small">
                    Traced with: <code>{problem.function_signature.match(/def\s+(\w+)/)?.[1]}(
                    {trace.traced_test_case_args.map((a) => JSON.stringify(a)).join(", ")})</code>
                  </p>
                )}
                <TraceViewer trace={trace} problem={problem} />
              </div>
            )}

            {tab === "Complexity" && (
              <div>
                <button className="chip" onClick={runComplexity} disabled={loadingComplexity}>
                  {loadingComplexity ? "Estimating..." : "Estimate complexity of my code"}
                </button>
                {complexity && (
                  <div className="complexity-result">
                    <p>
                      <strong>Structural estimate:</strong>{" "}
                      {complexity.structural?.structural_time_estimate || complexity.structural?.error}
                    </p>
                    {complexity.structural?.caveat && (
                      <p className="muted small">{complexity.structural.caveat}</p>
                    )}
                    {complexity.empirical?.timings?.length > 0 && (
                      <>
                        <strong>Empirical timing on this problem's test cases:</strong>
                        <ul>
                          {complexity.empirical.timings.map((t, i) => (
                            <li key={i}>
                              input size {t.input_size ?? "n/a"}: {(t.seconds * 1000).toFixed(3)} ms
                            </li>
                          ))}
                        </ul>
                        <p className="muted small">{complexity.empirical.note}</p>
                      </>
                    )}
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
