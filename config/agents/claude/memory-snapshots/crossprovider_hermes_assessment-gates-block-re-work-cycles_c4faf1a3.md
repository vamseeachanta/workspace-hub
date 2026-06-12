---
name: crossprovider hermes assessment-gates-block-re-work-cycles
description: Assessment gates block re-work cycles
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [assessment, gate, wave-planning]
---

Before queuing issues for a new implementation wave, verify: (1) is it already partially landed? (2) does the shipped code match the approved contract? Issues #2059 already done, #2063 partially shipped with wrong API, #2062 blocked on data. Assessment prevents queuing same-scope work twice.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
