---
name: crossprovider codex test-fixture-scanner-safety-requires-runtime-fra
description: Test fixture scanner safety requires runtime fragment building
metadata:
  type: reference
  source: codex
  bridged: 2026-07-02
  tags: [testing, security-scanning, fixture-hygiene]
---

Negative test literals (source_id, source_sha256, private_lookup_*, paths, commands) cannot be committed directly to test files. Build denied examples at test runtime and validate against self-scan to prevent publication leaks. This matters when tests intentionally create scanner-hostile content to verify rejection behavior.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
