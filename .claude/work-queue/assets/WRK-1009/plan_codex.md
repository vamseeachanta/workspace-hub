OpenAI Codex v0.112.0 (research preview)
--------
workdir: /mnt/local-analysis/workspace-hub
model: gpt-5.4
provider: openai
approval: never
sandbox: workspace-write [workdir, /tmp, $TMPDIR, /home/vamsee/.codex/memories]
reasoning effort: medium
reasoning summaries: none
session id: 019cd927-9f5c-7d63-8fc2-3b8ebebf2d02
--------
user
# Stance: Codex Plan Draft Review

You are a software engineer agent. Your focus is on **implementation correctness, edge cases, and testability**.

You will receive a Claude-authored plan draft. Walk it section-by-section and produce your own refined version.

When reviewing:
1. Challenge any assumptions about implementation approach — is there a simpler or more robust way?
2. Identify edge cases not covered (malformed input, missing fields, timezone/date math, quota exhaustion).
3. Flag AC gaps — things implementable but not covered by the listed tests.
4. Assess integration risks (nightly cron, file writes, CLI availability).
5. Verify uv run --no-project python is used wherever Python is called.

Your output must be a complete refined plan (same structure as the input draft).
Add a "Codex Notes" section at the end with your specific findings.

---
CLAUDE DRAFT PLAN:
# WRK-1009 Plan — Skill upkeep and curation: evals, A/B tests, daily cron integration

**Route B — Medium complexity | dev-primary | Orchestrator: Claude**

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
mcp startup: no servers
codex
Reviewing the WRK-1009 draft as a plan artifact, so I’m loading the minimum workflow/planning instructions first: `work-queue-workflow`, `workflow-gatepass`, and `plan-mode`, then I’ll refine the draft section-by-section with implementation and test risks called out.
exec
/bin/bash -lc "sed -n '1,220p' .claude/skills/workspace-hub/plan-mode/SKILL.md" in /mnt/local-analysis/workspace-hubexec
/bin/bash -lc "sed -n '1,220p' .claude/skills/workspace-hub/workflow-gatepass/SKILL.md" in /mnt/local-analysis/workspace-hubexec
/bin/bash -lc "sed -n '1,220p' .claude/skills/workspace-hub/work-queue-workflow/SKILL.md" in /mnt/local-analysis/workspace-hub succeeded in 51ms:
---
name: plan-mode
description: >
  Invoke EnterPlanMode at deliberative WRK stages before writing any artifact.
  Prevents premature file writes during analysis and synthesis phases.
version: 1.0.0
updated: 2026-03-09
category: workspace-hub
triggers:
  - Stage 4 plan draft
  - Stage 6 cross-review
  - Stage 10 work execution
  - Stage 13 agent cross-review
related_skills:
  - workspace-hub/work-queue-workflow
  - superpowers/writing-plans
---
# Plan-Mode Gates

## When to Enter Plan Mode
 succeeded in 51ms:
---
name: workflow-gatepass
description: >
  Enforce WRK lifecycle gatepass from session start through close/archive with
  machine-checkable evidence requirements and explicit no-bypass rules.
version: 1.0.6
updated: 2026-03-07
category: workspace-hub
triggers:
  - workflow gatepass
  - wrk gate enforcement
  - lifecycle gate
  - close gate evidence
related_skills:
  - workspace-hub/session-start
  - coordination/workspace/work-queue
  - workspace-hub/session-end
  - workspace-hub/wrk-lifecycle-testpack
capabilities:
  - lifecycle-gate-enforcement
 succeeded in 50ms:
---
name: work-queue-workflow
description: >
  Explicit entrypoint skill for the WRK work-queue lifecycle workflow. Points to
  the canonical work-queue process and gatepass enforcement sequence.
version: 1.7.1
updated: 2026-03-10
category: workspace-hub
triggers:
  - work-queue workflow
  - wrk workflow
  - /work workflow
  - lifecycle workflow
related_skills:
  - coordination/workspace/work-queue
  - workspace-hub/workflow-gatepass
  - workspace-hub/workflow-html
  - workspace-hub/session-start
  - workspace-hub/session-end
capabilities:
codex
The workflow contract is consistent with a Stage 5/6 plan review. I’m checking the actual repo paths next so the refined plan doesn’t assume scripts or report sections that don’t exist.
exec
/bin/bash -lc "rg -n \"comprehensive-learning-nightly|validate-skills|/today|reflect|skill-eval|duplicate\" scripts .claude -g '"'!**/.git/**'"'" in /mnt/local-analysis/workspace-hubexec
/bin/bash -lc "rg --files specs | rg 'skills|templates|wrk'" in /mnt/local-analysis/workspace-hubexec
/bin/bash -lc "rg --files scripts | rg 'skills|cron|productivity/sections|work-queue|review'" in /mnt/local-analysis/workspace-hub succeeded in 647ms:
specs/templates/plan-template-minimal.md
specs/templates/plan-html-review-final-template.md
specs/templates/future-work-template.yaml
specs/templates/future-work-recommendations-template.md
specs/templates/claim-evidence-template.yaml
specs/templates/route-c-generic.md
specs/templates/route-c-energy.md
specs/templates/plan-template.md
specs/templates/route-c-structural.md
specs/templates/route-c-marine.md
specs/templates/skill-invocation-log-template.yaml
specs/templates/user-review-browser-open-template.yaml
specs/templates/stage5-migration-exemption-template.yaml
specs/templates/stage5-evidence-contract.yaml
specs/templates/stage-evidence-template.yaml
specs/templates/skill-manifest-template.yaml
specs/templates/user-review-common-draft-template.yaml
specs/templates/user-review-capture.yaml
specs/templates/user-review-plan-draft-template.yaml
specs/templates/user-review-publish-template.yaml
 succeeded in 1.05s:
scripts/cron-repository-sync.sh
scripts/skills/validate-skills.sh
scripts/skills/sync-knowledge-work-plugins.sh
scripts/skills/review-skills-graph.sh
scripts/cron/update_portfolio_signals.py
scripts/cron/update-portfolio-signals.sh
scripts/cron/setup-cron.sh
scripts/cron/crontab-template.sh
scripts/cron/comprehensive-learning-nightly.sh
scripts/automation/gate_pass_review.sh
scripts/productivity/sections/wrk-health.sh
scripts/productivity/sections/summary-header.sh
scripts/productivity/sections/session-analysis.sh
scripts/productivity/sections/repo-health.sh
scripts/productivity/sections/learning-outcomes.sh
scripts/productivity/sections/git-summary.sh
scripts/productivity/sections/data-health.sh
scripts/productivity/sections/ai-usage-summary.sh
scripts/skills/repo-portfolio-steering/compute-balance.py
scripts/skills/merge-submodule-skills.sh
 succeeded in 17.61s:
.claude/rules/coding-style.md:48:- After edits: confirm imports not mangled, no duplicate definitions, no deleted adjacent code
.claude/docs/self-learning-workflow.md:26:5AM — claude-reflect
.claude/docs/self-learning-workflow.md:28:  → cross-repo git history reflection
.claude/docs/self-learning-workflow.md:47:| `claude-reflect` | 5AM cron | Git history + cross-repo patterns |
.claude/docs/self-learning-workflow.md:52:| `claude-reflect` | Daily/weekly | Feeds into session-analysis context |
.claude/docs/self-learning-workflow.md:63:| claude-reflect SKILL.md | .claude/skills/.../ | 5AM cron step | Current |
scripts/work-queue/exit_stage.py:323:    # Regenerate lifecycle HTML to reflect this stage as done
.claude/work-queue/triage-report.yaml:137:      reason: "WRK-087 (Improve test coverage across workspace repos) is an umbrella/duplicate of the existing per-repo test coverage items WRK-051 through WRK-056. The individual items are more actionable. Archive WRK-087 as redundant."
.claude/docs/plugins-vs-skills.md:26:**Invocation**: Plugin skills are namespaced — `/plugin-name:skill-name` — preventing collisions. Standalone skills keep short names like `/work` or `/reflect`.
.claude/docs/plugins-vs-skills.md:78:| **Naming** | `plugin-name:skill-name` prefix required | Arbitrary short names like `/work`, `/reflect`, `/commit` | Skills win: our commands are highly ergonomic |
.claude/docs/plugins-vs-skills.md:97:2. **Unnamespaced short commands** — `/work`, `/reflect`, `/commit`, `/improve` are two-to-eight character invocations. Plugin namespacing forces `/workspace-hub:work` which would break session muscle memory and all documented workflows.
.claude/commands/workspace-hub/work.md:91:- `/reflect` - Daily reflection includes work queue health check
.claude/knowledge/index.json:136:        "reflect",
.claude/knowledge/index.json:288:        "validate-skills",
.claude/docs/new-machine-setup.md:167:| 02:00 daily | `0 2 * * *` | `comprehensive-learning-nightly.sh` |
scripts/work-queue/checkpoint.sh:26:    # Avoid duplicates
.claude/commands/workspace-hub/repo-sync.md:44:- `/reflect` - Cross-repository reflection
.claude/commands/workspace-hub/repo-capability-map.md:71:- `/reflect` - Periodic reflection (tracks capability changes)
.claude/work-queue/pending/WRK-595.md:124:3. Update `scripts/data/orcaflex/README.md` to reflect all-licensed-win-1 pipeline
.claude/commands/workspace-hub/reflect.md:2:name: reflect
codex
# WRK-1009 Plan — Skill upkeep and curation: evals, A/B tests, daily cron integration

**Route B — Medium complexity | dev-primary | Orchestrator: Claude**

*Plan decisions (Stage 5 user review 2026-03-10):*
*① Eval defs: central `specs/skills/evals/` (not per-skill)*
*② A/B mode: static validation only — no live model/provider runs*
*③ Retirement threshold: `baseline_usage_rate < 0.05` + `calls_in_period < 10`, but only when usage data is present and window metadata is valid*
*④ Pilot skills: `work-queue`, `workflow-gatepass`, `comprehensive-learning`*
*⑤ Added: skill→script conversion scan phase*
*⑥ Implementation shape: keep shell entrypoints, but use `uv run --no-project python ...` for YAML/frontmatter/report parsing to avoid brittle bash parsing*

## Phase 0: Skill→Script Conversion Scan

- 0a. Implement `scripts/skills/identify-script-candidates.sh` as a thin wrapper over `uv run --no-project python scripts/skills/identify_script_candidates.py`; enumerate skills from the repo, do not hardcode “508”.
- 0b. Heuristic must classify `candidate`, `not_candidate`, or `needs_human_review`; pure regex matching is not sufficient. Treat references to context loading, user judgment, branching, or cross-file synthesis as non-deterministic.
- 0c. Emit both machine-readable and reviewable outputs:
  - `specs/skills/script-conversion-candidates.md`
  - `.claude/state/skill-script-candidates/<UTC-date>.json`
- 0d. Write outputs atomically and replace prior same-day artifacts instead of appending.
- 0e. No actual conversion in this WRK; each conversion remains a separate WRK.

## Phase 1: Eval Framework Design (TDD-first)

- 1a. Write `specs/skills/skill-eval-framework.md` with:
  - eval schema versioning
  - static capability/procedural checks only
  - required fields for each eval YAML
  - normalized PASS/WARN/FAIL/SKIP semantics
  - timestamp policy: ISO 8601 UTC in results
  - file-write and cron-failure behavior
- 1b. Write failing tests first. Prefer existing repo conventions over inventing “bats-style” if bats is not already required. Cover:
  - valid eval schema
  - malformed YAML
  - missing skill path
  - missing or malformed frontmatter
  - missing required markers in `SKILL.md`
  - invalid usage-window metadata
  - JSONL result schema
  - atomic output behavior on failure
- 1c. Implement `scripts/skills/run-skill-evals.sh` as wrapper plus `scripts/skills/run_skill_evals.py`; Python does schema/frontmatter/report work and is always invoked via `uv run --no-project python`.
- 1d. Emit results to `.claude/state/skill-eval-results/<UTC-date>.jsonl` with one record per check, including at minimum: `run_id`, `skill_name`, `skill_path`, `eval_id`, `eval_type`, `result`, `reason`, `timestamp`, `source_eval`.
- 1e. Define pilot evals in `specs/skills/evals/`:
  - `work-queue.yaml`
  - `workflow-gatepass.yaml`
  - `comprehensive-learning.yaml`
  Each file should declare exact markers/sections expected, not vague prose assertions.

## Phase 2: Curation Tooling

- 2a. Implement `scripts/cron/skill-curation-nightly.sh` as the orchestrator for:
  - skill eval run
  - duplicate-name detection
  - retirement-candidate detection
  - script-conversion scan
- 2b. Wire it into `scripts/cron/comprehensive-learning-nightly.sh` after `validate-skills.sh`, but keep the new step non-destructive and clearly logged. If it fails, log failure and exit policy must be explicit in the framework doc.
- 2c. Duplicate detection must normalize skill names before comparison: trim, lowercase, collapse whitespace, and compare canonical names. Emit WARNING only; no auto-delete or auto-rename.
- 2d. Retirement logic must not flag when usage data is missing, stale, or window length is undefined. “No data” is `SKIP`, not “retire”.
- 2e. Failing evals should produce proposal artifacts under `.claude/state/skill-eval-candidates/`; do not create real WRK queue items outside `.claude/work-queue/`.
- 2f. All state writes should use temp files plus rename to avoid partial cron artifacts.

## Phase 3: Daily Report Integration

- 3a. Add `scripts/productivity/sections/skill-evals.sh` for `/today`, showing PASS/FAIL/WARN/SKIP counts, duplicate-name warnings, retirement candidates, and script-conversion candidate count.
- 3b. Integrate the same summarized state into the `/reflect` ecosystem output, but first confirm the owning renderer/script instead of assuming a direct shell section hook.
- 3c. `/today` and `/reflect` should read the latest successful artifact only; they must degrade gracefully when no nightly report exists yet.
- 3d. Keep report parsing lightweight and deterministic; no provider/model calls in daily surfaces.

## Test Strategy

| Test | Type | Pass condition |
|------|------|---------------|
| Eval runner exits 0 on valid eval dir | unit | exit code = 0 |
| Eval runner exits non-zero on malformed YAML | unit | clear error, no partial JSONL |
| Eval runner exits non-zero on missing skill path | unit | exit code != 0, path named |
| JSONL report has required fields | unit | `run_id`, `skill_name`, `result`, `timestamp`, `eval_type` present |
| Frontmatter missing or malformed is handled | unit | result = FAIL with reason |
| Duplicate detection flags normalized same-name skill | unit | output contains WARNING for normalized collision |
| Retirement flag only when rate < 0.05 AND calls < 10 AND window valid | unit | flagged as candidate |
| Retirement safe when rate >= 0.05 or calls >= 10 | unit | not flagged |
| Retirement skip when usage data missing/stale | unit | result = SKIP, not candidate |
| Script-candidate scan produces both md and json outputs | unit | both files exist |
| Cron integration logs skill-curation step | integration | nightly log contains named step |
| `/today` section tolerates missing nightly artifact | integration | section renders fallback, exits 0 |
| Pilot eval `work-queue` PASS path | integration | JSONL contains pass for expected checks |
| Failed eval candidate proposal is written outside work queue | integration | proposal file exists only under `.claude/state/skill-eval-candidates/` |

## Scope Boundary (deferred)

External upstream scan (`openai/skills`, `anthropics/skills`), live A/B model runs, auto-remediation, auto-WRK creation, and cross-machine aggregation beyond `dev-primary` are follow-on WRKs.

## Deliverables

- `specs/skills/skill-eval-framework.md`
- `specs/skills/evals/work-queue.yaml`, `workflow-gatepass.yaml`, `comprehensive-learning.yaml`
- `specs/skills/script-conversion-candidates.md`
- `scripts/skills/run-skill-evals.sh`
- `scripts/skills/run_skill_evals.py`
- `scripts/skills/identify-script-candidates.sh`
- `scripts/skills/identify_script_candidates.py`
- test coverage for eval runner / cron integration / report section behavior
- `scripts/cron/skill-curation-nightly.sh`
- `scripts/productivity/sections/skill-evals.sh`
- updated `scripts/cron/comprehensive-learning-nightly.sh`

## Codex Notes

- The draft leans too hard on bash for YAML/frontmatter/report parsing. That is fragile; keep shell entrypoints, but use `uv run --no-project python` helpers for correctness.
- “A/B tests” needed sharper definition. With no live runs, this is static conformance/trigger-validation, not a real experiment.
- The retirement rule was underspecified for missing or stale usage data. Without a valid measurement window, retirement decisions will generate false positives.
- “Write candidate WRK file to `.claude/state/...`” must stay a proposal artifact only. Real WRK items belong in `.claude/work-queue/` per repo policy.
- The `/reflect` integration target is not obvious from the draft. The repo clearly has `/today` section scripts, but `/reflect` may require command/report wiring rather than a new shell section.
- Cron/file-write risks were missing: atomic writes, clear failure policy, and latest-successful-artifact lookup should be explicit.
- Date handling should be UTC in artifacts to avoid nightly boundary bugs.
- AC/test gaps in the draft: malformed YAML, malformed frontmatter, missing usage metadata, normalized duplicate names, missing nightly artifact for `/today`, and partial-write failure cases.
tokens used
52,730
# WRK-1009 Plan — Skill upkeep and curation: evals, A/B tests, daily cron integration

**Route B — Medium complexity | dev-primary | Orchestrator: Claude**

*Plan decisions (Stage 5 user review 2026-03-10):*
*① Eval defs: central `specs/skills/evals/` (not per-skill)*
*② A/B mode: static validation only — no live model/provider runs*
*③ Retirement threshold: `baseline_usage_rate < 0.05` + `calls_in_period < 10`, but only when usage data is present and window metadata is valid*
*④ Pilot skills: `work-queue`, `workflow-gatepass`, `comprehensive-learning`*
*⑤ Added: skill→script conversion scan phase*
*⑥ Implementation shape: keep shell entrypoints, but use `uv run --no-project python ...` for YAML/frontmatter/report parsing to avoid brittle bash parsing*

## Phase 0: Skill→Script Conversion Scan

- 0a. Implement `scripts/skills/identify-script-candidates.sh` as a thin wrapper over `uv run --no-project python scripts/skills/identify_script_candidates.py`; enumerate skills from the repo, do not hardcode “508”.
- 0b. Heuristic must classify `candidate`, `not_candidate`, or `needs_human_review`; pure regex matching is not sufficient. Treat references to context loading, user judgment, branching, or cross-file synthesis as non-deterministic.
- 0c. Emit both machine-readable and reviewable outputs:
  - `specs/skills/script-conversion-candidates.md`
  - `.claude/state/skill-script-candidates/<UTC-date>.json`
- 0d. Write outputs atomically and replace prior same-day artifacts instead of appending.
- 0e. No actual conversion in this WRK; each conversion remains a separate WRK.

## Phase 1: Eval Framework Design (TDD-first)

- 1a. Write `specs/skills/skill-eval-framework.md` with:
  - eval schema versioning
  - static capability/procedural checks only
  - required fields for each eval YAML
  - normalized PASS/WARN/FAIL/SKIP semantics
  - timestamp policy: ISO 8601 UTC in results
  - file-write and cron-failure behavior
- 1b. Write failing tests first. Prefer existing repo conventions over inventing “bats-style” if bats is not already required. Cover:
  - valid eval schema
  - malformed YAML
  - missing skill path
  - missing or malformed frontmatter
  - missing required markers in `SKILL.md`
  - invalid usage-window metadata
  - JSONL result schema
  - atomic output behavior on failure
- 1c. Implement `scripts/skills/run-skill-evals.sh` as wrapper plus `scripts/skills/run_skill_evals.py`; Python does schema/frontmatter/report work and is always invoked via `uv run --no-project python`.
- 1d. Emit results to `.claude/state/skill-eval-results/<UTC-date>.jsonl` with one record per check, including at minimum: `run_id`, `skill_name`, `skill_path`, `eval_id`, `eval_type`, `result`, `reason`, `timestamp`, `source_eval`.
- 1e. Define pilot evals in `specs/skills/evals/`:
  - `work-queue.yaml`
  - `workflow-gatepass.yaml`
  - `comprehensive-learning.yaml`
  Each file should declare exact markers/sections expected, not vague prose assertions.

## Phase 2: Curation Tooling

- 2a. Implement `scripts/cron/skill-curation-nightly.sh` as the orchestrator for:
  - skill eval run
  - duplicate-name detection
  - retirement-candidate detection
  - script-conversion scan
- 2b. Wire it into `scripts/cron/comprehensive-learning-nightly.sh` after `validate-skills.sh`, but keep the new step non-destructive and clearly logged. If it fails, log failure and exit policy must be explicit in the framework doc.
- 2c. Duplicate detection must normalize skill names before comparison: trim, lowercase, collapse whitespace, and compare canonical names. Emit WARNING only; no auto-delete or auto-rename.
- 2d. Retirement logic must not flag when usage data is missing, stale, or window length is undefined. “No data” is `SKIP`, not “retire”.
- 2e. Failing evals should produce proposal artifacts under `.claude/state/skill-eval-candidates/`; do not create real WRK queue items outside `.claude/work-queue/`.
- 2f. All state writes should use temp files plus rename to avoid partial cron artifacts.

## Phase 3: Daily Report Integration

- 3a. Add `scripts/productivity/sections/skill-evals.sh` for `/today`, showing PASS/FAIL/WARN/SKIP counts, duplicate-name warnings, retirement candidates, and script-conversion candidate count.
- 3b. Integrate the same summarized state into the `/reflect` ecosystem output, but first confirm the owning renderer/script instead of assuming a direct shell section hook.
- 3c. `/today` and `/reflect` should read the latest successful artifact only; they must degrade gracefully when no nightly report exists yet.
- 3d. Keep report parsing lightweight and deterministic; no provider/model calls in daily surfaces.

## Test Strategy

| Test | Type | Pass condition |
|------|------|---------------|
| Eval runner exits 0 on valid eval dir | unit | exit code = 0 |
| Eval runner exits non-zero on malformed YAML | unit | clear error, no partial JSONL |
| Eval runner exits non-zero on missing skill path | unit | exit code != 0, path named |
| JSONL report has required fields | unit | `run_id`, `skill_name`, `result`, `timestamp`, `eval_type` present |
| Frontmatter missing or malformed is handled | unit | result = FAIL with reason |
| Duplicate detection flags normalized same-name skill | unit | output contains WARNING for normalized collision |
| Retirement flag only when rate < 0.05 AND calls < 10 AND window valid | unit | flagged as candidate |
| Retirement safe when rate >= 0.05 or calls >= 10 | unit | not flagged |
| Retirement skip when usage data missing/stale | unit | result = SKIP, not candidate |
| Script-candidate scan produces both md and json outputs | unit | both files exist |
| Cron integration logs skill-curation step | integration | nightly log contains named step |
| `/today` section tolerates missing nightly artifact | integration | section renders fallback, exits 0 |
| Pilot eval `work-queue` PASS path | integration | JSONL contains pass for expected checks |
| Failed eval candidate proposal is written outside work queue | integration | proposal file exists only under `.claude/state/skill-eval-candidates/` |

## Scope Boundary (deferred)

External upstream scan (`openai/skills`, `anthropics/skills`), live A/B model runs, auto-remediation, auto-WRK creation, and cross-machine aggregation beyond `dev-primary` are follow-on WRKs.

## Deliverables

- `specs/skills/skill-eval-framework.md`
- `specs/skills/evals/work-queue.yaml`, `workflow-gatepass.yaml`, `comprehensive-learning.yaml`
- `specs/skills/script-conversion-candidates.md`
- `scripts/skills/run-skill-evals.sh`
- `scripts/skills/run_skill_evals.py`
- `scripts/skills/identify-script-candidates.sh`
- `scripts/skills/identify_script_candidates.py`
- test coverage for eval runner / cron integration / report section behavior
- `scripts/cron/skill-curation-nightly.sh`
- `scripts/productivity/sections/skill-evals.sh`
- updated `scripts/cron/comprehensive-learning-nightly.sh`

## Codex Notes

- The draft leans too hard on bash for YAML/frontmatter/report parsing. That is fragile; keep shell entrypoints, but use `uv run --no-project python` helpers for correctness.
- “A/B tests” needed sharper definition. With no live runs, this is static conformance/trigger-validation, not a real experiment.
- The retirement rule was underspecified for missing or stale usage data. Without a valid measurement window, retirement decisions will generate false positives.
- “Write candidate WRK file to `.claude/state/...`” must stay a proposal artifact only. Real WRK items belong in `.claude/work-queue/` per repo policy.
- The `/reflect` integration target is not obvious from the draft. The repo clearly has `/today` section scripts, but `/reflect` may require command/report wiring rather than a new shell section.
- Cron/file-write risks were missing: atomic writes, clear failure policy, and latest-successful-artifact lookup should be explicit.
- Date handling should be UTC in artifacts to avoid nightly boundary bugs.
- AC/test gaps in the draft: malformed YAML, malformed frontmatter, missing usage metadata, normalized duplicate names, missing nightly artifact for `/today`, and partial-write failure cases.
