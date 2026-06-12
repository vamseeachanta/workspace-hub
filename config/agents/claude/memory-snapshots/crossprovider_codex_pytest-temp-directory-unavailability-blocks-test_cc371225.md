---
name: crossprovider codex pytest-temp-directory-unavailability-blocks-test
description: Pytest temp directory unavailability blocks test execution in constrained environments
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [testing-ops, environment-constraints, test-portability]
---

Test frameworks that rely on /tmp or tempfile module fail with FileNotFoundError in sandboxed/containerized environments. Mock temp paths or use in-memory stores; document which tests require writable temp dirs.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
