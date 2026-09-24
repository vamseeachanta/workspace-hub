---
name: crossprovider codex multi-step-gates-need-end-to-end-integration-tes
description: Multi-step gates need end-to-end integration tests
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [testing, gates, integration-tests]
---

Gates that chain components (issue→score→comment→close) require integration tests proving the full path blocks/passes, not just unit tests of isolated functions. Test malformed metadata, stale records, missing dependencies, and the actual GitHub write (or proof it was blocked).

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
