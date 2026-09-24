---
name: crossprovider gemini pre-push-hooks-must-avoid-expensive-operations
description: Pre-push hooks must avoid expensive operations
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [git-hooks, developer-experience, ci-cd]
---

Running full test suites with coverage collection on every pre-push severely degrades developer UX. Move CPU-intensive checks to CI/CD pipeline; keep pre-push hooks fast (lint, format, basic sanity only). Addresses WRK-1067 finding.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
