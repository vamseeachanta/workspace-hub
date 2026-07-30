---
name: crossprovider codex empty-registries-allowlists-must-fail-closed-in-
description: Empty registries/allowlists must fail closed in security paths
metadata:
  type: reference
  source: codex
  bridged: 2026-07-03
  tags: [security, sampling, defaults]
---

Session 4 and 5 found the trusted-evidence registry empty and the sampling firewall properly rejecting requests without authorization. A security-relevant validator (sampling gate, evidence approval) must default-deny when the trust list is empty, not be optional.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
