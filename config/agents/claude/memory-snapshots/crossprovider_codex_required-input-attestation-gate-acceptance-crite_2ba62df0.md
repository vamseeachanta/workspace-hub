---
name: crossprovider codex required-input-attestation-gate-acceptance-crite
description: Required input attestation gate: acceptance criteria cannot assume existence
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [acceptance-criteria, attestation, required-inputs]
---

Plans that claim required inputs must prove they exist via attested evidence (attest-plan-claims.sh) or add them to planned artifacts. Smoke-test acceptance criteria that depend on unattested required files will fail pre-implementation if the repo state does not match plan assumptions. Treat all existence claims as falsifiable.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
