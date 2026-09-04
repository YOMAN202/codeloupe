import { useState } from "react";
import { NavLink, Routes, Route, useLocation } from "react-router-dom";
import CurriculumMap from "./pages/CurriculumMap/CurriculumMap";
import LessonDetail from "./pages/LessonDetail/LessonDetail";
import ProblemBrowser from "./pages/ProblemBrowser/ProblemBrowser";
import ProblemWorkspace from "./pages/ProblemWorkspace/ProblemWorkspace";
import Dashboard from "./pages/Dashboard/Dashboard";
import MistakeJournal from "./pages/MistakeJournal/MistakeJournal";
import Scratchpad from "./pages/Scratchpad/Scratchpad";
import Learn from "./pages/Learn/Learn";
import ConceptLesson from "./pages/ConceptLesson/ConceptLesson";
import Support from "./pages/Support/Support";
import "./App.css";

// Codeloupe's abstract focus-ring mark -- a lens ring with a center point,
// not a literal magnifying glass. Reused as the sidebar logo here and, in
// spirit, as the trace scrubber's "current step" thumb and the amber
// focus-ring styling elsewhere -- see docs/decisions.md for the full
// identity rationale.
function BrandMark({ size = 22 }) {
  return (
    <svg
      className="brand-mark"
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill="none"
      aria-hidden="true"
    >
      <circle cx="10" cy="10" r="7" stroke="var(--teal)" strokeWidth="2" />
      <circle cx="10" cy="10" r="1.6" fill="var(--teal)" />
    </svg>
  );
}

// The Support nav item's heart. Deliberately a real filled shape, not the
// Unicode "♥" (BLACK HEART SUIT) character used here previously -- that
// glyph reads thin and pointy in most UI fonts and there was no reliable
// way to make it look fuller/rounder without depending on font choice.
// This path (the same well-tested rounded-lobe "favorite" heart shape
// used across most icon sets) gives full, deliberate control over
// plumpness instead. `fill="currentColor"` picks up whatever `color` the
// wrapping .nav-link-heart / .nav-link-short-heart span sets (var(--heart)
// pink), so sizing is the only thing controlled per call site, via CSS on
// each of those two classes -- see App.css.
function HeartIcon() {
  return (
    <svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
      <path d="M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z" />
    </svg>
  );
}

// Navigation order, deliberately reconsidered (was Curriculum -> Problems
// -> Dashboard -> Mistake Journal -> Scratchpad):
//
//   Dashboard -> Learn -> Curriculum -> Problems -> Mistake Journal -> Scratchpad
//
// Dashboard is now both the landing route ("/") and first in the sidebar.
// It already carries "Today's session" (an adaptive next-thing-to-do
// recommender) plus stats/streak -- it also now surfaces the same
// resume-lesson prompt Curriculum shows (see Dashboard.jsx), making it the
// single most complete answer to "what should I do right now" the moment
// the app opens, rather than requiring a click over from Curriculum first.
//
// Learn sits right after Dashboard, before Curriculum: it's a genuinely
// different content type from the day-based Curriculum (concept/pattern
// lessons like "Arrays" or "Two pointers", not a day-by-day schedule), and
// giving it a real nav slot -- rather than burying it inside Curriculum or
// individual problem pages -- is what makes it obvious, per the teaching-
// system brief, that Codeloupe is a learning platform and not just a
// LeetCode-style question list. Everywhere else (problem pages, day
// lessons) links INTO a concept lesson contextually; this is the one place
// to browse all of them. See docs/decisions.md "Teaching system UX
// integration" for why this earned a nav slot rather than reusing Curriculum's.
//
// Curriculum keeps its own resume callout for when a learner lands there
// directly (e.g. mid-session, to plan ahead) -- it becomes purely the
// "browse/plan the full 45-day path" page. Problems and Mistake Journal
// keep their relative order per the reviewed suggestion; Scratchpad stays
// last, since it's a free-form utility rather than part of the guided
// learn -> solve -> review loop the other pages form.
// `short` is what the sidebar falls back to when collapsed to its narrow
// desktop rail (see .sidebar-is-collapsed in App.css) -- picked by hand
// rather than derived from `label` so e.g. "Mistake Journal" reads as "MJ"
// (initials) while a single word like "Dashboard" reads as "Da", instead of
// a generic slice-the-first-N-characters rule producing something less
// recognizable. The full label is still always available as a native
// tooltip (title) and to screen readers (aria-label), collapsed or not.
// `extraActivePaths` covers routes that conceptually belong to a nav item
// but don't share its own URL prefix -- today just Curriculum, whose day
// lesson pages live at /lessons/:day (see NavItem below for how this
// combines with NavLink's own to-based matching, and CurriculumMap.jsx for
// why lesson pages weren't just nested under /curriculum/:day instead:
// each keeps its own simpler route).
const NAV_ITEMS = [
  { to: "/", label: "Dashboard", end: true, short: "Da" },
  { to: "/learn", label: "Learn", short: "Le" },
  { to: "/curriculum", label: "Curriculum", short: "Cu", extraActivePaths: ["/lessons"] },
  { to: "/problems", label: "Problems", short: "Pr" },
  { to: "/mistakes", label: "Mistake Journal", short: "MJ" },
  { to: "/scratchpad", label: "Scratchpad & Trace", short: "Sc" },
];

// Kept entirely separate from NAV_ITEMS above (own array, own row in the
// sidebar, below a divider -- see .sidebar-bottom in App.css) rather than
// appended to it: this is a support/donation link, not part of the guided
// learn -> solve -> review flow the primary six items form, and mixing it
// into that list would visually imply it's another step in that flow.
// `heart: true` swaps its leading glyph for a CSS-colored heart (see
// NavItem) instead of the plain dot the primary six use, so it gets its
// own quiet red/pink identity without touching the rest of the item.
const SUPPORT_NAV_ITEM = { to: "/support", label: "Support Codeloupe", short: "♥", heart: true };

// Shared by both the primary nav list and the support link below so the
// two never drift into two different markup shapes for what is, in every
// way that matters to CSS/collapse behavior, the same kind of link.
// `item.heart` swaps the leading dot/short glyph for the plump HeartIcon
// above (in both its expanded and collapsed-rail slots) instead of the
// dot/mono-initials the primary six use, styled pink via
// .nav-link-heart / .nav-link-short-heart (color, sizing) in App.css.
function NavItem({ item }) {
  // Route-aware, not click-origin-aware: reads the current URL directly
  // (works identically on a client-side nav, a hard refresh, or a direct
  // link), rather than tracking "how the user got here" -- exactly what
  // makes it reliable on refresh/direct navigation. Only Curriculum
  // defines extraActivePaths, so this is a no-op for every other item.
  const location = useLocation();
  const extraActive = item.extraActivePaths?.some((p) => location.pathname.startsWith(p)) ?? false;

  return (
    <NavLink
      to={item.to}
      end={item.end}
      className={({ isActive }) =>
        `nav-link${item.heart ? " nav-link-support" : ""}${isActive || extraActive ? " active" : ""}`
      }
      title={item.label}
      aria-label={item.heart ? `${item.label} (support the project)` : item.label}
    >
      {item.heart ? (
        <span className="nav-link-heart" aria-hidden="true">
          <HeartIcon />
        </span>
      ) : (
        <span className="nav-link-dot" aria-hidden="true" />
      )}
      <span
        className={`nav-link-short${item.heart ? " nav-link-short-heart" : ""}`}
        aria-hidden="true"
      >
        {item.heart ? <HeartIcon /> : item.short}
      </span>
      <span className="nav-link-label">{item.label}</span>
    </NavLink>
  );
}

// Desktop-only "focus mode" affordance: collapsing the sidebar hands its
// ~170px back to the main content (problem text, the now-larger Monaco
// editor, Live Preview, test results, visualizations -- all of which
// benefit from the extra width).
//
// Deliberately PLAIN component state, not persisted to localStorage --
// same reasoning as ProblemWorkspace's livePreviewCollapsed (see that
// file's comment): collapsing is meant to be a temporary, session-scoped
// focus action, not a saved long-term preference. Every fresh page
// load/refresh should always start from the fully expanded default; this
// app used to persist the choice across sessions, but that's exactly the
// behavior being deliberately reverted here. Because App is the actual
// root of the whole single-page app -- it never unmounts while
// navigating between routes, only its <Routes> children swap -- plain
// state here already "remains collapsed only while continuing to use the
// currently loaded session" for free, with zero extra wiring: only an
// actual full page reload resets it, which is exactly the reset trigger
// asked for.
//
// Deliberately NOT wired into the existing @media (max-width: 860px)
// mobile layout at all -- that layout has no JS toggle today and isn't
// asked for one; every collapse-related CSS rule below is scoped to
// desktop widths (see the min-width: 861px block in App.css).
function App() {
  const [collapsed, setCollapsed] = useState(false);

  return (
    <div className={`app-shell${collapsed ? " sidebar-is-collapsed" : ""}`}>
      <nav className="sidebar" id="app-sidebar" aria-label="Main navigation">
        <div className="sidebar-top">
          <div className="brand">
            <div className="brand-lockup">
              <BrandMark />
              <span className="brand-wordmark">
                code<span className="accent">loupe</span>
              </span>
            </div>
            <p className="brand-tagline">Your Python DSA companion</p>
          </div>
          {/* Hidden on the existing mobile layout (see App.css) -- that
              layout has no collapse concept and this control shouldn't
              appear there. A subtle chevron rather than a labeled button:
              the accessible name carries the real meaning for anyone not
              just reading the glyph. */}
          <button
            type="button"
            className="sidebar-toggle"
            onClick={() => setCollapsed((c) => !c)}
            aria-expanded={!collapsed}
            aria-controls="app-sidebar"
            aria-label={collapsed ? "Expand sidebar" : "Collapse sidebar"}
            title={collapsed ? "Expand sidebar" : "Collapse sidebar"}
          >
            <span aria-hidden="true">{collapsed ? "»" : "«"}</span>
          </button>
        </div>
        <div className="sidebar-nav">
          {NAV_ITEMS.map((item) => (
            <NavItem key={item.to} item={item} />
          ))}
        </div>

        {/* Pushed to the bottom of the sidebar column via margin-top: auto
            on desktop (see .sidebar-bottom in App.css); on the mobile
            horizontal layout the sidebar isn't a fixed-height column, so
            it just falls in as its own row below the primary nav instead
            -- still visually separated by the divider either way. */}
        <div className="sidebar-bottom">
          <hr className="sidebar-divider" />
          <NavItem item={SUPPORT_NAV_ITEM} />
        </div>
      </nav>

      <main className="main-content">
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/learn" element={<Learn />} />
          <Route path="/learn/:slug" element={<ConceptLesson />} />
          <Route path="/curriculum" element={<CurriculumMap />} />
          <Route path="/lessons/:day" element={<LessonDetail />} />
          <Route path="/problems" element={<ProblemBrowser />} />
          <Route path="/problems/:slug" element={<ProblemWorkspace />} />
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/mistakes" element={<MistakeJournal />} />
          <Route path="/scratchpad" element={<Scratchpad />} />
          <Route path="/support" element={<Support />} />
        </Routes>
      </main>
    </div>
  );
}

export default App;
