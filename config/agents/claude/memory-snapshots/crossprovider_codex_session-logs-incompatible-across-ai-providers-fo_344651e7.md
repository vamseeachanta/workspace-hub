---
name: crossprovider codex session-logs-incompatible-across-ai-providers-fo
description: Session logs incompatible across AI providers for WRK tracking
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [cross-provider-logging, orchestration-analytics, work-tracking]
---

Claude JSONL has no structured WRK-ID tracking (appears only in message content), Codex uses flat shared daily logs, Gemini has native store only. Cross-provider analytics require post-hoc message parsing for work provenance, degrading audit traceability and orchestration assessment accuracy.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
