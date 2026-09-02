import { useCallback, useEffect, useRef, useState } from "react";
import { useParams, Link } from "react-router-dom";
import CodeEditor from "../../components/Editor/CodeEditor";
import TraceViewer from "../../components/TraceViewer/TraceViewer";
import SpecializedVisualization from "../../components/Visualizers/Visualizers";
import { DifficultyBadge, PriorityBadge, TierBadge } from "../../components/Badges/Badges";
import MultilineText, { renderInlineCode } from "../../components/MultilineText/MultilineText";
import { describeMismatch } from "../../utils/compare";
import { formatValue } from "../../utils/format";
import {
  fetchProblem,
  fetchHint,
  fetchHintFromCode,
  fetchSolution,
  runProblem,
  fetchComplexityEstimate,
  fetchApproachComparison,
  logAttempt,
  traceProblem,
  traceProblemCustom,
  runProblemCustom,
  fetchAttempts,
  updateMistake,
  fetchRevisionStatus,
  addToRevision,
  removeFromRevision,
} from "../../api/client";

// Ordered to match the actual learning loop: write code -> run tests ->
// (if something fails) trace it -> (if still stuck) hints -> the more
// analytical/optional tabs after. Was previously Tests/Hints/Trace/... --
// reordered so Trace sits directly next to Tests, since it's the natural
// next step after seeing a failure, not something to reach past Hints for.
const TABS = ["Tests", "Trace", "Hints", "Complexity", "Approaches", "Playground", "History"];

// Live preview tuning. 700ms (not the snappier end of the suggested
// 500-1000ms range) is deliberate: the dev backend (backend/app.py's
// `app.run(...)`) is single-threaded by default, so every live-trace
// request blocks "Run tests", the manual Trace tab, and everything else in
// the app for its duration -- skewing the debounce longer keeps the
// average request rate lower on that single worker. LIVE_TRACE_TIMEOUT_SECONDS
// is passed to the backend, which clamps it to at most its own default (see
// app.py's trace_problem) -- it can only make live requests time out
// FASTER than a manual trace, never slower, so a snippet that hangs mid-
// typing gives up in ~3s instead of tying up the server for the full 8s
// default on every debounce tick.
const LIVE_TRACE_DEBOUNCE_MS = 700;
const LIVE_TRACE_TIMEOUT_SECONDS = 3;

// Mirrors logic/mistakes.py's MISTAKE_CATEGORIES exactly -- the backend is
// the source of truth and rejects anything outside this list, so this
// stays a fixed, hand-kept copy rather than a runtime fetch (the list
// changes about as often as the app's core taxonomy does, i.e. rarely).
const MISTAKE_CATEGORIES = [
  "Off-by-one errors", "Missed edge cases", "Incorrect pointer movement",
  "Incorrect base case", "Incorrect data-structure usage", "Pattern recognition difficulty",
  "Logic errors", "Complexity misunderstanding", "Recursion issues", "Boundary-condition mistakes",
];

// Builds the classifier's evidence payload directly from a /run response
// the caller already has -- no extra request. See logic/mistakes.py for
// exactly how each field is (or deliberately isn't) turned into a category.
function buildFailureContext(runResult) {
  if (!runResult) return null;
  if (runResult.crashed) {
    return { crashed: true, first_failure: null, num_failed: null, num_total: null };
  }
  const results = runResult.results || [];
  const failing = results.filter((r) => !r.passed);
  if (failing.length === 0) return null;
  const first = failing[0];
  return {
    crashed: false,
    first_failure: { args: first.args, expected: first.expected, actual: first.actual, error: first.error },
    num_failed: failing.length,
    num_total: results.length,
  };
}

// Mistake-journal review prompt: shown once per failed run, right after
// the classifier (or lack of one) has an answer. Never presents a guess
// as fact -- a category is always paired with its confidence tag, and an
// unclassified result says so plainly rather than picking something.
function MistakeSuggestion({ suggestion, onConfirm, onOverride, pickerOpen, setPickerOpen, savedLabel }) {
  if (!suggestion) return null;
  return (
    <div className="mistake-suggestion">
      <h4>Possible mistake noticed</h4>
      {suggestion.category ? (
        <p>
          <strong>{suggestion.category}</strong>{" "}
          <span className="viz-type-tag">{suggestion.confidence.replace(/_/g, " ")}</span>
        </p>
      ) : (
        <p className="muted small">Couldn't confidently classify this one -- that's fine, not every mistake fits a category.</p>
      )}
      {suggestion.evidence && <p className="muted small">{suggestion.evidence}</p>}
      {savedLabel ? (
        <p className="success small">{savedLabel}</p>
      ) : !pickerOpen ? (
        <div className="hint-buttons">
          {suggestion.category && (
            <button className="chip chip-small" onClick={onConfirm}>
              Yes, that's it
            </button>
          )}
          <button className="chip chip-small" onClick={() => setPickerOpen(true)}>
            {suggestion.category ? "Not quite -- let me pick" : "Classify it myself"}
          </button>
        </div>
      ) : (
        <div className="pattern-choice-grid">
          {MISTAKE_CATEGORIES.map((c) => (
            <button key={c} className="pattern-choice" onClick={() => onOverride(c)}>
              {c}
            </button>
          ))}
        </div>
      )}
    </div>
  );
}

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
          <strong>Input:</strong> <code>{formatValue(firstFailure.args)}</code>
        </span>
      </div>
      <div className="failure-analysis-row">
        <span>
          <strong>Expected:</strong> <code>{formatValue(firstFailure.expected)}</code>
        </span>
        <span>
          <strong>Got:</strong>{" "}
          <code>{firstFailure.error ? firstFailure.error : formatValue(firstFailure.actual)}</code>
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
        {open ? "▾" : "▸"} Explain your thinking (optional)
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
        {open ? "▾" : "▸"} Pattern practice (optional) — what approach do you think applies?
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
                <p className="muted small">{renderInlineCode(problem.optimal_approach)}</p>
              )}
            </div>
          )}
        </>
      )}
    </div>
  );
}

// Approach comparison: one card per candidate (my code / optimal reference
// / brute-force baseline). Every number here is labeled with where it came
// from -- see logic/approach_comparison.py's module docstring for exactly
// what structural vs empirical_existing_tests vs growth_curve each mean.
// Deliberately never renders the reference code itself unless `code` is
// present on the candidate (i.e. the learner explicitly revealed it).
function ApproachCard({ title, candidate, narrative, onTrace, tracing }) {
  if (!candidate) return null;
  const growth = candidate.growth_curve;
  return (
    <div className="approach-card">
      <h4>{title}</h4>
      {narrative && <p className="muted small">{narrative}</p>}
      <p>
        <strong>Structural estimate:</strong>{" "}
        {candidate.structural?.structural_time_estimate || candidate.structural?.error}
      </p>
      {candidate.operation_count?.count != null && (
        <p className="muted small">
          {candidate.operation_count.count} trace step{candidate.operation_count.count === 1 ? "" : "s"}
          {candidate.operation_count.truncated ? " (capped -- real count is higher)" : ""} on one
          representative input
        </p>
      )}
      {candidate.empirical_existing_tests?.points?.length > 0 && (
        <>
          <p className="muted small approach-metric-label">On this problem's own test cases:</p>
          <ul className="approach-metric-list">
            {candidate.empirical_existing_tests.points.map((pt, i) => (
              <li key={i}>
                size {pt.input_size ?? "n/a"}: {(pt.seconds * 1000).toFixed(3)} ms
                {pt.peak_kb != null && `, ${Math.round(pt.peak_kb / 1024)} MB peak`}
              </li>
            ))}
          </ul>
        </>
      )}
      {growth?.points?.length > 0 && (
        <>
          <p className="muted small approach-metric-label">Growth across synthetic input sizes:</p>
          <ul className="approach-metric-list">
            {growth.points.map((pt, i) => (
              <li key={i}>
                n={pt.n}:{" "}
                {pt.seconds != null
                  ? `${(pt.seconds * 1000).toFixed(1)} ms${pt.peak_kb != null ? `, ${Math.round(pt.peak_kb / 1024)} MB peak` : ""}`
                  : pt.timed_out
                  ? "timed out (became impractical at this size)"
                  : "could not measure"}
              </li>
            ))}
          </ul>
          <p className="muted small">{growth.note}</p>
        </>
      )}
      {candidate.code && (
        <>
          <pre className="code-block">{candidate.code}</pre>
          {onTrace && (
            <button className="chip chip-small" onClick={onTrace} disabled={tracing}>
              Trace this approach &rarr;
            </button>
          )}
        </>
      )}
    </div>
  );
}

// ============================== Live preview ==============================
// A compact, always-updating snapshot next to the editor -- write code, see
// the effect without clicking "Trace my code". Deliberately NOT a second
// tracing system: it calls the exact same traceProblem() endpoint and
// renders the exact same SpecializedVisualization component the full Trace
// tab uses (see below), just with its own request lifecycle and a trimmed
// status strip instead of the full step/scrub/predict chrome.

// Best-effort "does this look mid-edit" check -- NOT a real Python parser,
// just enough to skip the network round trip for the extremely common
// "still typing this line" case (a dangling operator, an unterminated
// string, an unclosed bracket) before it ever reaches the backend. The
// backend's own compile() inside tracer.py stays the actual authority on
// syntax validity -- anything this heuristic lets through still gets
// checked for real and comes back as a normal, non-scary "syntax_error"
// status if it's still broken in some way this can't detect (e.g. a
// keyword typo). False negatives here are fine and expected; a false
// POSITIVE (blocking code that's actually valid) is the failure mode this
// is written to avoid, so it only flags the unambiguous cases.
function looksMidEdit(code) {
  const trimmed = code.trim();
  if (!trimmed) return true;
  const lastLine = code.replace(/\s+$/, "").split("\n").pop().trim();
  if (lastLine.endsWith("\\")) return true; // explicit line continuation
  // A trailing operator/comma/colon/dot on the last line -- "left =",
  // "if x:", "nums[i]," etc typed but not yet finished. The lookbehind
  // avoids flagging a completed "==" comparison as if it were a dangling
  // "=" assignment.
  if (
    /(?<!=)[=+\-*/%&|^~,:.]$/.test(lastLine) ||
    /[^=]<$/.test(lastLine) ||
    /[^=]>$/.test(lastLine) ||
    /[=!<>]=$/.test(lastLine) // dangling "==", "!=", "<=", ">=" with nothing after
  ) {
    return true;
  }

  // Best-effort bracket/quote balance, skipping over string contents so a
  // paren/bracket character inside a string literal doesn't miscount.
  // Doesn't special-case triple-quoted strings correctly (each `"""` is
  // just three toggles) -- an unclosed triple-quoted docstring can
  // therefore read as "unterminated string" here, which is usually true
  // anyway while it's still being typed.
  //
  // Also skips `#`-to-end-of-line comments (when not already inside a
  // string) the same way a real Python tokenizer would -- otherwise an
  // apostrophe in an ordinary English comment ("you're", "don't", "it's")
  // gets misread as opening a string literal that never closes, and
  // perfectly valid, untouched starter code ends up permanently flagged as
  // mid-edit. A `#` that appears INSIDE an already-open string is not a
  // comment start at all, so this must only take effect while `inString`
  // is falsy -- which the `if (inString) {...continue;}` branch below
  // already guarantees by handling in-string characters first.
  const stack = [];
  let inString = null;
  let escaped = false;
  let inComment = false;
  const pairs = { ")": "(", "]": "[", "}": "{" };
  for (const ch of code) {
    if (ch === "\n") {
      inComment = false;
      if (!inString) continue;
    }
    if (inString) {
      if (escaped) {
        escaped = false;
      } else if (ch === "\\") {
        escaped = true;
      } else if (ch === inString) {
        inString = null;
      }
      continue;
    }
    if (inComment) continue;
    if (ch === "#") {
      inComment = true;
    } else if (ch === '"' || ch === "'") {
      inString = ch;
    } else if (ch === "(" || ch === "[" || ch === "{") {
      stack.push(ch);
    } else if (ch === ")" || ch === "]" || ch === "}") {
      if (stack.pop() !== pairs[ch]) return true; // mismatched bracket
    }
  }
  if (inString || stack.length > 0) return true;

  return false;
}

const LIVE_STATUS_COPY = {
  empty: "Write some code to see a live preview.",
  invalid: "Waiting for valid code…",
  tracing: "Tracing…",
  error: "Live preview unavailable right now.",
};

// The trace's very last step is almost always a "return" event (either the
// learner's function returning, or the module-level completion synthesized
// by tracer.py -- see TraceViewer.jsx's isSyntheticLine) -- and "return"
// steps never carry a `locals` snapshot at all (see tracer.py's tracer
// function: only "call"/"line" events do). Defaulting the live preview to
// the literal last index would therefore show an empty/no-locals state on
// almost every successful trace. Show the last "line" step instead -- the
// last point where real computed state actually exists -- falling back to
// the true last step only for the degenerate case of a trace with no line
// events at all.
function lastMeaningfulIndex(steps) {
  for (let i = steps.length - 1; i >= 0; i--) {
    if (steps[i].event === "line") return i;
  }
  return steps.length - 1;
}

function LivePreviewPanel({ problem, liveStatus, liveTrace, onOpenFullTrace, onCollapse }) {
  const steps = liveTrace?.steps || [];
  const lastIndex = lastMeaningfulIndex(steps);
  // BUGFIX: this used to also require `liveStatus === "ready"`, which meant
  // the panel showed nothing at all (not even the dimmed last-good preview
  // the comments above promise) for the entire "tracing" window on every
  // single retrace, and for the "invalid" window whenever the learner paused
  // mid-edit -- confirmed by instrumenting a real run: the preview visibly
  // vanished to "Tracing..." and reappeared a moment later on every edit.
  // Whether there's anything to show is really just "do we have trace data",
  // independent of what the CURRENT in-flight status is -- see fireLiveTrace,
  // which only ever nulls out liveTrace for "empty" code and for a hard
  // error, never while a new request is merely pending/in flight.
  const hasRenderableTrace = steps.length > 0;
  // "stale" = the visible data is not guaranteed to match the code in the
  // editor RIGHT NOW (a newer trace is in flight, or the current code looks
  // incomplete/invalid) -- as opposed to "ready", where it's the exact
  // result of tracing exactly what's in the editor.
  const isStale = liveStatus === "tracing" || liveStatus === "invalid";

  // Reuses TraceViewer's own outcome labels/tone so the two surfaces agree
  // on what e.g. "truncated" means -- not duplicated wording invented here.
  const outcomeLabel = {
    completed: null, // the normal case -- no extra label needed
    runtime_error: "Runtime error",
    truncated: "Still running -- step limit reached",
  }[liveTrace?.status];

  return (
    <div id="live-preview-panel" className={`live-preview-panel${hasRenderableTrace ? "" : " live-preview-panel-empty"}`}>
      <div className="live-preview-header">
        <span className="live-preview-title">Live preview</span>
        {isStale && <span className="live-preview-status-dot" data-status={liveStatus} aria-hidden="true" />}
        {hasRenderableTrace && (
          <button className="chip chip-small" onClick={onOpenFullTrace}>
            Open in full Trace &rarr;
          </button>
        )}
        {/* Focus-editor mode: hides this whole panel so Monaco can take the
            row's full width. A persistent "Show Live Preview" control (see
            .live-preview-collapsed-bar in ProblemWorkspace's main render)
            takes this panel's place in the layout while hidden, so
            restoring it is never more than one obvious click away. */}
        <button
          type="button"
          className="chip chip-small live-preview-hide-btn"
          onClick={onCollapse}
          aria-expanded="true"
          aria-controls="live-preview-panel"
          aria-label="Hide Live Preview"
          title="Hide Live Preview"
        >
          Hide
        </button>
      </div>

      {/* Everything below the header lives in its own scroll container
          (App.css's .live-preview-scroll) so the header stays fixed at the
          top while THIS grows to fill the panel's stretched height (which
          now matches the editor's, via the row's align-items: stretch) --
          internal scrolling only ever kicks in here, and only as a
          fallback for a frame whose content genuinely doesn't fit even
          that full height. */}
      <div className="live-preview-scroll">
        {!hasRenderableTrace && (
          <p className="muted small live-preview-message">
            {LIVE_STATUS_COPY[liveStatus] || LIVE_STATUS_COPY.empty}
          </p>
        )}

        {hasRenderableTrace && (
          <div className={isStale ? "live-preview-dim" : ""}>
            {isStale && (
              <p className="muted small live-preview-stale-note">
                {liveStatus === "invalid"
                  ? "Showing your last successful preview -- the current code isn't valid yet."
                  : "Updating for your latest edit..."}
              </p>
            )}
            {outcomeLabel && <p className="muted small live-preview-outcome">{outcomeLabel}</p>}
            <LivePreviewBody problem={problem} steps={steps} index={lastIndex} />
          </div>
        )}
      </div>
    </div>
  );
}

// Mirrors TraceViewer.jsx's own layout: a compact locals list stays
// visible ABOVE the structural visualization rather than being replaced by
// it (TraceViewer's comment: "The generic locals table below always stays
// visible"). Matters beyond consistency -- a scalar running total like
// `best = float("inf")` in a two-pointer/sliding-window solution isn't
// part of the array/pointer structure SpecializedVisualization draws, so
// without this it would never be visible in Live Preview at all, even
// though it's plainly shown in full Trace. Falls back to just the locals
// list (or an empty-state note) when nothing structural is detected for
// this step (e.g. a problem topic/shape this app doesn't have a dedicated
// view for yet) -- SpecializedVisualization returns null in that case by
// design (see Visualizers.jsx).
function LivePreviewBody({ problem, steps, index }) {
  // Called as a plain function, NOT written as `<SpecializedVisualization
  // .../>`, deliberately: JSX would always hand back a truthy element
  // descriptor regardless of what the component eventually renders, so
  // there'd be no way to tell "it rendered nothing" apart from "it
  // rendered something" in order to decide whether to show the fallback
  // below. SpecializedVisualization has no hooks anywhere in its tree
  // (Visualizers.jsx is a pure presentational component tree), so calling
  // it directly to read its real return value up front is safe.
  const viz = SpecializedVisualization({ problem, steps, index });

  const locals = steps[index]?.locals || {};
  const entries = Object.entries(locals);
  const localsList =
    entries.length > 0 ? (
      <ul className="live-preview-locals">
        {entries.map(([k, v]) => (
          <li key={k}>
            <code>{k}</code> = <code>{formatValue(v)}</code>
          </li>
        ))}
      </ul>
    ) : viz == null ? (
      <p className="muted small">No local variables at this point yet.</p>
    ) : null;

  if (viz == null) return localsList;
  return (
    <>
      {localsList}
      {viz}
    </>
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

  // "Focus editor" mode: hides the Live Preview column so Monaco can use
  // the full row width. Deliberately PLAIN component state, not
  // localStorage like the sidebar's collapse (see App.jsx's
  // SIDEBAR_COLLAPSED_KEY) -- hiding Live Preview is meant to be a
  // temporary, session-scoped focus action, not a saved long-term
  // preference: every fresh page load/refresh should always introduce the
  // learner to Live Preview again, visible by default. Because
  // ProblemWorkspace stays mounted (React Router doesn't remount it) when
  // navigating between problems via the app's own links/nav -- only the
  // :slug param changes -- this still "remains hidden for the current
  // active workspace session" across problem switches for free, with zero
  // extra wiring; only an actual full page reload resets it, which is
  // exactly the reset trigger asked for.
  const [livePreviewCollapsed, setLivePreviewCollapsed] = useState(false);

  const [tab, setTab] = useState("Tests");

  const [hintsShown, setHintsShown] = useState([]); // rungs revealed, e.g. [1, 2]
  const [codeHint, setCodeHint] = useState(null);
  const [loadingCodeHint, setLoadingCodeHint] = useState(false);
  const [solution, setSolution] = useState(null);
  const [solutionRevealed, setSolutionRevealed] = useState(false);

  const [complexity, setComplexity] = useState(null);
  const [loadingComplexity, setLoadingComplexity] = useState(false);

  const [approachCompare, setApproachCompare] = useState(null);
  const [comparingApproaches, setComparingApproaches] = useState(false);

  const [trace, setTrace] = useState(null);
  const [tracing, setTracing] = useState(false);
  const [traceTestCaseIndex, setTraceTestCaseIndex] = useState(0);
  const [traceFocusEnd, setTraceFocusEnd] = useState(false);
  const [tracedLabel, setTracedLabel] = useState("Your code");

  // Live preview -- entirely separate state from `trace`/`tracing` above on
  // purpose, so an automatic background trace fired while the learner is
  // typing can NEVER overwrite or interrupt a manual "Trace my code" /
  // Predict-mode session they have open on the Trace tab. liveStatus is one
  // of: "empty" | "invalid" | "tracing" | "ready" | "error".
  const [liveTrace, setLiveTrace] = useState(null);
  const [liveStatus, setLiveStatus] = useState("empty");
  // Refs (not state) for everything the debounce/request machinery needs to
  // read at fire time without re-running effects on every change, and for
  // values that must never trigger a re-render on their own:
  //  - codeRef/testCaseRef/slugRef: always the LATEST inputs, read at the
  //    moment a (possibly delayed/coalesced) request actually fires, so a
  //    request scheduled earlier never sends stale code.
  //  - liveRequestIdRef: bumped on every fire; a response is only applied
  //    if its id is still the current one, so a slow, superseded response
  //    can never clobber a newer one ("stale response protection").
  //  - liveInFlightRef/livePendingRef: at most one live-trace request in
  //    flight at a time; a debounce tick that lands while one is still
  //    running just marks "pending" and re-fires (with fresh refs) the
  //    moment the in-flight one finishes, instead of firing concurrently.
  const codeRef = useRef(code);
  codeRef.current = code;
  const testCaseRef = useRef(traceTestCaseIndex);
  testCaseRef.current = traceTestCaseIndex;
  const slugRef = useRef(slug);
  slugRef.current = slug;
  const liveRequestIdRef = useRef(0);
  const liveInFlightRef = useRef(false);
  const livePendingRef = useRef(false);
  // "Open in full Trace" scroll handoff: `.workspace-right` (the column
  // holding the editor/Live Preview/tabs) is sticky-positioned, so once its
  // content is taller than the viewport -- which the Trace tab's content
  // usually is -- switching to it with setTab alone doesn't bring it into
  // view; the learner still has to scroll the page down by hand to find it.
  // tabRowRef marks the scroll target (the tab bar itself, not just the
  // trace content below it, so the highlighted "Trace" chip stays visible
  // as context). traceScrollToken is bumped on every click of that one
  // button (see openLiveTraceInFullView) and nothing else, so the effect
  // below re-fires on every click -- including a second click after
  // re-editing and re-tracing, where `tab` alone never changes away from
  // "Trace" and so couldn't retrigger an effect keyed on it.
  const tabRowRef = useRef(null);
  const [traceScrollToken, setTraceScrollToken] = useState(0);
  const liveDebounceRef = useRef(null);

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
  const [mistakeSuggestion, setMistakeSuggestion] = useState(null);
  const [mistakePickerOpen, setMistakePickerOpen] = useState(false);
  const [mistakeSavedLabel, setMistakeSavedLabel] = useState(null);

  // Manual "Add to revision" -- independent of runResult/attempts above,
  // since it reflects revision_schedule.source, not anything about the
  // learner's code. null while unloaded/loading (button stays disabled).
  const [revisionStatus, setRevisionStatus] = useState(null);
  const [revisionBusy, setRevisionBusy] = useState(false);

  useEffect(() => {
    setLoading(true);
    setRunResult(null);
    setHintsShown([]);
    setCodeHint(null);
    setSolution(null);
    setSolutionRevealed(false);
    setComplexity(null);
    setApproachCompare(null);
    setComparingApproaches(false);
    setTrace(null);
    setTraceTestCaseIndex(0);
    setTraceFocusEnd(false);
    setTracedLabel("Your code");
    // Invalidate rather than wait for it to time out on its own -- any
    // still-in-flight live-trace response for the PREVIOUS problem is now
    // guaranteed stale and will be dropped when it arrives (see the id
    // check in fireLiveTrace), and clearing liveInFlightRef lets the new
    // problem's own live preview start immediately instead of waiting
    // behind it.
    if (liveDebounceRef.current) clearTimeout(liveDebounceRef.current);
    liveRequestIdRef.current += 1;
    liveInFlightRef.current = false;
    livePendingRef.current = false;
    setLiveTrace(null);
    setLiveStatus("empty");
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
    setMistakeSuggestion(null);
    setMistakePickerOpen(false);
    setMistakeSavedLabel(null);
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

  // Loaded eagerly (not lazily like History below) since the header button
  // needs to know its state as soon as it renders. A fetch failure just
  // leaves the button disabled/unlabeled rather than surfacing a page-level
  // error -- this is a secondary affordance, not core problem data.
  useEffect(() => {
    if (!slug) return;
    setRevisionStatus(null);
    fetchRevisionStatus(slug)
      .then(setRevisionStatus)
      .catch(() => {});
  }, [slug]);

  async function handleToggleRevision() {
    setRevisionBusy(true);
    try {
      const updated = revisionStatus?.in_revision
        ? await removeFromRevision(slug)
        : await addToRevision(slug);
      setRevisionStatus(updated);
    } catch (e) {
      setError(e.message);
    } finally {
      setRevisionBusy(false);
    }
  }

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
    setMistakeSuggestion(null);
    setMistakePickerOpen(false);
    setMistakeSavedLabel(null);
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
        failure_context: result.all_passed ? null : buildFailureContext(result),
      });
      setAttemptFeedback(attempt);
      if (attempt.mistake) setMistakeSuggestion(attempt.mistake);
      if (tab === "History") {
        fetchAttempts(slug)
          .then((result) => setAttempts(result.attempts || []))
          .catch(() => {});
      }
      // A logged attempt (pass or fail) hands a manually-added problem's
      // revision row back to the automatic ladder server-side (source
      // reverts to 'auto' -- see app.py's log_attempt), so re-fetch here
      // to flip the header button back to "Add to revision" right away.
      fetchRevisionStatus(slug).then(setRevisionStatus).catch(() => {});
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
    setTracedLabel("Your code");
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

  // Fires one live-preview trace using whatever code/test-case/slug are
  // CURRENT at the moment it actually runs (via the refs above), never
  // whatever they were when this particular call was scheduled. Reads
  // nothing from component state/closures directly for that reason, so it
  // never needs re-creating -- stable across renders (empty dep array).
  const fireLiveTrace = useCallback(async () => {
    if (liveInFlightRef.current) {
      // Already tracing one version of the code; don't fire a second,
      // overlapping request against this single-worker dev backend. Once
      // the in-flight one finishes, its `finally` block below re-fires
      // this same function, which will pick up whatever is newest in the
      // refs at that point -- so this coalesces any number of edits that
      // happened while we were waiting into exactly one follow-up request.
      livePendingRef.current = true;
      return;
    }
    liveInFlightRef.current = true;
    const myRequestId = ++liveRequestIdRef.current;
    const myCode = codeRef.current;
    const myTestCaseIndex = testCaseRef.current;
    const mySlug = slugRef.current;
    setLiveStatus("tracing");
    try {
      const result = await traceProblem(mySlug, myCode, myTestCaseIndex, { timeoutSeconds: LIVE_TRACE_TIMEOUT_SECONDS });
      if (myRequestId !== liveRequestIdRef.current) return; // superseded -- drop it
      if (result.status === "syntax_error") {
        // Our client-side heuristic let this through (it only catches the
        // unambiguous cases), but the backend's real compile() says it's
        // still not valid Python yet -- same non-scary "still typing"
        // treatment as the cases the heuristic DOES catch, not an error.
        // Deliberately does NOT clear liveTrace (it used to) -- the last
        // successful preview should stay visible and dimmed here too, same
        // as the client-heuristic "invalid" path just below, rather than
        // vanishing the moment the backend independently confirms invalid
        // syntax. See LivePreviewPanel's isStale/live-preview-stale-note.
        setLiveStatus("invalid");
      } else {
        setLiveTrace(result);
        setLiveStatus("ready");
      }
    } catch {
      // Network/HTTP failure only -- a bad-but-parseable response is
      // handled in the `try` above, and this deliberately never touches
      // the page-level `error` state (that one blanks the ENTIRE
      // workspace -- see the `if (error) return ...` guard near the top of
      // this component -- which would be a wildly disproportionate
      // reaction to a single background live-preview request failing).
      if (myRequestId !== liveRequestIdRef.current) return;
      setLiveTrace(null);
      setLiveStatus("error");
    } finally {
      liveInFlightRef.current = false;
      if (livePendingRef.current) {
        livePendingRef.current = false;
        fireLiveTrace();
      }
    }
  }, []);

  // Debounced trigger: every keystroke lands here, cancels whatever wait
  // was already pending, and (if the code doesn't look obviously mid-edit)
  // starts a fresh LIVE_TRACE_DEBOUNCE_MS wait before actually tracing.
  // Deliberately does NOT clear liveTrace on every keystroke -- the last
  // successful preview stays on screen (dimmed while a new one is pending/
  // tracing) instead of flashing empty on every character typed.
  useEffect(() => {
    if (liveDebounceRef.current) clearTimeout(liveDebounceRef.current);
    if (!code.trim()) {
      setLiveStatus("empty");
      setLiveTrace(null);
      return undefined;
    }
    if (looksMidEdit(code)) {
      setLiveStatus("invalid");
      return undefined;
    }
    liveDebounceRef.current = setTimeout(fireLiveTrace, LIVE_TRACE_DEBOUNCE_MS);
    return () => clearTimeout(liveDebounceRef.current);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [code, traceTestCaseIndex, slug, fireLiveTrace]);

  // "Open in full Trace": the live preview already has a perfectly good
  // trace of this exact code -- hand it straight to the manual `trace`
  // state (starting from step 0, like a fresh "Trace my code" click would)
  // rather than making the learner re-request the same thing. This is a
  // one-time, explicitly user-initiated handoff, not a live sync -- once
  // open on the Trace tab it behaves exactly like any other manual trace
  // and further typing won't touch it.
  function openLiveTraceInFullView() {
    if (!liveTrace) return;
    setTracedLabel("Your code");
    setTraceFocusEnd(false);
    setTrace(liveTrace);
    setTab("Trace");
    setTraceScrollToken((n) => n + 1);
  }

  // Runs the actual scroll for openLiveTraceInFullView above, once React has
  // committed the "Trace" tab's content to the DOM (an effect, rather than
  // scrolling inline in the handler, specifically so it runs after that
  // commit rather than against the still-on-the-previous-tab DOM). Skips the
  // very first render (token starts at 0, and this effect's own setup would
  // otherwise fire it on mount) via the ref guard below. `prefers-reduced-
  // motion` disables the smooth animation, matching how the rest of the app
  // already treats that setting elsewhere.
  const skippedInitialScrollRef = useRef(false);
  useEffect(() => {
    if (!skippedInitialScrollRef.current) {
      skippedInitialScrollRef.current = true;
      return;
    }
    const reduceMotion = window.matchMedia?.("(prefers-reduced-motion: reduce)").matches;
    tabRowRef.current?.scrollIntoView({ behavior: reduceMotion ? "auto" : "smooth", block: "start" });
  }, [traceScrollToken]);

  // Approach comparison: numbers first (reveal_code=false), reference code
  // only on an explicit second click -- same two-stage gate as the Hints
  // tab's solution reveal, and revealing either candidate's code marks the
  // attempt assisted via the same solutionRevealed flag (see app.py's
  // approach_comparison docstring for why).
  async function compareApproaches() {
    setComparingApproaches(true);
    try {
      const result = await fetchApproachComparison(slug, code, false);
      setApproachCompare(result);
    } catch (e) {
      setError(e.message);
    } finally {
      setComparingApproaches(false);
    }
  }

  async function revealApproachCode() {
    setComparingApproaches(true);
    try {
      const result = await fetchApproachComparison(slug, code, true);
      setApproachCompare(result);
      setSolutionRevealed(true);
    } catch (e) {
      setError(e.message);
    } finally {
      setComparingApproaches(false);
    }
  }

  // "Trace this approach": reuses the exact same trace endpoint/viewer as
  // "Trace my code", just pointed at a revealed reference implementation
  // instead of the editor's contents -- no new visualization code, just a
  // label so it's never ambiguous whose execution is on screen.
  async function traceApproachCode(label, referenceCode) {
    setTab("Trace");
    setTraceFocusEnd(true);
    setTracedLabel(label);
    setTracing(true);
    setTrace(null);
    try {
      const sampleArgs = problem.visible_test_cases?.[0]?.args || [];
      const result = await traceProblemCustom(slug, referenceCode, sampleArgs);
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
    setTracedLabel("Your code");
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

  // Mistake-journal review: the learner either confirms the classifier's
  // guess as-is, or picks their own category (also how an unclassified
  // mistake gets one at all). Either way the human's answer is final --
  // see app.py's update_mistake, which never re-runs the heuristic.
  async function confirmMistake() {
    if (!mistakeSuggestion) return;
    try {
      await updateMistake(mistakeSuggestion.id, { confirm: true });
      setMistakeSavedLabel("Saved to your mistake journal.");
    } catch (e) {
      setError(e.message);
    }
  }

  async function overrideMistake(category) {
    if (!mistakeSuggestion) return;
    try {
      await updateMistake(mistakeSuggestion.id, { category });
      setMistakeSavedLabel(`Saved as "${category}".`);
      setMistakePickerOpen(false);
    } catch (e) {
      setError(e.message);
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
            <button
              className={`chip chip-small${revisionStatus?.in_revision ? " chip-active" : ""}`}
              onClick={handleToggleRevision}
              disabled={revisionBusy || !revisionStatus}
              title={
                revisionStatus?.in_revision
                  ? "Remove this problem from your revision queue"
                  : "Add this problem to your revision queue, due today"
              }
            >
              {revisionStatus?.in_revision ? "Remove from revision" : "Add to revision"}
            </button>
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

          {problem.concept_lessons?.length > 0 && (
            <div className="callout-row">
              {problem.concept_lessons.map((c) => (
                <Link key={c.slug} to={`/learn/${c.slug}`} className="callout callout-next">
                  <strong>{c.kind === "pattern" ? "Pattern" : "Concept"} to know: {c.title}</strong>
                  <span>{c.summary}</span>
                </Link>
              ))}
            </div>
          )}

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
                    <code>{formatValue(tc.args)}</code> &rarr;{" "}
                    <code>{formatValue(tc.expected)}</code>
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
          <div className={`editor-live-row${livePreviewCollapsed ? " live-preview-is-collapsed" : ""}`}>
            <div className="editor-live-column">
              {livePreviewCollapsed && (
                // Lives INSIDE the editor column's own vertical stack, not
                // as a sibling column in the row -- a sibling wide enough
                // to read as a real button (long label, real padding) ends
                // up costing nearly as much row width as the Live Preview
                // panel it replaced, which was tried and measured: the
                // editor only gained ~9px. Putting it here instead means
                // the row has nothing else in it when collapsed, so the
                // editor column's flex: 1 1 auto (below) claims the ENTIRE
                // freed width -- while the button still sits right above
                // Monaco's top-right corner, i.e. still "near the right
                // edge... where Live Preview previously existed", and is
                // still always visible (a static bar, not tied to scroll
                // position).
                <div className="live-preview-collapsed-bar">
                  <button
                    type="button"
                    className="live-preview-restore-btn"
                    onClick={() => setLivePreviewCollapsed(false)}
                    aria-expanded="false"
                    aria-controls="live-preview-panel"
                    aria-label="Show Live Preview"
                    title="Show Live Preview"
                  >
                    <span aria-hidden="true">&#9664;</span> Show Live Preview
                  </button>
                </div>
              )}
              <CodeEditor value={code} onChange={setCode} />
              <button className="run-button" onClick={handleRun} disabled={running}>
                {running ? "Running..." : "Run tests"}
              </button>
            </div>
            {!livePreviewCollapsed && (
              <LivePreviewPanel
                problem={problem}
                liveStatus={liveStatus}
                liveTrace={liveTrace}
                onOpenFullTrace={openLiveTraceInFullView}
                onCollapse={() => setLivePreviewCollapsed(true)}
              />
            )}
          </div>

          {attemptFeedback && (
            <p className={attemptFeedback.is_independent ? "success" : "warning"}>
              {attemptFeedback.result === "failed"
                ? "Not passing yet -- keep going."
                : attemptFeedback.is_independent
                ? `Solved independently. Next review: ${attemptFeedback.next_due_date}.`
                : `Solved with help (hints/solution used). Next review: ${attemptFeedback.next_due_date}.`}
            </p>
          )}

          <MistakeSuggestion
            suggestion={mistakeSuggestion}
            onConfirm={confirmMistake}
            onOverride={overrideMistake}
            pickerOpen={mistakePickerOpen}
            setPickerOpen={setMistakePickerOpen}
            savedLabel={mistakeSavedLabel}
          />

          <ExplainThinking
            problem={problem}
            plan={approachPlan}
            setPlan={setApproachPlan}
            open={thinkingOpen}
            setOpen={setThinkingOpen}
            hasRun={!!runResult}
            complexity={complexity}
          />

          <div className="tab-row" ref={tabRowRef}>
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
                          <code>input: {formatValue(r.args)}</code>
                          {!r.passed && (
                            <>
                              <code>expected: {formatValue(r.expected)}</code>
                              <code>got: {r.error ? r.error : formatValue(r.actual)}</code>
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
                        <strong>Hint {rung}:</strong> {renderInlineCode(codeHint?.[`static-${rung}`])}
                      </p>
                    )
                )}
                {codeHint?.fromCode && (
                  <p className="hint-text">
                    <strong>About your code:</strong> {renderInlineCode(codeHint.fromCode)}
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
                      <strong>Brute force:</strong> {renderInlineCode(solution.brute_force_approach)}
                    </p>
                    <p>
                      <strong>Optimal:</strong> {renderInlineCode(solution.optimal_approach)}
                    </p>
                    <pre className="code-block">{solution.solution_code}</pre>
                  </div>
                )}
              </div>
            )}

            {tab === "Trace" && (
              <div>
                {!runResult ? (
                  <p className="muted small">
                    Tracing works on any code, even before you run tests -- but it's most useful once
                    you've seen which case actually fails: run your tests first, then come back here
                    (or use "Inspect this case in the Trace tab" on the Tests tab) to step through
                    exactly what your code did on that input.
                  </p>
                ) : (
                  !runResult.all_passed && (
                    <p className="muted small">
                      Tracing this test case will show you exactly what your code did, line by line --
                      the fastest way to find where your logic diverges from what's expected.
                    </p>
                  )
                )}
                {problem.visible_test_cases?.length > 1 && (
                  <label className="trace-testcase-picker">
                    Trace against:{" "}
                    <select
                      value={traceTestCaseIndex}
                      onChange={(e) => setTraceTestCaseIndex(Number(e.target.value))}
                    >
                      {problem.visible_test_cases.map((tc, i) => (
                        <option key={i} value={i}>
                          test case {i + 1}{tc.label ? ` (${tc.label})` : ""}: {formatValue(tc.args)}
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
                {trace && tracedLabel !== "Your code" && (
                  <p className="muted small">
                    <strong>Showing trace of: {tracedLabel}</strong>
                  </p>
                )}
                {trace?.traced_test_case_args && (
                  <p className="muted small">
                    Traced with: <code>{problem.function_signature.match(/def\s+(\w+)/)?.[1]}(
                    {trace.traced_test_case_args.map((a) => formatValue(a)).join(", ")})</code>
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

            {tab === "Approaches" && (
              <div>
                {!runResult ? (
                  <p className="muted">
                    Run your code at least once first -- approach comparison works best once you've
                    actually attempted the problem, even if that attempt is a naive first pass.
                  </p>
                ) : (
                  <>
                    <p className="muted small">
                      Compares your code's own numbers against a reference approach, so you can see
                      *why* one is better, not just that it is. Reference code stays hidden until you
                      explicitly reveal it below -- the numbers alone are the point.
                    </p>
                    <div className="hint-buttons">
                      <button className="chip" onClick={compareApproaches} disabled={comparingApproaches}>
                        {comparingApproaches ? "Comparing..." : "Compare my approach"}
                      </button>
                      {approachCompare && !approachCompare.optimal_reference?.code && (
                        <button className="chip chip-danger" onClick={revealApproachCode} disabled={comparingApproaches}>
                          Show reference code (last resort)
                        </button>
                      )}
                    </div>
                    {approachCompare?.optimal_reference?.code && (
                      <p className="warning">
                        This attempt will be tagged assisted, not independent, per the spaced-revision
                        system.
                      </p>
                    )}
                    {approachCompare && (
                      <>
                        <p className="muted small approach-progression">
                          {approachCompare.has_baseline
                            ? "Naive baseline → your approach → optimized reference"
                            : "No curated naive baseline exists for this problem -- comparing your approach directly against the optimized reference."}
                          {" "}Target: {approachCompare.expected_time_complexity} time,{" "}
                          {approachCompare.expected_space_complexity} space.
                        </p>
                        <div className="approach-columns">
                          {approachCompare.has_baseline && (
                            <ApproachCard
                              title="Naive baseline"
                              candidate={approachCompare.brute_force_baseline}
                              narrative={approachCompare.brute_force_baseline?.narrative}
                              onTrace={
                                approachCompare.brute_force_baseline?.code
                                  ? () => traceApproachCode("Naive baseline", approachCompare.brute_force_baseline.code)
                                  : null
                              }
                              tracing={tracing}
                            />
                          )}
                          <ApproachCard
                            title="Your approach"
                            candidate={approachCompare.my_approach}
                          />
                          <ApproachCard
                            title="Optimized reference"
                            candidate={approachCompare.optimal_reference}
                            narrative={approachCompare.optimal_reference?.narrative}
                            onTrace={
                              approachCompare.optimal_reference?.code
                                ? () => traceApproachCode("Optimized reference", approachCompare.optimal_reference.code)
                                : null
                            }
                            tracing={tracing}
                          />
                        </div>
                      </>
                    )}
                  </>
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
                        <strong>Output:</strong> <code>{formatValue(customResult.actual)}</code>
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
                        {a.mistake && (
                          <div className="attempt-history-row muted small">
                            <span>
                              Mistake: <strong>{a.mistake.category || "Unclassified"}</strong>{" "}
                              <span className="viz-type-tag">{a.mistake.confidence.replace(/_/g, " ")}</span>
                            </span>
                          </div>
                        )}
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
                          <div className="failure-analysis complexity-compare-card">
                            <h4>Complexity comparison</h4>
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
                              empirical timing on either version, or the Approaches tab to compare your current
                              code against a reference approach instead of a past attempt.
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
