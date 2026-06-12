---
name: crossprovider codex silent-detector-failure-hidden-by-zero-violation
description: Silent detector failure hidden by zero-violation assertion
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [testing, error-handling, test-design]
---

Tests that assert 'detector reports 0 violations' pass even if the detector silently fails (e.g., missing dependency, broken regex). The test cannot distinguish success-with-no-findings from failure. Capture stderr, check exit codes, and verify detector preconditions before asserting on output.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
