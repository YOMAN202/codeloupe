import Editor from "@monaco-editor/react";
import "../../monacoSetup";

// Milestone 1: a plain Monaco editor wrapper. No step-highlighting or trace
// overlay yet -- that's added in Milestone 2 once the tracer exists.
export default function CodeEditor({ value, onChange }) {
  return (
    <Editor
      height="360px"
      defaultLanguage="python"
      value={value}
      onChange={(v) => onChange(v ?? "")}
      theme="vs-dark"
      options={{
        fontSize: 14,
        minimap: { enabled: false },
        scrollBeyondLastLine: false,
      }}
    />
  );
}
