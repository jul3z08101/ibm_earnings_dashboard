import { useEffect, useState } from 'react';
import { api, Document, LibraryItem, Transcript } from '../lib/api';

const DOC_TYPE_LABELS: Record<string, string> = {
  transcript: 'Transcript', presentation: 'Presentation',
  'press-release': 'Press Release', '8-k': '8-K',
  '10-q': '10-Q', '10-k': '10-K', proxy: 'Proxy', other: 'Other',
};

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

export default function Overview() {
  const [documents, setDocuments]   = useState<Document[]>([]);
  const [transcripts, setTranscripts] = useState<Transcript[]>([]);
  const [library, setLibrary]       = useState<LibraryItem[]>([]);
  const [uploading, setUploading]   = useState(false);
  const [extracting, setExtracting] = useState<number | null>(null);
  const [uploadMsg, setUploadMsg]   = useState('');

  // Upload form state
  const [upCompany, setUpCompany]   = useState('IBM');
  const [upPeriod, setUpPeriod]     = useState(buildQuarters()[0]);
  const [upType, setUpType]         = useState('transcript');
  const [upFile, setUpFile]         = useState<File | null>(null);

  const quarters = buildQuarters();

  const refresh = () => {
    api.documents.list().then(setDocuments).catch(() => {});
    api.transcripts.list().then(setTranscripts).catch(() => {});
    api.library.list().then(setLibrary).catch(() => {});
  };

  useEffect(() => { refresh(); }, []);

  const handleUpload = async () => {
    if (!upFile) { setUploadMsg('Select a file first.'); return; }
    setUploading(true);
    setUploadMsg('');
    try {
      await api.documents.upload(upFile, upCompany, upPeriod, upType);
      setUploadMsg(`Uploaded: ${upFile.name}`);
      setUpFile(null);
      refresh();
    } catch (e) {
      setUploadMsg(`Upload failed: ${(e as Error).message}`);
    } finally {
      setUploading(false);
    }
  };

  const handleExtract = async (docId: number) => {
    setExtracting(docId);
    try {
      const result = await api.documents.extract(docId);
      alert(`Extraction complete — ${result.suggestions.length} items found. Open Transcript Analyzer to review.`);
    } catch (e) {
      alert(`Extraction failed: ${(e as Error).message}`);
    } finally {
      setExtracting(null);
    }
  };

  const handleDeleteDoc = async (docId: number) => {
    if (!confirm('Remove this document?')) return;
    await api.documents.delete(docId);
    refresh();
  };

  const openFlags  = 0; // Placeholder — flags deferred to Phase 3
  const ibmScore   = '—';

  return (
    <div className="container">
      {/* Stats row */}
      <div className="grid-4" style={{ marginBottom: 18 }}>
        <div className="card"><h3>Companies Tracked</h3><div className="stat-val">{COMPANIES.length}</div><div className="stat-sub">IBM + proxy peers</div></div>
        <div className="card"><h3>Compliance Flags</h3><div className="stat-val" style={{ color: '#b91c1c' }}>{openFlags}</div><div className="stat-sub">Open items requiring review</div></div>
        <div className="card"><h3>Library Items</h3><div className="stat-val">{library.length}</div><div className="stat-sub">Extracted measures and KPIs</div></div>
        <div className="card"><h3>Documents Loaded</h3><div className="stat-val">{documents.length}</div><div className="stat-sub">Uploaded to server</div></div>
      </div>

      <div className="grid-2" style={{ marginBottom: 18 }}>
        {/* IBM score */}
        <div className="card">
          <h3>IBM Compliance Score</h3>
          <div style={{ display: 'flex', alignItems: 'center', gap: 14, marginTop: 8 }}>
            <div style={{ width: 64, height: 64, borderRadius: '50%', background: '#e5e7eb', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 18, fontWeight: 700 }}>
              {ibmScore}
            </div>
            <div style={{ flex: 1, fontSize: 13, color: '#57606a' }}>
              Enter compliance flags to generate a score. Flags are available in the Compliance tab (Phase 3).
            </div>
          </div>
        </div>

        {/* Recent transcripts */}
        <div className="card">
          <h3>Recent Transcript Sections</h3>
          {transcripts.length === 0
            ? <span style={{ fontSize: 13, color: '#57606a' }}>No transcripts saved yet.</span>
            : transcripts.slice(0, 4).map(t => (
              <div key={t.id} style={{ padding: '6px 0', borderBottom: '1px solid #f0f2f5', fontSize: 13 }}>
                <strong>{t.company}</strong> · {t.period} · <em>{t.section}</em>
                <span className={`badge ${t.source === 'live' ? 'badge-green' : 'badge-gray'}`} style={{ marginLeft: 6 }}>{t.source}</span>
              </div>
            ))
          }
        </div>
      </div>

      {/* Document upload */}
      <div className="card" style={{ marginBottom: 18 }}>
        <h3>Upload Document</h3>
        <div className="form-row">
          <div>
            <label>Company</label>
            <select value={upCompany} onChange={e => setUpCompany(e.target.value)}>
              {COMPANIES.map(c => <option key={c}>{c}</option>)}
            </select>
          </div>
          <div>
            <label>Quarter</label>
            <select value={upPeriod} onChange={e => setUpPeriod(e.target.value)}>
              {quarters.map(q => <option key={q}>{q}</option>)}
            </select>
          </div>
        </div>
        <div style={{ marginBottom: 12 }}>
          <label>Document Type</label>
          <select value={upType} onChange={e => setUpType(e.target.value)}>
            {Object.entries(DOC_TYPE_LABELS).map(([v, l]) => <option key={v} value={v}>{l}</option>)}
          </select>
        </div>
        <div style={{ marginBottom: 12 }}>
          <label>File (.txt, .pdf, .html — max 20 MB)</label>
          <input type="file" accept=".txt,.pdf,.htm,.html"
            onChange={e => setUpFile(e.target.files?.[0] ?? null)}
            style={{ border: 'none', padding: 0 }} />
        </div>
        <button className="btn btn-primary" onClick={handleUpload} disabled={uploading}>
          {uploading ? <><span className="spinner" />Uploading…</> : 'Upload Document'}
        </button>
        {uploadMsg && <div className="alert alert-info" style={{ marginTop: 10 }}>{uploadMsg}</div>}
      </div>

      {/* Document registry */}
      <div className="card">
        <h3>Document Registry</h3>
        {documents.length === 0
          ? <span className="note">No documents uploaded yet.</span>
          : (
            <table>
              <thead>
                <tr><th>File</th><th>Company</th><th>Period</th><th>Type</th><th>Size</th><th>Uploaded</th><th>Actions</th></tr>
              </thead>
              <tbody>
                {documents.map(d => (
                  <tr key={d.id}>
                    <td><strong>{d.file_name}</strong></td>
                    <td>{d.company}</td>
                    <td>{d.period}</td>
                    <td><span className="badge badge-gray">{DOC_TYPE_LABELS[d.doc_type] ?? d.doc_type}</span></td>
                    <td style={{ color: '#57606a' }}>{d.char_count.toLocaleString()} chars</td>
                    <td style={{ fontSize: 11, color: '#57606a' }}>{new Date(d.uploaded_at).toLocaleString()}</td>
                    <td style={{ whiteSpace: 'nowrap' }}>
                      <button className="btn btn-secondary btn-sm" onClick={() => handleExtract(d.id)} disabled={extracting === d.id}>
                        {extracting === d.id ? 'Extracting…' : 'Extract'}
                      </button>
                      {' '}
                      <button className="btn btn-danger btn-sm" onClick={() => handleDeleteDoc(d.id)}>Del</button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )
        }
      </div>
    </div>
  );
}
