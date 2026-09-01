import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { fetchConcepts } from "../../api/client";
import { StatusBadge } from "../../components/Badges/Badges";

const KIND_LABEL = { topic: "Topic", pattern: "Pattern" };

export default function Learn() {
  const [concepts, setConcepts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchConcepts()
      .then(setConcepts)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <p className="muted">Loading lessons...</p>;
  if (error) return <p className="error">{error}</p>;

  // Grouped by topic (matches problems.topic, so "arrays" here is the same
  // "arrays" a problem or day lesson is tagged with) rather than by
  // curriculum day -- this page answers "what concept do I want to learn",
  // Curriculum answers "what's next in the 45-day schedule". Both stay
  // freely browsable; neither gates the other.
  const byTopic = [];
  for (const c of concepts) {
    let group = byTopic.find((g) => g.topic === c.topic);
    if (!group) {
      group = { topic: c.topic, items: [] };
      byTopic.push(group);
    }
    group.items.push(c);
  }

  return (
    <div className="page">
      <div className="page-header">
        <h2>Learn</h2>
        <p className="muted">
          The concepts and patterns behind the problem bank &mdash; what they are, when to
          reach for them, and a worked example before you try one yourself. Browse freely;
          nothing here is required before you can attempt a problem.
        </p>
      </div>

      {concepts.length === 0 ? (
        <p className="muted">No lessons yet.</p>
      ) : (
        byTopic.map((group) => (
          <section key={group.topic} className="block-section">
            <h3>{group.topic.replace(/-/g, " ")}</h3>
            <div className="lesson-grid">
              {group.items.map((c) => (
                <Link key={c.slug} to={`/learn/${c.slug}`} className={`lesson-card status-${c.status}`}>
                  <div className="lesson-card-top">
                    <span className="day-number">{KIND_LABEL[c.kind] || c.kind}</span>
                    <StatusBadge status={c.status} />
                  </div>
                  <div className="lesson-card-title">{c.title}</div>
                  <div className="muted small">{c.summary}</div>
                  {c.estimated_minutes && (
                    <div className="muted small">~{c.estimated_minutes} min</div>
                  )}
                </Link>
              ))}
            </div>
          </section>
        ))
      )}
    </div>
  );
}
