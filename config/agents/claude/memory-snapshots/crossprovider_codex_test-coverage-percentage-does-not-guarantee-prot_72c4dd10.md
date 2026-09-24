---
name: crossprovider codex test-coverage-percentage-does-not-guarantee-prot
description: Test coverage percentage does not guarantee protocol-edge-case coverage
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [testing, test-adequacy, edge-cases]
---

A test suite with high pass rate (14/14) using mocked/fake payloads can miss real failure modes at the protocol layer. Tests verifying exception handling and error responses gave false confidence while truncated-stream edge cases remained uncovered. Distinguish error-handling coverage from protocol-edge-case coverage; use code-path probes and live tests as complementary to unit suites.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
