---
name: crossprovider hermes nested-dual-repo-topology-protected-secondary-wi
description: Nested dual-repo topology: protected secondary with untracked artifacts
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [workspace-topology, nested-repos, repo-management, git-structure]
---

Repos in workspace-hub exist at both `/mnt/local-analysis/<repo>` (primary working checkout) and `/mnt/local-analysis/workspace-hub/<repo>` (secondary containing untracked planning/review artifacts). Never delete the nested secondary until artifacts are triaged; sibling is production checkout. This pattern preserves decision history while allowing independent primary work.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
