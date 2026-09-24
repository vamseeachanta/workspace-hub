---
name: crossprovider codex public-routing-boolean-reduction-loses-canary-ev
description: Public routing boolean reduction loses canary evidence requirement
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [public-safety, canary-testing, contract-enforcement]
---

Reducing public routing to a boolean `public_clearance: true` allows rows to bypass canary evidence gates (#63). Public clearance must carry explicit proof of canary testing on the exact surface, not just a boolean flag. Contract must name the gate; validator must check the gate artifact reference.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
