import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { fetchProgress, fetchPracticeSession, removeFromRevision } from "../../api/client";

const SESSION_KIND_LABEL = {
  revision: "Revision",
  recurring_mistake: "Recurring mistake",
  revisit_lesson: "Revisit lesson",
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

  // Revision-removal flow -- deliberately the same shape as the Mistake
  // Journal's remove flow (removingId/deletingId/deleteError/deletedNotice
  // there; -Slug here since revision rows are keyed by problem slug, not a
  // numeric id) rather than a new pattern, per the instruction to reuse
  // existing removal logic/UX instead of inventing a second inconsistent
  // one. `removingSlug` is which item (if any) currently shows the inline
  // confirm prompt in place of its normal row; `deletingSlug` is which one
  // has a request actually in flight.
  const [removingSlug, setRemovingSlug] = useState(null);
  const [deletingSlug, setDeletingSlug] = useState(null);
  const [deleteError, setDeleteError] = useState(null); // { slug, message }
  const [deletedNotice, setDeletedNotice] = useState(null);

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

  // This reuses the exact same backend call/route the Problem Workspace's
  // "Remove from revision" button already uses (DELETE
  // /api/problems/<slug>/revision -- see api/client.js and app.py's
  // remove_manual_revision) rather than adding a second endpoint. That
  // handler deletes the problem's revision_schedule row outright, whatever
  // its source ('auto' from the normal ladder or 'manual') -- it never
  // touches `attempts` or logged mistakes, and solving the problem again
  // later starts a brand new schedule the normal way via log_attempt. So
  // removing one item here can never disable future automatic revisions
  // for that problem, and never affects any other problem's schedule.
  async function handleRemoveRevision(item) {
    setDeletingSlug(item.slug);
    setDeleteError(null);
    try {
      await removeFromRevision(item.slug);
      setProgress((p) => ({
        ...p,
        problems_due_for_revision: p.problems_due_for_revision.filter((r) => r.slug !== item.slug),
      }));
      setRemovingSlug(null);
      setDeletedNotice(`Removed "${item.title}" from your revision schedule.`);
    } catch (e) {
      // Deliberately does NOT remove the item from `progress` -- a failed
      // removal must leave the schedule (and the UI) exactly as it was,
      // never a falsely-removed-looking state.
      setDeleteError({ slug: item.slug, message: e.message });
    } finally {
      setDeletingSlug(null);
    }
  }

  const dueCount = progress.problems_due_for_revision.length;

  return (
    <div className="page">
      <div className="page-header">
        <h2>Dashboard</h2>
        <p className="muted">
          Python DSA and coding-interview preparation -- where you actually stand, no points, no
          streak badges, just data.
        </p>
      </div>

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
        {/* Always rendered, even at zero -- a revision count that vanishes
            when it hits 0 reads as missing/broken data rather than "you're
            caught up". The empty-state modifier class swaps the usual amber
            (attention-needed) accent for a neutral one below, so "0 due"
            reads as calm and intentional instead of a false alarm.
            A plain button, not a <Link>, on purpose -- this app runs under
            HashRouter (see main.jsx), which already owns the URL's "#" for
            routing, so a Link/anchor pointing at "#due-for-revision" fights
            the router instead of scrolling. A button with its own handler
            sidesteps that entirely, and gets Enter/Space activation and
            the site's existing :focus-visible ring for free just by being
            a real <button>. */}
        <button
          type="button"
          className={`callout callout-revision callout-button${dueCount === 0 ? " callout-revision-empty" : ""}`}
          onClick={() =>
            document.getElementById("due-for-revision")?.scrollIntoView({ behavior: "smooth", block: "start" })
          }
        >
          <strong>{dueCount} due for revision</strong>
          <span>See below</span>
        </button>
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
                <Link to={item.kind === "revisit_lesson" ? `/learn/${item.slug}` : `/problems/${item.slug}`}>
                  {item.title}
                </Link>{" "}
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
              Core 50-Day Path: {progress.path_tier_progress.core.solved} /{" "}
              {progress.path_tier_progress.core.total} solved
            </h3>
            <span className="muted small">
              The recommended, job-ready foundation -- not a gate. Extended and Advanced below are
              optional add-ons that never count against it, and every problem stays open regardless
              of order or what you've solved so far.
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
              Extended: {progress.path_tier_progress.extended.solved} /{" "}
              {progress.path_tier_progress.extended.total}{" "}
              <span className="muted">(optional reinforcement)</span>
            </span>
            <span>
              Advanced: {progress.path_tier_progress.advanced.solved} /{" "}
              {progress.path_tier_progress.advanced.total}{" "}
              <span className="muted">(optional Hard/Complex challenges)</span>
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
          <h3>Curriculum progress</h3>
          <p className="muted small">The 50-day, day-by-day sequence.</p>
          <div className="lesson-status-bar">
            {(() => {
              // Derived from the actual counts returned, never a hardcoded
              // day total -- self-correcting if the curriculum's length
              // ever changes again (it already did once, 45 -> 50 days).
              const totalLessons = Object.values(progress.lesson_status_counts).reduce((a, b) => a + b, 0);
              return ["completed", "known", "in_progress", "skipped", "not_started"].map((s) => {
                const count = progress.lesson_status_counts[s] || 0;
                const width = pct(count, totalLessons);
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
              });
            })()}
          </div>
          <ul className="status-legend">
            {Object.entries(progress.lesson_status_counts).map(([s, c]) => (
              <li key={s}>
                <span className={`status-dot status-${s}`} /> {s.replace("_", " ")}: {c}
              </li>
            ))}
          </ul>
        </section>

        {progress.concept_lesson_status_counts && (
          <section className="lesson-section">
            <h3>Concept lessons</h3>
            <p className="muted small">
              The <Link to="/learn">Learn hub</Link>'s topic and pattern lessons -- a separate track
              from the curriculum above, not merged into it.
            </p>
            <div className="lesson-status-bar">
              {["completed", "known", "in_progress", "skipped", "not_started"].map((s) => {
                const count = progress.concept_lesson_status_counts[s] || 0;
                const total = Object.values(progress.concept_lesson_status_counts).reduce((a, b) => a + b, 0);
                const width = pct(count, total);
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
              {Object.entries(progress.concept_lesson_status_counts).map(([s, c]) => (
                <li key={s}>
                  <span className={`status-dot status-${s}`} /> {s.replace("_", " ")}: {c}
                </li>
              ))}
            </ul>
          </section>
        )}

        <section className="lesson-section" id="due-for-revision">
          <h3>Due for revision ({dueCount})</h3>
          {deletedNotice && <p className="success small">{deletedNotice}</p>}
          {dueCount === 0 ? (
            <p className="muted">0 due for revision -- you're caught up right now.</p>
          ) : (
            <ul className="problem-list">
              {progress.problems_due_for_revision.map((p) =>
                removingSlug === p.slug ? (
                  <li key={p.slug} className="mistake-remove-confirm">
                    <p className="mistake-remove-confirm-question">
                      Remove &ldquo;{p.title}&rdquo; from your revision schedule?
                    </p>
                    <p className="muted small">
                      This only removes this scheduled revision. It won't delete the problem,
                      your attempt history, or your solutions -- and future revisions can still be
                      scheduled for it automatically the next time you attempt it.
                    </p>
                    {deleteError?.slug === p.slug && <p className="error small">{deleteError.message}</p>}
                    <div className="hint-buttons">
                      <button
                        type="button"
                        className="chip chip-small"
                        onClick={() => setRemovingSlug(null)}
                        disabled={deletingSlug === p.slug}
                      >
                        Cancel
                      </button>
                      <button
                        type="button"
                        className="chip chip-small chip-danger"
                        onClick={() => handleRemoveRevision(p)}
                        disabled={deletingSlug === p.slug}
                      >
                        {deletingSlug === p.slug ? "Removing..." : "Remove from revision"}
                      </button>
                    </div>
                  </li>
                ) : (
                  <li key={p.slug}>
                    <div className="attempt-history-row">
                      <span>
                        <Link to={`/problems/${p.slug}`}>{p.title}</Link>{" "}
                        <span className="muted small">
                          ({p.topic}, due {p.next_due_date}, last: {p.last_result || "added manually"})
                        </span>
                      </span>
                      <span className="attempt-history-row-actions">
                        <button
                          type="button"
                          className="mistake-remove-btn"
                          onClick={() => {
                            setDeleteError(null);
                            setDeletedNotice(null);
                            setRemovingSlug(p.slug);
                          }}
                          aria-label={`Remove "${p.title}" from revision`}
                          title="Remove from revision"
                        >
                          <span aria-hidden="true">&#10005;</span>
                        </button>
                      </span>
                    </div>
                  </li>
                )
              )}
            </ul>
          )}
        </section>

        <section className="lesson-section">
          <h3>Weakest topics</h3>
          {progress.top_weaknesses.length === 0 ? (
            <p className="muted">No data yet -- this fills in once you've attempted a few problems.</p>
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
            <p className="muted">No data yet -- same as above, more specific once you've made a few attempts.</p>
          ) : (
            <ul>
              {progress.pattern_weaknesses.map((p) => (
                <li key={p.pattern_family}>
                  {p.pattern_family}: {p.mistake_count} mistake{p.mistake_count === 1 ? "" : "s"}
                  {p.top_category && <span className="muted small"> (most often: {p.top_category})</span>}
                  {p.related_lesson && (
                    <>
                      {" "}
                      <span className="muted small">
                        &middot; <Link to={`/learn/${p.related_lesson.slug}`}>revisit lesson</Link>
                      </span>
                    </>
                  )}
                </li>
              ))}
            </ul>
          )}
        </section>

        <section className="lesson-section">
          <h3>Strongest topics</h3>
          {progress.top_strengths.length === 0 ? (
            <p className="muted">No data yet -- this fills in as you solve problems independently.</p>
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
