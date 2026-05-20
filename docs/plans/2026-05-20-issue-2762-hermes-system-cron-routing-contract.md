# Issue #2762 Plan — plan(operations): define Hermes-vs-system cron scheduler routing contract

- **Issue**: https://github.com/vamseeachanta/workspace-hub/issues/2762
- **Status**: draft — round 1 adversarial review returned MAJOR; revision required
- **Date**: 2026-05-20
- **Complexity**: T2
- **Execution mode**: parallel-readonly for resource intelligence and review; single-lane for the eventual contract/test implementation because it touches shared schedule/governance files.

## Resource Intelligence Summary

### Evidence
- **GitHub issue #2762** — Live issue body verified open with `status:needs-plan`; scope asks for inventory across `schedule-tasks.yaml`, setup-cron dry-run, live crontab, and `hermes cron list`.
- **`config/scheduled-tasks/schedule-tasks.yaml`** — Header declares the schedule YAML the single source of truth for system scheduled tasks; `gsd-researcher` is marked `is_claude_task: true` with `requires: [claude, python3, uv]`.
- **`scripts/cron/setup-cron.sh:1-185`** — Installer renders only YAML tasks where `scheduler: cron` and current hostname is listed; it does not inspect Hermes Gateway cron jobs.
- **`logs/orchestrator/README.md` + provider audit** — Provider log ecosystem already separates Claude/Hermes/Codex/Gemini raw logs; audit command succeeds, so routing contract can consume existing evidence rather than inventing new log stores.
- **`.claude/hooks/session-logger.sh`** — Claude native sessions dual-write into Claude-specific repo orchestrator logs, proving observability integration but not Hermes runtime/proxy flow.

### Reproduction proofs
- **Runtime failure reproduction**: N/A — governance/scheduler contract plan; no single failing runtime claim to reproduce.
- **Live issue state**: `gh issue view 2762` confirmed the issue is open and labeled `status:needs-plan` before this plan was drafted.

### Gaps / assumptions
- Current planning uses previously captured `hermes cron list` evidence from issue intake; implementation should capture fresh live output in tests/report fixtures before changing runtime behavior.
- Raw provider logs may contain local/private runtime evidence and should remain local-only unless already tracked reports explicitly require redacted summaries.
- No secrets or credential values are required for this plan.

## Artifact Map

| Artifact | Path |
|---|---|
| Plan | `docs/plans/2026-05-20-issue-2762-hermes-system-cron-routing-contract.md` |
| Review artifacts | `scripts/review/results/2026-05-20-plan-2762-*.md` |
| GitHub issue | `https://github.com/vamseeachanta/workspace-hub/issues/2762` |

## Deliverable

A repo-backed scheduler routing contract and read-only validation surface that classifies each scheduled job by scheduler plane and runtime, making Hermes-managed AI work vs deterministic system cron explicit.

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
| create | `docs/standards/SCHEDULER_ROUTING_CONTRACT.md` | Define scheduler planes, runtime classes, migration rules, evidence requirements, and owner approval boundaries. |
| update | `config/scheduled-tasks/schedule-tasks.yaml` | Add/normalize explicit runtime classification metadata only after tests prove parser compatibility. |
| create | `scripts/cron/scheduler-routing-audit.py` | Read-only validator/report generator for YAML tasks; may optionally ingest captured Hermes cron list output. |
| create | `tests/cron/test_scheduler_routing_audit.py` | Fixture-backed tests for classification, AI runtime detection, and forbidden ambiguous tasks. |
| update | `docs/plans/README.md` | Index this plan. |

## TDD Test List

| Test | Verification | Input | Expected Output |
|---|---|---|---|
| `test_classifies_deterministic_system_cron` | Fixture YAML with no AI requirements returns scheduler_plane=system-cron/runtime=deterministic. | Minimal YAML task | JSON classification row |
| `test_flags_native_provider_ai_work` | Fixture task with `requires: [claude]` or `is_claude_task: true` is classified native-provider-ai and linked to migration guidance. | gsd-researcher-like fixture | Warning with issue #2763 |
| `test_does_not_treat_claude_hook_logs_as_hermes_runtime` | Claude log path fixture remains observability evidence, not Hermes runtime evidence. | Claude hook/log path sample | runtime=claude-native-observed |
| `test_contract_fails_on_missing_runtime_class_for_ai_task` | AI task without explicit runtime metadata fails validation. | Malformed YAML task | Non-zero validation result |

## Acceptance Criteria

- [ ] Scheduler planes and runtime classes are documented with examples.
- [ ] Read-only validator/report identifies deterministic system cron, native-provider AI, Hermes-managed AI, and bridge/export/audit jobs.
- [ ] Contract explicitly distinguishes Hermes runtime/proxy flow from repo observability/logging.
- [ ] No scheduler mutation occurs in this issue.
- [ ] Targeted tests pass before implementation closeout.
- [ ] Adversarial plan review artifacts are saved under `scripts/review/results/`.
- [ ] GitHub issue is moved only to `status:plan-review` after review has no unresolved MAJOR findings.
- [ ] Implementation remains blocked until the user applies `status:plan-approved`.

## Adversarial Review Summary

Round 1 adversarial review complete: Claude artifact verdict UNKNOWN/insufficient, Codex MAJOR, Gemini MAJOR. Do not move to status:plan-review. Blocking themes: insufficient harness/control-plane retrieval, missing embedded/live scheduler evidence, optional vs required Hermes/crontab surfaces, incomplete artifact map/tests, and disputed/missing evidence from reviewers. Next action is revise resource intelligence and plan before re-review.

Review artifacts:
- `scripts/review/results/2026-05-20-plan-2762-claude.md`
- `scripts/review/results/2026-05-20-plan-2762-codex.md`
- `scripts/review/results/2026-05-20-plan-2762-gemini.md`
- `scripts/review/results/2026-05-20-plan-2762-disagreement.md`

## Risks and Open Questions

- Over-classifying deterministic maintenance jobs as Hermes-managed would add unnecessary moving parts.
- Under-classifying native Claude jobs would preserve the ambiguity this issue is meant to remove.
- Hermes Gateway cron list output may differ across CLI versions; parser must be fixture-backed and fail-soft.

## Implementation Notes for Future Approved Work

- Write tests first and confirm RED where applicable.
- Use `uv run --no-project` for Python commands in this repository.
- Use `--body-file` for all GitHub comments/edits containing Markdown.
- Keep raw logs local-only unless redacted/tracked report policy explicitly allows them.
