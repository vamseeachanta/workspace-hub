# WRK-1261: Skill Quality Tier Hierarchy

## Context

`patterns.md` defines an enforcement gradient (Level 0 Prose → Level 3 Hook) but the skill evaluation tooling doesn't measure where each skill sits on that gradient. This WRK adds a measurable 4-tier classification (A/B/C/D) wired into the eval pipeline.

## Files

### New (4 files)

| File | Lines | Purpose |
|------|-------|---------|
| `config/skills/quality-tiers.yaml` | ~25 | Tier definitions (A/B/C/D) with criteria |
| `scripts/skills/skill_tier_lib.py` | ~70 | Pure library: `classify_tier()`, `tier_distribution()`, `classify_skill_file()` |
| `scripts/skills/skill-tier-report.py` | ~80 | CLI: ranked tier list, flags Tier D, YAML output |
| `scripts/skills/tests/test_skill_tier_lib.py` | ~100 | TDD tests (15+ cases) |

### Modified (4 files, minimal changes)

| File | Change |
|------|--------|
| `.claude/skills/development/skill-eval/scripts/eval-skills.py` | +10 lines: import tier lib, add `quality_tier` field to `SkillResult` + JSON output, add `tier_distribution` to report summary |
| `scripts/skills/ecosystem-eval-report.sh` | +12 lines: run `skill-tier-report.py` as tool 4, merge `tier_summary` into collated YAML |
| `.claude/skills/_internal/builders/skill-creator/SKILL.md` | +6 lines: `## Quality Tiers` section |
| `.claude/skills/workspace-hub/comprehensive-learning/SKILL.md` | +4 lines: tier reference in Phase 9 |

## Tier Classification Logic

Priority order (first match wins):
1. **Tier A** — frontmatter `scripts:` list with ≥1 entry
2. **Tier B** — body matches `EXEC_PATTERN` (reused from `audit_skill_lib.py`)
3. **Tier D** — body word count > 500 AND no script refs (decomposition candidate)
4. **Tier C** — everything else (focused prose, ≤200 lines typical)

Key: `skill_tier_lib.py` imports `EXEC_PATTERN` and `parse_frontmatter` from `audit_skill_lib.py` (same directory).

## Build Sequence (TDD)

| Step | Action |
|------|--------|
| 1 | Create `config/skills/quality-tiers.yaml` |
| 2 | Write `tests/test_skill_tier_lib.py` (RED) — 15 test cases |
| 3 | Implement `skill_tier_lib.py` (GREEN) |
| 4 | Write CLI tests, implement `skill-tier-report.py` |
| 5 | Add `quality_tier` to `eval-skills.py` (~10 lines) |
| 6 | Add tool 4 to `ecosystem-eval-report.sh` |
| 7 | Document in skill-creator + comprehensive-learning |
| 8 | Run full `ecosystem-eval-report.sh` → capture baseline |

## Verification

```bash
# Unit tests
uv run --no-project python -m pytest scripts/skills/tests/test_skill_tier_lib.py -v

# Standalone tier report
uv run --no-project python scripts/skills/skill-tier-report.py

# eval-skills.py JSON includes quality_tier
uv run --no-project python .claude/skills/development/skill-eval/scripts/eval-skills.py --format json | python3 -c "import json,sys; d=json.load(sys.stdin); print(d['summary']['tier_distribution'])"

# Full ecosystem report includes tier_summary
bash scripts/skills/ecosystem-eval-report.sh
grep tier_summary specs/audit/skill-eval-*.yaml
```
