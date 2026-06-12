---
name: crossprovider hermes validator-status-aliasing-creates-fail-open-bug
description: Validator status aliasing creates fail-open bug
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [validation, safety-gate, bug-pattern]
---

When a validator returns multiple status values ('pass', 'fail', 'not_present'), grouping 'not_present' with 'pass' creates a fail-open vulnerability. Missing required artifacts report as passing when checks only count 'fail' as failure. Must distinguish 'not_present' (missing required artifact) as a distinct failure condition.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
