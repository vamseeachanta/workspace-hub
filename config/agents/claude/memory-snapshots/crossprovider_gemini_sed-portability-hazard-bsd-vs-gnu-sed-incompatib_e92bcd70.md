---
name: crossprovider gemini sed-portability-hazard-bsd-vs-gnu-sed-incompatib
description: Sed portability hazard: BSD vs GNU sed incompatibility
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [shell-scripting, portability, gotcha]
---

BSD sed (macOS) and GNU sed (Linux) differ on newline handling in append commands (`a\`) and regex anchoring. Fragile sed replacements can match unintended locations if not properly anchored. For cross-platform shell scripts, prefer awk, Python, or temp-file approaches over sed.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
