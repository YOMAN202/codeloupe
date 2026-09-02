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

// Fix for a real bug, not a hypothetical one: the editor's cursor visibly
// drifts left of the actual last-typed character, worse the more you type,
// and eventually can't track typing/clicks correctly at all. Root cause:
// "IBM Plex Mono" (this editor's configured fontFamily, see CodeEditor.jsx)
// is self-hosted via @fontsource and imported in main.jsx as plain CSS --
// its @font-face rules use font-display: swap (see
// node_modules/@fontsource/ibm-plex-mono/400.css), so the browser paints
// with a fallback font FIRST and swaps to the real one only once its .woff2
// file finishes downloading, typically tens to a couple hundred ms after
// first paint, and Monaco mounts (and does its one-time, cached
// per-character width measurement) well before that swap happens on a cold
// load. Monaco positions the cursor/selection by MATH -- character index
// times that cached measured width -- not by asking the DOM where the
// glyph actually landed, so once the real IBM Plex Mono font swaps in with
// even slightly different metrics than the fallback that was actually
// measured, every subsequent character adds a fixed error that never
// self-corrects on its own. That's exactly the "falls further behind with
// every keystroke, cursor can't keep up" symptom -- it's a stale-
// measurement bug, not a CSS/zoom/layout issue (which is why nothing
// turned up searching for transform/zoom/letter-spacing).
//
// monaco.editor.remeasureFonts() (present in this monaco-editor version,
// 0.56.0) is Monaco's own API for this: it clears Monaco's cached
// per-character-width measurements (see
// node_modules/monaco-editor/.../standaloneEditor.js's remeasureFonts,
// which is literally `FontMeasurements.clearAllFontInfos()`). That's
// necessary but NOT sufficient on its own -- clearing the cache doesn't
// itself make any ALREADY-MOUNTED editor recompute and re-render; a
// mounted editor only re-reads font info when its configuration actually
// changes. Confirmed empirically (see cursor_drift_check.mjs run against a
// throttled font load): calling remeasureFonts() alone left the drift
// fully intact after the real font swapped in, because nothing told the
// already-open editor(s) to look at the now-cleared cache. The fix is
// remeasureFonts() PLUS nudging every currently-open editor's
// configuration (re-applying its own fontFamily is a no-op for the actual
// font choice but IS a configuration change, which is what makes Monaco
// recompute FontInfo and re-render the cursor/text at the correct
// position) -- monaco.editor.getEditors() is the global registry of every
// standalone editor instance, so this reaches every editor on the page
// without CodeEditor.jsx or any page needing its own per-instance fix.
//
// document.fonts.addEventListener("loadingdone", ...) (rather than the
// one-shot .ready promise) is what actually triggers this: `.ready`
// resolves exactly once for whatever was already pending the first time
// something reads it, but a fresh page load can very plausibly have
// nothing pending yet at the instant this module evaluates (before
// React/Monaco have rendered anything that would request the font),
// which would resolve `.ready` immediately and fire the fix too early --
// before the real (possibly slow/cold-cache) font request has even
// started. "loadingdone" fires every time a batch of font loads actually
// completes, however many times that happens, so it reliably catches the
// swap whenever it really occurs instead of racing page-load order.
function refreshMountedEditorFonts() {
  monaco.editor.remeasureFonts();
  for (const editor of monaco.editor.getEditors()) {
    const fontFamily = editor.getRawOptions().fontFamily;
    editor.updateOptions({ fontFamily });
  }
}
if (typeof document !== "undefined" && document.fonts) {
  document.fonts.addEventListener("loadingdone", refreshMountedEditorFonts);
}

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