---
name: crossprovider gemini hardcoded-paths-break-cross-machine-portability
description: Hardcoded paths break cross-machine portability
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [shell-scripting, portability, paths]
---

Absolute paths like `/mnt/github/workspace-hub` in shell scripts fail on different machines. Replace with relative resolution: `$(cd "$(dirname "$0")/../.." && pwd)`. Applied across 18 files in commit 7152452.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
