import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { fetchProblems } from "../../api/client";
import { DifficultyBadge, PriorityBadge, TIER_META } from "../../components/Badges/Badges";

const TIER_ORDER = ["core", "extended", "advanced"];

const TIER_NOTE = {
  core: "The required 45-day path. Primarily Easy/Medium. Finishing this is a strong foundation for internship and entry-level interviews on its own.",
  extended: "Optional Easy/Medium reinforcement for weak topics or extra pattern practice — not required within the 45 days.",
  advanced: "Optional Hard problems for going further after Easy/Medium fundamentals are solid. Never required, never blocks Core Path completion.",
};

function ProblemTable({ problems }) {
  return (
    <table className="problem-table">
      <thead>
        <tr>
          <th>Title</th>
          <th>Topic</th>
          <th>Pattern</th>
          <th>Difficulty</th>
          <th>Priority</th>
          <th>Est. time</th>
        </tr>
      </thead>
      <tbody>
        {problems.map((p) => (
          <tr key={p.slug}>
            <td>
              <Link to={`/problems/${p.slug}`}>{p.title}</Link>
              {p.progression_stage === "variation" && (
                <span className="muted small"> (variation)</span>
              )}
            </td>
            <td>{p.topic}</td>
            <td className="muted">{p.pattern}</td>
            <td>
              <DifficultyBadge difficulty={p.difficulty} />
            </td>
            <td>
              <PriorityBadge priority={p.interview_priority} />
            </td>
            <td className="muted">{p.estimated_solve_minutes} min</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}

export default function ProblemBrowser() {
  const [problems, setProblems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [topicFilter, setTopicFilter] = useState("all");
  const [tierFilter, setTierFilter] = useState("all");

  useEffect(() => {
    fetchProblems()
      .then(setProblems)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <p className="muted">Loading problems...</p>;
  if (error) return <p className="error">{error}</p>;

  const topics = ["all", ...new Set(problems.map((p) => p.topic))];
  const byTopic = problems.filter((p) => topicFilter === "all" || p.topic === topicFilter);
  const tierCounts = Object.fromEntries(TIER_ORDER.map((t) => [t, problems.filter((p) => p.path_tier === t).length]));

  return (
    <div className="page">
      <div className="page-header">
        <h2>Problem bank</h2>
        <p className="muted">
          {problems.length} curated problems, organized by interview pattern and priority tier.
          Core = you should instantly recognize this shape in an internship OA or phone screen.
          Easy/Medium mastery is the primary goal — Advanced Challenges are optional.
        </p>
      </div>

      <div className="filter-row">
        <label>Topic:</label>
        {topics.map((t) => (
          <button
            key={t}
            className={`chip ${topicFilter === t ? "chip-active" : ""}`}
            onClick={() => setTopicFilter(t)}
          >
            {t}
          </button>
        ))}
      </div>
      <div className="filter-row">
        <label>Tier:</label>
        <button className={`chip ${tierFilter === "all" ? "chip-active" : ""}`} onClick={() => setTierFilter("all")}>
          all
        </button>
        {TIER_ORDER.map((t) => (
          <button
            key={t}
            className={`chip ${tierFilter === t ? "chip-active" : ""}`}
            onClick={() => setTierFilter(t)}
          >
            {TIER_META[t].emoji} {TIER_META[t].label} ({tierCounts[t]})
          </button>
        ))}
      </div>

      {TIER_ORDER.filter((t) => tierFilter === "all" || tierFilter === t).map((tier) => {
        const tierProblems = byTopic.filter((p) => p.path_tier === tier);
        if (tierProblems.length === 0) return null;
        return (
          <div key={tier}>
            <div className="tier-section-heading">
              <h3>
                {TIER_META[tier].emoji} {TIER_META[tier].label}
              </h3>
              <span className="tier-count">{tierProblems.length} problems</span>
            </div>
            <p className="tier-section-note">{TIER_NOTE[tier]}</p>
            <ProblemTable problems={tierProblems} />
          </div>
        );
      })}
    </div>
  );
}
