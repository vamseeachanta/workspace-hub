---
name: crossprovider codex pre-completion-cleanup-audit-is-non-negotiable
description: Pre-completion cleanup audit is non-negotiable
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [cleanup, workflow-hygiene, completion-gate]
---

Before claiming any task complete, run the workspace's mandatory pre-completion cleanup audit (CLEAN/EXPECTED/UNEXPECTED triage) to surface unintended residue (orphan stashes, scratch directories, dirty worktrees). Sessions repeatedly accumulate sibling-repo state and abandoned lock/trash that forces heavyweight later remediation.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
