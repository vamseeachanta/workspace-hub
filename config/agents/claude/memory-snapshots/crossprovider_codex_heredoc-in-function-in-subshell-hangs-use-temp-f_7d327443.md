---
name: crossprovider codex heredoc-in-function-in-subshell-hangs-use-temp-f
description: Heredoc-in-function-in-subshell hangs: use temp file
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [bash, heredoc, background-processes]
---

Writing heredoc inside a function that's spawned as a background subshell (&) can hang on some shells. Workaround: write helper script to mktemp, trap cleanup, exec the helper. Avoids shell escaping horrors.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
