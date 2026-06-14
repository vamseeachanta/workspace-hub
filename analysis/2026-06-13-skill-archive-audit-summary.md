<!-- Generated 2026-06-13 by scripts/skills/skill_archive_audit.py. Epic #3058 / #3062. -->
# Skill archive-tree audit — summary (2026-06-13)

Non-destructive audit of the skill **archive trees** for consolidation (#3062, harden-ecosystem epic #3058). Nothing moved or deleted.

> **Scope note (discovery-first correction).** Retirement-candidate *selection* already exists in `scripts/skills/check_retirement_candidates.py` (threshold `usage<0.05 AND calls<10`), fed by `scripts/skills/skill-usage-report.py`. This audit does **not** duplicate that — it covers the gap those tools don't: the duplicated archive trees.

## Context (from the canonical tools, after a fresh score run)
- `skill-usage-report.py --days 90` regenerated `skill-scores.yaml` (the committed copy was ~10 weeks stale): **830 skills scored**.
- `check_retirement_candidates.py` then flagged **532 retirement candidates** → `.claude/state/skill-retirement-candidates/<date>.json`. (Use that tool, not this one, for the candidate list. Retirement itself = reviewed follow-up: archive, reversible.)

## Archive-tree finding (this tool's contribution)
| Tree | SKILL.md | fingerprint | note |
|---|---|---|---|
| `.claude/skills/_archive` | 2,100 | `7af31e6d…` | **identical content** |
| `.claude/skills-archive` | 2,100 | `7af31e6d…` | **identical content** |
| `_archive/skills` | 88 | `484e0613…` | distinct |

**Confirmed: `.claude/skills/_archive` and `.claude/skills-archive` are a true duplicate** — identical SKILL.md relative-path set, neither a symlink → ~2,100 files duplicated on disk (the archives together hold more than the ~3,113-file live tree).

## Recommendation (reviewed follow-up — NOT done here)
1. Consolidate the two duplicate trees into one convention (proposal: keep `.claude/skills-archive/`, drop `.claude/skills/_archive/`) after a final content diff, with a dated manifest.
2. Fold `_archive/skills` (88) into the same convention.
3. Run retirement via `check_retirement_candidates.py` output, archiving (reversible) the confirmed-dead set.

## Related finding (separate issue)
Pre-existing client identifier in a public skill slug — tracked at #3073 (not part of this audit).
