# Disagreement report — plan #2762 (2026-05-20)

## Verdicts

| Provider | Verdict |
|---|---|
| claude | UNKNOWN |
| codex | MAJOR |
| gemini | MAJOR |

## Findings unique to each provider

A finding is 'unique to X' if its text appears in X's artifact but not
verbatim in any other provider's artifact.

### claude

(no findings unique to this provider)

### codex

- Issue [#2762](https://github.com/vamseeachanta/workspace-hub/issues/2762) explicitly scopes inventory across `config/scheduled-tasks/schedule-tasks.yaml`, `setup-cron.sh --dry-run`, live `crontab -l`, and `hermes cron list`, but the plan’s Pseudocode says only `load optional live scheduler evidence`, and the TDD list has no test for dry-run output, live crontab capture, or Hermes cron list parsing. This makes the core inventory requirement optional and untested.
- The plan’s Resource Intelligence is insufficient for a `cat:harness` / operations issue. `docs/plans/README.md` requires Harness/Infra plans to consult `CONTROL_PLANE_CONTRACT.md`, `config/agents/` settings, and `.claude/rules/`; the plan’s Evidence section cites only the issue, schedule YAML, `setup-cron.sh`, `logs/orchestrator/README.md`, provider audit, and `.claude/hooks/session-logger.sh`.
- The plan claims `config/scheduled-tasks/schedule-tasks.yaml` will be updated “only after tests prove parser compatibility,” but the TDD list does not include compatibility tests for existing consumers. `scripts/cron/setup-cron.sh` parses task fields and filters `task.get('scheduler', 'cron')`, while `scripts/cron/validate-schedule.py` validates required fields, scheduler values, machines, capabilities, cron syntax, and Claude invocation rules. New runtime metadata must be proven not to break both paths.
- The plan’s Acceptance Criteria require the validator/report to identify “Hermes-managed AI,” but the implementation design only says the validator “may optionally ingest captured Hermes cron list output.” Without required Hermes input fixtures or a required degraded-mode behavior, the validator can pass while never validating the Hermes scheduler plane that the issue is about.
- The plan’s Artifact Map omits the test and implementation artifacts it proposes later. `docs/plans/_template-issue-plan.md` requires Artifact Map rows for Tests and Implementation, but this plan lists only the plan, review artifacts, and GitHub issue. That weakens review traceability before implementation.
- The issue body cites related issues [#2089](https://github.com/vamseeachanta/workspace-hub/issues/2089), [#2291](https://github.com/vamseeachanta/workspace-hub/issues/2291), and [#1434](https://github.com/vamseeachanta/workspace-hub/issues/1434), but the plan’s Resource Intelligence does not verify their current state or extract decisions from them. `docs/plans/_template-issue-plan.md` requires every cited issue number to show state and title in embedded verification.

### gemini

- Plan cites `config/scheduled-tasks/schedule-tasks.yaml` as existing evidence and a target for update. Glob returns zero matches for this file at HEAD.
- Plan cites `scripts/cron/setup-cron.sh:1-185` as existing evidence. Glob returns zero matches for this file at HEAD.
- Plan cites `logs/orchestrator/README.md` and `.claude/hooks/session-logger.sh` as existing evidence. Neither file exists at HEAD.
- Scope contradiction in §Files to Change vs. §Deliverable/Pseudocode: The Deliverable restricts scope to a "read-only validation surface" and Pseudocode explicitly mandates "write/read report or validation result without mutating scheduler state". However, §Files to Change requires an update to `config/scheduled-tasks/schedule-tasks.yaml` to "Add/normalize explicit runtime classification metadata". Modifying the canonical scheduling configuration is a mutation, violating the read-only constraint.
- Unbound external reference in §TDD Test List: `test_flags_native_provider_ai_work` specifies an expected output of "Warning with issue #2763". Issue #2763 is completely undefined in the plan (the plan is scoped to issue #2762).
