---
name: crossprovider codex mutable-source-toctou-validate-original-convert-
description: Mutable-source TOCTOU: validate original, convert original, attest copy → race window
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [file-handling, toctou, race-condition, pipeline-safety]
---

Validating source A, converting from A later, and attesting the output's hash creates a window where concurrent mutation of A goes undetected. Fix: validate and hash the staged copy once, run conversion against that exact file, derive attestation from staged digest. Generalizes to any multi-stage file-transformation pipeline.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
