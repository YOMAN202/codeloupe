import { useEffect, useState } from "react";
import { useParams, useNavigate, Link } from "react-router-dom";
import { fetchLesson, setLessonProgress } from "../../api/client";
import { StatusBadge, DifficultyBadge } from "../../components/Badges/Badges";
import MultilineText from "../../components/MultilineText/MultilineText";

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

      {lesson.prediction_question && (
        <section className="lesson-section">
          <h3>Predict before you run it</h3>
          <p>{lesson.prediction_question}</p>
          {!showAnswer ? (
            <button className="chip" onClick={() => setShowAnswer(true)}>
              Reveal answer
            </button>
          ) : (
            <p className="prediction-answer">{lesson.prediction_answer}</p>
          )}
        </section>
      )}

      <section className="lesson-section">
        <h3>Exercises</h3>
        <MultilineText text={lesson.exercises_markdown} />
        <p className="muted">
          Try these in the <Link to="/scratchpad">scratchpad</Link> first.
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
        <button className="chip" onClick={() => navigate(`/lessons/${Number(day) + 1}`)} disabled={Number(day) >= 45}>
          Day {Number(day) + 1} &rarr;
        </button>
      </div>
    </div>
  );
}
