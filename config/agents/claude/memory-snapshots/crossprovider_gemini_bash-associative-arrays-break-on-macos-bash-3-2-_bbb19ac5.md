---
name: crossprovider gemini bash-associative-arrays-break-on-macos-bash-3-2-
description: Bash associative arrays break on macOS Bash 3.2 default
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [bash-scripting, compatibility, macos, environment-specific]
---

WRK-1058: `declare -A` syntax requires Bash 4.0+, but macOS ships with 3.2 by default. Either add explicit version check at top of script or refactor to avoid associative arrays (use parallel string variables or function returns). Critical for cross-platform bash scripts.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
