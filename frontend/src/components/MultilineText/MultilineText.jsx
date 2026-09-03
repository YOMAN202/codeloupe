// Lesson/problem content is plain multi-line text (not full markdown).
// Render it as paragraphs, turning consecutive dash/number-prefixed
// lines into a real list so it doesn't look like a wall of text, turning
// single-backtick spans (`nums`, `O(n)`) into real inline code instead of
// showing literal backtick characters -- about half the problem bank's
// descriptions use that convention -- and turning **double-asterisk**
// spans into real bold (the concept-lesson content in
// backend/db/seed_concepts.py uses this to name sub-patterns inline, e.g.
// "**opposite-direction**"). No markdown library needed for content this
// simple; these are the only two inline conventions this content pipeline
// supports, deliberately, rather than reaching for full markdown.

// Shared with LessonDetail.jsx and ConceptLesson.jsx for the same reason:
// any free-text field from the same content pipeline can contain either
// span, and it should render the same way everywhere it appears.
export function renderInlineCode(text) {
  if (!text) return text;
  const parts = text.split(/(`[^`]+`|\*\*[^*]+\*\*)/g);
  if (parts.length === 1) return text;
  return parts.map((part, i) => {
    if (part.startsWith("`") && part.endsWith("`") && part.length > 1) {
      return <code key={i}>{part.slice(1, -1)}</code>;
    }
    if (part.startsWith("**") && part.endsWith("**") && part.length > 4) {
      return <strong key={i}>{part.slice(2, -2)}</strong>;
    }
    return <span key={i}>{part}</span>;
  });
}

// The same "one non-empty line = one item" split MultilineText itself uses
// below, pulled out standalone so anything that needs to address an
// individual line (not just render the whole block) can share the exact
// same rule rather than re-implementing it. Used by LessonDetail.jsx (to
// give each line of a day's exercises_markdown its own "Try in Scratchpad"
// link) and Scratchpad.jsx (to pick the matching line back out by that
// same 0-based index) -- both read the SAME canonical exercises_markdown
// field the lesson API already returns, so this never duplicates content,
// only the parsing rule.
export function splitNonEmptyLines(text) {
  if (!text) return [];
  return text.split("\n").filter((l) => l.trim().length > 0);
}

export default function MultilineText({ text, className = "" }) {
  if (!text) return null;
  const lines = splitNonEmptyLines(text);

  const blocks = [];
  let currentList = null;
  for (const line of lines) {
    const isListItem = /^[-*]\s+/.test(line.trim()) || /^\d+[.)]\s+/.test(line.trim());
    if (isListItem) {
      const content = line.trim().replace(/^[-*]\s+/, "").replace(/^\d+[.)]\s+/, "");
      if (!currentList) {
        currentList = [];
        blocks.push(currentList);
      }
      currentList.push(content);
    } else {
      currentList = null;
      blocks.push(line);
    }
  }

  return (
    <div className={`multiline-text ${className}`}>
      {blocks.map((block, i) =>
        Array.isArray(block) ? (
          <ul key={i}>
            {block.map((item, j) => (
              <li key={j}>{renderInlineCode(item)}</li>
            ))}
          </ul>
        ) : (
          <p key={i}>{renderInlineCode(block)}</p>
        )
      )}
    </div>
  );
}
