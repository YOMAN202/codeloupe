import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { fetchProgress, fetchPracticeSession } from "../../api/client";
import { TIER_META } from "../../components/Badges/Badges";

const SESSION_KIND_LABEL = {
  revision: "Revision",
  recurring_mistake: "Recurring mistake",
  weak_pattern: "Weak pattern",
  weak_topic: "Weak topic",
  new: "New problem",
};

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
  const [session, setSession] = useState(null);

  useEffect(() => {
    fetchProgress()
      .then(setProgress)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
    fetchPracticeSession()
      .then(setSession)
      .catch(() => {});
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

      {session?.items?.length > 0 && (
        <section className="practice-session">
          <div className="practice-session-header">
            <h3>Today's session</h3>
            <span className="muted small">
              A suggested starting point, built from your own attempts and revision schedule -- never a
              required path. Jump to any lesson, topic, or problem you want instead.
            </span>
          </div>
          <ul className="problem-list">
            {session.items.map((item) => (
              <li key={item.slug}>
                <Link to={`/problems/${item.slug}`}>{item.title}</Link>{" "}
                <span className="viz-type-tag">{SESSION_KIND_LABEL[item.kind] || item.kind}</span>
                <br />
                <span className="muted small">{item.reason}</span>
              </li>
            ))}
          </ul>
        </section>
      )}

      {progress.path_tier_progress && (
        <section className="core-path-progress">
          <div className="core-path-progress-header">
            <h3>
              {TIER_META.core.emoji} Core 45-Day Path: {progress.path_tier_progress.core.solved} /{" "}
              {progress.path_tier_progress.core.total} solved
            </h3>
            <span className="muted small">
              This is the required, job-ready foundation. Extended and Advanced below are optional
              add-ons -- they never count against Core Path completion.
            </span>
          </div>
          <div className="core-path-progress-bar">
            <div
              className="core-path-progress-fill"
              style={{
                width: `${pct(progress.path_tier_progress.core.solved, progress.path_tier_progress.core.total)}%`,
              }}
            />
          </div>
          <div className="core-path-tier-mini-stats">
            <span>
              {TIER_META.extended.emoji} Extended: {progress.path_tier_progress.extended.solved} /{" "}
              {progress.path_tier_progress.extended.total}{" "}
              <span className="muted">(optional reinforcement)</span>
            </span>
            <span>
              {TIER_META.advanced.emoji} Advanced: {progress.path_tier_progress.advanced.solved} /{" "}
              {progress.path_tier_progress.advanced.total}{" "}
              <span className="muted">(optional Hard challenges)</span>
            </span>
          </div>
        </section>
      )}

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
          <h3>Weakest patterns</h3>
          <p className="muted small">
            Enhances the topic breakdown above with more specific technique-level detail, e.g. "fast/slow
            pointers" instead of just "linked lists". See the <Link to="/mistakes">Mistake Journal</Link>{" "}
            for individual entries.
          </p>
          {!progress.pattern_weaknesses || progress.pattern_weaknesses.length === 0 ? (
            <p className="muted">No data yet.</p>
          ) : (
            <ul>
              {progress.pattern_weaknesses.map((p) => (
                <li key={p.pattern_family}>
                  {p.pattern_family}: {p.mistake_count} mistake{p.mistake_count === 1 ? "" : "s"}
                  {p.top_category && <span className="muted small"> (most often: {p.top_category})</span>}
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
