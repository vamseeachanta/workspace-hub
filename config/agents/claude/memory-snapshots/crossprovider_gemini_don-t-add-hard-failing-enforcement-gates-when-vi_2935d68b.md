---
name: crossprovider gemini don-t-add-hard-failing-enforcement-gates-when-vi
description: Don't add hard-failing enforcement gates when violations already exist
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [ci-cd, enforcement, migration, governance]
---

Adding a check that FAILs on line limits or config drift while 6+ existing files violate the rule breaks CI immediately. Either migrate the violations first (include fixes in the same PR) or start with WARN-only and graduate to FAIL in a follow-up after baseline is clean.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
