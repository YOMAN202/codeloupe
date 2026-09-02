import Editor from "@monaco-editor/react";
import "../../monacoSetup";

// Height lives in CSS (.code-editor-wrap in App.css), not as a fixed
// "360px" prop here -- a hardcoded pixel height on the Editor itself can't
// be adjusted per breakpoint by a media query (it'd need to fight an
// inline style), so the wrapper gets a real CSS height instead and the
// editor just fills it at height="100%". This is also what makes the
// editor "significantly larger, ~65-70% of the coding area" sizing a pure
// CSS change (see App.css's "editor + live preview" section) rather than
// something touched here again later.
export default function CodeEditor({ value, onChange }) {
  return (
    <div className="code-editor-wrap">
      <Editor
        height="100%"
        defaultLanguage="python"
        value={value}
        onChange={(v) => onChange(v ?? "")}
        theme="codeloupe-dark"
        options={{
          fontSize: 14,
          fontFamily: "'IBM Plex Mono', ui-monospace, monospace",
          minimap: { enabled: false },
          scrollBeyondLastLine: false,
          // Monaco does NOT observe its own container by default -- without
          // this, toggling the Live Preview panel (or collapsing the
          // sidebar, or resizing the browser) leaves the editor's internal
          // canvas at its OLD pixel width even though the wrapping flex
          // column has visibly grown, until something else happens to
          // trigger a relayout (e.g. a keystroke). automaticLayout makes
          // Monaco poll its container's size and call its own .layout()
          // whenever that size actually changes, covering every resize
          // cause above with one option instead of wiring a manual
          // .layout() call to each of them separately.
          automaticLayout: true,
        }}
        onMount={(editor) => {
          // Expose the live editor instance on window for E2E testing --
          // simulated keystrokes (Playwright) trigger Monaco's
          // auto-indent-on-Enter for every embedded newline in a pasted
          // block, cascading indentation on multi-line inserts. A real
          // user's actual paste/typing doesn't have this problem; test code
          // calling editor.setValue() directly sidesteps it. Harmless outside
          // a test harness -- nothing reads this window property at runtime.
          window.__tracevizEditor = editor;
        }}
      />
    </div>
  );
}
