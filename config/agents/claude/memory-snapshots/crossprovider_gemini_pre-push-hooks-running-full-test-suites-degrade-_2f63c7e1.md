---
name: crossprovider gemini pre-push-hooks-running-full-test-suites-degrade-
description: Pre-push hooks running full test suites degrade developer UX
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [hooks, ci-cd, developer-experience, testing]
---

Full test suite execution on pre-push blocks pushes for minutes, harming workflow. Expensive checks (full coverage, integration tests) belong in CI/CD; keep pre-push hooks for fast, local checks (linting, syntax). If pre-push validation is needed, use CI-gated pre-commit instead.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
