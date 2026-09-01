import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { fetchProgress } from "../../api/client";

function Stat({ label, value }) {
  return (
    <div className="stat-box">
      <div className="stat-value">{value}</div>
      <div className="stat-label">{label}</div>
    </div>
  );
}

export default function Dashboard() {
  const [progress, setProgress] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchProgress()
      .then(setProgress)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <p className="muted">Loading dashboard...</p>;
  if (error) return <p className="error">{error}</p>;
  if (!progress) return null;

  const pct = (n, d) => (d ? Math.round((n / d) * 100) : 0);

  return (
    <div className="page">
      <div className="page-header">
        <h2>Dashboard</h2>
        <p className="muted">Where you actually stand -- no points, no streak badges, just data.</p>
      </div>

      <div className="stat-grid">
        <Stat label="Problems attempted" value={progress.total_problems_attempted} />
        <Stat label="Problems solved" value={progress.total_problems_solved} />
        <Stat
          label="Independent solve rate"
          value={
            progress.independent_solve_rate != null
              ? `${Math.round(progress.independent_solve_rate * 100)}%`
              : "--"
          }
        />
        <Stat label="Current streak" value={`${progress.current_streak_days} days`} />
        <Stat
          label="Avg solve time"
          value={
            progress.average_solve_time_seconds
              ? `${Math.round(progress.average_solve_time_seconds / 60)} min`
              : "--"
          }
        />
        <Stat
          label="Hint usage rate"
          value={progress.hint_usage_rate != null ? progress.hint_usage_rate.toFixed(2) : "--"}
        />
      </div>

      <div className="dashboard-columns">
        <section className="lesson-section">
          <h3>Lesson progress</h3>
          <div className="lesson-status-bar">
            {["completed", "known", "in_progress", "skipped", "not_started"].map((s) => {
              const count = progress.lesson_status_counts[s] || 0;
              const width = pct(count, 45);
              return (
                width > 0 && (
                  <div
                    key={s}
                    className={`lesson-status-segment status-${s}`}
                    style={{ width: `${width}%` }}
                    title={`${s}: ${count}`}
                  />
                )
              );
            })}
          </div>
          <ul className="status-legend">
            {Object.entries(progress.lesson_status_counts).map(([s, c]) => (
              <li key={s}>
                <span className={`status-dot status-${s}`} /> {s.replace("_", " ")}: {c}
              </li>
            ))}
          </ul>
        </section>

        <section className="lesson-section">
          <h3>Due for revision</h3>
          {progress.problems_due_for_revision.length === 0 ? (
            <p className="muted">Nothing due right now.</p>
          ) : (
            <ul className="problem-list">
              {progress.problems_due_for_revision.map((p) => (
                <li key={p.slug}>
                  <Link to={`/problems/${p.slug}`}>{p.title}</Link>{" "}
                  <span className="muted small">
                    ({p.topic}, due {p.next_due_date}, last: {p.last_result})
                  </span>
                </li>
              ))}
            </ul>
          )}
        </section>

        <section className="lesson-section">
          <h3>Weakest topics</h3>
          {progress.top_weaknesses.length === 0 ? (
            <p className="muted">No data yet.</p>
          ) : (
            <ul>
              {progress.top_weaknesses.map((t) => (
                <li key={t.topic}>
                  {t.topic}: {t.mistake_count} struggle{t.mistake_count === 1 ? "" : "s"}
                </li>
              ))}
            </ul>
          )}
        </section>

        <section className="lesson-section">
          <h3>Strongest topics</h3>
          {progress.top_strengths.length === 0 ? (
            <p className="muted">No data yet.</p>
          ) : (
            <ul>
              {progress.top_strengths.map((t) => (
                <li key={t.topic}>
                  {t.topic}: {t.independent_count} independent solve
                  {t.independent_count === 1 ? "" : "s"}
                </li>
              ))}
            </ul>
          )}
        </section>

        {progress.topics_mastered.length > 0 && (
          <section className="lesson-section">
            <h3>Mastered</h3>
            <p>{progress.topics_mastered.join(", ")}</p>
          </section>
        )}
      </div>
    </div>
  );
}
