---
name: crossprovider codex sequencing-dependencies-must-have-machine-checka
description: Sequencing dependencies must have machine-checkable preflight, not prose assertions
metadata:
  type: reference
  source: codex
  bridged: 2026-06-23
  tags: [tdd-testability, dependency-gating, llm-wiki-dnv]
---

Sessions #759–#763 found sequencing claims like 'wait for batch-006 config' stated in plan prose without corresponding RED tests. Updater config only supports batches 001–002 (dnv_batch_models.py:31), but plans assume batch-003+ regression coverage. Implementations can skip planned dependencies silently. Add explicit RED preflights: e.g., a test that fails when `.planning/plan-approved/<dependency>.md` or batch config for N is absent.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
