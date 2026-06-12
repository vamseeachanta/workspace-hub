---
name: crossprovider hermes ai-review-enforcement-policy-document-lag
description: AI review enforcement policy document lag
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [policy-lag, documentation, review-gates]
---

AI_REVIEW_ROUTING_POLICY.md states 'currently advisory (Level 0 — Prose)' but Level 3 hooks are already deployed: cross-review-gate.sh wired into .claude/settings.json PreToolUse matcher. When enforcement level changes, policy docs must be updated or reviewers believe it's not enforced.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
