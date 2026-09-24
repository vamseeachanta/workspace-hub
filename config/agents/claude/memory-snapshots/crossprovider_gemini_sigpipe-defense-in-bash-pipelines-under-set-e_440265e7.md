---
name: crossprovider gemini sigpipe-defense-in-bash-pipelines-under-set-e
description: SIGPIPE defense in bash pipelines under set -e
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [bash, set-e, piping, sigpipe]
---

Piping to `head` (e.g., `echo "$var" | head -n N`) in a `set -eo pipefail` script causes premature exit on pipe closure. Use `printf '%s\n' "$var" | head -n N || true` instead to gracefully handle the expected SIGPIPE.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
