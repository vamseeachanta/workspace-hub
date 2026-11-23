# Archived Skill: `skill-dedup-collision-reconciliation-with-content-security-scan`

Original path: `/home/vamsee/.hermes/skills/workspace-hub-learned/skill-dedup-collision-reconciliation-with-content-security-scan`
Archived into: `/home/vamsee/.hermes/skills/.archive/umbrella-2026-04-29/workspace-hub-learned/skill-dedup-collision-reconciliation-with-content-security-scan`
Consolidation date: 2026-04-29

---

---
name: skill-dedup-collision-reconciliation-with-content-security-scan
description: Reconcile duplicate/colliding workspace-hub skills without losing useful content, while avoiding pre-commit skill-content security scan regressions.
version: 1.0.0
author: Hermes Agent
license: MIT
---

# Skill dedup collision reconciliation with content security scan

Use when:
- a weekly skills audit or duplicate detector identifies duplicate skill names or leaf collisions
- implementation requires merging or deleting skill directories
- pre-commit skill-content scanning may block commits if merged content includes sensitive credential-handling examples

## Why this exists

In #2290, several duplicate pairs were not truly byte-identical. A naive "keep richer copy" strategy caused the canonical GitHub review skill to inherit credential-oriented examples from a duplicate, which then triggered the skill-content security scan and blocked commit.

The correct pattern was:
- inventory at directory level first
- preserve useful auxiliary files separately
- prefer the safer canonical body when the richer duplicate introduces security-hook violations
- merge only the safe, non-sensitive additions actually needed

## Procedure

1. Inventory every pair at directory level, not just `SKILL.md`
   - compare `SKILL.md`
   - list auxiliary files under references or scripts subfolders
   - hash identical files when useful

2. Classify each pair before editing
   - exact duplicate -> delete stale copy
   - near-identical with metadata/category drift only -> copy canonical-safe text, preserve any safe auxiliary files
   - divergent content -> diff carefully and decide whether the richer copy is actually safe to merge

3. Before overwriting canonical content, inspect for commit-hook-sensitive patterns
   Common blockers:
   - examples that explicitly show credential-bearing network requests
   - examples that read secret-bearing local environment files
   - token extraction snippets
   - unpinned installer examples may warn but usually do not block

4. If richer duplicate contains blocked patterns
   - do NOT wholesale replace canonical skill
   - keep the safer canonical body
   - manually port only safe additions, such as:
     - better checklist text
     - non-sensitive examples
     - harmless references/templates
   - move auxiliary reference files explicitly if they add value

5. Preserve auxiliary files with explicit moves
   Examples from #2290:
   - move the review output template into the canonical GitHub review skill references folder
   - move the DSPy examples/modules/optimizers references into the canonical DSPy skill references folder

6. Add a regression test for the exact target findings
   - assert target duplicate names are gone
   - assert target leaf collisions are gone
   - assert stale directories are removed
   - assert canonical directories still exist

7. Validate in this order
   - targeted regression test for the issue-specific findings
   - broader weekly audit tests
   - duplicate detector script
   - weekly skills audit script
   - deleted-path reference search in the repo surfaces relevant to the cleanup

8. Only then stage and commit
   - if commit is blocked by skill-content scan, back out the unsafe merged text and keep the safer canonical wording

## Pitfalls

- "Richer" duplicate content may be operationally worse because it trips security hooks
- reference cleanup scope must include documentation surfaces, not just the immediate skill tree
- transient generated files can reappear and block push/rebase; restore them before final push

## Minimal heuristic

When reconciling duplicate skills:
- preserve files first
- prefer safe canonical text over richer unsafe text
- merge surgically, not wholesale

## Verification signals

Good final state looks like:
- target duplicate/collision findings cleared from weekly audit
- moved reference files present in canonical locations
- zero deleted-path references in checked surfaces
- commit passes skill-content security scan without bypassing hooks
