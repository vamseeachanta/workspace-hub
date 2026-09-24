---
name: crossprovider gemini import-path-renames-after-package-refactor-must-
description: Import-path renames after package refactor must be verified across all sites
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [refactoring, ci-health, import-paths]
---

Package renames (e.g., `aceengineer_automation` → `aceengineer_admin`) can leave stale imports in test files and internal modules undetected until the first CI run. Grep all import sites before green validation to catch missing propagation.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
