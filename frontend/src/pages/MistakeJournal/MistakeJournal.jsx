import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { fetchMistakeJournal, deleteMistake } from "../../api/client";

const CONFIDENCE_LABEL = {
  observed_confirmed: "observed",
  likely_issue: "likely",
  user_confirmed: "you confirmed",
  manually_selected: "you classified",
};

// Recomputes the journal's category-count summary from whatever entries
// are left after a deletion -- rather than re-fetching the whole journal
// from the server, which would also work but means an extra round trip
// (and a brief flash of stale/loading state) for something this cheap to
// derive locally from data already in hand. Mirrors exactly what app.py's
// mistake_journal endpoint computes server-side.
function summarize(entries) {
  const categoryCounts = {};
  let unclassifiedCount = 0;
  for (const e of entries) {
    if (e.category) categoryCounts[e.category] = (categoryCounts[e.category] || 0) + 1;
    else unclassifiedCount += 1;
  }
  const recurringCategories = Object.entries(categoryCounts)
    .map(([category, count]) => ({ category, count }))
    .sort((a, b) => b.count - a.count);
  return { unclassifiedCount, recurringCategories };
}

// Answers "what kinds of mistakes do I repeatedly make?" honestly: real
// counts by category (including how many are still unclassified, shown
// as its own number rather than hidden), and every individual entry
// linking back to the exact problem/attempt it came from. See
// logic/mistakes.py for why the automated classifier never claims more
// than "likely" on its own.
export default function MistakeJournal() {
  const [journal, setJournal] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [filterCategory, setFilterCategory] = useState(null);

  // Removal flow -- entirely separate from the page-fatal `error` above
  // (that one blanks the whole page; a failed deletion should leave the
  // journal exactly as it was, with a small inline explanation instead).
  // `removingId` is which entry (if any) currently shows the inline
  // confirm prompt in place of its normal card content; `deletingId` is
  // which one has a request actually in flight.
  const [removingId, setRemovingId] = useState(null);
  const [deletingId, setDeletingId] = useState(null);
  const [deleteError, setDeleteError] = useState(null); // { id, message }
  const [deletedNotice, setDeletedNotice] = useState(null);

  useEffect(() => {
    fetchMistakeJournal()
      .then(setJournal)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <p className="muted">Loading your mistake journal...</p>;
  if (error) return <p className="error">{error}</p>;
  if (!journal) return null;

  async function handleDeleteMistake(entry) {
    setDeletingId(entry.id);
    setDeleteError(null);
    try {
      await deleteMistake(entry.id);
      const remaining = journal.entries.filter((e) => e.id !== entry.id);
      const { unclassifiedCount, recurringCategories } = summarize(remaining);
      setJournal({
        ...journal,
        entries: remaining,
        total_mistakes: remaining.length,
        unclassified_count: unclassifiedCount,
        recurring_categories: recurringCategories,
      });
      // If that was the last entry in the currently-filtered category,
      // drop the filter rather than leaving the page stuck showing "0
      // results" against a chip that no longer corresponds to anything.
      if (filterCategory && !remaining.some((e) => e.category === filterCategory)) {
        setFilterCategory(null);
      }
      setRemovingId(null);
      setDeletedNotice(`Removed the mistake for "${entry.title}".`);
    } catch (e) {
      // Deliberately does NOT remove the entry from `journal` -- a failed
      // delete must leave the learner's data (and the UI) exactly as it
      // was, never a falsely-deleted-looking state.
      setDeleteError({ id: entry.id, message: e.message });
    } finally {
      setDeletingId(null);
    }
  }

  const entries = filterCategory
    ? journal.entries.filter((e) => e.category === filterCategory)
    : journal.entries;

  return (
    <div className="page">
      <div className="page-header">
        <h2>Mistake journal</h2>
        <p className="muted">
          What kinds of mistakes you actually make, based on your own failed attempts -- not a
          diagnosis, a record. {journal.unclassified_count} of {journal.total_mistakes} mistakes
          couldn't be confidently classified, and that's shown honestly rather than guessed at.
        </p>
      </div>

      {deletedNotice && <p className="success small">{deletedNotice}</p>}

      {journal.total_mistakes === 0 ? (
        <div className="empty-state">
          No mistakes logged yet -- this fills in as you attempt problems.
        </div>
      ) : (
        <>
          <section className="lesson-section">
            <h3>Recurring categories</h3>
            <div className="playground-presets">
              {journal.recurring_categories.map((c) => (
                <button
                  key={c.category}
                  className={`chip chip-small ${filterCategory === c.category ? "chip-active" : ""}`}
                  onClick={() => setFilterCategory(filterCategory === c.category ? null : c.category)}
                >
                  {c.category} ({c.count})
                </button>
              ))}
              {filterCategory && (
                <button className="chip chip-small" onClick={() => setFilterCategory(null)}>
                  Clear filter
                </button>
              )}
            </div>
          </section>

          <ol className="attempt-history">
            {entries.map((e) => (
              <li key={e.id} className={e.category ? "attempt-fail" : ""}>
                {removingId === e.id ? (
                  <div className="mistake-remove-confirm">
                    <p className="mistake-remove-confirm-question">Remove this mistake from your journal?</p>
                    <p className="muted small">
                      This will remove the recorded mistake for &ldquo;{e.title}&rdquo;.
                    </p>
                    {deleteError?.id === e.id && <p className="error small">{deleteError.message}</p>}
                    <div className="hint-buttons">
                      <button
                        type="button"
                        className="chip chip-small"
                        onClick={() => setRemovingId(null)}
                        disabled={deletingId === e.id}
                      >
                        Cancel
                      </button>
                      <button
                        type="button"
                        className="chip chip-small chip-danger"
                        onClick={() => handleDeleteMistake(e)}
                        disabled={deletingId === e.id}
                      >
                        {deletingId === e.id ? "Removing..." : "Remove mistake"}
                      </button>
                    </div>
                  </div>
                ) : (
                  <>
                    <div className="attempt-history-row">
                      <span>
                        <Link to={`/problems/${e.slug}`}>{e.title}</Link>{" "}
                        <span className="muted small">
                          ({e.topic} &middot; {e.pattern_family})
                        </span>
                      </span>
                      <span className="attempt-history-row-actions">
                        <span className="muted small">{e.created_at}</span>
                        <button
                          type="button"
                          className="mistake-remove-btn"
                          onClick={() => {
                            setDeleteError(null);
                            setDeletedNotice(null);
                            setRemovingId(e.id);
                          }}
                          aria-label={`Remove the mistake for ${e.title}`}
                          title="Remove this mistake"
                        >
                          <span aria-hidden="true">&#10005;</span>
                        </button>
                      </span>
                    </div>
                    <p>
                      <strong>{e.category || "Unclassified"}</strong>{" "}
                      <span className="viz-type-tag">{CONFIDENCE_LABEL[e.confidence] || e.confidence}</span>
                    </p>
                    {e.evidence && <p className="muted small">{e.evidence}</p>}
                    {e.related_lesson && (
                      <p className="muted small">
                        Revise: <Link to={`/learn/${e.related_lesson.slug}`}>{e.related_lesson.title}</Link>
                      </p>
                    )}
                  </>
                )}
              </li>
            ))}
          </ol>
        </>
      )}
    </div>
  );
}
