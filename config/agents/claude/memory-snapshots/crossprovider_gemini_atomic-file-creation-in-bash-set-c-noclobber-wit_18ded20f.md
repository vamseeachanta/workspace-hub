---
name: crossprovider gemini atomic-file-creation-in-bash-set-c-noclobber-wit
description: Atomic file creation in Bash: set -C (noclobber) with output redirection
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [concurrency, bash-atomicity, file-operations]
---

bash `set -C` (noclobber) combined with output redirection (`>`) is POSIX-standard for atomic file creation under concurrent access. Pair with 5-retry loop on EEXIST. Restore state with `set +C` immediately after successful reservation to avoid unintended side effects.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
