---
name: crossprovider gemini bash-4-0-associative-array-incompatibility
description: Bash 4.0+ associative array incompatibility
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [bash, portability]
---

Bash associative arrays (`declare -A`) require version 4.0+. On macOS (ships 3.2 by default), they cause syntax errors. Either require Bash 4.0+ explicitly or refactor to avoid them (e.g., return strings from functions, collect in main loop).

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
