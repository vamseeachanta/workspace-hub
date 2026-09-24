---
name: crossprovider gemini deduplication-impact-radius-hardcoded-path-refer
description: Deduplication impact radius: hardcoded path references in config
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [refactoring, deduplication, dependency-tracking, skill-system, configuration]
---

When deduplicating or relocating files, validation must include not just the new canonical location structure but also any agents, wrapper scripts, or config files that may have hardcoded references to old paths. Auth scripts, sourced helpers, and skill metadata files are particularly high-risk for stale path references that break when the old tree is deleted.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
