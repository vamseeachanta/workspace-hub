# WRK-1261: Quantify Skill Curation Quality Hierarchy

## Context

patterns.md defines an enforcement gradient (prose → micro-skill → script → hook) but
skill eval tooling didn't measure where each skill sits. WRK-1261 makes this measurable.
All code artifacts were implemented in a prior session but remain **untracked** — this plan
covers verification, baseline recording, and commit.

## AC Verification Status

| AC | Artifact | Status |
|----|----------|--------|
| 1 | `config/skills/quality-tiers.yaml` (4 tiers: A/B/C/D) | PASS — exists |
| 2 | `eval-skills.py` computes `quality_tier` per skill | PASS — lines 587-594, 790, 804 |
| 3 | `ecosystem-eval-report.sh` includes `tier_summary` in collated YAML | PASS — line 123, verified in output |
| 4 | `scripts/skills/skill-tier-report.py` ranked list, Tier D flagged | PASS — 143 lines |
| 5 | Docs in skill-creator (lines 114-120) + comprehensive-learning Phase 9 | PASS |
| 6 | Baseline: `specs/audit/skill-eval-2026-03-16.yaml` tier_summary | PASS — A=8 B=58 C=2957 D=104 |

## Baseline Tier Distribution

```
Tier A (Script-wired):            8  ( 0.3%)
Tier B (Exec-pattern):           58  ( 1.9%)
Tier C (Focused prose):        2957  (94.6%)
Tier D (Decomposition candidate): 104  ( 3.3%)
Total:                          3127
```

## Implementation Plan

1. **Stage and commit** the following untracked/modified files:
   - `config/skills/quality-tiers.yaml`
   - `scripts/skills/skill_tier_lib.py`
   - `scripts/skills/tests/test_skill_tier_lib.py`
   - `specs/audit/skill-tiers-2026-03-16.yaml` (baseline)

2. **No code changes needed** — all 6 ACs verified against existing artifacts.

## Verification

- 23/23 TDD tests PASS (`test_skill_tier_lib.py`)
- Full pipeline run: `ecosystem-eval-report.sh` → tier_summary in collated YAML
- `skill-tier-report.py --format yaml` → correct distribution
