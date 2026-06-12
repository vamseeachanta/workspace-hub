---
name: crossprovider gemini pre-ci-import-verification-prevents-first-run-fa
description: Pre-CI import verification prevents first-run failure
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [ci, testing, import-paths, pre-flight-checks]
---

Foundational test files often contain outdated import paths that will fail silently at collection time on first CI run. Verify import paths against actual module structure and refactor aliases before enabling CI gates (#2444).

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
