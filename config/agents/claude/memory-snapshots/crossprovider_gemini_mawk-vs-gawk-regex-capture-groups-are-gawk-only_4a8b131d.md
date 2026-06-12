---
name: crossprovider gemini mawk-vs-gawk-regex-capture-groups-are-gawk-only
description: mawk vs gawk: regex capture groups are gawk-only
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [shell-scripting, portability]
---

AWK `match($0, /regex/, arr)` capture groups work in gawk but fail in mawk (Ubuntu default). For portable shell JSON extraction, use index()/substr()/sub() instead.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
