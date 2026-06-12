---
name: crossprovider hermes fixture-runtime-probes-must-validate-live-state-
description: Fixture runtime probes must validate live state, not trust recorded results
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [fixtures, testing, infrastructure, evidence-validation, workspace-hub]
---

Fixtures recording probe results (e.g., `test -d /path` with `status: recorded`) diverge from current host state. Tests must re-validate probes against live filesystem rather than assume recorded status. Mark expected absences as `absent_recorded` if intentional; canonical paths in fixtures require live verification or explicit staleness markers.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
