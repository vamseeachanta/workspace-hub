---
name: crossprovider codex literal-string-based-code-discovery-is-silently-
description: Literal-string-based code discovery is silently incomplete
metadata:
  type: reference
  source: codex
  bridged: 2026-07-30
  tags: [code-scanning, test-coverage, ci-validation]
---

Discovery mechanisms that search for exact string matches (e.g., 'write_text', 'docs/api/') will miss valid producers using synonymous patterns (open(), write_bytes()) or constructed paths. Failing to find a producer silently passes, leaving stale outputs undetected. Use adversarial test cases and fail-closed validation logic.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
