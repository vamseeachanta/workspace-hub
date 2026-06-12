---
name: crossprovider hermes windows-sibling-repo-path-resolution-bug
description: Windows sibling-repo path resolution bug
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [cross-platform, windows, sibling-repos, path-handling]
---

POSIX string splitting in `tier1_repo_root` fallback fails on Windows paths: `rsplit('/', 1)` applied to `D:\workspace-hub` returns the full path instead of parent `D:\`. Breaks skill discovery on licensed Windows hosts. Fix: explicit `tier1_repo_root` configuration or `PureWindowsPath` handling for cross-platform safety.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
