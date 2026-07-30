---
name: crossprovider codex validator-false-greens-hide-evidence-gaps
description: Validator false-greens hide evidence gaps
metadata:
  type: reference
  source: codex
  bridged: 2026-07-14
  tags: [testing, validation, qa]
---

Schema validators can print success (e.g., '0 findings') without ever invoking the checks they promise; the validator only runs adjacent guards and prints a hardcoded result. Always verify that validators actually call their claimed schema.validate() or check functions, not just adjacent collection/anchor logic.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
