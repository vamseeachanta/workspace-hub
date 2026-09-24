---
name: crossprovider codex generated-artifacts-must-carry-provenance-self-c
description: Generated artifacts must carry provenance self-contained
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [artifact-design, provenance, metadata]
---

Each output (page, CSV row, log entry, report) should embed source_id, citation, revision, artifact SHA, and provenance level rather than relying on external files or reader knowledge. Self-contained metadata survives repo copies, archival, and handoff.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
