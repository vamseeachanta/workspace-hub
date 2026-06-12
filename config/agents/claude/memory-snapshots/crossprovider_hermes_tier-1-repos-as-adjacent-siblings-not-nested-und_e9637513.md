---
name: crossprovider hermes tier-1-repos-as-adjacent-siblings-not-nested-und
description: Tier-1 repos as adjacent siblings, not nested under workspace-hub
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [repo-architecture, monorepo-patterns, filesystem-organization]
---

Repository structure should keep tier-1 repos (digitalmodel, assetutilities, llm-wiki, etc.) as adjacent siblings under `/mnt/local-analysis/<repo>`, not nested inside workspace-hub. Reason: avoids nested-git ambiguity, preserves repo autonomy, keeps workspace-hub as pure control/orchestration plane, enables cleaner path-class contracts and simpler parallel worktrees.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
