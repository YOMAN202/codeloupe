// Wire up Monaco's web worker using Vite's built-in `?worker` import
// syntax, and point @monaco-editor/react at the locally-bundled
// `monaco-editor` package instead of its default CDN loader.
//
// Why this exists: @monaco-editor/react fetches Monaco from
// cdn.jsdelivr.net by default, which this sandboxed environment's network
// doesn't allow (see docs/decisions.md). A locally-bundled editor is also
// simply the right choice for a tool meant to run offline on your own
// machine, so this isn't a workaround we'd want to undo later.
import * as monaco from "monaco-editor";
import { loader } from "@monaco-editor/react";
// Note: monaco-editor's package.json "exports" map already rewrites
// "monaco-editor/*" to "./esm/vs/*.js" internally, so the subpath below
// must NOT repeat the "esm/vs" prefix (that would double it and fail to
// resolve -- confirmed by inspecting node_modules/monaco-editor/package.json).
import EditorWorker from "monaco-editor/editor/editor.worker.js?worker";

self.MonacoEnvironment = {
  getWorker() {
    // We only use Python's built-in Monarch grammar (bundled with
    // monaco-editor core, no language server needed), so every request
    // can be served by the generic editor worker.
    return new EditorWorker();
  },
};

loader.config({ monaco });

// A Monaco theme drawn from the same tokens as the rest of the app
// (App.css's :root) instead of the stock "vs-dark", so the editor reads
// as part of Codeloupe rather than a generic embedded widget dropped on
// top of it. Kept intentionally simple -- a handful of token colors, not
// a full syntax-highlight redesign.
monaco.editor.defineTheme("codeloupe-dark", {
  base: "vs-dark",
  inherit: true,
  rules: [
    { token: "comment", foreground: "7a8492", fontStyle: "italic" },
    { token: "keyword", foreground: "8a7bff" },
    { token: "string", foreground: "43d17a" },
    { token: "number", foreground: "f2b134" },
    { token: "type", foreground: "5fb0e6" },
    { token: "identifier", foreground: "eef1f5" },
  ],
  colors: {
    "editor.background": "#171b22",
    "editor.foreground": "#eef1f5",
    "editor.lineHighlightBackground": "#1e232c",
    "editor.lineHighlightBorder": "#00000000",
    "editorCursor.foreground": "#2fd0b7",
    "editorLineNumber.foreground": "#7a8492",
    "editorLineNumber.activeForeground": "#9aa3b2",
    "editor.selectionBackground": "#2fd0b733",
    "editorIndentGuide.background": "#242a34",
    "editorIndentGuide.activeBackground": "#333b47",
    "editorWidget.background": "#11141a",
    "editorWidget.border": "#242a34",
  },
});
