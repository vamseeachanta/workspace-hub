---
name: crossprovider codex acceptance-tests-must-invoke-actual-cli-entry-po
description: Acceptance tests must invoke actual CLI entry points, not just internal functions
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [testing, acceptance-testing, integration-testing]
---

Performance/latency acceptance tests that measure in-process function behavior do not capture CLI startup overhead, argument parsing, or real-environment costs. Use `subprocess` or shell invocation to test the actual shipped entrypoint.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
