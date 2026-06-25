---
name: crossprovider codex test-only-allowances-must-not-be-trusted-from-tr
description: Test-only allowances must not be trusted from tracked artifacts
metadata:
  type: reference
  source: codex
  bridged: 2026-06-24
  tags: [configuration-safety, privacy-enforcement, test-isolation]
---

Configuration that permits test-only keys (e.g., placeholder HMAC keys) must be injected by test environment variables, not self-declared in tracked artifacts. A production run that loads a tracked config file claiming `test_only: true` will accept the test key, violating fail-closed semantics. Real runs must default to rejecting test material; tests inject explicit opt-in.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
