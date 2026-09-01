import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { HashRouter } from 'react-router-dom'
import './index.css'
import App from './App.jsx'

// HashRouter (not BrowserRouter): this app is meant to be run locally
// (`npm run dev` or a plain static build served with any file server) --
// HashRouter needs no server-side SPA-fallback configuration to make
// deep links / refreshes work, which matters a lot for a "clone it and
// run it locally" project.
createRoot(document.getElementById('root')).render(
  <StrictMode>
    <HashRouter>
      <App />
    </HashRouter>
  </StrictMode>,
)
