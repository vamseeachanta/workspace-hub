---
name: crossprovider hermes portfolio-repo-scanning-needs-explicit-inventory
description: Portfolio repo scanning needs explicit inventory, not filesystem discovery
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [portfolio-management, multi-repo, inventory]
---

Scanning 20+ repos via os.listdir, file patterns, and .git detection is fragile and slow; fails on submodules, worktrees, and .git-as-file. Maintain explicit repo inventory (YAML or structured doc) instead of discovering via filesystem walks.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
