import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { fetchProblems } from "../../api/client";
import { DifficultyBadge, PriorityBadge, TIER_META } from "../../components/Badges/Badges";

const TIER_ORDER = ["core", "extended", "advanced"];

const TIER_NOTE = {
  core: "The recommended 45-day path, not a gate -- primarily Easy/Medium, and a strong foundation for internship and entry-level interviews on its own. Every problem here stays open regardless of order or what else you've solved.",
  extended: "Optional Easy/Medium reinforcement for weak topics or extra pattern practice -- not required within the 45 days.",
  advanced: "Optional Hard problems for going further after Easy/Medium fundamentals are solid. Never required, never blocks Core Path completion.",
};

// A responsive row list rather than an HTML table -- a table can only
// ever be shrunk (or scrolled sideways) on a narrow screen, never
// genuinely redesigned for one. Below 760px (see App.css) each row
// collapses from a grid into a stacked card instead.
function ProblemList({ problems }) {
  return (
    <div className="problem-list-rows">
      <div className="problem-list-header" aria-hidden="true">
        <span>Title</span>
        <span>Topic</span>
        <span>Pattern</span>
        <span>Difficulty</span>
        <span>Priority</span>
        <span>Est. time</span>
      </div>
      {problems.map((p) => (
        <Link key={p.slug} to={`/problems/${p.slug}`} className="problem-list-row">
          <span className="problem-list-row-title">
            <span>{p.title}</span>
            {p.progression_stage === "variation" && (
              <span className="problem-list-row-meta">variation</span>
            )}
          </span>
          <span className="problem-list-row-topic">{p.topic}</span>
          <span className="problem-list-row-pattern">{p.pattern}</span>
          <span>
            <DifficultyBadge difficulty={p.difficulty} />
          </span>
          <span>
            <PriorityBadge priority={p.interview_priority} />
          </span>
          <span className="problem-list-row-time">{p.estimated_solve_minutes} min</span>
        </Link>
      ))}
    </div>
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
            {TIER_META[t].label} ({tierCounts[t]})
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
                <span className={`tier-dot tier-dot-${tier}`} aria-hidden="true" />
                {TIER_META[tier].label}
              </h3>
              <span className="tier-count">{tierProblems.length} problems</span>
            </div>
            <p className="tier-section-note">{TIER_NOTE[tier]}</p>
            <ProblemList problems={tierProblems} />
          </div>
        );
      })}
    </div>
  );
}
