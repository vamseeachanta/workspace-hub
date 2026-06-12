---
name: crossprovider gemini provider-specific-logging-schema-divergence-no-u
description: Provider-specific logging schema divergence; no unified logging interface
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [logging, orchestration, observability]
---

Session logging varies by provider: Claude uses JSONL with unstructured message bodies (WRK-IDs embedded in text), Codex uses plaintext logs with structured WRK refs, Gemini uses native store only (no named log files). Parsing must be provider-aware; unified schema is missing. This is an architectural debt limiting cross-provider observability.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
