---
name: crossprovider gemini shell-awk-portability-gawk-only-capture-groups-f
description: Shell awk portability: gawk-only capture groups fail on mawk
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [shell-scripting, portability, awk]
---

`match($0, /regex/, arr)` with capture groups is gawk-only; mawk (Ubuntu/Debian default) fails silently. Use `index()` + `substr()` + `sub()` for portable regex extraction in shell scripts. Check with `awk --version` if uncertain.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
