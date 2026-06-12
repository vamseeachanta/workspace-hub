---
name: crossprovider gemini printf-not-echo-for-json-binary-data
description: Printf not echo for JSON/binary data
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [shell-scripting, data-integrity]
---

Shell `echo` can corrupt JSON and binary streams if they contain backslashes or special chars. Use `printf "%s" "$var"` or `printf "%s\n" "$var"` instead. WRK-1090 implementation review flagged echo-based JSON piping as unsafe.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
