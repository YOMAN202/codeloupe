import { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import CodeEditor from "../../components/Editor/CodeEditor";
import TraceViewer from "../../components/TraceViewer/TraceViewer";
import { DifficultyBadge, PriorityBadge, TierBadge } from "../../components/Badges/Badges";
import MultilineText from "../../components/MultilineText/MultilineText";
import { describeMismatch } from "../../utils/compare";
import {
  fetchProblem,
  fetchHint,
  fetchHintFromCode,
  fetchSolution,
  runProblem,
  fetchComplexityEstimate,
  logAttempt,
  traceProblem,
  traceProblemCustom,
  runProblemCustom,
  fetchAttempts,
} from "../../api/client";

const TABS = ["Tests", "Hints", "Trace", "Complexity", "Playground", "History"];

// Optional pattern-recognition practice: the standard pattern categories a
// learner should be building intuition for. Deliberately not tied 1:1 to
// the problem bank's free-text `pattern` field (e.g. "opposite-direction
// two-pointer") -- this is a coarse self-check, not an auto-graded quiz,
// since trying to auto-match a guess against free text would either be
// too strict (marking a reasonable guess "wrong") or too lenient (fake
// precision). The learner compares their own guess to the revealed
// answer and judges for themselves.
const PATTERN_CATEGORIES = [
  "Hash map / set", "Two pointers", "Sliding window", "Binary search",
  "Stack", "Queue", "Linked list manipulation", "Recursion",
  "Tree traversal", "BFS / DFS", "Heap / priority queue", "Dynamic programming",
  "Sorting", "Greedy", "Not sure yet",
];

// Better failure analysis: identifies the FIRST failing test case (not
// all of them at once -- one clear starting point beats a wall of red),
// shows expected vs actual with a plain structural description of how
// they differ (never a claimed diagnosis of WHY -- that's not something
// this can reliably determine), and offers a one-click path into the
// Trace tab against that exact case. Renders nothing when everything
// passed or when there's nothing failing to analyze yet.
function FailureAnalysis({ runResult, onInspect }) {
  if (!runResult?.results?.length) return null;
  const firstFailure = runResult.results.find((r) => !r.passed);
  if (!firstFailure) return null;
  return (
    <div className="failure-analysis">
      <h4>First failing case (test {firstFailure.index + 1})</h4>
      <div className="failure-analysis-row">
        <span>
          <strong>Input:</strong> <code>{JSON.stringify(firstFailure.args)}</code>
        </span>
      </div>
      <div className="failure-analysis-row">
        <span>
          <strong>Expected:</strong> <code>{JSON.stringify(firstFailure.expected)}</code>
        </span>
        <span>
          <strong>Got:</strong>{" "}
          <code>{firstFailure.error ? firstFailure.error : JSON.stringify(firstFailure.actual)}</code>
        </span>
      </div>
      {!firstFailure.error && (
        <p className="failure-analysis-diff">{describeMismatch(firstFailure.expected, firstFailure.actual)}</p>
      )}
      {firstFailure.error && (
        <p className="failure-analysis-diff">
          Your code raised an error on this input rather than returning a value — the trace below
          will show exactly which line it happened on and the state leading up to it.
        </p>
      )}
      <p className="muted small">
        This points at where things diverge, not necessarily why — step through the actual execution
        to see your own logic play out on this exact input.
      </p>
      <button className="chip chip-small" onClick={() => onInspect(firstFailure.index)}>
        Inspect this case in the Trace tab &rarr;
      </button>
    </div>
  );
}

// Optional pattern-recognition practice. Collapsed by default so it never
// gets in the way of just solving the problem; picking a guess does NOT
// reveal the answer -- that needs an explicit second action, and even
// then the learner compares their own guess to the real pattern rather
// than being told "correct" or "wrong" (auto-grading a coarse category
// guess against a free-text pattern description would be either falsely
// strict or falsely lenient).
// Custom test-case playground: suggests a handful of beginner-friendly edge
// cases (empty / single element / duplicates / negative / reverse-sorted /
// boundary) derived from the SHAPE of a real example the problem already
// has, rather than a fixed generic list -- so a string problem gets string
// presets and a numeric-list problem gets numeric-list presets. Only the
// first parameter is varied; deliberately small (never more than ~4
// buttons) per "do not automatically overwhelm me with tests."
function buildEdgeCasePresets(sampleArgs) {
  if (!Array.isArray(sampleArgs) || sampleArgs.length === 0) return [];
  const [first, ...rest] = sampleArgs;
  if (Array.isArray(first)) {
    const presets = [{ label: "Empty list", args: [[], ...rest] }];
    if (first.length > 0) presets.push({ label: "Single element", args: [[first[0]], ...rest] });
    if (first.every((x) => typeof x === "number")) {
      const v = typeof first[0] === "number" ? first[0] : 1;
      presets.push({ label: "Duplicates", args: [[v, v, v], ...rest] });
      presets.push({ label: "Negative values", args: [first.map((x) => -Math.abs(x) - 1), ...rest] });
    }
    return presets;
  }
  if (typeof first === "string") {
    return [
      { label: "Empty string", args: ["", ...rest] },
      { label: "Single character", args: [first[0] || "a", ...rest] },
    ];
  }
  if (typeof first === "number") {
    return [
      { label: "Zero", args: [0, ...rest] },
      { label: "Negative", args: [-Math.abs(first) - 1, ...rest] },
      { label: "Large boundary", args: [(first || 100) * 1000, ...rest] },
    ];
  }
  return [];
}

// Explain-your-thinking: optional interview-prep step, entirely client-side
// (no backend persistence -- it's ungraded scratch reflection, not
// something that needs a schema migration to be useful). Write a plan
// before running, then compare it against the problem's real pattern (and,
// if already computed, the actual estimated complexity) after.
function ExplainThinking({ problem, plan, setPlan, open, setOpen, hasRun, complexity }) {
  return (
    <div className="explain-thinking">
      <button className="explain-thinking-toggle" onClick={() => setOpen((o) => !o)}>
        {open ? "▾" : "▸"} &#127908; Explain your thinking (optional)
      </button>
      {open && (
        <>
          <p className="viz-caption">
            Before you run: briefly describe the approach you're planning, like you would out loud in
            an interview. After you run, compare it with the problem's actual pattern.
          </p>
          <textarea
            className="predict-input"
            rows={2}
            placeholder="e.g. I'll use a hash map to track values I've already seen..."
            value={plan}
            onChange={(e) => setPlan(e.target.value)}
          />
          {hasRun && (
            <div className="pattern-reveal">
              <p>
                <strong>What you planned:</strong> {plan.trim() || "(nothing written)"}
              </p>
              <p>
                <strong>This problem's pattern:</strong> {problem.pattern}
              </p>
              {complexity?.structural?.structural_time_estimate && (
                <p className="muted small">
                  Your code's estimated complexity: {complexity.structural.structural_time_estimate}
                  {problem.expected_time_complexity && <> (target: {problem.expected_time_complexity})</>}
                </p>
              )}
            </div>
          )}
        </>
      )}
    </div>
  );
}

function PatternPractice({ problem, open, setOpen, guess, setGuess, revealed, setRevealed }) {
  return (
    <div className="pattern-practice">
      <button className="pattern-practice-toggle" onClick={() => setOpen((o) => !o)}>
        {open ? "▾" : "▸"} 🧩 Pattern practice (optional) — what approach do you think applies?
      </button>
      {open && (
        <>
          <div className="pattern-choice-grid">
            {PATTERN_CATEGORIES.map((cat) => (
              <button
                key={cat}
                className={`pattern-choice ${guess === cat ? "pattern-choice-selected" : ""}`}
                onClick={() => setGuess(cat)}
                disabled={revealed}
              >
                {cat}
              </button>
            ))}
          </div>
          {!revealed ? (
            <button className="chip chip-small" onClick={() => setRevealed(true)} disabled={!guess}>
              Reveal the actual pattern
            </button>
          ) : (
            <div className="pattern-reveal">
              <p>
                <strong>Your guess:</strong> {guess}
              </p>
              <p>
                <strong>Actual pattern:</strong> {problem.pattern}
              </p>
              {problem.optimal_approach && (
                <p className="muted small">{problem.optimal_approach}</p>
              )}
            </div>
          )}
        </>
      )}
    </div>
  );
}

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
  const [traceFocusEnd, setTraceFocusEnd] = useState(false);

  const [patternOpen, setPatternOpen] = useState(false);
  const [patternGuess, setPatternGuess] = useState(null);
  const [patternRevealed, setPatternRevealed] = useState(false);

  const [thinkingOpen, setThinkingOpen] = useState(false);
  const [approachPlan, setApproachPlan] = useState("");

  const [customArgsText, setCustomArgsText] = useState("[]");
  const [customResult, setCustomResult] = useState(null);
  const [customRunning, setCustomRunning] = useState(false);
  const [customArgsError, setCustomArgsError] = useState(null);

  const [attempts, setAttempts] = useState([]);
  const [loadingAttempts, setLoadingAttempts] = useState(false);
  const [expandedAttemptId, setExpandedAttemptId] = useState(null);
  const [complexityCompare, setComplexityCompare] = useState(null);
  const [comparingAttemptId, setComparingAttemptId] = useState(null);

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
    setTraceFocusEnd(false);
    setPatternOpen(false);
    setPatternGuess(null);
    setPatternRevealed(false);
    setThinkingOpen(false);
    setApproachPlan("");
    setCustomArgsText("[]");
    setCustomResult(null);
    setCustomArgsError(null);
    setAttempts([]);
    setExpandedAttemptId(null);
    setComplexityCompare(null);
    setAttemptFeedback(null);
    setStartedAt(Date.now());
    setTab("Tests");
    fetchProblem(slug)
      .then((p) => {
        setProblem(p);
        setCode(p.starter_code || "");
        if (p.visible_test_cases?.[0]) {
          setCustomArgsText(JSON.stringify(p.visible_test_cases[0].args));
        }
      })
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, [slug]);

  // History tab loads lazily -- attempt data isn't needed until the learner
  // actually asks to see their journey on this problem.
  useEffect(() => {
    if (tab !== "History" || !slug) return;
    setLoadingAttempts(true);
    fetchAttempts(slug)
      .then((result) => setAttempts(result.attempts || []))
      .catch((e) => setError(e.message))
      .finally(() => setLoadingAttempts(false));
  }, [tab, slug]);

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
      if (tab === "History") {
        fetchAttempts(slug)
          .then((result) => setAttempts(result.attempts || []))
          .catch(() => {});
      }
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

  async function runTrace(overrideTestCaseIndex) {
    const idx = overrideTestCaseIndex ?? traceTestCaseIndex;
    setTracing(true);
    setTrace(null);
    try {
      // Traces against a real test case (not the bare code as-typed) --
      // starter code is just a function signature with no call to it, so
      // without this the trace would never actually enter the function
      // body. See client.js's traceProblem / app.py's /trace docstring.
      const result = await traceProblem(slug, code, idx);
      setTrace(result);
    } catch (e) {
      setError(e.message);
    } finally {
      setTracing(false);
    }
  }

  // Failure analysis's "inspect this in the trace" jump: switch to the
  // Trace tab, point it at the SAME test case that failed (run's results
  // and visible_test_cases share index ordering -- both queries are
  // ORDER BY id server-side), trace it, and land on the final step so the
  // actual return value is immediately visible next to what was expected.
  function inspectFailureInTrace(testCaseIndex) {
    setTab("Trace");
    setTraceTestCaseIndex(testCaseIndex);
    setTraceFocusEnd(true);
    runTrace(testCaseIndex);
  }

  // Custom test-case playground: parses the learner's own JSON args and
  // runs them ungraded (see backend app.py's run_custom) -- this is
  // exploration, not scoring, so there's no pass/fail here, just output.
  function parsePlaygroundArgs() {
    try {
      const parsed = JSON.parse(customArgsText);
      if (!Array.isArray(parsed)) throw new Error("must be a JSON array, e.g. [[1,2,3], 5]");
      setCustomArgsError(null);
      return parsed;
    } catch (e) {
      setCustomArgsError(`Couldn't parse that as JSON: ${e.message}`);
      return null;
    }
  }

  async function runPlayground() {
    const args = parsePlaygroundArgs();
    if (args === null) return;
    setCustomRunning(true);
    setCustomResult(null);
    try {
      const result = await runProblemCustom(slug, code, args);
      setCustomResult(result);
    } catch (e) {
      setError(e.message);
    } finally {
      setCustomRunning(false);
    }
  }

  // Enter or modify test input -> Run -> Trace -> Inspect: this is the
  // "Trace" half of the playground loop, reusing the same TraceViewer
  // (with focusEnd so the final step is immediately visible) rather than
  // building a second trace UI.
  async function tracePlaygroundInput() {
    const args = parsePlaygroundArgs();
    if (args === null) return;
    setTab("Trace");
    setTraceFocusEnd(true);
    setTracing(true);
    setTrace(null);
    try {
      const result = await traceProblemCustom(slug, code, args);
      setTrace(result);
    } catch (e) {
      setError(e.message);
    } finally {
      setTracing(false);
    }
  }

  // Compare approaches / complexity: re-estimates complexity for an OLD
  // submission's code side by side with the current editor content, so the
  // learner can see concretely how their solution improved (or didn't).
  // Reuses the existing complexity-estimate endpoint against stored
  // attempt code -- no new estimation logic, no overclaiming beyond what
  // that endpoint already carefully scopes as structural vs empirical.
  async function compareAttemptComplexity(attempt) {
    setComparingAttemptId(attempt.id);
    setComplexityCompare(null);
    try {
      const [past, current] = await Promise.all([
        fetchComplexityEstimate(slug, attempt.submitted_code),
        fetchComplexityEstimate(slug, code),
      ]);
      setComplexityCompare({ attemptId: attempt.id, past, current });
    } catch (e) {
      setError(e.message);
    } finally {
      setComparingAttemptId(null);
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
          {problem.pattern && (
            <PatternPractice
              problem={problem}
              open={patternOpen}
              setOpen={setPatternOpen}
              guess={patternGuess}
              setGuess={setPatternGuess}
              revealed={patternRevealed}
              setRevealed={setPatternRevealed}
            />
          )}
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

          <ExplainThinking
            problem={problem}
            plan={approachPlan}
            setPlan={setApproachPlan}
            open={thinkingOpen}
            setOpen={setThinkingOpen}
            hasRun={!!runResult}
            complexity={complexity}
          />

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
                  <>
                    <FailureAnalysis runResult={runResult} onInspect={inspectFailureInTrace} />
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
                  </>
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
                <button
                  className="chip"
                  onClick={() => {
                    setTraceFocusEnd(false);
                    runTrace();
                  }}
                  disabled={tracing}
                >
                  {tracing ? "Tracing..." : "Trace my code"}
                </button>
                {trace?.traced_test_case_args && (
                  <p className="muted small">
                    Traced with: <code>{problem.function_signature.match(/def\s+(\w+)/)?.[1]}(
                    {trace.traced_test_case_args.map((a) => JSON.stringify(a)).join(", ")})</code>
                  </p>
                )}
                <TraceViewer trace={trace} problem={problem} focusEnd={traceFocusEnd} />
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

            {tab === "Playground" && (
              <div>
                <p className="muted small">
                  Enter your own test input -- ungraded. See exactly what your code returns (or the
                  error it raises) for input you choose, then trace it if you want to inspect further.
                </p>
                <label className="trace-testcase-picker">Args (JSON array matching the function's parameters):</label>
                <textarea
                  className="predict-input"
                  rows={2}
                  value={customArgsText}
                  onChange={(e) => setCustomArgsText(e.target.value)}
                />
                {problem.visible_test_cases?.[0]?.args && buildEdgeCasePresets(problem.visible_test_cases[0].args).length > 0 && (
                  <div className="playground-presets">
                    <span className="muted small">Quick edge cases: </span>
                    {buildEdgeCasePresets(problem.visible_test_cases[0].args).map((preset) => (
                      <button
                        key={preset.label}
                        className="chip chip-small"
                        onClick={() => setCustomArgsText(JSON.stringify(preset.args))}
                      >
                        {preset.label}
                      </button>
                    ))}
                  </div>
                )}
                {customArgsError && <p className="error">{customArgsError}</p>}
                <div className="hint-buttons">
                  <button className="chip" onClick={runPlayground} disabled={customRunning}>
                    {customRunning ? "Running..." : "Run with this input"}
                  </button>
                  {customResult && !customResult.crashed && !customResult.error && (
                    <button className="chip" onClick={tracePlaygroundInput} disabled={tracing}>
                      Trace this input &rarr;
                    </button>
                  )}
                </div>
                {customResult && (
                  <div className="playground-result">
                    {customResult.crashed || customResult.error ? (
                      <p className="error">
                        {customResult.error || "Your code crashed before producing a result for this input."}
                      </p>
                    ) : (
                      <p>
                        <strong>Output:</strong> <code>{JSON.stringify(customResult.actual)}</code>
                      </p>
                    )}
                  </div>
                )}
              </div>
            )}

            {tab === "History" && (
              <div>
                {loadingAttempts && <p className="muted">Loading your attempts...</p>}
                {!loadingAttempts && attempts.length === 0 && (
                  <p className="muted">No attempts logged yet -- run your code once to start your history here.</p>
                )}
                {attempts.length > 0 && (
                  <ol className="attempt-history">
                    {attempts.map((a, i) => (
                      <li key={a.id} className={a.passed ? "attempt-pass" : "attempt-fail"}>
                        <div className="attempt-history-row">
                          <span>
                            <strong>Attempt {i + 1}</strong> &middot; {a.passed ? "Accepted" : "Not passing"}
                          </span>
                          <span className="muted small">{a.created_at}</span>
                        </div>
                        <div className="attempt-history-row muted small">
                          {a.hints_used > 0 && <span>{a.hints_used} hint(s) used</span>}
                          {a.solution_revealed ? <span>solution revealed</span> : null}
                          {a.time_taken_seconds != null && <span>{a.time_taken_seconds}s</span>}
                          {a.is_independent ? <span className="success">independent solve</span> : null}
                        </div>
                        <div className="hint-buttons">
                          <button
                            className="chip chip-small"
                            onClick={() => setExpandedAttemptId(expandedAttemptId === a.id ? null : a.id)}
                          >
                            {expandedAttemptId === a.id ? "Hide code" : "View code"}
                          </button>
                          <button
                            className="chip chip-small"
                            onClick={() => compareAttemptComplexity(a)}
                            disabled={comparingAttemptId === a.id}
                          >
                            {comparingAttemptId === a.id ? "Comparing..." : "Compare complexity to current code"}
                          </button>
                        </div>
                        {expandedAttemptId === a.id && <pre className="code-block">{a.submitted_code}</pre>}
                        {complexityCompare?.attemptId === a.id && (
                          <div className="failure-analysis" style={{ marginTop: "0.5rem" }}>
                            <h4 style={{ color: "#7ec8ff" }}>Complexity comparison</h4>
                            <div className="failure-analysis-row">
                              <span>
                                <strong>This attempt:</strong>{" "}
                                {complexityCompare.past.structural?.structural_time_estimate ||
                                  complexityCompare.past.structural?.error}
                              </span>
                              <span>
                                <strong>Current code:</strong>{" "}
                                {complexityCompare.current.structural?.structural_time_estimate ||
                                  complexityCompare.current.structural?.error}
                              </span>
                            </div>
                            <p className="muted small">
                              Structural estimates from each version's code shape -- see the Complexity tab for
                              empirical timing on either version.
                            </p>
                          </div>
                        )}
                      </li>
                    ))}
                  </ol>
                )}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
