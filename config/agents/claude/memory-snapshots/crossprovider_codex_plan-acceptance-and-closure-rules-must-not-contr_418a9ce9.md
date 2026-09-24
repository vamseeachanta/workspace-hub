---
name: crossprovider codex plan-acceptance-and-closure-rules-must-not-contr
description: Plan acceptance and closure rules must not contradict
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [planning-antipattern, acceptance-criteria, issue-closure]
---

When a plan allows an acceptance criterion to be satisfied by partial evidence (e.g., failure captured) while the closure rule requires full success, the issue becomes stuck in ambiguous state. Split acceptance into separate criteria or align closure rule to match acceptance, so implementers know whether the issue is done or blocked.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
