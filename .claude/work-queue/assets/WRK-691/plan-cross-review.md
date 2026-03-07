# WRK-691 Plan Cross-Review Results
date: 2026-03-06
stage: 6 (Plan Cross-Review)

## Gemini — REQUEST_CHANGES
**Issues (all MEDIUM):**
1. Regex scanning of logs for commit messages susceptible to false positives (conversational mentions)
2. Persistence mechanism for 30-day rolling trend undefined
3. No `mkdir -p logs/orchestrator/claude/` guard before log write

## Codex — REQUEST_CHANGES
**Issues HIGH:**
1. Git commit drift detection unreliable — session logger truncates bash cmds at 150 chars; can't reconstruct commit messages from logs → use `git log --since` on real commits instead
2. Commit regex stricter than actual repo policy (`check-commit-msg.sh` exempts build/ci/merge/revert/wip; scope syntax not consistently required) → align regex or split into violation categories
3. `comprehensive-learning/SKILL.md` edit insufficient — runtime lives in `scripts/learning/comprehensive-learning.sh`; must update executable too

**Issues MEDIUM:**
4. Shell test location → `scripts/session/tests/` per file-taxonomy, not `tests/unit/`
5. `drift-summary.yaml` storage, retention, gitignore status undefined
6. `drift_rules_loaded` log guarantee weak if only in skill markdown (not a hook)

## Resolution Required
All 3 Codex HIGH items must be fixed in plan before Stage 7.
MEDIUM items to be addressed in plan revision.
