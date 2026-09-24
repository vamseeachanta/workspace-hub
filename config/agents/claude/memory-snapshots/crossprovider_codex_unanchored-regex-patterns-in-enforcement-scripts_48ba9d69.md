---
name: crossprovider codex unanchored-regex-patterns-in-enforcement-scripts
description: Unanchored regex patterns in enforcement scripts enable path-based bypasses
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [security, enforcement-scripts, shell-scripting]
---

Enforcement scripts using unanchored patterns (e.g., `echo "$f" | grep -qE "$SELF"`) to exclude files allow bypasses through path naming. A file like `/tmp/scripts/enforcement/model-id-baseline.txt.py` containing the substring will be excluded from scanning even if it has violations. Use anchored patterns or explicit full-path matching.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
