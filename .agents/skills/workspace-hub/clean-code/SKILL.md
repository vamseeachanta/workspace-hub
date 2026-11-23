---
name: clean-code
version: 2.1.0
category: workspace
description: 'Clean code enforcement for workspace-hub Python repos: file/function
  size limits, God Object detection, naming rules, dead code removal, and refactor
  decision guidance. Consult before writing new modules or accepting large files.'
type: reference
invocation: /clean-code
applies-to:
- claude
- codex
- gemini
capabilities: []
requires: []
updated: 2026-02-25
changelog: "v2.1.0 \u2014 Module Migration Shim Protocol (WRK-602): API compat check,\
  \ diverged-API handling, patch.object scope for shim modules; v2.0.0 \u2014 God\
  \ Object splits, horizontal-split, parallel team"
tags: []
---

# Clean Code

## Sub-Skills

- [Hard Limits (Zero-Tolerance)](hard-limits-zero-tolerance/SKILL.md)
- [Quick Scan Commands](quick-scan-commands/SKILL.md)
- [File Size Decision Tree](file-size-decision-tree/SKILL.md)
- [Pattern 1: Responsibility Split (most common) (+5)](pattern-1-responsibility-split-most-common/SKILL.md)
- [Naming Rules (Enforcement)](naming-rules-enforcement/SKILL.md)
- [Dead Code Identification and Removal](dead-code-identification-and-removal/SKILL.md)
- [God Object Detection](god-object-detection/SKILL.md)
- [Top P1 Candidates (2026-02-25 audit)](top-p1-candidates-2026-02-25-audit/SKILL.md)
- [Pre-commit Integration](pre-commit-integration/SKILL.md)
- [Git Plumbing for Repos with Large Pack Files (+1)](git-plumbing-for-repos-with-large-pack-files/SKILL.md)
- [Step 1: API Compatibility Check (MANDATORY before writing shims) (+2)](step-1-api-compatibility-check-mandatory-before-wr/SKILL.md)
- [See Also](see-also/SKILL.md)

## Iron Law

> No file shall exceed the hard limit, and no function shall exceed 50 lines — no exceptions, no deferrals, no "I'll refactor later."

## Rationalization Defense

| Excuse | Reality |
|--------|---------|
| "It's only slightly over the limit" | Limits exist at exact thresholds for a reason — 301 lines is a violation, not a rounding error. Split now. |
| "Splitting this file would be premature" | The limit exists precisely because developers always say this. The file is already too large; splitting is overdue, not premature. |
| "I'll refactor after I finish the feature" | Post-feature refactors have a near-zero completion rate. The limit is enforced at write time, not review time. |
| "This function is complex — it needs to be long" | Complex functions need to be decomposed, not excused. Length is a symptom of missing abstractions. |
| "The tests pass so the structure is fine" | Tests validate behavior, not maintainability. Passing tests do not exempt code from structural rules. |

## Red Flags

These phrases signal you are about to violate the Iron Law:
- "just a few lines over"
- "I'll clean this up in a follow-up"
- "splitting would add unnecessary complexity"
- "this is a one-off / special case"
- "the logic is tightly coupled — it has to stay together"
