---
name: crossprovider codex bootstrap-shell-script-executable-bit-silent-fai
description: Bootstrap shell script executable-bit silent failure
metadata:
  type: reference
  source: codex
  bridged: 2026-07-09
  tags: [bootstrap, git-modes, executable-bits, shell]
---

Bootstrap hooks that check `[[ -x <script> ]]` fail silently if the script is committed as mode 100644 instead of 100755. This breaks symlink installers and leaves commands in PATH unusable. Verify committed executable modes match actual usage via `git ls-tree` before pushing.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
