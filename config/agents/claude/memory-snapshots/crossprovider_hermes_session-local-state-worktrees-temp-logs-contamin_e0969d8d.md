---
name: crossprovider hermes session-local-state-worktrees-temp-logs-contamin
description: Session-local state (worktrees, temp, logs) contaminates provider audit records
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [provider-audit, session-state, artifact-filtering]
---

Hermes provider logs can include session-scoped transient artifacts: worktree paths, temp directories, local tool outputs. The audit pipeline must filter these with remediation rules (`session_local_worktree_path_drift`, `nested_repo_context_drift`) to prevent noise in cross-session learnings.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
