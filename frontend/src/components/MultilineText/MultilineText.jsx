// Lesson/problem content is plain multi-line text (not full markdown).
// Render it as paragraphs, turning consecutive dash/number-prefixed
// lines into a real list so it doesn't look like a wall of text. No
// markdown library needed for content this simple.

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
              <li key={j}>{item}</li>
            ))}
          </ul>
        ) : (
          <p key={i}>{block}</p>
        )
      )}
    </div>
  );
}
