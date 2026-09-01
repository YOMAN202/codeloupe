import { useState } from "react";
import { renderInlineCode } from "../MultilineText/MultilineText";

const KIND_LABEL = {
  predict_output: "Predict the output",
  choose_pattern: "Which pattern applies?",
  spot_bug: "Spot the bug",
  complexity: "Complexity check",
};

// Lightweight reinforcement after a concept, per the teaching-system brief:
// "not a generic quiz app". choose_pattern gets real multiple-choice
// buttons with immediate right/wrong feedback (there's a fixed small set
// of good answers, so a click is more honest than free text); the other
// three kinds are think-it-through-yourself-then-reveal, same interaction
// LessonDetail already uses for its day-1-style prediction questions --
// deliberately not a free-text grader, which would either be trivially
// gameable or need real answer-matching logic for little pedagogical gain
// over "commit to an answer in your head, then check it".
export default function Checkpoint({ checkpoint }) {
  const [answered, setAnswered] = useState(false);
  const [picked, setPicked] = useState(null);

  const isChoice = checkpoint.kind === "choose_pattern" && Array.isArray(checkpoint.choices);

  return (
    <div className="checkpoint-card">
      <div className="checkpoint-kind">{KIND_LABEL[checkpoint.kind] || checkpoint.kind}</div>
      <p className="checkpoint-prompt">{renderInlineCode(checkpoint.prompt_markdown)}</p>
      {checkpoint.code && <pre className="code-block">{checkpoint.code}</pre>}

      {isChoice ? (
        <div className="checkpoint-choices">
          {checkpoint.choices.map((choice) => {
            const isPicked = picked === choice;
            const isCorrect = choice === checkpoint.correct_answer;
            const showState = answered && (isPicked || isCorrect);
            return (
              <button
                key={choice}
                className={`chip checkpoint-choice ${showState ? (isCorrect ? "checkpoint-correct" : "checkpoint-incorrect") : ""}`}
                onClick={() => {
                  setPicked(choice);
                  setAnswered(true);
                }}
                disabled={answered}
              >
                {choice}
              </button>
            );
          })}
        </div>
      ) : (
        !answered && (
          <button className="chip" onClick={() => setAnswered(true)}>
            Reveal answer
          </button>
        )
      )}

      {answered && (
        <div className="checkpoint-explanation">
          {!isChoice && (
            <p>
              <strong>Answer:</strong> {renderInlineCode(checkpoint.correct_answer)}
            </p>
          )}
          <p className="muted small">{renderInlineCode(checkpoint.explanation_markdown)}</p>
        </div>
      )}
    </div>
  );
}
