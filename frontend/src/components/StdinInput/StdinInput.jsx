// Reusable multiline stdin box for free-form (top-level-script) Python
// execution: code that calls input() / sys.stdin.readline() / sys.stdin.read()
// needs SOME source of input, and this is it. Deliberately a single small,
// shared component (rather than an inline <textarea> inside Scratchpad.jsx)
// even though Scratchpad is its only caller today -- free-form execution is
// the one place stdin is a meaningful concept (see run_code()/trace_code()
// in the backend), but if a second free-form-execution surface is ever
// added, it gets this for free instead of a second hand-rolled copy.
//
// Deliberately NOT used by the Problem Workspace: that page grades a
// function call against fixed test-case arguments (run_against_tests() in
// test_runner.py calls `fn(*args)` directly) -- there's no stdin concept
// there at all, and adding this box to it would misleadingly suggest
// problem test cases can be fed via stdin, which they can't.
export default function StdinInput({ value, onChange }) {
  return (
    <div className="stdin-input">
      <label className="stdin-input-label" htmlFor="scratchpad-stdin">
        Input (stdin)
        <span className="muted small stdin-input-hint">
          {" "}
          -- one value per line, fed to input()/sys.stdin in order
        </span>
      </label>
      <textarea
        id="scratchpad-stdin"
        className="stdin-input-textarea"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder={"e.g.\n5\n1 2 3 4 5"}
        spellCheck={false}
        rows={3}
      />
    </div>
  );
}
