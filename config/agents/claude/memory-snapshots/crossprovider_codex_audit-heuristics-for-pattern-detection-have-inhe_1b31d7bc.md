---
name: crossprovider codex audit-heuristics-for-pattern-detection-have-inhe
description: Audit heuristics for pattern detection have inherent false-negatives; document or use canonical sources
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [audit-scripting, heuristics, testing]
---

WRK-1053 skill-coverage audit used regex heuristics (bash scripts/, python scripts/...) and required multiple rounds of refinement, still missing cases like bare nested paths. Heuristics for detecting 'is this wired' inherently miss edge cases — either use canonical sources (frontmatter) as source-of-truth or document false-negative gaps explicitly.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
