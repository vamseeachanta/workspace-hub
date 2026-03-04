# Skills Canonicalization Review

Generated: 2026-03-04

## Scope

- `.claude/skills/_archive/**/SKILL.md`
- `.claude/skills/_diverged/**/SKILL.md`
- Canonical target set: active skills under `.claude/skills/**/SKILL.md` excluding `_archive` and `_diverged`

## Findings Summary

| Area | Total | Has active canonical by `name` | Missing active canonical by `name` |
|---|---:|---:|---:|
| `_archive` | 30 | 1 | 29 |
| `_diverged` | 115 | 98 | 13 |

| Diverged canonical_ref quality | Count |
|---|---:|
| With `canonical_ref` | 57 |
| Without `canonical_ref` | 54 |
| `canonical_ref: UNMATCHED` | 14 |
| `canonical_ref: AMBIGUOUS` | 2 |

## Decision Rule (Required)

Each archived/diverged skill must end in exactly one state:

1. **Canonicalized**  
   - Has a valid canonical target in active tree.
   - `canonical_ref` is concrete and resolvable.
   - Legacy copy then eligible for deletion after verification.
2. **Deleted**  
   - No valid canonical target and no approved need to maintain.
   - Remove file instead of retaining orphaned copy.

No indefinite holding state.

## Immediate Candidates

### Safe delete now (duplicate already canonical)

- `.claude/skills/_archive/eng/mesh-utilities/gmsh-meshing/SKILL.md`  
  Canonical exists at `.claude/skills/engineering/cad/gmsh-meshing/SKILL.md`.

### Missing canonical active target by name (requires decision: create canonical or delete)

- `.claude/skills/_diverged/digitalmodel/documentation/sphinx/SKILL.md`
- `.claude/skills/_diverged/digitalmodel/automation/windmill/SKILL.md`
- `.claude/skills/_diverged/digitalmodel/documentation/gitbook/SKILL.md`
- `.claude/skills/_diverged/digitalmodel/documentation/pandoc/SKILL.md`
- `.claude/skills/_diverged/digitalmodel/automation/n8n/SKILL.md`
- `.claude/skills/_diverged/digitalmodel/documentation/marp/SKILL.md`
- `.claude/skills/_diverged/digitalmodel/documentation/docusaurus/SKILL.md`
- `.claude/skills/_diverged/digitalmodel/ai-prompting/pandasai/SKILL.md`
- `.claude/skills/_diverged/digitalmodel/ai-prompting/dspy/SKILL.md`
- `.claude/skills/_diverged/digitalmodel/ai-prompting/langchain/SKILL.md`
- `.claude/skills/_diverged/digitalmodel/automation/airflow/SKILL.md`
- `.claude/skills/_diverged/digitalmodel/ai-prompting/agenta/SKILL.md`
- `.claude/skills/_diverged/digitalmodel/automation/activepieces/SKILL.md`

### Archive orphan pool (29 files)

Archive skills currently have no active canonical by name and should be triaged under the same rule: either promote to canonical active location with explicit ownership, or delete.

