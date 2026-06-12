---
name: crossprovider hermes orchestrator-session-logs-contain-client-names-b
description: Orchestrator session logs contain client names but are internal operational data, not public artifacts
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [legal-compliance, session-logs, exclusion-policy]
---

Session JSONL files log tool calls mentioning client work (e.g., filenames like 'Lakach BoD DRAFT'); these are raw operational logs (like `.claude/state/`), not exported artifacts. Exclude `logs/orchestrator/` from legal scans using directory-prefix patterns.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
