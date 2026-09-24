---
name: crossprovider codex fail-open-when-validators-skip-downstream-firewa
description: Fail-open when validators skip downstream firewall delegation
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [sampling, firewall, validator-composition, policy-gate]
---

Validators that accept fixture evidence directly instead of delegating to authorization gatekeepers bypass policy enforcement. #52 validator accepted shape-only manifest evidence while #67/#70 firewall would reject the same object as self-attested. Sampling/firewall checks must always delegate to the canonical firewall path, never duplicate or bypass it.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
