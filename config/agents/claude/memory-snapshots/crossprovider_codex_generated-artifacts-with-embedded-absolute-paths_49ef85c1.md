---
name: crossprovider codex generated-artifacts-with-embedded-absolute-paths
description: Generated artifacts with embedded absolute paths become stale in worktree execution contexts
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [artifact-drift, generated-artifacts, path-canonicalization, worktree-execution, code-generation]
---

JSON/YAML audit and report files embedding absolute repo paths (e.g., 'repo_root': '/mnt/local-analysis/workspace-hub') capture the generation environment's context. When execution context changes from direct checkout to worktree ('/mnt/local-analysis/worktrees/workspace-hub-2657'), paths in the artifact become environment-specific and require explicit regeneration, not just path substitution in diffs.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
