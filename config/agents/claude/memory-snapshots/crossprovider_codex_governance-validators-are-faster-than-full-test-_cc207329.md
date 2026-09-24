---
name: crossprovider codex governance-validators-are-faster-than-full-test-
description: Governance validators are faster than full test suite
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [testing, efficiency, validation]
---

Targeted validators like `validate_completion_artifacts.py` and `validate_governance_artifacts.py` complete reliably and quickly. Full `pytest` can hang indefinitely. Use validators for rapid feedback during scouting and report-writing. Reserve full test suite for implementation confirmation.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
