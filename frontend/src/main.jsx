import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { HashRouter } from 'react-router-dom'
// Self-hosted via @fontsource (not a Google Fonts CDN link) -- same reason
// Monaco is bundled locally instead of CDN-loaded (see monacoSetup.js):
// this app is meant to clone-and-run fully offline.
import '@fontsource/hanken-grotesk/400.css'
import '@fontsource/hanken-grotesk/500.css'
import '@fontsource/hanken-grotesk/600.css'
import '@fontsource/hanken-grotesk/700.css'
import '@fontsource/hanken-grotesk/800.css'
import '@fontsource/ibm-plex-mono/400.css'
import '@fontsource/ibm-plex-mono/500.css'
import '@fontsource/ibm-plex-mono/600.css'
import '@fontsource/martian-mono/400.css'
import '@fontsource/martian-mono/500.css'
import '@fontsource/martian-mono/600.css'
import '@fontsource/martian-mono/700.css'
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
