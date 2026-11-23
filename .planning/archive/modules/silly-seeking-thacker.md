# WRK-1098 Plan: Ecosystem Terminology Skill

## Context

Coding assistants and new humans regularly use inconsistent names for repos, modules,
machines, and concepts in this ecosystem. The terminology is scattered across CLAUDE.md,
MEMORY.md, AGENTS.md, and various docs — there is no single reference.

This WRK creates one authoritative skill that every agent loads on demand
(`/ecosystem-terminology`) with canonical tables, relationship vocabulary, and a
do-not-use list. Related: WRK-1073 (repo onboarding maps).

## Implementation Steps

1. **Create skill directory and SKILL.md**
   - Path: `.claude/skills/workspace-hub/ecosystem-terminology/SKILL.md`
   - Frontmatter: `name`, `version: 1.0.0`, `category: workspace-hub`,
     `applies-to: [claude, codex, gemini]`, `invocation: /ecosystem-terminology`
   - Sections (tables):
     - **Canonical Repo Names** — repo | canonical id | package name | tier | maturity | aliases | do-not-use
     - **Relationship Vocabulary** — term | definition (tier-1, submodule, hub, harness, WRK, stage, phase, checkpoint)
     - **File/Directory Naming** — correct | incorrect examples (work-queue not work_queue, SKILL.md not skill.md)
     - **Acronyms & Abbreviations** — WRK, GTM, CP, VIV, TDD, AC (acceptance criteria)
     - **Machines / People** — canonical | alias | never-use
     - **Do-Not-Use List** — deprecated names, client codenames (none currently in deny list), wrong plurals

2. **Register slash command**
   - Create `.claude/commands/workspace-hub/ecosystem-terminology.md`
   - One-line invocation: `@.claude/skills/workspace-hub/ecosystem-terminology/SKILL.md`
   - This makes `/ecosystem-terminology` discoverable in the slash command menu

3. **Cross-reference CLAUDE.md**
   - Add `Terminology: /ecosystem-terminology` to the Quick Reference section
   - CLAUDE.md is currently 17 lines (limit 20); stays within limit

4. **Legal scan**
   - Run `scripts/legal/legal-sanity-scan.sh` on the new skill file
   - All examples must use generic names; no client identifiers

5. **Codex cross-review**
   - Submit terminology table to Codex for completeness review
   - Record verdict in `assets/WRK-1098/evidence/cross-review-codex.md`
   - APPROVE or MINOR required to close

## Tests / Evals

| Test | Scenario | Expected |
|------|----------|----------|
| Legal scan | Run scan on new SKILL.md | Exit 0, no block violations |
| Slash command visible | Invoke `/ecosystem-terminology` in session | Skill loads, full content shown |
| All 6 sections present | Read SKILL.md | Canonical repos, relationships, file naming, acronyms, machines, do-not-use all present |
| CLAUDE.md line count | After cross-ref addition | ≤20 lines |
| Codex review | Submit terminology tables | Verdict APPROVE or MINOR (no MAJOR) |

## Pseudocode
n/a_reason: "pure-doc WRK — no implementation logic; all deliverables are documentation tables"

## Risks

- CLAUDE.md currently 17 lines — adding 1 line keeps it at 18 (safe)
- AGENTS.md already exceeds 20-line limit (28 lines) — do NOT modify it for this WRK; capture as separate debt item
- Do-not-use list must stay generic — verify against `.legal-deny-list.yaml` before commit
- Codex quota may be exhausted — Claude Opus fallback per cross-review.sh policy

## Out of Scope

- Updating AGENTS.md (already over 20-line limit — separate WRK)
- Adding terminology to CODEX.md / GEMINI.md (thin adapters; skill is the place)
- Comprehensive acronym audit beyond what appears in current documentation
