---
name: crossprovider codex submodule-dirty-state-makes-parent-repo-diff-non
description: Submodule dirty-state makes parent-repo diff non-reviewable
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [git, review-gates, submodules, merge-blocking]
---

Parent-repo showing only '-dirty' on a submodule reference prevents the actual changes from being reviewed or merged. The submodule must have a committed SHA and be added to parent staging before review; dirty submodules block the entire review gate.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
