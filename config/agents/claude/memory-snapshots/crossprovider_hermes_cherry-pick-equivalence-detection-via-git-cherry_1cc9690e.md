---
name: crossprovider hermes cherry-pick-equivalence-detection-via-git-cherry
description: Cherry-pick equivalence detection via git cherry; empty commits signal upstream absorption
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [git, cherry-pick, commit-analysis, verification]
---

Use `git cherry` to find patch equivalence across branches. Empty cherry-pick results indicate the change was already applied upstream in equivalent form. Diff the parent of the attempted commit against the remote to confirm upstream inclusion.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
