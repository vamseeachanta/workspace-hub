---
name: crossprovider codex artifact-map-must-assign-test-module-ownership-e
description: Artifact map must assign test module ownership explicitly
metadata:
  type: reference
  source: codex
  bridged: 2026-07-03
  tags: [plan-completeness, test-ownership, implementation-risk]
---

A plan's Artifact Map listed changed files but omitted which test module owned new test coverage, leaving implementation at risk of adding tests to the wrong module or duplicating across modules. Plans that change source files must explicitly map each file to its test-owner module; aggregate test imports don't substitute for direct assignment.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
