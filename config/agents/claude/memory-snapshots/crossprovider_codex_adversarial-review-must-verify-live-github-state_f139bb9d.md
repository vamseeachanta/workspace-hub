---
name: crossprovider codex adversarial-review-must-verify-live-github-state
description: Adversarial review must verify live GitHub state, not plan assertions
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [review, github-issues, verification]
---

When a plan says "live issue #264 is status:pending," the review should fetch the live issue via `gh issue view` rather than trusting the plan's snapshot. Stale status/dependency assertions in the plan text are common and can cascade into incorrect implementation sequencing.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
