---
name: crossprovider hermes provider-ecosystem-audit-metrics-session-volume-
description: Provider ecosystem audit metrics: session volume, post records, and health signals
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [provider-ecosystem, monitoring, audit]
---

The `provider-session-ecosystem-audit.py` script measures provider health by tracking: source (raw_logs), session/file count, post record count, python-performance (python3/1k), uv-python-performance (uv/1k), and health status (red/yellow/green). These metrics expose provider imbalances and performance anomalies across Claude, Codex, Hermes, and Gemini.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
