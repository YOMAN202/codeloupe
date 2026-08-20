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
