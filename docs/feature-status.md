# Feature Status

## Live Transcribe

Fully functional. The entire recording pipeline is wired end-to-end.

- `web/src/hooks/useTranscript.ts` manages the Web Speech API lifecycle (start, stop, auto-restart, elapsed timer, word count)
- `web/src/pages/LiveTranscribe.tsx` renders the controls and calls `api.transcripts.save()` to persist to the server
- The API backend handles `POST /transcripts` and stores to SQLite

**Requirements:** Chrome or Edge + microphone permission granted for `127.0.0.1`.

---

## Transcript Analyzer

Save and load work correctly. The **Analyze** button is partially wired:

- Runs an in-browser safe harbor keyword scan
- Saves the text as a transcript via `POST /transcripts`
- Does **not** call the Python extraction service — `ExtractionSuggestion[]` always stays empty and the "New Items" panel never populates

**Blocker:** A `POST /transcripts/{id}/extract` endpoint (or equivalent text-in endpoint) needs to be added to the API to connect the frontend analyzer to `api/src/services/extraction.py`.

---

## Status Table

| Feature | Status | Notes |
|---|---|---|
| Live recording (start / stop / auto-restart) | Working | Chrome and Edge only |
| Save transcript to server | Working | API must be running |
| Load saved transcript sections | Working | — |
| Safe harbor keyword check | Working | In-browser only |
| Extraction vs. Reference Library | Not connected | Missing extract endpoint for raw text |
| New Items suggestions panel | Not populated | Depends on extraction result |
| Add suggestion to library | Working | Depends on suggestions being populated first |
