---
name: crossprovider codex untracked-review-artifacts-block-legal-scan-gate
description: Untracked review artifacts block legal-scan gates
metadata:
  type: reference
  source: codex
  bridged: 2026-07-03
  tags: [legal-gate, review-artifacts, git-state]
---

Untracked files in the repo root (review artifacts, findings) are treated as candidate public surfaces by `legal-sanity-scan --diff-only`. Either move them to an `ignore` path (e.g., `scripts/review/results/`) or clean them before pushing.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
