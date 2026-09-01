import { useState } from "react";
import { ArrayPointerView } from "../Visualizers/Visualizers";

// A teaching walkthrough steps through a hand-authored, VERIFIED-BY-HAND
// sequence of {caption, locals} frames (see backend/db/seed_concepts.py) --
// a controlled example chosen to demonstrate a concept clearly. It reuses
// ArrayPointerView, the same component the real trace-your-own-code system
// (TraceViewer.jsx) uses to render array/pointer state, so a learner sees
// one consistent visual language for "array + pointers" everywhere in the
// app. That is where the reuse stops on purpose: this component never
// touches /api/.../trace or sys.settrace. Codeloupe's actual differentiator
// -- write your own code, run it, trace what IT actually did -- lives only
// in TraceViewer.jsx. This is clearly a separate, simpler stepper (no
// play/predict-mode, no event/line/depth -- there's no real execution here
// to report on) so the two are never visually confusable.
export default function ConceptWalkthrough({ frames, topic, pattern }) {
  const [index, setIndex] = useState(0);
  if (!frames || frames.length === 0) return null;
  const frame = frames[index];

  return (
    <div className="concept-walkthrough">
      <div className="trace-controls">
        <button className="chip" onClick={() => setIndex((i) => Math.max(0, i - 1))} disabled={index === 0}>
          &larr; Back
        </button>
        <button
          className="chip"
          onClick={() => setIndex((i) => Math.min(frames.length - 1, i + 1))}
          disabled={index >= frames.length - 1}
        >
          Next &rarr;
        </button>
        <span className="muted">
          step {index + 1} / {frames.length}
        </span>
      </div>

      <input
        type="range"
        min={0}
        max={frames.length - 1}
        value={index}
        onChange={(e) => setIndex(Number(e.target.value))}
        className="trace-scrubber"
        style={{ "--scrub-pct": `${frames.length > 1 ? (index / (frames.length - 1)) * 100 : 100}%` }}
        aria-label={`Walkthrough step ${index + 1} of ${frames.length}`}
      />

      <p className="concept-walkthrough-caption">{frame.caption}</p>
      <ArrayPointerView locals={frame.locals} topic={topic} pattern={pattern} />
    </div>
  );
}
