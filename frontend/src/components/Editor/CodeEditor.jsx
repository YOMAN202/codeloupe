import Editor from "@monaco-editor/react";
import "../../monacoSetup";

export default function CodeEditor({ value, onChange }) {
  return (
    <Editor
      height="360px"
      defaultLanguage="python"
      value={value}
      onChange={(v) => onChange(v ?? "")}
      theme="codeloupe-dark"
      options={{
        fontSize: 14,
        fontFamily: "'IBM Plex Mono', ui-monospace, monospace",
        minimap: { enabled: false },
        scrollBeyondLastLine: false,
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
  );
}
