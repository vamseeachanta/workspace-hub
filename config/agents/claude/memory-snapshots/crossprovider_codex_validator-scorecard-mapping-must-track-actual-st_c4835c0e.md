---
name: crossprovider codex validator-scorecard-mapping-must-track-actual-st
description: Validator scorecard mapping must track actual state generator
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [validation, test-sync, state-contracts]
---

When validators define static scorecard_pair_mapping, the mapping becomes stale if the scorecard generator produces new valid states the mapping lacks. Add sync-check tests that verify all possible generator outputs are in the mapping, or make mapping dynamic.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
