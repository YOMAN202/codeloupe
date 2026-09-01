// Small, reusable status/metadata badges shared across pages.

const STATUS_LABELS = {
  not_started: "Not started",
  in_progress: "In progress",
  completed: "Completed",
  skipped: "Skipped",
  known: "Already known",
};

export function StatusBadge({ status }) {
  return (
    <span className={`badge status-${status}`}>
      {STATUS_LABELS[status] || status}
    </span>
  );
}

export function PriorityBadge({ priority }) {
  if (!priority) return null;
  return <span className={`badge priority-${priority}`}>{priority}</span>;
}

export function DifficultyBadge({ difficulty }) {
  if (!difficulty) return null;
  return <span className={`badge difficulty-${difficulty}`}>{difficulty}</span>;
}
