/**
 * api.ts — Typed API client.
 * All requests go through /api/* which Vite proxies to http://127.0.0.1:8000 in dev.
 */

const BASE = '/api';

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    headers: { 'Content-Type': 'application/json', ...options?.headers },
    ...options,
  });
  if (!res.ok) {
    const detail = await res.text();
    throw new Error(`API ${res.status}: ${detail}`);
  }
  // 204 No Content — return null
  if (res.status === 204) return null as T;
  return res.json();
}

// ── Types ─────────────────────────────────────────────────────────────────────

export interface Document {
  id: number;
  company: string;
  period: string;
  doc_type: string;
  file_name: string;
  char_count: number;
  uploaded_at: string;
}

export interface Transcript {
  id: number;
  company: string;
  period: string;
  section: string;
  body: string;
  source: string;
  created_at: string;
}

export interface LibraryItem {
  id: number;
  company: string;
  name: string;
  measure_type: string;
  category: string;
  periods: string;
  context: string;
  source_file: string;
  first_seen: string;
  confidence: number;
  created_at: string;
}

export interface ExtractionSuggestion {
  name: string;
  measure_type: string;
  category: string;
  contexts: string[];
  company: string;
  period: string;
  source_file: string;
  operating_reclassified: boolean;
}

export interface ExtractionResponse {
  doc_id: number;
  suggestions: ExtractionSuggestion[];
}

export interface TranscriptExtractionResponse {
  transcript_id: number;
  has_safe_harbor: boolean;
  has_fwd_looking: boolean;
  suggestions: ExtractionSuggestion[];
}

// ── Documents ─────────────────────────────────────────────────────────────────

export const api = {
  documents: {
    list(company?: string): Promise<Document[]> {
      const q = company ? `?company=${encodeURIComponent(company)}` : '';
      return request(`/documents${q}`);
    },
    upload(file: File, company: string, period: string, docType: string): Promise<Document> {
      const form = new FormData();
      form.append('file', file);
      form.append('company', company);
      form.append('period', period);
      form.append('doc_type', docType);
      return request('/documents', {
        method: 'POST',
        headers: {},     // Let browser set multipart boundary
        body: form,
      });
    },
    extract(docId: number): Promise<ExtractionResponse> {
      return request(`/documents/${docId}/extract`, { method: 'POST' });
    },
    delete(docId: number): Promise<null> {
      return request(`/documents/${docId}`, { method: 'DELETE' });
    },
  },

  // ── Transcripts ─────────────────────────────────────────────────────────────

  transcripts: {
    list(company?: string): Promise<Transcript[]> {
      const q = company ? `?company=${encodeURIComponent(company)}` : '';
      return request(`/transcripts${q}`);
    },
    save(payload: Omit<Transcript, 'id' | 'created_at'>): Promise<Transcript> {
      return request('/transcripts', { method: 'POST', body: JSON.stringify(payload) });
    },
    extract(id: number): Promise<TranscriptExtractionResponse> {
      return request(`/transcripts/${id}/extract`, { method: 'POST' });
    },
    delete(id: number): Promise<null> {
      return request(`/transcripts/${id}`, { method: 'DELETE' });
    },
  },

  // ── Library ──────────────────────────────────────────────────────────────────

  library: {
    list(company?: string, measureType?: string): Promise<LibraryItem[]> {
      const params = new URLSearchParams();
      if (company) params.set('company', company);
      if (measureType) params.set('measure_type', measureType);
      const q = params.toString() ? `?${params}` : '';
      return request(`/library${q}`);
    },
    add(payload: Omit<LibraryItem, 'id' | 'created_at'>): Promise<LibraryItem> {
      return request('/library', { method: 'POST', body: JSON.stringify(payload) });
    },
    delete(id: number): Promise<null> {
      return request(`/library/${id}`, { method: 'DELETE' });
    },
  },
};
