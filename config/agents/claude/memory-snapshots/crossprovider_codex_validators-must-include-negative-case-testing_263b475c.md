---
name: crossprovider codex validators-must-include-negative-case-testing
description: Validators must include negative-case testing
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [validator-design, testing, adversarial-review]
---

Validators that check only file existence and basic text patterns often miss row-level schema violations (missing fields, unsafe values, wrong types). Negative cases—data that should fail—reveal gaps not visible in unit tests of valid inputs. Always test validators against malformed/unsafe data.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
