---
name: crossprovider codex untracked-artifact-handling-in-legal-security-ga
description: Untracked artifact handling in legal/security gates creates late-stage blockers
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [CI, legal, governance]
---

When gates use `--diff-only` flags but fail on untracked public-surface files, this is discovered late (during closeout/review) rather than early. Consistency rules (e.g., whether untracked files are DENY or ignored) should be explicit and tested before approval.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
