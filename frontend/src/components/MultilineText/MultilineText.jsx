// Lesson/problem content is plain multi-line text (not full markdown).
// Render it as paragraphs, turning consecutive dash/number-prefixed
// lines into a real list so it doesn't look like a wall of text, and
// turning single-backtick spans (`nums`, `O(n)`) into real inline code
// instead of showing literal backtick characters -- about half the
// problem bank's descriptions use that convention. No markdown library
// needed for content this simple.

// Shared with LessonDetail.jsx for the same reason: any free-text field
// from the same content pipeline can contain a `backtick span`, and it
// should render the same way everywhere it appears.
export function renderInlineCode(text) {
  if (!text) return text;
  const parts = text.split(/(`[^`]+`)/g);
  if (parts.length === 1) return text;
  return parts.map((part, i) =>
    part.startsWith("`") && part.endsWith("`") && part.length > 1 ? (
      <code key={i}>{part.slice(1, -1)}</code>
    ) : (
      <span key={i}>{part}</span>
    )
  );
}

export default function MultilineText({ text, className = "" }) {
  if (!text) return null;
  const lines = text.split("\n").filter((l) => l.trim().length > 0);

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
