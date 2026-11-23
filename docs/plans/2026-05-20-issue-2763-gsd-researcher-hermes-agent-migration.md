# Issue #2763 Plan — plan(operations): migrate gsd-researcher scheduled AI work through Hermes Agent

- **Issue**: https://github.com/vamseeachanta/workspace-hub/issues/2763
- **Status**: draft — round 1 adversarial review returned MAJOR; revision required
- **Date**: 2026-05-20
- **Complexity**: T2
- **Execution mode**: single-lane implementation after approval; planning/review may be parallel-readonly because the script, schedule YAML, and Hermes cron evidence are separable.

## Resource Intelligence Summary

### Evidence
- **GitHub issue #2763** — Live issue body verified open with `status:needs-plan`; child of #2762 focused on `gsd-researcher`.
- **`config/scheduled-tasks/schedule-tasks.yaml`** — `gsd-researcher` is a system-cron YAML task with schedule `35 1 * * *`, machines including `ace-linux-1`, `requires: [claude, python3, uv]`, and `is_claude_task: true`.
- **`scripts/cron/gsd-researcher-nightly.sh`** — Script writes logs to `logs/research`, outputs to `.planning/research`, rotates domains by weekday, and calls native `claude -p` inside `run_claude()`.
- **`scripts/cron/tests/test_gsd_researcher_nightly.sh`** — Existing shell behavioral tests cover nightly researcher behavior and provide a natural place to add migration/compatibility tests.
- **Hermes skill/docs and Gateway cron evidence** — Hermes cron jobs exist independently from system cron; future cron prompts must be self-contained and cannot ask clarification.

### Reproduction proofs
- **Runtime failure reproduction**: N/A — governance/scheduler contract plan; no single failing runtime claim to reproduce.
- **Live issue state**: `gh issue view 2763` confirmed the issue is open and labeled `status:needs-plan` before this plan was drafted.

### Gaps / assumptions
- Current planning uses previously captured `hermes cron list` evidence from issue intake; implementation should capture fresh live output in tests/report fixtures before changing runtime behavior.
- Raw provider logs may contain local/private runtime evidence and should remain local-only unless already tracked reports explicitly require redacted summaries.
- No secrets or credential values are required for this plan.

## Artifact Map

| Artifact | Path |
|---|---|
| Plan | `docs/plans/2026-05-20-issue-2763-gsd-researcher-hermes-agent-migration.md` |
| Review artifacts | `scripts/review/results/2026-05-20-plan-2763-*.md` |
| GitHub issue | `https://github.com/vamseeachanta/workspace-hub/issues/2763` |

## Deliverable

A tested migration path for `gsd-researcher` that either runs scheduled AI research through Hermes Agent/Gateway cron or documents a deliberate exception with explicit evidence and health checks.

## Scope Boundaries

### In scope
- Plan, tests, documentation, and read-only validation/reporting surfaces named below.
- Scheduler/runtime classification and evidence capture.
- Explicit no-implementation-before-approval hard stop.

### Out of scope
- Applying `status:plan-approved` without user approval.
- Mutating live crontab or Hermes Gateway cron during planning.
- Migrating unrelated scheduled tasks not named by this issue.
- Committing raw local session logs or secrets.

## Pseudocode

```text
load canonical schedule/config fixtures
load optional live scheduler evidence
classify each scheduled job by scheduler plane and runtime type
if job executes AI/provider work and bypasses Hermes runtime:
    emit migration/exception finding with related issue link
if same logical job exists in multiple scheduler planes:
    emit duplicate warning
write/read report or validation result without mutating scheduler state
return non-zero only for contract violations that should block closeout
```

## Files to Change

| Action | Path | Reason |
|---|---|---|
| update | `config/scheduled-tasks/schedule-tasks.yaml` | Change task metadata/command only after migration design and tests specify the new authority. |
| update | `scripts/cron/gsd-researcher-nightly.sh` | Introduce a Hermes wrapper path or deprecate native Claude path behind an explicit exception flag. |
| update | `scripts/cron/tests/test_gsd_researcher_nightly.sh` | Add RED tests for no direct native Claude invocation in Hermes-managed mode and no duplicate schedule installation. |
| create | `docs/ops/gsd-researcher-scheduler.md` | Operator runbook for cadence, prompt context, logs, retries, and evidence. |
| update | `docs/plans/README.md` | Index this plan. |

## TDD Test List

| Test | Verification | Input | Expected Output |
|---|---|---|---|
| `test_hermes_mode_does_not_call_claude_binary` | Stub `claude` and `hermes` commands; Hermes mode must call Hermes wrapper/cron path and never invoke `claude -p`. | PATH stubs + dry-run env | Hermes command captured; Claude stub untouched |
| `test_native_exception_requires_explicit_flag` | If native Claude remains, script exits non-zero unless `ALLOW_NATIVE_CLAUDE_GSD_RESEARCHER=1` or documented config is present. | Unset flag with native mode | Fail-closed message |
| `test_schedule_yaml_metadata_matches_runtime` | YAML metadata no longer says only `requires: [claude]` when the runtime is Hermes-managed. | schedule fixture | Validation passes only for consistent metadata |
| `test_no_duplicate_system_and_hermes_entries` | Parity fixture with both active system cron and Hermes Gateway job for same logical ID is reported duplicate. | cron + Hermes list fixtures | Duplicate warning |

## Acceptance Criteria

- [ ] Decision is explicit: Hermes-managed migration or documented native exception.
- [ ] Existing cadence and output locations are preserved or intentionally changed in docs.
- [ ] Tests prove the selected runtime path and duplicate prevention.
- [ ] Operator runbook names log/evidence paths and retry/failure behavior.
- [ ] No implementation before user approval.
- [ ] Adversarial plan review artifacts are saved under `scripts/review/results/`.
- [ ] GitHub issue is moved only to `status:plan-review` after review has no unresolved MAJOR findings.
- [ ] Implementation remains blocked until the user applies `status:plan-approved`.

## Adversarial Review Summary

Round 1 adversarial review complete: Claude MAJOR, Codex MAJOR, Gemini MAJOR. Do not move to status:plan-review. Blocking themes: migration target is unresolved, setup-cron installer handling is missing, Hermes prompt/context artifact is unspecified, invented/native-exception flag lacks governance, #2762 dependency is not gated, and tests do not prove live scheduler equivalence. Next action is revise plan after #2762 contract direction is hardened.

Review artifacts:
- `scripts/review/results/2026-05-20-plan-2763-claude.md`
- `scripts/review/results/2026-05-20-plan-2763-codex.md`
- `scripts/review/results/2026-05-20-plan-2763-gemini.md`
- `scripts/review/results/2026-05-20-plan-2763-disagreement.md`

## Risks and Open Questions

- Hermes cron jobs run in fresh sessions, so prompt/context currently assembled by the shell script must be made self-contained.
- Removing native Claude too quickly could break a useful nightly signal if Hermes Gateway delivery/toolsets are not equivalent.
- Dual-running system cron and Hermes cron would duplicate research output and spend provider credits twice.

## Implementation Notes for Future Approved Work

- Write tests first and confirm RED where applicable.
- Use `uv run --no-project` for Python commands in this repository.
- Use `--body-file` for all GitHub comments/edits containing Markdown.
- Keep raw logs local-only unless redacted/tracked report policy explicitly allows them.
