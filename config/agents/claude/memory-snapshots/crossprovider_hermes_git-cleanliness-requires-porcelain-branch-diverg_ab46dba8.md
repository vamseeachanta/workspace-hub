---
name: crossprovider hermes git-cleanliness-requires-porcelain-branch-diverg
description: Git cleanliness requires porcelain + branch divergence checks, not porcelain alone
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [git-validation, shared-checkout, divergence-detection]
---

In #2740, initial implementation checked git status --porcelain for dirty/untracked but missed ahead/behind divergence on shared checkouts. Safe execution requires both: `git status --porcelain=v1` (clean working tree) AND `git status --porcelain=v1 --branch` to block if branch line contains 'ahead' or 'behind'.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
