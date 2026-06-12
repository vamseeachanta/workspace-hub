---
name: crossprovider hermes hermes-external-dirs-wiring-pattern-for-repo-eco
description: Hermes external_dirs wiring pattern for repo ecosystem skills
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [hermes, skill-integration, cross-agent]
---

Hermes loads external skills via `skills.external_dirs: []` config. To bridge workspace-hub's 2,734 skills (382 active) to Hermes, patch skill_utils.py to exclude _archive/_internal/_runtime/_core dirs (prevents bloat), then add `/mnt/local-analysis/workspace-hub/.claude/skills` to external_dirs. Patch survives harness updates via config/agents/hermes/patches/.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
