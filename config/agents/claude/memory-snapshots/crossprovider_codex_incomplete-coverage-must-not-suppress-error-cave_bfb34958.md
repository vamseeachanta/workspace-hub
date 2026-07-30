---
name: crossprovider codex incomplete-coverage-must-not-suppress-error-cave
description: Incomplete coverage must not suppress error caveats
metadata:
  type: reference
  source: codex
  bridged: 2026-07-06
  tags: [error-caveats, state-semantics]
---

Report logic removes issue #807 deferred caveat when a sidecar has `coverage_status="defaulted"` or `"missing"`, but these explicitly mean work is incomplete. Caveat suppression should require COMPLETE coverage + accepted factors for every actual oil field, not just partial coverage presence.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
