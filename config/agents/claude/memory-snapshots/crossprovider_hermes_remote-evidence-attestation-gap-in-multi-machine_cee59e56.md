---
name: crossprovider hermes remote-evidence-attestation-gap-in-multi-machine
description: Remote evidence attestation gap in multi-machine dispatch
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [dispatch-safety, multi-machine, evidence-validation, fail-closed]
---

Remote host readiness evidence validation must not accept minimal schemas (host_id, hostname, generated_at, status) without attestation that local safety gates (env token checks, bot token presence, workspace root existence, AGENTS flag) were actually executed on the remote host. Current pattern trusts fabricated minimal evidence as sufficient proof, enabling dispatch without evidence of required host-local safety gates.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
