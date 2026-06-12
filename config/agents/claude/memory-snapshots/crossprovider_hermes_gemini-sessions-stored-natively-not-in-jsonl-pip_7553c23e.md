---
name: crossprovider hermes gemini-sessions-stored-natively-not-in-jsonl-pip
description: Gemini sessions stored natively, not in JSONL pipeline
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [gemini, session-export, provider-parity]
---

Gemini stores native sessions at ~/.gemini/tmp/<project>/chats/session-*.json, not logs/orchestrator/gemini/. The multi-provider session audit only reads JSONL, so Gemini appears absent (0 sessions, 0 records) even when sessions exist. A dedicated exporter (scripts/cron/gemini-session-export.sh) is needed to produce session_YYYYMMDD.jsonl for parity with Claude/Codex/Hermes.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
