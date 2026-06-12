---
name: crossprovider codex safe-lane-scoping-prefer-verification-over-green
description: Safe lane scoping: prefer verification over greenfield for approved work
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [scope-pattern, approved-implementation, workflow]
---

When accepting plan-approved work with tight scope, bias toward verification/validation lanes (test existing contract, confirm PR landed elsewhere, validate live proof) rather than greenfield implementation. Use TDD-first: run tests RED/GREEN, produce proof artifact, avoid re-authoring completed work.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
