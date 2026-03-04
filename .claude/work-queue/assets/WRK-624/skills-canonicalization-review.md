# Skills Canonicalization Review

Generated: 2026-03-04

## Scope

- `.claude/skills/_archive/**/SKILL.md`
- `.claude/skills/_diverged/**/SKILL.md`
- Canonical target set: active skills under `.claude/skills/**/SKILL.md` excluding `_archive` and `_diverged`

## Findings Summary

| Area | Total | Has active canonical by `name` | Missing active canonical by `name` |
|---|---:|---:|---:|
| `_archive` | 0 | 0 | 0 |
| `_diverged` | 114 | 114 | 0 |

| Diverged canonical_ref quality | Count |
|---|---:|
| With `canonical_ref` | 114 |
| Without `canonical_ref` | 0 |
| `canonical_ref: UNMATCHED` | 0 |
| `canonical_ref: AMBIGUOUS` | 0 |

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

## Progress Completed

- Added canonical references to 54 diverged skills that had no `canonical_ref` and a unique active canonical target.
- Canonicalized 13 previously unmatched diverged skills by promoting active canonical skill files under:
  - `.claude/skills/operations/automation/`
  - `.claude/skills/development/documentation/`
  - `.claude/skills/ai/prompting/`
- Resolved all `AMBIGUOUS` canonical refs (now 0).
- Deleted 14 archive duplicates now covered by active canonical skills:
  - 1 prior duplicate (`gmsh-meshing`)
  - 13 additional legacy duplicates in archive prompting/automation/documentation groups
- Deleted remaining 16 archive orphan skills after decision-table triage.
- Deleted the final unmatched diverged file (`worldenergydata/.../python-code-refactor`).

## Remaining Unresolved

- None. All reviewed `_archive` / `_diverged` skills now have explicit canonicalization or deletion outcomes.

## Tracking Artifact

- Detailed row-level decision + execution status:
  - `.claude/work-queue/assets/WRK-624/skills-canonicalization-decision-table.md`
  - `.claude/work-queue/assets/WRK-624/skills-canonicalization-decision-table.html`
