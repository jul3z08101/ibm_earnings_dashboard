import { BrowserRouter, NavLink, Route, Routes } from 'react-router-dom';
import Overview from './pages/Overview';
import LiveTranscribe from './pages/LiveTranscribe';
import TranscriptAnalyzer from './pages/TranscriptAnalyzer';

export default function App() {
  return (
    <BrowserRouter>
      <header className="app-header">
        <div>
          <h1>
            IBM Earnings Transcript Dashboard{' '}
            <span className="header-sub">Technical Accounting &amp; Compliance Review</span>
          </h1>
        </div>
      </header>

      <nav className="app-tabs">
        <NavLink to="/"          end className={({ isActive }) => isActive ? 'tab-btn active' : 'tab-btn'}>Overview</NavLink>
        <NavLink to="/transcribe"     className={({ isActive }) => isActive ? 'tab-btn active' : 'tab-btn'}>Live Transcribe</NavLink>
        <NavLink to="/analyze"        className={({ isActive }) => isActive ? 'tab-btn active' : 'tab-btn'}>Transcript Analyzer</NavLink>
      </nav>

      <main>
        <Routes>
          <Route path="/"           element={<Overview />} />
          <Route path="/transcribe" element={<LiveTranscribe />} />
          <Route path="/analyze"    element={<TranscriptAnalyzer />} />
        </Routes>
      </main>
    </BrowserRouter>
  );
}
