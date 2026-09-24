---
name: crossprovider codex mocked-tests-runtime-stubs-for-optional-external
description: Mocked tests + runtime stubs for optional external dependencies
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [testing, tdd, external-dependencies]
---

When implementing features that depend on external services (APIs, Ollama, databases), write TDD tests against mocked responses and implement code with stubs that cleanly skip or fail if credentials/services are unavailable at runtime. Tests pass green; runtime degrades safely. Avoids credential/environment coupling in the test suite.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
