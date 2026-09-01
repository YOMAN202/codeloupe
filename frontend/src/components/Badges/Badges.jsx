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

// Tiers read as a rank (Core -> Extended -> Advanced), so they're
// distinguished by color + a small dot rather than emoji -- keeps the
// two-accent system (teal/amber) untouched by metadata and avoids emoji
// as a section marker (see docs/decisions.md's design-system notes).
const TIER_META = {
  core: { label: "Core 45-Day Path" },
  extended: { label: "Extended Practice" },
  advanced: { label: "Advanced Challenge" },
};

export function TierBadge({ tier }) {
  const meta = TIER_META[tier];
  if (!meta) return null;
  return (
    <span className={`badge tier-${tier}`}>
      <span className="tier-dot" aria-hidden="true" />
      {meta.label}
    </span>
  );
}

export { TIER_META };
