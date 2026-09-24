---
name: crossprovider gemini gnu-vs-bsd-command-incompatibilities-surface-dur
description: GNU vs BSD command incompatibilities surface during multi-platform expansion
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [portability, shell-scripting, macos, bsd-compatibility, cross-platform]
---

Shell scripts using GNU-specific flags (sed -i, stat -c) fail on macOS/BSD. Audit all downstream consumers when adding a new platform; portability issues are common gotchas, especially in readiness/monitoring scripts that will now operate on new machine types.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
