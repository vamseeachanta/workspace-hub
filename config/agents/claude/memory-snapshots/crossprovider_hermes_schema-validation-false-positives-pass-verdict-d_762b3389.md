---
name: crossprovider hermes schema-validation-false-positives-pass-verdict-d
description: Schema validation false positives: pass verdict doesn't guarantee content scope
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [artifact-validation, scope-enforcement, test-coverage]
---

Artifact validators can pass while generators emit out-of-scope content (e.g., wikis/raw/**, wikis/**/CLAUDE.md). Validator checking file-list presence ≠ validator checking edge/node eligibility. Scope enforcement must live in *generator* allowlist, and tests must verify that ineligible sources are never emitted, not just that validator rejects them post-hoc.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
