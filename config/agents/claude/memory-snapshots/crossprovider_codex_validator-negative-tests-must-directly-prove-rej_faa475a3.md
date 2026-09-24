---
name: crossprovider codex validator-negative-tests-must-directly-prove-rej
description: Validator negative tests must directly prove rejection
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [testing, validation]
---

Happy-path validator tests do not prove the validator rejects invalid inputs. Governance-artifact validator needed negative tests mutating expected field values and asserting failure, ensuring validators catch actual malformed input rather than just accepting good input.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
