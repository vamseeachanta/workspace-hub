---
name: crossprovider gemini exit-codes-in-cli-tools-must-distinguish-success
description: Exit codes in CLI tools must distinguish success from automation failures
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [exit-codes, cli-design, automation-friction]
---

Exit code 1 for 'no results' is misinterpreted as failure by shell scripts and CI pipelines. Distinguish: 0 = success (empty or full result set), 2+ = errors. Affects downstream automation: `if ! cmd; then fail` will incorrectly trigger on empty-result 1. Design exit codes upfront with automation consumers in mind.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
