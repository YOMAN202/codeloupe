import { NavLink, Routes, Route } from "react-router-dom";
import CurriculumMap from "./pages/CurriculumMap/CurriculumMap";
import LessonDetail from "./pages/LessonDetail/LessonDetail";
import ProblemBrowser from "./pages/ProblemBrowser/ProblemBrowser";
import ProblemWorkspace from "./pages/ProblemWorkspace/ProblemWorkspace";
import Dashboard from "./pages/Dashboard/Dashboard";
import MistakeJournal from "./pages/MistakeJournal/MistakeJournal";
import Scratchpad from "./pages/Scratchpad/Scratchpad";
import "./App.css";

// Codeloupe's abstract focus-ring mark -- a lens ring with a center point,
// not a literal magnifying glass. Reused as the sidebar logo here and, in
// spirit, as the trace scrubber's "current step" thumb and the amber
// focus-ring styling elsewhere -- see docs/decisions.md for the full
// identity rationale.
function BrandMark({ size = 22 }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" aria-hidden="true">
      <circle cx="10" cy="10" r="7" stroke="var(--teal)" strokeWidth="2" />
      <circle cx="10" cy="10" r="1.6" fill="var(--teal)" />
    </svg>
  );
}

// Navigation order, deliberately reconsidered (was Curriculum -> Problems
// -> Dashboard -> Mistake Journal -> Scratchpad):
//
//   Dashboard -> Curriculum -> Problems -> Mistake Journal -> Scratchpad
//
// Dashboard is now both the landing route ("/") and first in the sidebar.
// It already carries "Today's session" (an adaptive next-thing-to-do
// recommender) plus stats/streak -- it also now surfaces the same
// resume-lesson prompt Curriculum shows (see Dashboard.jsx), making it the
// single most complete answer to "what should I do right now" the moment
// the app opens, rather than requiring a click over from Curriculum first.
// Curriculum keeps its own resume callout for when a learner lands there
// directly (e.g. mid-session, to plan ahead) -- it becomes purely the
// "browse/plan the full 45-day path" page. Problems and Mistake Journal
// keep their relative order per the reviewed suggestion; Scratchpad stays
// last, since it's a free-form utility rather than part of the guided
// learn -> solve -> review loop the other four pages form.
const NAV_ITEMS = [
  { to: "/", label: "Dashboard", end: true },
  { to: "/curriculum", label: "Curriculum" },
  { to: "/problems", label: "Problems" },
  { to: "/mistakes", label: "Mistake Journal" },
  { to: "/scratchpad", label: "Scratchpad & Trace" },
];

function App() {
  return (
    <div className="app-shell">
      <nav className="sidebar">
        <div className="brand">
          <div className="brand-lockup">
            <BrandMark />
            <span className="brand-wordmark">
              code<span className="accent">loupe</span>
            </span>
          </div>
          <p className="brand-tagline">45-day Python + DSA companion</p>
        </div>
        <div className="sidebar-nav">
          {NAV_ITEMS.map((item) => (
            <NavLink key={item.to} to={item.to} end={item.end} className="nav-link">
              <span className="nav-link-dot" aria-hidden="true" />
              {item.label}
            </NavLink>
          ))}
        </div>
      </nav>

      <main className="main-content">
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/curriculum" element={<CurriculumMap />} />
          <Route path="/lessons/:day" element={<LessonDetail />} />
          <Route path="/problems" element={<ProblemBrowser />} />
          <Route path="/problems/:slug" element={<ProblemWorkspace />} />
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/mistakes" element={<MistakeJournal />} />
          <Route path="/scratchpad" element={<Scratchpad />} />
        </Routes>
      </main>
    </div>
  );
}

export default App;
