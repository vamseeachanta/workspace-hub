---
name: crossprovider codex adversarial-privacy-reviews-must-verify-code-mec
description: Adversarial privacy reviews must verify code mechanisms, not plan prose
metadata:
  type: reference
  source: codex
  bridged: 2026-06-23
  tags: [privacy-review, code-audit, control-verification]
---

When reviewing plans with sensitive data controls (e.g., "no raw labels in output"), check whether those controls are backed by actual code/tests or inherited from prior batch patches — do not trust plan prose alone. Example: a plan can promise opaque handles while the updater code still has an `emit_source_label` flag enabled for earlier batches; prior reviews must be checked to confirm patches were applied.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
