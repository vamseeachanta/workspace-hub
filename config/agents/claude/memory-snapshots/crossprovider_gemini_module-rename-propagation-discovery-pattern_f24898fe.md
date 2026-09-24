---
name: crossprovider gemini module-rename-propagation-discovery-pattern
description: Module rename propagation discovery pattern
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [refactoring, testing, ci]
---

When a package is renamed, systematically grep the old name across tests, imports, scripts, and documentation to find all breakage sites. First CI run will collect many import errors if renames are incomplete.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
