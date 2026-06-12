---
name: crossprovider hermes bash-audit-command-family-extraction-corrupted-b
description: Bash audit command family extraction corrupted by environment prefixes
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [audit, bash-parsing, provider-session-ecosystem]
---

Provider session audit script's bash command normalizer fails to strip leading environment variable assignments (e.g., `WT=/mnt/local-analysis/worktrees/...`) before extracting command families. Polluted reports show variables as command names instead of actual `cmd` field values. Fix: patch helper to detect and remove `VAR=value` prefixes before family classification; classify resulting empty payloads separately.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
