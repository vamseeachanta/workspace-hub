---
name: crossprovider codex toctou-in-validate-copy-hash-provenance-workflow
description: TOCTOU in validate-copy-hash provenance workflows
metadata:
  type: reference
  source: codex
  bridged: 2026-07-11
  tags: [provenance, toctou, attestation, manifest-fidelity, transactionality]
---

When source validation, file copying, and digest attestation happen at different times, concurrent replacement between validation and hash can produce manifests that attest to different content than was converted. Validate and hash the same staged copy via single file descriptor (with O_NOFOLLOW to block symlinks); bind all manifests to the staged immutable digest.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
