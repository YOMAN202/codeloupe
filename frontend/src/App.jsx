import { NavLink, Routes, Route } from "react-router-dom";
import CurriculumMap from "./pages/CurriculumMap/CurriculumMap";
import LessonDetail from "./pages/LessonDetail/LessonDetail";
import ProblemBrowser from "./pages/ProblemBrowser/ProblemBrowser";
import ProblemWorkspace from "./pages/ProblemWorkspace/ProblemWorkspace";
import Dashboard from "./pages/Dashboard/Dashboard";
import Scratchpad from "./pages/Scratchpad/Scratchpad";
import "./App.css";

function App() {
  return (
    <div className="app-shell">
      <nav className="sidebar">
        <div className="brand">
          <h1>Traceviz</h1>
          <p className="muted">45-day Python + DSA companion</p>
        </div>
        <NavLink to="/" end className="nav-link">
          Curriculum
        </NavLink>
        <NavLink to="/problems" className="nav-link">
          Problems
        </NavLink>
        <NavLink to="/dashboard" className="nav-link">
          Dashboard
        </NavLink>
        <NavLink to="/scratchpad" className="nav-link">
          Scratchpad &amp; Trace
        </NavLink>
      </nav>

      <main className="main-content">
        <Routes>
          <Route path="/" element={<CurriculumMap />} />
          <Route path="/lessons/:day" element={<LessonDetail />} />
          <Route path="/problems" element={<ProblemBrowser />} />
          <Route path="/problems/:slug" element={<ProblemWorkspace />} />
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/scratchpad" element={<Scratchpad />} />
        </Routes>
      </main>
    </div>
  );
}

export default App;
