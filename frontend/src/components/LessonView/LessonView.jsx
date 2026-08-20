// Milestone 1: renders lesson concept text fetched from the backend.
// No interactive teaching-loop UI yet (prediction questions, etc.) --
// that's layered on in later milestones as topic visualizers land.
export default function LessonView({ lesson, loading, error }) {
  if (loading) return <p className="muted">Loading lesson...</p>;
  if (error) return <p className="error">Could not load lesson: {error}</p>;
  if (!lesson) return null;

  return (
    <div className="lesson-view">
      <h2>
        Day {lesson.day} — {lesson.title}
      </h2>
      <pre className="lesson-markdown">{lesson.concept_markdown}</pre>
    </div>
  );
}
