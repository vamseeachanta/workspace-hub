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

## Generated Evidence Exception Pattern

When tracked files already exist under generated-output roots (`outputs/**`, `reports/**`, `dist/**`, etc.), do **not** blindly move or delete them during a structure refactor. First classify the path as unauthorized generated artifact, durable evidence, or temporary durable exception. Temporary durable exceptions must include owner/category/review-date metadata, a concrete follow-up issue URL or permanent-justification schema, and checker coverage that rejects placeholders. If live source/docs intentionally reference the generated path, broad zero-match stale-reference gates are invalid; use scoped checks that only reject unauthorized tracked generated roots and stale committed-evidence links.

Checker pitfall: path-only parsing of `git status --short` is insufficient. Preserve status codes so the checker rejects deletion (`D`) and rename/relocation (`R`) of generated-output paths; otherwise a prohibited generated-artifact move can pass merely because the path itself is classified.

## Phase 1 Contract Checker Pattern

For approved Phase 1 repo-structure issues, use the packaged pattern in [`references/phase1-contract-checker-pattern.md`](references/phase1-contract-checker-pattern.md): bounded docs/config/checker/tests/enforcement only, TDD slices for unapproved roots and generated-root metadata, default checker coverage of `git ls-files` plus non-ignored working-tree paths, and no broad moves/deletions until artifacts are classified.

## Agent/runtime folder authority mapping

When work touches provider identity/config folders, generated runtime files, local home-directory symlinks, memory bridges, or skill roots, classify each path by authority before editing. Use [`references/agent-runtime-authority-map.md`](references/agent-runtime-authority-map.md) for the canonical source vs generated runtime vs local symlink vs bridge output workflow and issue-body shape for recurring human/agent folder-confusion reports.

## Red Flags

These phrases signal you are about to violate the Iron Law:
- "I'll just put this here for now"
- "it doesn't matter where this file goes"
- "this is a temporary file"
- "the existing structure doesn't have a place for this"
- "tests/ is too far from the code"
