---
name: crossprovider gemini file-input-safety-in-shell-scripts
description: File input safety in shell scripts
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [shell, defensive-programming, safety]
---

When reading arbitrary files via `cat` in shell, cap to 5MB (`head -c 5000000`) and strip null bytes (`tr -d '\000'`) to prevent bash OOMs on accidentally provided binaries or huge files.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
