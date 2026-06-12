---
name: crossprovider hermes codex-nested-repo-context-drift-submodule-path-p
description: Codex nested_repo_context_drift: submodule path pollution in isolation
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [provider-session-audit, nested-repo-risk, codex, remediation-rules]
---

Sessions in workspace-hub nested-repo contexts (worktrees, subrepos) reference paths relative to parent; when isolated in sandbox, paths break. Remediation rule flags `nested_repo_context_drift` for manual review; occurs in ~61 Codex sessions.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
