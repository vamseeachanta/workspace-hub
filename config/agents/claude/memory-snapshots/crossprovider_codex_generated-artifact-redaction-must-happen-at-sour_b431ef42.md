---
name: crossprovider codex generated-artifact-redaction-must-happen-at-sour
description: Generated artifact redaction must happen at source
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [pii, generation, ci-gates, redaction]
---

Report/dashboard generators must codename-redact issue titles and repo/path labels before writing tracked HTML/Markdown; regenerated artifacts without source-level redaction reintroduce PII into CI-gated files and fail Client-PII checks, requiring downstream patch + re-scan.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
