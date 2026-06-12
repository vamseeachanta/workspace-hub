---
name: crossprovider hermes sensitive-token-scan-required-for-monitoring-evi
description: Sensitive-token scan required for monitoring evidence artifacts
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [security, evidence-hygiene, credential-handling]
---

All monitoring evidence files (JSON, Markdown, logs) must be scanned for unredacted API keys, credentials, tokens before preservation. Redact with `[REDACTED]` if found. Omit GitHub API tokens and session IDs from human-readable evidence unless essential for auditing.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
