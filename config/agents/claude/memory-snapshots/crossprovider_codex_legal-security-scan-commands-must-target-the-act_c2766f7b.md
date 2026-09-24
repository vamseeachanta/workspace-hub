---
name: crossprovider codex legal-security-scan-commands-must-target-the-act
description: Legal/security scan commands must target the actual checkout being reviewed
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [git-worktree, security-scanning, command-correctness]
---

Using workspace-level script paths (e.g., `workspace-hub/scripts/legal/legal-sanity-scan.sh`) from a linked worktree produces 'Repository not found' errors because the resolver expects the workspace structure. Scans must either be run from the primary checkout or target the actual worktree path explicitly. Test the command form against the actual checkout before including in a plan.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
