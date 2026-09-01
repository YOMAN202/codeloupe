import { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import { fetchConcept, setConceptProgress } from "../../api/client";
import { StatusBadge, DifficultyBadge } from "../../components/Badges/Badges";
import { renderInlineCode } from "../../components/MultilineText/MultilineText";
import ConceptWalkthrough from "../../components/ConceptWalkthrough/ConceptWalkthrough";
import Checkpoint from "../../components/Checkpoint/Checkpoint";

const KIND_LABEL = { topic: "Topic", pattern: "Pattern" };

function PracticeExercise({ exercise, index }) {
  const [revealed, setRevealed] = useState(false);
  return (
    <div className="lesson-section practice-exercise">
      <h4>Exercise {index + 1}</h4>
      <p>{renderInlineCode(exercise.prompt_markdown)}</p>
      {exercise.starter_code && <pre className="code-block">{exercise.starter_code}</pre>}
      <p className="muted small">
        Try it in the <Link to="/scratchpad">scratchpad</Link> first, then check your approach here.
      </p>
      {!revealed ? (
        <button className="chip" onClick={() => setRevealed(true)}>
          {exercise.hint_markdown ? "Show hint + solution" : "Show solution"}
        </button>
      ) : (
        <div>
          {exercise.hint_markdown && (
            <p className="muted small">
              <strong>Hint:</strong> {renderInlineCode(exercise.hint_markdown)}
            </p>
          )}
          <pre className="code-block">{exercise.solution_code}</pre>
        </div>
      )}
    </div>
  );
}

export default function ConceptLesson() {
  const { slug } = useParams();
  const [concept, setConcept] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [savingStatus, setSavingStatus] = useState(false);

  function load() {
    setLoading(true);
    fetchConcept(slug)
      .then(setConcept)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }

  useEffect(load, [slug]);

  async function updateStatus(status) {
    setSavingStatus(true);
    try {
      await setConceptProgress(slug, status);
      setConcept((prev) => ({ ...prev, status }));
    } catch (e) {
      setError(e.message);
    } finally {
      setSavingStatus(false);
    }
  }

  if (loading) return <p className="muted">Loading lesson...</p>;
  if (error) return <p className="error">{error}</p>;
  if (!concept) return null;

  return (
    <div className="page">
      <div className="page-header">
        <div className="lesson-detail-title">
          <span className="viz-type-tag">{KIND_LABEL[concept.kind] || concept.kind}</span>
          <h2>{concept.title}</h2>
          <StatusBadge status={concept.status} />
        </div>
        <p className="muted">
          {concept.summary}
          {concept.estimated_minutes ? ` · ~${concept.estimated_minutes} min` : ""}
        </p>
      </div>

      <div className="status-controls">
        {["in_progress", "completed", "known"].map((s) => (
          <button
            key={s}
            className={`chip ${concept.status === s ? "chip-active" : ""}`}
            disabled={savingStatus}
            onClick={() => updateStatus(s)}
          >
            Mark {s.replace("_", " ")}
          </button>
        ))}
      </div>

      {concept.prerequisites?.length > 0 && (
        <div className="prereq-box">
          <strong>Recommended background</strong> (not required &mdash; jump in anytime):
          <ul>
            {concept.prerequisites.map((p) => (
              <li key={p.slug}>
                <Link to={`/learn/${p.slug}`}>{p.title}</Link>{" "}
                <span className="muted small">({p.status.replace("_", " ")})</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      <section className="lesson-section">
        <h3>What it is</h3>
        <p>{renderInlineCode(concept.what_markdown)}</p>
      </section>

      <section className="lesson-section">
        <h3>Why it matters</h3>
        <p>{renderInlineCode(concept.why_markdown)}</p>
      </section>

      {concept.recognize_markdown && (
        <section className="lesson-section recognize-section">
          <h3>When should I use this?</h3>
          <p>{renderInlineCode(concept.recognize_markdown)}</p>
        </section>
      )}

      <section className="lesson-section">
        <h3>Core intuition</h3>
        <p>{renderInlineCode(concept.intuition_markdown)}</p>
      </section>

      {concept.walkthrough_code && (
        <section className="lesson-section">
          <h3>Worked example</h3>
          {concept.walkthrough_intro_markdown && <p>{renderInlineCode(concept.walkthrough_intro_markdown)}</p>}
          <pre className="code-block">{concept.walkthrough_code}</pre>
          {concept.walkthrough_frames?.length > 0 && (
            <ConceptWalkthrough frames={concept.walkthrough_frames} topic={concept.topic} pattern={concept.pattern_family || ""} />
          )}
        </section>
      )}

      {concept.common_mistakes_markdown && (
        <section className="lesson-section">
          <h3>Common mistakes</h3>
          <p>{renderInlineCode(concept.common_mistakes_markdown)}</p>
        </section>
      )}

      {concept.complexity_markdown && (
        <section className="lesson-section">
          <h3>Complexity</h3>
          <p>{renderInlineCode(concept.complexity_markdown)}</p>
        </section>
      )}

      {concept.checkpoints?.length > 0 && (
        <section className="lesson-section">
          <h3>Quick checks</h3>
          {concept.checkpoints.map((chk) => (
            <Checkpoint key={chk.id} checkpoint={chk} />
          ))}
        </section>
      )}

      {concept.practice_exercises?.length > 0 && (
        <section className="lesson-section">
          <h3>Practice before a full problem</h3>
          {concept.practice_exercises.map((ex, i) => (
            <PracticeExercise key={ex.id} exercise={ex} index={i} />
          ))}
        </section>
      )}

      {concept.related_problems?.length > 0 && (
        <section className="lesson-section">
          <h3>Apply it</h3>
          <p className="muted small">Problems in the bank that put this concept into practice.</p>
          <div className="problem-list">
            {concept.related_problems.map((p) => (
              <Link key={p.slug} to={`/problems/${p.slug}`} className="problem-row">
                <span>
                  {p.title}
                  {p.day && <span className="muted small"> &mdash; Day {p.day}</span>}
                </span>
                <DifficultyBadge difficulty={p.difficulty} />
              </Link>
            ))}
          </div>
        </section>
      )}
    </div>
  );
}
