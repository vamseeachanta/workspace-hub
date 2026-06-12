---
name: crossprovider hermes digitalmodel-is-a-separate-nested-git-repo-commi
description: digitalmodel is a separate nested git repo — commits must go to nested .git, not parent
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [git, monorepo, digitalmodel, parallel-agents]
---

workspace-hub/.gitignore ignores digitalmodel/ entirely. Commits to files inside digitalmodel/ must use `cd digitalmodel && git commit/push`, not the parent workspace-hub repo. This is structural and affects all parallel multi-agent work targeting digitalmodel packages (orcawave, orcaflex, structural, subsea, etc.).

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
