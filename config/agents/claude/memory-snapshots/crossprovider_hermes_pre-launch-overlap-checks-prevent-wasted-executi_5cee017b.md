---
name: crossprovider hermes pre-launch-overlap-checks-prevent-wasted-executi
description: Pre-launch overlap checks prevent wasted execution
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [governance, parallel-work, blocking]
---

Before starting execution, check for overlapping in-flight work (e.g., via gh issue view --comments) that may affect scope. Deferral rules in issue bodies can cause session postponement.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
