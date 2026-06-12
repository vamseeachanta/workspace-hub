---
name: crossprovider hermes forbidden-phrase-tdd-tests-self-collide-when-phr
description: Forbidden-phrase TDD tests self-collide when phrases required in approved disclaimers
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [tdd, test-scope]
---

Testing for forbidden phrases like 'signoff' fails when those phrases are required in an approved limitation sentence. Fix: scan forbidden phrases only outside the approved disclaimer span by explicitly defining the span and excluding it from the matcher.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
