import { useEffect, useState } from 'react';
import { api, ExtractionSuggestion, LibraryItem, Transcript, TranscriptExtractionResponse } from '../lib/api';

const COMPANIES = ['IBM', 'ACN', 'MSFT', 'GOOGL', 'AMZN', 'ORCL', 'CRM', 'CSCO'];

function buildQuarters(): string[] {
  const now = new Date();
  const curY = now.getFullYear();
  const curQ = Math.ceil((now.getMonth() + 1) / 3);
  const out: string[] = [];
  for (let y = curY; y >= curY - 2; y--) {
    for (let q = (y === curY ? curQ : 4); q >= 1; q--) out.push(`Q${q} ${y}`);
  }
  return out;
}

export default function TranscriptAnalyzer() {
  const [company, setCompany]   = useState('IBM');
  const [period, setPeriod]     = useState(buildQuarters()[0]);
  const [section, setSection]   = useState('');
  const [body, setBody]         = useState('');
  const [status, setStatus]     = useState('');
  const [suggestions, setSuggestions] = useState<ExtractionSuggestion[]>([]);
  const [saved, setSaved]       = useState<Transcript[]>([]);
  const [library, setLibrary]   = useState<LibraryItem[]>([]);
  const [scanning, setScanning] = useState(false);
  const quarters = buildQuarters();

  // Load saved transcripts and library for this company when company changes
  useEffect(() => {
    api.transcripts.list(company).then(setSaved).catch(() => setSaved([]));
    api.library.list(company).then(setLibrary).catch(() => setLibrary([]));
  }, [company]);

  const handleSave = async () => {
    if (!body.trim()) return;
    try {
      const t = await api.transcripts.save({
        company, period,
        section: section || 'Unnamed Section',
        body,
        source: 'manual',
      });
      setSaved(prev => [t, ...prev]);
      setSection('');
      setBody('');
      setStatus('Section saved.');
    } catch {
      setStatus('Save failed — check API connection.');
    }
  };

  const handleAnalyze = async () => {
    if (!body.trim()) return;
    setScanning(true);
    setStatus('');
    setSuggestions([]);
    try {
      // Save the text first to get a transcript ID
      const saved = await api.transcripts.save({
        company, period,
        section: section || 'Analysis Input',
        body,
        source: 'manual',
      });
      setSaved(prev => prev.some(t => t.id === saved.id) ? prev : [saved, ...prev]);

      // Run extraction against the saved transcript
      const result: TranscriptExtractionResponse = await api.transcripts.extract(saved.id);

      // Classify suggestions as New (not in library) vs already known
      const libNorm = new Set(library.map(l => l.name.toLowerCase().replace(/[^a-z0-9]/g, '')));
      const newItems = result.suggestions.filter(
        s => !libNorm.has(s.name.toLowerCase().replace(/[^a-z0-9]/g, ''))
      );
      setSuggestions(newItems);

      const shMsg = result.has_safe_harbor
        ? 'Safe harbor language present.'
        : result.has_fwd_looking
        ? 'Forward-looking terms found — safe harbor language NOT detected.'
        : '';
      setStatus(
        `Analysis complete. ${result.suggestions.length} measure(s) found, ` +
        `${newItems.length} new. ${shMsg} ` +
        `Library contains ${library.length} items for ${company}.`
      );
    } catch {
      setStatus('Analysis failed — check API connection.');
    } finally {
      setScanning(false);
    }
  };

  const handleAcceptToLibrary = async (s: ExtractionSuggestion) => {
    try {
      await api.library.add({
        company: s.company || company,
        name: s.name,
        measure_type: s.measure_type,
        category: s.category,
        periods: s.period || period,
        context: s.contexts[0] || '',
        source_file: s.source_file || '',
        first_seen: s.period || period,
        confidence: 1.0,
      });
      setSuggestions(prev => prev.filter(x => x.name !== s.name));
      api.library.list(company).then(setLibrary);
    } catch {
      alert('Failed to add to library.');
    }
  };

  const loadSection = (t: Transcript) => {
    setCompany(t.company);
    setPeriod(t.period);
    setSection(t.section);
    setBody(t.body);
  };

  return (
    <div className="container">
      <div className="section-title">Transcript Analyzer</div>
      <div className="alert alert-purple">
        Paste transcript text and run an analysis against the company's Reference Library.
        Results classify findings as <strong>Known</strong> (in library),{' '}
        <strong>New</strong> (first appearance), or <strong>Compliance Flag</strong> (requires review).
      </div>

      <div className="grid-2" style={{ marginBottom: 18 }}>
        {/* Entry */}
        <div className="card">
          <h3>Transcript Entry</h3>
          <div className="form-row">
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
          <div style={{ marginBottom: 10 }}>
            <label>Section Title</label>
            <input type="text" value={section} onChange={e => setSection(e.target.value)}
              placeholder="e.g. CFO Prepared Remarks" />
          </div>
          <div style={{ marginBottom: 10 }}>
            <label>Transcript Text</label>
            <textarea value={body} onChange={e => setBody(e.target.value)}
              style={{ minHeight: 220 }} placeholder="Paste transcript text here…" />
          </div>
          <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
            <button className="btn btn-primary" onClick={handleSave}>Save Section</button>
            <button className="btn btn-success" onClick={handleAnalyze} disabled={scanning}>
              {scanning ? <><span className="spinner" />Analyzing…</> : 'Analyze vs. Reference Library'}
            </button>
          </div>
          {status && <div className="alert alert-info" style={{ marginTop: 12 }}>{status}</div>}
        </div>

        {/* Library status + results */}
        <div className="card">
          <h3>Reference Library — {company}</h3>
          {library.length === 0 ? (
            <div className="alert alert-warning">
              No Reference Library items for <strong>{company}</strong> yet.
              Upload documents and accept extracted items to build the library.
            </div>
          ) : (
            <div className="alert alert-success" style={{ marginBottom: 10 }}>
              <strong>{library.length} items</strong> in library —{' '}
              {library.filter(l => l.measure_type === 'nongaap').length} Non-GAAP ·{' '}
              {library.filter(l => l.measure_type === 'kpi').length} KPIs ·{' '}
              {library.filter(l => l.measure_type === 'gaap').length} GAAP
            </div>
          )}

          {suggestions.length > 0 && (
            <>
              <h3 style={{ marginTop: 14 }}>New Items — Pending Review</h3>
              <div className="note" style={{ marginBottom: 8 }}>
                These measures appear in the transcript but are not yet in the library.
              </div>
              {suggestions.map((s, i) => (
                <div key={i} className="scan-item new-item">
                  <span className="scan-item-dot dot-yellow" />
                  <div style={{ flex: 1 }}>
                    <strong>{s.name}</strong>{' '}
                    <span className={`badge ${s.measure_type === 'nongaap' ? 'badge-yellow' : s.measure_type === 'gaap' ? 'badge-blue' : 'badge-gray'}`}>
                      {s.measure_type.toUpperCase()}
                    </span>
                    {s.contexts[0] && (
                      <div style={{ fontSize: 11, color: '#57606a', marginTop: 4, fontStyle: 'italic' }}>
                        "{s.contexts[0].slice(0, 140)}…"
                      </div>
                    )}
                    <div style={{ display: 'flex', gap: 6, marginTop: 6 }}>
                      <button className="btn btn-success btn-sm" onClick={() => handleAcceptToLibrary(s)}>Add to Library</button>
                    </div>
                  </div>
                </div>
              ))}
            </>
          )}
        </div>
      </div>

      {/* Saved sections */}
      <div className="card">
        <h3>Saved Transcript Sections</h3>
        {saved.length === 0 ? (
          <span className="note">No transcript sections saved yet.</span>
        ) : (
          saved.map(t => (
            <div key={t.id} style={{ padding: 12, border: '1px solid #e5e7eb', borderRadius: 4, marginBottom: 10, background: '#f7f8fa' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 6 }}>
                <div>
                  <strong>{t.company}</strong> · {t.period} · <em>{t.section}</em>{' '}
                  <span className={`badge ${t.source === 'live' ? 'badge-green' : 'badge-gray'}`}>{t.source}</span>
                </div>
                <button className="btn btn-secondary btn-sm" onClick={() => loadSection(t)}>Load</button>
              </div>
              <div style={{ fontSize: 12, color: '#374151', maxHeight: 60, overflow: 'hidden' }}>
                {t.body.slice(0, 300)}{t.body.length > 300 ? '…' : ''}
              </div>
              <div style={{ fontSize: 11, color: '#57606a', marginTop: 4 }}>
                Saved: {new Date(t.created_at).toLocaleString()}
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
