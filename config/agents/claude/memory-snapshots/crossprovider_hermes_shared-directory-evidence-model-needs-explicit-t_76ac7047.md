---
name: crossprovider hermes shared-directory-evidence-model-needs-explicit-t
description: Shared-directory evidence model needs explicit trust boundary documentation
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [documentation, security, ops, hermes]
---

#2720 docs recommend 'shared/synced evidence directory' for multi-machine readiness but don't disclose it's a trust-on-first-write boundary, not verified attestation. Ops control planes must explicitly document which trust boundaries are cryptographically enforced vs. which are configuration assumptions. Implicit trust is a silent failure mode for security gates.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
