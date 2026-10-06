import { useEffect, useRef, useState } from 'react';
import { useTranscript } from '../hooks/useTranscript';
import { api } from '../lib/api';

const COMPANIES = ['IBM', 'ACN', 'MSFT', 'GOOGL', 'AMZN', 'ORCL', 'CRM', 'CSCO'];

function buildQuarters(): string[] {
  const now = new Date();
  const curY = now.getFullYear();
  const curQ = Math.ceil((now.getMonth() + 1) / 3);
  const out: string[] = [];
  for (let y = curY; y >= curY - 2; y--) {
    for (let q = (y === curY ? curQ : 4); q >= 1; q--) {
      out.push(`Q${q} ${y}`);
    }
  }
  return out;
}

export default function LiveTranscribe() {
  const [company, setCompany] = useState('IBM');
  const [period, setPeriod]   = useState(buildQuarters()[0]);
  const [section, setSection] = useState('');
  const [lang, setLang]       = useState('en-US');
  const [saveStatus, setSaveStatus] = useState('');
  const outputRef = useRef<HTMLDivElement>(null);

  const { finalText, status, statusLabel, elapsed, wordCount, start, stop, clear, isActive } = useTranscript();

  // Auto-scroll transcript output
  useEffect(() => {
    if (outputRef.current) outputRef.current.scrollTop = outputRef.current.scrollHeight;
  }, [finalText]);

  // Stop recording when component unmounts (user navigates away)
  useEffect(() => () => { if (isActive) stop(); }, [isActive, stop]);

  const handleCopy = () => {
    if (!finalText.trim()) return;
    navigator.clipboard.writeText(finalText).then(
      () => flash(setSaveStatus, 'Copied to clipboard'),
      () => alert('Clipboard unavailable — use Download instead.'),
    );
  };

  const handleDownload = () => {
    if (!finalText.trim()) return;
    const name = [company, period, section.replace(/[^a-z0-9_-]/gi, '_'), new Date().toISOString().slice(0, 10)]
      .filter(Boolean).join('_') + '.txt';
    const a = document.createElement('a');
    a.href = URL.createObjectURL(new Blob([finalText], { type: 'text/plain' }));
    a.download = name;
    a.click();
  };

  const handleSave = async () => {
    if (!finalText.trim()) return;
    try {
      await api.transcripts.save({
        company, period,
        section: section || 'Live Transcription',
        body: finalText,
        source: 'live',
      });
      flash(setSaveStatus, 'Saved to server');
    } catch (e) {
      setSaveStatus('Save failed — check API connection');
    }
  };

  const quarters = buildQuarters();

  return (
    <div className="container">
      <div className="section-title">Live Transcription</div>
      <div className="alert alert-info" style={{ marginBottom: 14 }}>
        Records from your selected microphone input. To transcribe webcasts or meetings
        playing through speakers, enable <strong>Stereo Mix</strong> (Windows) or use{' '}
        <strong>VB-Cable</strong>. Works in <strong>Chrome and Edge</strong> only.
        Audio is processed by Google.
      </div>

      <div className="grid-2" style={{ marginBottom: 18 }}>
        {/* Controls */}
        <div className="card">
          <h3>Recording Controls</h3>
          <div className="form-row" style={{ marginBottom: 14 }}>
            <div>
              <label>Company</label>
              <select value={company} onChange={e => setCompany(e.target.value)}>
                {COMPANIES.map(c => <option key={c}>{c}</option>)}
              </select>
            </div>
            <div>
              <label>Quarter</label>
              <select value={period} onChange={e => setPeriod(e.target.value)}>
                {quarters.map(q => <option key={q}>{q}</option>)}
              </select>
            </div>
          </div>

          <div style={{ marginBottom: 14 }}>
            <label>Section / Label</label>
            <input type="text" value={section} onChange={e => setSection(e.target.value)}
              placeholder="e.g. Q2 2026 Earnings Call — CFO Remarks" />
          </div>

          <div style={{ marginBottom: 14 }}>
            <label>Language</label>
            <select value={lang} onChange={e => setLang(e.target.value)}>
              <option value="en-US">English (US)</option>
              <option value="en-GB">English (UK)</option>
              <option value="en-AU">English (AU)</option>
            </select>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: 12, flexWrap: 'wrap', marginBottom: 16 }}>
            {!isActive
              ? <button className="rec-btn rec-btn-start" onClick={() => start(lang)}>Start Recording</button>
              : <button className="rec-btn rec-btn-stop" onClick={stop}>Stop</button>
            }
            <span className={`status-pill status-${status}`}>{statusLabel}</span>
            <span style={{ fontSize: 13, color: '#57606a', fontVariantNumeric: 'tabular-nums' }}>{elapsed}</span>
          </div>

          <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap', marginBottom: 6 }}>
            <button className="btn btn-secondary btn-sm" onClick={handleCopy}>Copy Transcript</button>
            <button className="btn btn-secondary btn-sm" onClick={handleDownload}>Download .txt</button>
            <button className="btn btn-danger btn-sm" onClick={clear}>Clear</button>
          </div>
          <div className="note">Timestamps are relative to when recording started.</div>

          <hr style={{ margin: '16px 0', border: 'none', borderTop: '1px solid #e5e7eb' }} />
          <h3>Save Transcript</h3>
          <p style={{ fontSize: 13, color: '#57606a', marginBottom: 10 }}>
            Save the finalized transcript to the server for later analysis.
          </p>
          <button className="btn btn-primary" onClick={handleSave}>Save to Server</button>
          {saveStatus && <div style={{ fontSize: 12, color: '#15803d', marginTop: 6 }}>{saveStatus}</div>}
        </div>

        {/* Live output */}
        <div className="card">
          <h3>Live Transcript Output</h3>
          <div style={{ marginBottom: 8, display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <span style={{ fontSize: 12, color: '#57606a' }}>Greyed text = in-progress phrase</span>
            <span style={{ fontSize: 12, color: '#57606a' }}>{wordCount.toLocaleString()} words</span>
          </div>
          <div ref={outputRef} className="transcript-output">
            {finalText || <span style={{ color: '#9ca3af' }}>Transcript will appear here once recording starts…</span>}
          </div>
        </div>
      </div>

      {/* Tips */}
      <div className="card">
        <h3>Setup and Limitations</h3>
        <div className="grid-2" style={{ marginTop: 8, fontSize: 13 }}>
          <div>
            <div style={{ fontWeight: 600, marginBottom: 6 }}>Stereo Mix / VB-Cable (Windows)</div>
            <ol style={{ paddingLeft: 18, color: '#374151', lineHeight: 1.9 }}>
              <li>Right-click speaker icon → <strong>Sound settings</strong></li>
              <li>Go to <strong>Recording</strong> devices tab</li>
              <li>Right-click empty area → <strong>Show Disabled Devices</strong></li>
              <li>Enable <strong>Stereo Mix</strong> → Set as Default</li>
              <li>If unavailable, install <strong>VB-Cable</strong> and set as default input</li>
              <li>Reload this page — the browser will now capture system audio</li>
            </ol>
          </div>
          <div>
            <div style={{ fontWeight: 600, marginBottom: 6 }}>Known Limitations</div>
            <ul style={{ paddingLeft: 18, color: '#374151', lineHeight: 1.9 }}>
              <li>Chrome / Edge only (Firefox not supported)</li>
              <li>Internet required — audio processed by Google</li>
              <li>No speaker identification</li>
              <li>Limited punctuation and capitalization</li>
              <li>Auto-restart handles session timeouts</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}

function flash(setter: (s: string) => void, msg: string, ms = 3000) {
  setter(msg);
  setTimeout(() => setter(''), ms);
}
