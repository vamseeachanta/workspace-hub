---
name: crossprovider gemini script-atomicity-pattern-guard-pre-validate-exit
description: Script atomicity pattern: guard + pre-validate + EXIT trap cleanup
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [scripts, atomicity, queue-management, error-handling]
---

For scripts that modify queue state, use: (1) guard at top checking if already modified (exit 1), (2) pass 1a allocate IDs/build maps with sentinel files, (1b) validate all operations and resolve dependencies, (3) EXIT trap cleans up sentinels on failure, (4) pass 2 disarm trap then do actual writes. Prevents partial writes and orphan files.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
