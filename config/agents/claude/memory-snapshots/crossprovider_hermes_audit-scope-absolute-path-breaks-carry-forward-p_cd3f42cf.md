---
name: crossprovider hermes audit-scope-absolute-path-breaks-carry-forward-p
description: Audit scope absolute path breaks carry-forward portability
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [architecture, audit, path-portability, baseline]
---

Audit baseline carry-forward depends on matching audit_scope, and using absolute paths (e.g., `skills_dir.resolve()`) breaks reuse when repo is cloned/checked-out to a different worktree or machine path. Same repo scanned from different paths behaves like first run, losing prior findings. Use relative paths or stable logical identity instead of absolute filesystem paths for audit scope.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
