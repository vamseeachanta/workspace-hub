---
name: crossprovider hermes nested-repo-artifacts-are-protected-until-classi
description: Nested repo artifacts are protected until classification
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [repo-layout, artifacts, workspace]
---

When moving repo from nested path (workspace-hub) to sibling path (/mnt/local-analysis/), the nested location may contain untracked planning/review artifacts. Mark nested as protected secondary until artifacts are triaged/classified. Don't delete nested copy until all untracked files are accounted for. Sibling path becomes primary working checkout.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
