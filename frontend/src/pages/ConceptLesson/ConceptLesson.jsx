import { useEffect, useState } from "react";
import { useParams, useNavigate, Link } from "react-router-dom";
import { fetchConcept, fetchConcepts, setConceptProgress } from "../../api/client";
import { StatusBadge, DifficultyBadge } from "../../components/Badges/Badges";
import { renderInlineCode } from "../../components/MultilineText/MultilineText";
import ConceptWalkthrough from "../../components/ConceptWalkthrough/ConceptWalkthrough";
import Checkpoint from "../../components/Checkpoint/Checkpoint";

const KIND_LABEL = { topic: "Topic", pattern: "Pattern" };

function PracticeExercise({ exercise, index, conceptSlug }) {
  const [revealed, setRevealed] = useState(false);
  return (
    <div className="lesson-section practice-exercise">
      <h4>Exercise {index + 1}</h4>
      <p>{renderInlineCode(exercise.prompt_markdown)}</p>
      {exercise.starter_code && <pre className="code-block">{exercise.starter_code}</pre>}
      <p className="muted small">
        Try it in the{" "}
        <Link to={`/scratchpad?from=concept-exercise&concept=${conceptSlug}&id=${exercise.id}`}>
          scratchpad
        </Link>{" "}
        first, then check your approach here.
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
  const navigate = useNavigate();
  const [concept, setConcept] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [savingStatus, setSavingStatus] = useState(false);
  // Canonical Learn ordering for Previous/Next topic nav, straight from
  // the same /api/concepts list the Learn hub itself renders from (see
  // Learn.jsx and app.py's list_concepts: ORDER BY topic, kind, then
  // display_order) -- not a second, hand-picked ordering. Fetched once on
  // mount (empty dep array), independent of `slug`: the set of all 29
  // concepts and their order never changes as you move between them, so
  // this doesn't re-fetch on every Previous/Next click, and it's already
  // in place on a direct nav or hard refresh to any single concept page.
  // Best-effort, same spirit as the rest of this page's error handling --
  // if it fails, the page still works, it just won't offer prev/next nav.
  const [conceptOrder, setConceptOrder] = useState([]);

  function load() {
    setLoading(true);
    fetchConcept(slug)
      .then(setConcept)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }

  useEffect(load, [slug]);

  useEffect(() => {
    fetchConcepts()
      .then((list) => setConceptOrder(list.map((c) => ({ slug: c.slug, title: c.title }))))
      .catch(() => {});
  }, []);

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

  // Position of the currently-open concept within the canonical order.
  // -1 (not found -- e.g. conceptOrder hasn't loaded yet) disables both
  // buttons via the null checks below, same as an out-of-range index at
  // either end of the list would.
  const orderIndex = conceptOrder.findIndex((c) => c.slug === slug);
  const prevConcept = orderIndex > 0 ? conceptOrder[orderIndex - 1] : null;
  const nextConcept =
    orderIndex >= 0 && orderIndex < conceptOrder.length - 1 ? conceptOrder[orderIndex + 1] : null;

  return (
    <div className="page">
      {/* Symmetric to LessonDetail.jsx's "Back to Curriculum" link -- same
          .lesson-back-link/.chip class (identical styling/spacing), same
          placement immediately above .page-header, same unconditional
          "always shown, always the same destination" shape rather than
          anything referrer/query-param-based. That's what makes this work
          correctly on direct navigation and a hard refresh: it doesn't
          depend on how this concept lesson was reached, exactly like
          "Back to Curriculum" doesn't depend on how a day lesson was
          reached either. Reuses the existing /learn route/component --
          no new route. */}
      <Link to="/learn" className="chip lesson-back-link">
        &larr; Back to Learn
      </Link>
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
        {["in_progress", "completed", "known"].map((s) => {
          // Same toggle-off shape as LessonDetail's status-controls (see
          // that file): "known" is the one status a learner reaches
          // deliberately rather than by progressing through the material,
          // so clicking it again while already known removes the known
          // status (back to not_started) instead of just re-saving the
          // same value. "in_progress"/"completed" stay one-way "mark X"
          // buttons -- concept_lesson_progress has no "skipped" status
          // (see schema.sql), so unlike LessonDetail there's no fourth
          // button here; that's an intentional difference in the data
          // model, not a gap in this control.
          const isActive = concept.status === s;
          const isKnownToggle = s === "known";
          const label = isKnownToggle && isActive ? "Unmark known" : `Mark ${s.replace("_", " ")}`;
          const targetStatus = isKnownToggle && isActive ? "not_started" : s;
          return (
            <button
              key={s}
              className={`chip ${isActive ? "chip-active" : ""}`}
              disabled={savingStatus}
              aria-pressed={isKnownToggle ? isActive : undefined}
              onClick={() => updateStatus(targetStatus)}
            >
              {label}
            </button>
          );
        })}
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
            <PracticeExercise key={ex.id} exercise={ex} index={i} conceptSlug={slug} />
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

      {/* Previous/Next Learn topic -- same logical spot and same
          .lesson-nav-buttons/.chip shape as LessonDetail's Day
          prev/next controls, at the very end of the page, after all
          lesson content. Pure navigation only: unlike LessonDetail's
          goToDay, this never calls setConceptProgress -- moving between
          Learn topics has no completion side effect. Rendered only once
          conceptOrder has loaded, so there's no flash of a wrongly
          enabled/disabled button before the canonical order is known. */}
      {conceptOrder.length > 0 && (
        <div className="lesson-nav-buttons">
          <button
            className="chip"
            onClick={() => prevConcept && navigate(`/learn/${prevConcept.slug}`)}
            disabled={!prevConcept}
          >
            &larr; {prevConcept ? prevConcept.title : "First topic"}
          </button>
          {/* Boundary label deliberately avoids the bare word "Next" --
              ConceptWalkthrough's own step control (rendered on this same
              page, in "Worked example" above) has its own unrelated
              "Next ->" button, and the two would otherwise collide as
              ambiguous matches for anything selecting a button by that
              name (see e2e_teaching_test.py's walkthrough-stepping check,
              which does exactly that). Every other state here shows the
              actual destination topic's title instead, which never
              collides. */}
          <button
            className="chip"
            onClick={() => nextConcept && navigate(`/learn/${nextConcept.slug}`)}
            disabled={!nextConcept}
          >
            {nextConcept ? nextConcept.title : "Last topic"} &rarr;
          </button>
        </div>
      )}
    </div>
  );
}
