---
name: crossprovider codex cli-scripts-with-repository-scope-must-have-expl
description: CLI scripts with repository scope must have explicit --repo args, not implicit defaults
metadata:
  type: reference
  source: codex
  bridged: 2026-07-09
  tags: [cli-design, defaults, repo-specificity, safety-gates]
---

Scripts like legal-sanity-scan.sh that operate on repositories default to scanning their own location if no `--repo` argument is given. This causes gates targeting different checkouts to silently scan the wrong directory. Always require explicit `--repo` targeting and verify the correct path is scanned by the gate.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
