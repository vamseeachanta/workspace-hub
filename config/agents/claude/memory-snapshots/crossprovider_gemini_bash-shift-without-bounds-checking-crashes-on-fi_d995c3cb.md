---
name: crossprovider gemini bash-shift-without-bounds-checking-crashes-on-fi
description: Bash shift without bounds-checking crashes on final argument
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [bash, argument-parsing, robustness]
---

Pattern `--provider) PROVIDER="${2:-all}"; shift 2 ;;` crashes if flag is last arg without value. Validate `[[ -n "${2:-}" ]]` before shift 2, or shift once if flag alone.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
