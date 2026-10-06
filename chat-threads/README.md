# chat-threads — Session Reference Library

> **Purpose:** Preserves chat sessions as structured, reusable context documents.
> Each file captures decisions made, rationale, key outputs, and open items from a session.
> Load the relevant thread before starting new work to avoid re-establishing context from scratch.

---

## Contents

| File | Session | Key Topics |
|---|---|---|
| `session-00-original-transcript.txt` | 2026-09-14 | Raw visible conversation log from the original prototype session |
| `session-01-prototype-and-live-transcribe.md` | 2026-09-14 | Prototype build, Web Speech API, Live Transcribe feature, project packaging |
| `session-02-production-strategy.md` | 2026-09-14 | Evaluation, tab visibility, executive polish, scaffold, resource planning, implementation |

---

## How to Use

When starting a new session that builds on prior work:

1. Open the relevant thread file.
2. Share it with Bob as context at the start of the session ("here is the prior session context").
3. Bob will use it to avoid re-asking decided questions and maintain continuity.
4. At the end of the session, update or create a new thread file capturing what changed.

---

## Thread File Format

Each file follows this structure:

```
# Session NN — Title
Date | Status | Phase

## What Was Decided
## What Was Built / Changed
## Key Rationale
## Open Items / Carry-Forward
## File Index (what files were created or modified)
```
