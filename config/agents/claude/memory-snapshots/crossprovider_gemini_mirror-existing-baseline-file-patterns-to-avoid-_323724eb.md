---
name: crossprovider gemini mirror-existing-baseline-file-patterns-to-avoid-
description: Mirror existing baseline file patterns to avoid tool fragmentation
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [patterns, tools, configuration, maintainability]
---

When adding new enforcement tools (gitleaks, vulture, radon), follow the baseline file naming and storage pattern already established in the repo (e.g., config/quality/bandit-baseline-*.json). Deviating creates tool fragmentation and maintenance burden. Consolidate configuration sources.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
