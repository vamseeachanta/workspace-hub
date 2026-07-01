---
name: crossprovider codex review-skill-is-branch-scoped-artifact-only-chec
description: Review skill is branch-scoped; artifact-only checks need posture adjustment
metadata:
  type: reference
  source: codex
  bridged: 2026-06-28
  tags: [code-review, skill-fitness, artifact-review]
---

The generic `review` skill assumes git-repo context (diffs, blame, branches). For standalone pasted-artifact checks without repo context, disable contextual lookups and apply only the adversarial-verification posture: cross-check supplied artifacts against source directly, no outside sources.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
