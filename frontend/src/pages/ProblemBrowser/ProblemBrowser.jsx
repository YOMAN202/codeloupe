import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { fetchProblems } from "../../api/client";
import { DifficultyBadge, PriorityBadge } from "../../components/Badges/Badges";

export default function ProblemBrowser() {
  const [problems, setProblems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [topicFilter, setTopicFilter] = useState("all");

  useEffect(() => {
    fetchProblems()
      .then(setProblems)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <p className="muted">Loading problems...</p>;
  if (error) return <p className="error">{error}</p>;

  const topics = ["all", ...new Set(problems.map((p) => p.topic))];
  const visible = problems.filter((p) => topicFilter === "all" || p.topic === topicFilter);

  return (
    <div className="page">
      <div className="page-header">
        <h2>Problem bank</h2>
        <p className="muted">
          {problems.length} curated problems, organized by interview pattern. Core = you should
          instantly recognize this shape in an internship OA or phone screen.
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
          {visible.map((p) => (
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
    </div>
  );
}
