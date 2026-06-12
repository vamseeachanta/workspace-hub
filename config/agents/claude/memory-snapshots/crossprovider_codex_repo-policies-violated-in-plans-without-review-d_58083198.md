---
name: crossprovider codex repo-policies-violated-in-plans-without-review-d
description: Repo policies violated in plans without review detection
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [policy, enforcement, review]
---

Plans contradict repo-level policies (e.g., AGENTS.md says 'uv run always' but plan TDD uses bare python3) without review catching it. Explicitly check policies during adversarial review.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
