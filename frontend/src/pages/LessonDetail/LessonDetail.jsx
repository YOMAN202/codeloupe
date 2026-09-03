import { useEffect, useState } from "react";
import { useParams, useNavigate, Link } from "react-router-dom";
import { fetchLesson, setLessonProgress } from "../../api/client";
import { StatusBadge, DifficultyBadge } from "../../components/Badges/Badges";
import MultilineText, { renderInlineCode, splitNonEmptyLines } from "../../components/MultilineText/MultilineText";

// A prediction question is usually one plain sentence ("How many times
// does `for i in range(5):` run?"), but a few (e.g. Day 1) are a short
// question followed by a blank line and a small code snippet to read
// before answering. Splitting on the first blank line and rendering the
// second part as a real code block (same treatment as the Example
// section) avoids collapsing that snippet into one run-on sentence,
// which is what a plain <p> did with embedded newlines.
function splitPredictionQuestion(text) {
  const parts = text.split(/\n\s*\n/);
  if (parts.length < 2) return { question: text, code: null };
  return { question: parts[0], code: parts.slice(1).join("\n\n") };
}

export default function LessonDetail() {
  const { day } = useParams();
  const navigate = useNavigate();
  const [lesson, setLesson] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showAnswer, setShowAnswer] = useState(false);
  const [savingStatus, setSavingStatus] = useState(false);

  function load() {
    setLoading(true);
    setShowAnswer(false);
    fetchLesson(day)
      .then(setLesson)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }

  useEffect(load, [day]);

  async function updateStatus(status) {
    setSavingStatus(true);
    try {
      await setLessonProgress(day, status);
      setLesson((prev) => ({ ...prev, status }));
    } catch (e) {
      setError(e.message);
    } finally {
      setSavingStatus(false);
    }
  }

  if (loading) return <p className="muted">Loading lesson...</p>;
  if (error) return <p className="error">{error}</p>;
  if (!lesson) return null;

  return (
    <div className="page">
      <div className="page-header">
        <div className="lesson-detail-title">
          <h2>
            Day {lesson.day}: {lesson.title}
          </h2>
          <StatusBadge status={lesson.status} />
        </div>
        <p className="muted">
          {lesson.block} &middot; ~{lesson.estimated_minutes} min
        </p>
      </div>

      <div className="status-controls">
        {["in_progress", "completed", "known", "skipped"].map((s) => {
          // "known" is the one status with a real toggle-off: clicking it
          // again while already known should remove the known status
          // rather than just re-saving the same value (see updateStatus's
          // targetStatus below). The other three stay one-way "mark X"
          // buttons, same as before -- "not_started" has no dedicated
          // button and is reached only by unmarking known, exactly like
          // it always could be reached via the status API.
          const isActive = lesson.status === s;
          const isKnownToggle = s === "known";
          const label = isKnownToggle && isActive ? "Unmark known" : `Mark ${s.replace("_", " ")}`;
          const targetStatus = isKnownToggle && isActive ? "not_started" : s;
          return (
            <button
              key={s}
              className={`chip ${isActive ? "chip-active" : ""}`}
              disabled={savingStatus}
              aria-pressed={isKnownToggle ? isActive : undefined}
              onClick={() => updateStatus(targetStatus)}
            >
              {label}
            </button>
          );
        })}
      </div>

      {lesson.recommended_prerequisites?.length > 0 && (
        <div className="prereq-box">
          <strong>Recommended background</strong> (not required &mdash; jump in anytime):
          <ul>
            {lesson.recommended_prerequisites.map((p) => (
              <li key={p.block}>
                {p.block}: {p.days_done}/{p.days_total} days done
                {p.satisfied ? " (all set)" : ""}
              </li>
            ))}
          </ul>
        </div>
      )}

      {lesson.concept_lessons?.length > 0 && (
        <div className="callout-row">
          {lesson.concept_lessons.map((c) => (
            <Link key={c.slug} to={`/learn/${c.slug}`} className="callout callout-next">
              <strong>Learn: {c.title}</strong>
              <span>{c.summary}</span>
            </Link>
          ))}
        </div>
      )}

      <section className="lesson-section">
        <h3>Concept</h3>
        <MultilineText text={lesson.concept_markdown} />
        {lesson.python_concepts && (
          <p className="muted">
            <strong>Python:</strong> {lesson.python_concepts}
          </p>
        )}
        {lesson.dsa_concepts && (
          <p className="muted">
            <strong>DSA:</strong> {lesson.dsa_concepts}
          </p>
        )}
      </section>

      {lesson.example_code && (
        <section className="lesson-section">
          <h3>Example</h3>
          <pre className="code-block">{lesson.example_code}</pre>
        </section>
      )}

      {lesson.prediction_question && (() => {
        const { question, code } = splitPredictionQuestion(lesson.prediction_question);
        return (
          <section className="lesson-section">
            <h3>Predict before you run it</h3>
            <p>{renderInlineCode(question)}</p>
            {code && <pre className="code-block">{code}</pre>}
            {!showAnswer ? (
              <button className="chip" onClick={() => setShowAnswer(true)}>
                Reveal answer
              </button>
            ) : (
              <p className="prediction-answer">{renderInlineCode(lesson.prediction_answer)}</p>
            )}
          </section>
        );
      })()}

      <section className="lesson-section">
        <h3>Exercises</h3>
        {/* Each drill is its own list item with its own "Try in Scratchpad"
            link carrying &exercise=<index> -- exercises_markdown has no
            problem row / stable id of its own (see schema.sql), so the
            0-based position among this day's non-empty lines is the
            identifier, computed the SAME way MultilineText itself splits
            this field for display (splitNonEmptyLines), never a second
            parse of it. Scratchpad re-derives the exact line from that
            index against the canonical lesson.exercises_markdown it
            already fetches -- the text itself is never duplicated here. */}
        <ol className="exercise-list">
          {splitNonEmptyLines(lesson.exercises_markdown).map((line, i) => (
            <li key={i} className="exercise-list-item">
              <span className="exercise-list-item-text">{renderInlineCode(line)}</span>
              <Link to={`/scratchpad?from=lesson&day=${day}&exercise=${i}`} className="exercise-try-link">
                Try in Scratchpad
              </Link>
            </li>
          ))}
        </ol>
      </section>

      {lesson.must_explain && (
        <section className="lesson-section">
          <h3>You should be able to explain</h3>
          <MultilineText text={lesson.must_explain} />
        </section>
      )}

      {lesson.common_mistakes && (
        <section className="lesson-section">
          <h3>Common mistakes</h3>
          <MultilineText text={lesson.common_mistakes} />
        </section>
      )}

      {lesson.problems?.length > 0 && (
        <section className="lesson-section">
          <h3>Practice problems for this day</h3>
          <div className="problem-list">
            {lesson.problems.map((p) => (
              <Link key={p.slug} to={`/problems/${p.slug}`} className="problem-row">
                <span>{p.title}</span>
                <DifficultyBadge difficulty={p.difficulty} />
              </Link>
            ))}
          </div>
        </section>
      )}

      <div className="lesson-nav-buttons">
        <button className="chip" onClick={() => navigate(`/lessons/${Number(day) - 1}`)} disabled={Number(day) <= 1}>
          &larr; Day {Number(day) - 1}
        </button>
        <button className="chip" onClick={() => navigate(`/lessons/${Number(day) + 1}`)} disabled={Number(day) >= 50}>
          Day {Number(day) + 1} &rarr;
        </button>
      </div>
    </div>
  );
}
