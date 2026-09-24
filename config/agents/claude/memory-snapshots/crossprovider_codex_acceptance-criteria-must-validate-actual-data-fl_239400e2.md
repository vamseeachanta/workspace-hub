---
name: crossprovider codex acceptance-criteria-must-validate-actual-data-fl
description: Acceptance criteria must validate actual data flow, not assumed buckets
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [acceptance-criteria, testing, data-flow]
---

In WRK-1125, AC2 stated 'show `not_before` in IN-PROGRESS UNCLAIMED' but the script's classifier never puts pending items there—they land in MED_UNBLOCKED. Codex caught this in round 5. Trace where data actually flows before writing acceptance criteria, or the ACs will pass while the feature still fails to work as intended.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
