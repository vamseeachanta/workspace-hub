---
name: clean-code
version: 2.1.0
category: workspace
description: 'Clean code enforcement for workspace-hub Python repos: file/function
  size limits, God Object detection, naming rules, dead code removal, and refactor
  decision guidance. Consult before writing new modules or accepting large files.'
invocation: /clean-code
applies-to:
- claude
- codex
- gemini
capabilities: []
requires: []
see_also:
- clean-code-hard-limits-zero-tolerance
- clean-code-quick-scan-commands
- clean-code-file-size-decision-tree
- clean-code-pattern-1-responsibility-split-most-common
- clean-code-naming-rules-enforcement
- clean-code-dead-code-identification-and-removal
- clean-code-god-object-detection
- clean-code-top-p1-candidates-2026-02-25-audit
- clean-code-pre-commit-integration
- clean-code-git-plumbing-for-repos-with-large-pack-files
- clean-code-step-1-api-compatibility-check-mandatory-before-wr
- clean-code-see-also
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
