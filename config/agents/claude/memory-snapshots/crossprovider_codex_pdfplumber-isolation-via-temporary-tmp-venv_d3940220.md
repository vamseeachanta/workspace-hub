---
name: crossprovider codex pdfplumber-isolation-via-temporary-tmp-venv
description: pdfplumber isolation via temporary /tmp venv
metadata:
  type: reference
  source: codex
  bridged: 2026-05-28
  tags: [tooling, dependency-isolation]
---

When pdfplumber not in base environment, create isolated /tmp/ingest-pdf-venv rather than altering repo or user Python. Clean it up after table extraction. Avoids polluting environment and enables stateless repetition.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
