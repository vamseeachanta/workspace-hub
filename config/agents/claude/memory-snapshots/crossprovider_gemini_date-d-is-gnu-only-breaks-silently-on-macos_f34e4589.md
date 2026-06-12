---
name: crossprovider gemini date-d-is-gnu-only-breaks-silently-on-macos
description: date -d is GNU-only; breaks silently on macOS
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [portability, bash, date-parsing]
---

Bash `date -d` is a Coreutils extension. On BSD/macOS, it's an invalid flag. When stderr is redirected (e.g., `2>/dev/null`), it fails silently, leaving variables empty and breaking downstream logic. Require OS detection + fallback: `date -j -f` on Darwin.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
