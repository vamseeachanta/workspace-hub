---
name: crossprovider gemini mawk-vs-gawk-regex-capture-groups-are-gawk-only
description: mawk vs gawk: regex capture groups are gawk-only
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [shell-scripting, portability, awk]
---

The `match($0, /regex/, arr)` pattern with capture groups into array `arr` is gawk-specific; mawk (Ubuntu/Debian default) fails silently or errors. Portable alternative: use `index()`, `substr()`, `sub()` for text extraction instead of regex captures in awk.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
