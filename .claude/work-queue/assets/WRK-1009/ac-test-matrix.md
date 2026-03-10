# WRK-1009 AC Test Matrix

| AC | Test | Result | Evidence |
|----|------|--------|---------|
| Eval framework design documented | `specs/skills/skill-eval-framework.md` exists with schema | PASS | specs/skills/skill-eval-framework.md |
| Capability + procedural eval schemas defined | Schemas in skill-eval-framework.md; pilot YAMLs use them | PASS | specs/skills/evals/*.yaml |
| 3 pilot skills have evals | work-queue.yaml, workflow-gatepass.yaml, comprehensive-learning.yaml | PASS | specs/skills/evals/ |
| run-skill-evals.sh executes and emits JSONL report | 6 checks all pass (0 skipped, 0 errors) | PASS | .claude/state/skill-eval-results/2026-03-10.jsonl |
| comprehensive-learning cron calls eval script | Step 4b added to comprehensive-learning-nightly.sh | PASS | scripts/cron/comprehensive-learning-nightly.sh |
| Low-scoring evals create candidate proposals | run_skill_evals.py writes proposals to skill-eval-candidates/ when checks don't pass | PASS | scripts/skills/run_skill_evals.py |
| Duplicate skill detection | detect_duplicate_skills.py found 8 duplicates across 393 skills | PASS | scripts/skills/detect_duplicate_skills.py |
| Retirement threshold 0.05/10inv conservative | check_retirement_candidates.py; SKIP on missing data | PASS | scripts/skills/check_retirement_candidates.py |
| Script→skill conversion scan | identify_script_candidates.py emits md+json; 3-way classifier | PASS | scripts/skills/identify_script_candidates.py |
| /today section shows eval health | scripts/productivity/sections/skill-evals.sh gracefully degrades | PASS | scripts/productivity/sections/skill-evals.sh |
| TDD tests pass (9/9) | bash scripts/skills/tests/test_skill_evals.sh → 9/9 pass | PASS | scripts/skills/tests/test_skill_evals.sh |
| Atomic writes (temp+rename) | All Python state writes use tmp+mv pattern | PASS | scripts/skills/run_skill_evals.py |
| uv run --no-project python for YAML ops | All Python invoked via uv; no bare python3 | PASS | scripts/skills/*.py, scripts/cron/skill-curation-nightly.sh |
