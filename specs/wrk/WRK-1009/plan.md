# WRK-1009 Plan — Skill upkeep and curation: evals, A/B tests, daily cron integration

**Route B — Medium complexity | ace-linux-1 | Orchestrator: Claude**

*Plan decisions (Stage 5 user review 2026-03-10):*
*① Eval defs: central `specs/skills/evals/` (not per-skill)*
*② A/B mode: static schema validation only — no live model runs*
*③ Retirement threshold: 0.05 baseline_usage_rate + ≥10 invocations minimum (conservative)*
*④ Pilot skills: work-queue, workflow-gatepass, comprehensive-learning*
*⑤ Added: skill→script conversion scan phase*

## Phase 0: Skill→Script Conversion Scan

- 0a. Script `scripts/skills/identify-script-candidates.sh` — scans all 508 SKILL.md files
  for the pattern: skill body is purely deterministic (runs commands, no reasoning, no
  branching on model judgment). Criteria: body contains only bash/script instructions,
  no "think about", no conditional guidance, no context-reading steps.
- 0b. Emit `specs/skills/script-conversion-candidates.md` — list of skill name, path,
  rationale, and suggested script path for each candidate.
- 0c. No actual conversion in this WRK — output is a candidate list only; each conversion
  is a separate WRK. (Aligned with `.claude/rules/patterns.md` "Scripts Over LLM Judgment".)

## Phase 1: Eval Framework Design (TDD-first)

- 1a. Write `specs/skills/skill-eval-framework.md` — capability eval schema, procedural
  eval schema, A/B eval modes (static only: schema fidelity + triggering accuracy, NOT
  live model runs), eval definition format (central YAML in `specs/skills/evals/`).
- 1b. Write failing tests in `scripts/skills/tests/test_skill_evals.sh` (bash, bats-style)
  covering: eval schema validation, JSONL report format, cron hook integration,
  retirement threshold logic.
- 1c. Implement `scripts/skills/run-skill-evals.sh` — reads eval defs from
  `specs/skills/evals/*.yaml`, validates each against its skill's SKILL.md, emits JSONL
  report to `.claude/state/skill-eval-results/YYYY-MM-DD.jsonl`.
- 1d. Write central eval definitions for 3 pilot skills in `specs/skills/evals/`:
  - `work-queue.yaml` — capability: required commands present; procedural: 20-stage lifecycle documented
  - `workflow-gatepass.yaml` — capability: R-25/R-26/R-27 rules documented; procedural: gate sequence correct
  - `comprehensive-learning.yaml` — capability: all phases documented; procedural: cron integration hook present

## Phase 2: Curation Tooling

- 2a. Write `scripts/cron/skill-curation-nightly.sh` — wraps run-skill-evals.sh, duplicate
  detection, retirement flagging (retirement candidate if `baseline_usage_rate < 0.05` AND
  `calls_in_period < 10`; never auto-deletes, only logs candidate).
- 2b. Wire into `scripts/cron/comprehensive-learning-nightly.sh` as new Step 4b (after
  existing Step 4 validate-skills.sh).
- 2c. Duplicate detection: scan all SKILL.md `name:` frontmatter fields; emit WARNING if
  two skills share the same name across subdirectories.
- 2d. Failing evals → write candidate WRK file to `.claude/state/skill-eval-candidates/`
  (non-blocking; orchestrator reviews at next session).

## Phase 3: Daily Report Integration

- 3a. Eval summary (PASS/FAIL counts, retirement candidates, script-conversion candidates)
  emitted via `scripts/productivity/sections/skill-evals.sh` for `/today`.
- 3b. `/reflect` ecosystem block shows: eval health, # retirement candidates, # duplicates.

## Test Strategy

| Test | Type | Pass condition |
|------|------|---------------|
| Eval script exits 0 on valid eval dir | unit | exit code = 0 |
| Eval script exits 1 on missing skill | unit | exit code = 1, error message |
| JSONL report has required fields | unit | skill, result, timestamp, eval_type |
| Duplicate detection flags same-name skill | unit | stdout contains "DUPLICATE" |
| Retirement flag: rate < 0.05 AND calls < 10 | unit | flagged as candidate |
| Retirement safe: rate ≥ 0.05 → not flagged | unit | not in candidate list |
| script-candidate scan produces output file | unit | specs/skills/script-conversion-candidates.md exists |
| Cron integration: step 4b runs | integration | comprehensive-learning log has "skill-curation" |
| Pilot eval work-queue PASS | integration | JSONL result=pass for work-queue |

## Scope Boundary (deferred)

External upstream scan (openai/skills, anthropics/skills), live A/B model runs,
auto-remediation — all follow-on WRKs.

## Deliverables

- `specs/skills/skill-eval-framework.md`
- `specs/skills/evals/work-queue.yaml`, `workflow-gatepass.yaml`, `comprehensive-learning.yaml`
- `specs/skills/script-conversion-candidates.md`
- `scripts/skills/run-skill-evals.sh`
- `scripts/skills/identify-script-candidates.sh`
- `scripts/skills/tests/test_skill_evals.sh`
- `scripts/cron/skill-curation-nightly.sh`
- Updated `scripts/cron/comprehensive-learning-nightly.sh` (Step 4b)
