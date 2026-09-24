---
name: crossprovider codex adversarial-review-artifacts-accumulate-in-scrip
description: Adversarial review artifacts accumulate in scripts/review/results/ with dated, provider-specific outputs
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [review-governance, artifact-location, approval-chain]
---

Cross-provider adversarial reviews (Claude, Codex, Gemini) store their outputs at `scripts/review/results/<date>-plan-<issue>-<provider>.md` or `<date>-<issue>-final.md`. These artifacts are referenced in plan files and linked into the approval chain. Keep this location stable for future plan retrieval and cross-review evidence auditing.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
