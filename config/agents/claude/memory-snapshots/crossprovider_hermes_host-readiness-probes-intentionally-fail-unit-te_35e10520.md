---
name: crossprovider hermes host-readiness-probes-intentionally-fail-unit-te
description: Host readiness probes intentionally fail; unit test passes don't imply environment readiness
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [testing-strategy, readiness-gates, unit-vs-integration]
---

Repo-side tests verify logic but not host prerequisites (systemd config, env vars, file presence). Host-side verifier intentionally fails closed on real system state. Don't auto-claim deployment readiness from unit test passes; require separate live host probes with truthful status reporting.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
