# WRK-1081 Plan

Plan artifact reference. Full plan: `.claude/work-queue/assets/WRK-1081/plan-draft.md`

## Summary
Extended static analysis harness: bandit (security), radon (complexity), vulture (dead code)
across all 5 tier-1 Python repos via `scripts/quality/check-all.sh`.

## Architecture
- `--bandit`: two-pass (Pass 1 LOW warn; Pass 2 MEDIUM+ gate with -b baseline)
- `--radon`: non-blocking complexity C+ report
- `--vulture`: non-blocking 80%+ dead-code report
- `--static`: expands to all three
