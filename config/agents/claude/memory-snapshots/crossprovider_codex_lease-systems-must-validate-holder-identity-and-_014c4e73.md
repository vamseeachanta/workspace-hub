---
name: crossprovider codex lease-systems-must-validate-holder-identity-and-
description: Lease systems must validate holder identity and token, not just return value
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [lease-systems, authorization, fail-closed]
---

Trusting any non-None return from acquire/reclaim without asserting holder identity and token match allows unauthorized writes. Must verify lease["holder"] == expected and lease["token"] == current before granting access.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
