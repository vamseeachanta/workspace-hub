---
name: crossprovider gemini script-enforcement-gates-are-all-or-nothing-part
description: Script enforcement gates are all-or-nothing; partial wiring creates dead code
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [enforcement, testing-strategy, code-governance]
---

Plans that propose multiple enforcement scripts but wire only one to pre-commit/CI leave others unenforced and unexecuted. Incomplete enforcement is worse than no enforcement (creates false security sense). All scripts in a gate must be wired or explicitly justified as follow-up work.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
