/**
 * useTranscript.ts — Web Speech API state management hook.
 * Encapsulates all recognition lifecycle logic from the prototype's lt object.
 */

// Web Speech API types are not included in the default TypeScript lib.
// Declare the minimum surface needed so the compiler is satisfied without
// pulling in a third-party types package.
declare global {
  interface Window {
    SpeechRecognition: new () => ISpeechRecognition;
    webkitSpeechRecognition: new () => ISpeechRecognition;
  }
}

interface ISpeechRecognitionEvent {
  readonly resultIndex: number;
  readonly results: SpeechRecognitionResultList;
}

interface ISpeechRecognitionErrorEvent {
  readonly error: string;
}

interface ISpeechRecognition extends EventTarget {
  continuous: boolean;
  interimResults: boolean;
  lang: string;
  onstart: (() => void) | null;
  onresult: ((e: ISpeechRecognitionEvent) => void) | null;
  onerror: ((e: ISpeechRecognitionErrorEvent) => void) | null;
  onend: (() => void) | null;
  start(): void;
  stop(): void;
}

import { useCallback, useRef, useState } from 'react';

type Status = 'idle' | 'listening' | 'paused' | 'error';

interface TranscriptState {
  finalText: string;
  status: Status;
  statusLabel: string;
  elapsed: string;
  wordCount: number;
}

interface UseTranscriptReturn extends TranscriptState {
  start: (lang: string) => void;
  stop: () => void;
  clear: () => void;
  isActive: boolean;
}

const RESTART_DELAY_MS = 200;

function elapsedLabel(startTime: number): string {
  const s = Math.floor((Date.now() - startTime) / 1000);
  const m = Math.floor(s / 60);
  return `${m}:${String(s % 60).padStart(2, '0')}`;
}

export function useTranscript(): UseTranscriptReturn {
  const [state, setState] = useState<TranscriptState>({
    finalText: '',
    status: 'idle',
    statusLabel: 'Idle',
    elapsed: '',
    wordCount: 0,
  });

  const recognitionRef = useRef<ISpeechRecognition | null>(null);
  const activeRef      = useRef(false);
  const startTimeRef   = useRef<number | null>(null);
  const timerRef       = useRef<ReturnType<typeof setInterval> | null>(null);
  const finalTextRef   = useRef('');

  const setStatus = (status: Status, label: string) => {
    setState(prev => ({ ...prev, status, statusLabel: label }));
  };

  const buildRecognition = useCallback((lang: string): ISpeechRecognition => {
    const SR = window.SpeechRecognition ?? window.webkitSpeechRecognition;
    const r: ISpeechRecognition = new SR();
    r.continuous     = true;
    r.interimResults = true;
    r.lang           = lang;

    r.onstart = () => setStatus('listening', 'Listening');

    r.onresult = (e: ISpeechRecognitionEvent) => {
      let interim = '';
      for (let i = e.resultIndex; i < e.results.length; i++) {
        const t = e.results[i][0].transcript;
        if (e.results[i].isFinal) {
          const ts = startTimeRef.current ? elapsedLabel(startTimeRef.current) : '0:00';
          finalTextRef.current += `[${ts}] ${t.trim()}\n`;
          interim = '';
        } else {
          interim += t;
        }
      }
      const words = finalTextRef.current.trim()
        ? finalTextRef.current.trim().split(/\s+/).length
        : 0;
      setState(prev => ({ ...prev, finalText: finalTextRef.current, wordCount: words }));
    };

    r.onerror = (e: ISpeechRecognitionErrorEvent) => {
      if (e.error === 'not-allowed' || e.error === 'service-not-allowed') {
        setStatus('error', 'Mic permission denied');
        activeRef.current = false;
        return;
      }
      if (e.error === 'no-speech') return;
      setStatus('paused', e.error);
    };

    r.onend = () => {
      if (activeRef.current) {
        setStatus('paused', 'Restarting…');
        setTimeout(() => {
          if (activeRef.current) {
            recognitionRef.current = buildRecognition(lang);
            try { recognitionRef.current.start(); } catch { /* already started */ }
          }
        }, RESTART_DELAY_MS);
      } else {
        setStatus('idle', 'Idle');
      }
    };

    return r;
  }, []);

  const start = useCallback((lang: string) => {
    const SR = window.SpeechRecognition ?? window.webkitSpeechRecognition;
    if (!SR) {
      alert('Live transcription requires Chrome or Edge. Firefox is not supported.');
      return;
    }
    if (activeRef.current) return;

    activeRef.current = true;
    if (!startTimeRef.current) startTimeRef.current = Date.now();

    timerRef.current = setInterval(() => {
      if (startTimeRef.current) {
        setState(prev => ({ ...prev, elapsed: `Elapsed: ${elapsedLabel(startTimeRef.current!)}` }));
      }
    }, 1000);

    recognitionRef.current = buildRecognition(lang);
    try {
      recognitionRef.current.start();
    } catch (err) {
      setStatus('error', `Could not start: ${(err as Error).message}`);
      activeRef.current = false;
    }
  }, [buildRecognition]);

  const stop = useCallback(() => {
    activeRef.current = false;
    if (recognitionRef.current) {
      try { recognitionRef.current.stop(); } catch { /* already stopped */ }
      recognitionRef.current = null;
    }
    if (timerRef.current) {
      clearInterval(timerRef.current);
      timerRef.current = null;
    }
    setStatus('idle', 'Idle');
  }, []);

  const clear = useCallback(() => {
    finalTextRef.current = '';
    startTimeRef.current = null;
    if (timerRef.current) { clearInterval(timerRef.current); timerRef.current = null; }
    setState(prev => ({ ...prev, finalText: '', wordCount: 0, elapsed: '' }));
  }, []);

  return { ...state, start, stop, clear, isActive: activeRef.current };
}
