import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { fetchLessons, fetchProgress } from "../../api/client";
import { StatusBadge } from "../../components/Badges/Badges";

export default function CurriculumMap() {
  const [lessons, setLessons] = useState([]);
  const [progress, setProgress] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [filter, setFilter] = useState("all");

  function load() {
    setLoading(true);
    Promise.all([fetchLessons(), fetchProgress()])
      .then(([l, p]) => {
        setLessons(l);
        setProgress(p);
      })
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }

  useEffect(load, []);

  if (loading) return <p className="muted">Loading curriculum...</p>;
  if (error) return <p className="error">{error}</p>;

  const blocks = [];
  for (const lesson of lessons) {
    let block = blocks.find((b) => b.name === lesson.block);
    if (!block) {
      block = { name: lesson.block, lessons: [] };
      blocks.push(block);
    }
    block.lessons.push(lesson);
  }

  const visible = (status) => filter === "all" || status === filter;

  return (
    <div className="page">
      <div className="page-header">
        <h2>Curriculum</h2>
        <p className="muted">
          A recommended path, not a locked course &mdash; jump to any day, mark what you
          already know, and come back to anything anytime.
        </p>
      </div>

      {progress && (progress.recommended_next_lesson || progress.resume_lesson) && (
        <div className="callout-row">
          {progress.resume_lesson && (
            <Link to={`/lessons/${progress.resume_lesson.day}`} className="callout callout-resume">
              <strong>Resume</strong>
              <span>
                Day {progress.resume_lesson.day}: {progress.resume_lesson.title}
              </span>
            </Link>
          )}
          {progress.recommended_next_lesson && (
            <Link
              to={`/lessons/${progress.recommended_next_lesson.day}`}
              className="callout callout-next"
            >
              <strong>Recommended next</strong>
              <span>
                Day {progress.recommended_next_lesson.day}: {progress.recommended_next_lesson.title}
              </span>
            </Link>
          )}
          {progress.problems_due_for_revision?.length > 0 && (
            <Link to="/dashboard" className="callout callout-revision">
              <strong>{progress.problems_due_for_revision.length} due for revision</strong>
              <span>See your dashboard</span>
            </Link>
          )}
        </div>
      )}

      <div className="filter-row">
        <label>Show:</label>
        {["all", "not_started", "in_progress", "completed", "known", "skipped"].map((s) => (
          <button
            key={s}
            className={`chip ${filter === s ? "chip-active" : ""}`}
            onClick={() => setFilter(s)}
          >
            {s === "all" ? "All" : s.replace("_", " ")}
          </button>
        ))}
      </div>

      {blocks.map((block) => (
        <section key={block.name} className="block-section">
          <h3>{block.name}</h3>
          <div className="lesson-grid">
            {block.lessons
              .filter((l) => visible(l.status))
              .map((l) => (
                <Link key={l.day} to={`/lessons/${l.day}`} className={`lesson-card status-${l.status}`}>
                  <div className="lesson-card-top">
                    <span className="day-number">Day {l.day}</span>
                    <StatusBadge status={l.status} />
                  </div>
                  <div className="lesson-card-title">{l.title}</div>
                  <div className="muted small">{l.estimated_minutes} min</div>
                </Link>
              ))}
          </div>
        </section>
      ))}
    </div>
  );
}
