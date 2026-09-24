---
name: crossprovider codex scorecard-pair-coverage-mismatch
description: Scorecard pair coverage mismatch
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [validation, state-machine, cross-module-consistency]
---

When existing scorecard generator proves a state is valid (e.g., fresh|sample) but validator's pair mapping doesn't include it, validator rejects valid system states. Validator must accept all generated pairs or the scorecard must be constrained to not generate unmapped pairs.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
