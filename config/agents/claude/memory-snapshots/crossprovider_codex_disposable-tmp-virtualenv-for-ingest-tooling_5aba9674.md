---
name: crossprovider codex disposable-tmp-virtualenv-for-ingest-tooling
description: Disposable /tmp virtualenv for ingest tooling
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [tooling-hygiene, environment-isolation, ingest-pipeline]
---

Keep extraction libraries (pdfplumber, OCR, etc.) in isolated `/tmp` virtualenv rather than polluting repo or user environment. Keeps ingest pipeline and repo dependencies clean.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
