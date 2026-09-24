---
name: repo-structure
version: 1.4.0
category: workspace
description: Canonical source layout, test mirroring, root cleanliness, gitignore,
  docs classification, and committed artifact rules for all workspace-hub tier-1 repos.
  Consult before creating directories or files in any submodule.
type: reference
invocation: /repo-structure
applies-to:
- claude
- codex
- gemini
capabilities: []
requires: []
tags: []
---

# Repo Structure

## Sub-Skills

- [Tier Classification (Determines Which Rules Apply)](tier-classification-determines-which-rules-apply/SKILL.md)
- [Canonical Structure (+1)](canonical-structure/SKILL.md)
- [Allowed at Repo Root (+2)](allowed-at-repo-root/SKILL.md)
- [Gitignore Enforcement: Root-Level Output Artifacts](gitignore-enforcement-root-level-output-artifacts/SKILL.md)
- [Allowed in docs/ (+1)](allowed-in-docs/SKILL.md)
- [Agent Infrastructure Rules](agent-infrastructure-rules/SKILL.md)
- [Compliance Quick-Check](compliance-quick-check/SKILL.md)
- [NEVER: tests/ inside src/ (+7)](never-tests-inside-src/SKILL.md)
- [See Also](see-also/SKILL.md)

## Iron Law

> No file or directory shall be created outside the canonical structure without consulting this skill first — ever.

## Rationalization Defense

| Excuse | Reality |
|--------|---------|
| "I just need a quick temp directory at the root" | Root-level clutter is permanent. Use the canonical location or it does not get created. |
| "Tests next to source files are easier to find" | Tests inside src/ is an explicit NEVER rule (+7 violations tracked). Use the tests/ mirror. |
| "This output file is small, no need for .gitignore" | Committed artifacts accumulate. If it is generated, it belongs in .gitignore, regardless of size. |
| "The user didn't specify where to put this" | That is exactly when you consult repo-structure. Silence is not permission to improvise. |

## Red Flags

These phrases signal you are about to violate the Iron Law:
- "I'll just put this here for now"
- "it doesn't matter where this file goes"
- "this is a temporary file"
- "the existing structure doesn't have a place for this"
- "tests/ is too far from the code"
