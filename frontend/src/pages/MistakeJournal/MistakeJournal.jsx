import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { fetchMistakeJournal } from "../../api/client";

const CONFIDENCE_LABEL = {
  observed_confirmed: "observed",
  likely_issue: "likely",
  user_confirmed: "you confirmed",
  manually_selected: "you classified",
};

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

  useEffect(() => {
    fetchMistakeJournal()
      .then(setJournal)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <p className="muted">Loading your mistake journal...</p>;
  if (error) return <p className="error">{error}</p>;
  if (!journal) return null;

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
                <div className="attempt-history-row">
                  <span>
                    <Link to={`/problems/${e.slug}`}>{e.title}</Link>{" "}
                    <span className="muted small">
                      ({e.topic} &middot; {e.pattern_family})
                    </span>
                  </span>
                  <span className="muted small">{e.created_at}</span>
                </div>
                <p>
                  <strong>{e.category || "Unclassified"}</strong>{" "}
                  <span className="viz-type-tag">{CONFIDENCE_LABEL[e.confidence] || e.confidence}</span>
                </p>
                {e.evidence && <p className="muted small">{e.evidence}</p>}
              </li>
            ))}
          </ol>
        </>
      )}
    </div>
  );
}
