import { useEffect, useState } from "react";
import { useParams, useNavigate, Link } from "react-router-dom";
import { fetchLesson, setLessonProgress } from "../../api/client";
import { StatusBadge, DifficultyBadge } from "../../components/Badges/Badges";
import MultilineText, { renderInlineCode } from "../../components/MultilineText/MultilineText";

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
        {["in_progress", "completed", "known", "skipped"].map((s) => (
          <button
            key={s}
            className={`chip ${lesson.status === s ? "chip-active" : ""}`}
            disabled={savingStatus}
            onClick={() => updateStatus(s)}
          >
            Mark {s.replace("_", " ")}
          </button>
        ))}
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
        <MultilineText text={lesson.exercises_markdown} />
        <p className="muted">
          Try these in the <Link to={`/scratchpad?from=lesson&day=${day}`}>scratchpad</Link> first.
        </p>
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
