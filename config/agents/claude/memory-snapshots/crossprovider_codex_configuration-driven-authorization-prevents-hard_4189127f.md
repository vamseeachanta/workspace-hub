---
name: crossprovider codex configuration-driven-authorization-prevents-hard
description: Configuration-driven authorization prevents hard-coded trust roots
metadata:
  type: reference
  source: codex
  bridged: 2026-08-03
  tags: [security, configuration, fleet-auth]
---

Restrict fleet authorization to exactly-verified, reachable hosts; preserve exact origin spelling and state machine-readable evidence (DIVERGES, MISSING-EVIDENCE). This pattern decouples policy from code and forces explicit validation before authorization.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
