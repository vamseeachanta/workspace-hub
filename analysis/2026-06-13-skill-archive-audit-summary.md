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
| `.claude/skills/_archive` | 2,100 | `7af31e6d…` | same path-set |
| `.claude/skills-archive` | 2,100 | `7af31e6d…` | same path-set |
| `_archive/skills` | 88 | `484e0613…` | distinct |

**`.claude/skills/_archive` and `.claude/skills-archive` share an identical SKILL.md path-set** (same 2,100 relpaths, neither a symlink). A follow-up `diff -rq` shows they are a **near-duplicate, not byte-identical**: ~2,086/2,100 match, but **14 SKILL.md differ in content** (all newer on `.claude/skills/_archive`) and `.claude/skills-archive` carries an extra `README.md`. So consolidation is **not a blind delete** — it needs reconciliation (carry the 14 newer `_archive` versions into the keeper first), tracked as a follow-up.

## Recommendation (reviewed follow-up — NOT done here)
1. Consolidate to one convention (keep `.claude/skills-archive/`) — but **reconcile first**: carry the 14 newer `.claude/skills/_archive` SKILL.md versions into `.claude/skills-archive/`, then drop `_archive/`. Not a blind delete; preserve the newer content + a dated manifest.
2. Fold `_archive/skills` (88) into the same convention.
3. Run retirement via `check_retirement_candidates.py` output, archiving (reversible) the confirmed-dead set.

## Related finding (separate issue)
Pre-existing client identifier in a public skill slug — tracked at #3073 (not part of this audit).
