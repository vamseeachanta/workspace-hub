# WRK-1142 Acceptance Test Matrix

| ID | What | Type | Expected | Result |
|----|------|------|----------|--------|
| T50 | start_stage.py stdout includes 'scripts-over-LLM' for stage-04 | happy | string present in output, exit 0 | PASS |
| T51 | stage-10-prompt.md includes 'TDD MANDATORY' after fresh run | happy | string in file, exit 0, no stale artifact | PASS |
| T52 | missing micro-skill returns warning string, no crash | edge | "[stage micro-skill not found: ...]" | PASS |
| T53 | duplicate stage-04 micro-skills raise RuntimeError | error | RuntimeError with 'multiple' in message | PASS |
| T54 | all 20 stage micro-skill files have ≥5 non-blank lines | coverage | assertion passes for stages 01-20 | PASS |
| T55 | SKILL.md ≤150 lines after migration | constraint | 120 lines (under limit) | PASS |

Test command: `uv run --no-project python -m pytest scripts/work-queue/tests/test_stage_micro_skills.py -v`
All 6 tests: PASS
