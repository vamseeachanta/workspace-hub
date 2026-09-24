---
name: crossprovider gemini code-relocation-requires-codebase-wide-reference
description: Code relocation requires codebase-wide reference search and update
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [plan-review, maintenance, pseudocode]
---

Moving or archiving code without searching for and updating all call sites leaves broken references. Add an explicit search step (`grep -r <old-path>`) to pseudocode and include reference updates in the implementation scope when code is moved or deprecated.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
