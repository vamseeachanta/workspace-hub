---
name: crossprovider codex validator-backed-stage-contracts-prevent-self-co
description: Validator-backed stage contracts prevent self-contradiction
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [stage-contracts, validator-design, error-prevention]
---

Stage implementations (e.g., Resource Intelligence skill) require mechanical validators (bash/Python scripts), not just documentation. Missing validators let contradictory states pass: P1 gap + continue_to_planning both true simultaneously. Validators must enforce gate rules at commit time.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
