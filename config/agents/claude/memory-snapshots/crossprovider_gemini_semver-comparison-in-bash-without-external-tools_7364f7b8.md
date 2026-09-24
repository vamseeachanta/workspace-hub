---
name: crossprovider gemini semver-comparison-in-bash-without-external-tools
description: Semver comparison in bash without external tools: sort -V with head
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [bash, version-management, no-deps]
---

Compare semver strings using `printf '%s\n%s' "$a" "$m" | sort -V | head -1`. If the result equals the minimum, actual >= minimum. Handles suffixes (e.g., -rc1) by stripping non-digit prefixes first with sed.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
