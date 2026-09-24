---
name: crossprovider codex attestation-binding-test-evidence-can-fabricate-
description: Attestation binding: test evidence can fabricate attestation without re-running tools
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [testing, attestation, defect-class, scientific-code]
---

Test manifests that accept self-declared metadata (toolchain versions, mesh counts, load metrics) without binding to actual tool execution enable fabricated attestation. Require complete source provenance (input digests, command argv, measured outputs), not just schema-conformant metadata. Rerun validation inside snapshot or cryptographically bind captured output.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
