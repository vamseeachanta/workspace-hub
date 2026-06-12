---
name: crossprovider gemini bash-scripts-use-relative-path-resolution-not-en
description: Bash scripts use relative path resolution, not env vars
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [bash, portability, infrastructure]
---

Script portability requires relative path resolution: `WORKSPACE_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"` instead of env fallbacks like `${WORKSPACE_ROOT:-/mnt/github/workspace-hub}`. Relative resolution works in cron, CI, and multi-machine contexts without configuration; env vars break when not exported or set.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
