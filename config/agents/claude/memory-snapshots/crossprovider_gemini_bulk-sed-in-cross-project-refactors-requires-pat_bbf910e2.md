---
name: crossprovider gemini bulk-sed-in-cross-project-refactors-requires-pat
description: Bulk sed in cross-project refactors requires pattern categorization
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [tooling-hazard, refactoring, automation-risk]
---

Multiple distinct call patterns (shebangs, inline execution, jq fallback chains, heredoc invocation) each need different fixes. Audit and categorize by pattern type before any automated replacement; bulk sed across mixed patterns leads to silent breakage. Workspace-hub uses file-by-file, pattern-specific edits instead.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
