---
name: crossprovider gemini missing-dependency-smoke-tests-catch-optional-im
description: Missing-dependency smoke tests catch optional import failures at collection
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [testing, dependencies, ci-health, optional-imports]
---

Unguarded imports of optional dependencies (e.g., `from pylife import ...`) fail only when test collection runs, not at install time. A smoke import test that runs before the main suite catches these failures early and prevents latent broken imports in CI.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
