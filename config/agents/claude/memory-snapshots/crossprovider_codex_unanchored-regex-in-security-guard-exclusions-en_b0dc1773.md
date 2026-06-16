---
name: crossprovider codex unanchored-regex-in-security-guard-exclusions-en
description: Unanchored regex in security guard exclusions enables path-based bypass
metadata:
  type: reference
  source: codex
  bridged: 2026-06-15
  tags: [security-guard, regex-bypass, unanchored-pattern, path-matching]
---

Guard scripts using unanchored `grep -E` patterns to exclude self-referential files can be bypassed via file paths containing the substring. workspace-hub #3060: `echo "$f" | grep -qE "$SELF"` with pattern `scripts/enforcement/model-id-baseline.txt` excludes any path containing that substring, e.g., `model-id-baseline.txt.py`. Attacker or accidental file naming can bypass. Anchor patterns or use full-path matching instead.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
