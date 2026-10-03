---
name: cursor-cost-handoff
description: >-
  Cost model and practical guidance for reducing agent-session token use.
  Covers session boundaries, bounded reads, tool-output control, and model
  tiering. Use `compact-chat` when the user wants an actual handoff artifact.
---

# Cursor Cost Handoff

Token cost grows mainly with session length and tool-result size:

```text
cost ≈ turns × context resent per turn
```

A fresh chat with a tight handoff is usually cheaper and clearer than extending
a marathon session.

## Ranked waste

1. Long sessions that resend the full history.
2. Re-reading generated HTML or large source files.
3. Unbounded API, log, database, and CI output.
4. Mixing investigation, implementation, review, and publishing in one chat.
5. Loading large skills or transcripts wholesale.
6. Using a high-cost model for mechanical work.

## Handoff thresholds

- At 60% context: stop broad reads and persist findings.
- At 75%: hand off to a fresh chat.
- At 85%: do not start another implementation step.
- Proxy signals: 40+ assistant turns, 80+ tool calls, or repeated full-file reads.

Use `compact-chat` for COMPACT and RESUME behavior.

## In-turn compression

| Content | Prefer | Avoid |
|---|---|---|
| Source | Search, then bounded line ranges | Re-reading whole large files |
| JSON/API | Selected fields and capped rows | Raw response dumps |
| Logs/CI | Targeted error search and saved logs | Streaming full jobs |
| HTML | Browser inspection and section edits | Whole-file ingestion each pass |
| Exploration | Isolated subagent | Parent chat absorbing every search result |

## Session design

- One ticket or one logical change per chat.
- Separate investigate, implement, and review phases.
- Persist decisions and next steps before switching.
- Start the next session from the handoff, not the entire transcript.
- Use the least expensive model that can complete the phase reliably.

## Local compression proxies

Tools that sit between the editor and model can reduce payloads, but they add
privacy, reliability, and routing risk. Prefer bounded reads and explicit
handoffs first. Evaluate any proxy against organizational policy before use.

## Quick check

Hand off now if any is true:

1. Context is above 60%.
2. The same large file has been read twice.
3. HTML or CI iteration is consuming the chat.
4. The work is moving from investigation to implementation.
5. Tool output is larger than the reasoning needed from it.
