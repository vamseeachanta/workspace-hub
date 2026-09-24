---
name: crossprovider codex script-reuse-claims-require-surface-verification
description: Script reuse claims require surface verification, not deference
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [implementation-verification, script-reuse, test-coverage]
---

Plans proposing to 'extend existing scripts' (e.g., `scripts/ingest/mechanical_extract.py`) without verifying the scripts actually handle the new corpus requirements create implementation gaps. Existing PDF-oriented ingest scripts write hardcoded source paths; reuse for ABS metadata/database/manifest pipelines is not automatic. Claims about existing test coverage for new artifact types must be verified by reading tests, not trusted from plan text.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
