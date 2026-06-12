---
name: crossprovider codex pdfplumber-install-to-tmp-when-system-unavailabl
description: pdfplumber install to /tmp when system unavailable
metadata:
  type: reference
  source: codex
  bridged: 2026-05-28
  tags: [sandbox-tooling, pdf-extraction, environment-constraint]
---

When pdfplumber is not available in the active Python environment (e.g., read-only home paths in sandbox), install it to a throwaway `/tmp` virtualenv and set PYTHONPATH for the ingest session. Avoids polluting the repo or system, keeps the ingest isolated.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
