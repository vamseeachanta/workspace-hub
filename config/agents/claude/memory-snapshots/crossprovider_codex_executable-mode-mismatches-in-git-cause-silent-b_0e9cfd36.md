---
name: crossprovider codex executable-mode-mismatches-in-git-cause-silent-b
description: Executable mode mismatches in git cause silent bootstrap failures
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [git-permissions, bootstrap, shell-scripts]
---

Scripts committed as `100644` when they should be `100755` cause checks like `[[ -x /path/to/script ]]` to silently skip installation. Symlinks to non-executable scripts become unusable on the PATH. Always verify `git ls-tree` modes for scripts intended to run directly, or remove `-x` checks and invoke with explicit `bash script.sh` instead.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
