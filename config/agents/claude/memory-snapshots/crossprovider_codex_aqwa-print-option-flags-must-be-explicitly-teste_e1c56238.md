---
name: crossprovider codex aqwa-print-option-flags-must-be-explicitly-teste
description: AQWA print-option flags must be explicitly tested in TDD
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [aqwa, tdd-requirement, solver-domain]
---

AQWA RESTART/print-option flags (PFLH PRFS PRRI PRRP PRRS PRTI PRTS, RESTART 1 5) control RAO/added-mass/damping table output. Plans that modify AQWA decks must include a TDD test (`test_print_options_preserved`) verifying these flags survive the corrected run; otherwise deliverables depending on printed RAO cannot be produced.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
