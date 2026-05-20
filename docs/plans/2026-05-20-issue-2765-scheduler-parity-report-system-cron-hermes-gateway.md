# Issue #2765 Plan — feat(operations): add scheduler parity report for system cron and Hermes Gateway cron

- **Issue**: https://github.com/vamseeachanta/workspace-hub/issues/2765
- **Status**: draft — round 1 adversarial review returned MAJOR; revision required
- **Date**: 2026-05-20
- **Complexity**: T2
- **Execution mode**: parallel-readonly for evidence gathering; single-lane implementation after approval because report schema and tests share parser code.

## Resource Intelligence Summary

### Evidence
- **GitHub issue #2765** — Live issue body verified open with `status:needs-plan`; asks for a single parity view across system cron and Hermes Gateway cron.
- **`scripts/cron/setup-cron.sh:88-134`** — Dry-run emits system crontab entries from YAML for current hostname; this is the canonical system-cron render source.
- **`config/scheduled-tasks/schedule-tasks.yaml`** — Single source of truth for in-repo system scheduled tasks, but does not include Hermes Gateway cron jobs.
- **`hermes cron list` live evidence from issue body** — Gateway-managed jobs like memory bridge, Gmail digest, wiki health, tier1 indexing, and cleanup exist outside system-cron YAML.
- **`scripts/monitoring/tests/test_cron_health_check.sh`** — Existing cron-health tests parse log freshness and errors; parity report should complement, not replace, health checks.

### Reproduction proofs
- **Runtime failure reproduction**: N/A — governance/scheduler contract plan; no single failing runtime claim to reproduce.
- **Live issue state**: `gh issue view 2765` confirmed the issue is open and labeled `status:needs-plan` before this plan was drafted.

### Gaps / assumptions
- Current planning uses previously captured `hermes cron list` evidence from issue intake; implementation should capture fresh live output in tests/report fixtures before changing runtime behavior.
- Raw provider logs may contain local/private runtime evidence and should remain local-only unless already tracked reports explicitly require redacted summaries.
- No secrets or credential values are required for this plan.

## Artifact Map

| Artifact | Path |
|---|---|
| Plan | `docs/plans/2026-05-20-issue-2765-scheduler-parity-report-system-cron-hermes-gateway.md` |
| Review artifacts | `scripts/review/results/2026-05-20-plan-2765-*.md` |
| GitHub issue | `https://github.com/vamseeachanta/workspace-hub/issues/2765` |

## Deliverable

A read-only operator report that compares schedule YAML, setup-cron rendering, live crontab, and Hermes Gateway cron jobs, classifies each job, and highlights missing/stale/duplicated scheduler state.

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
| create | `scripts/cron/scheduler-parity-report.py` | Read-only CLI collecting/parsing YAML, setup-cron dry-run text, optional crontab text, and Hermes cron list text. |
| create | `tests/cron/test_scheduler_parity_report.py` | Fixture-backed parser/classification/duplicate tests. |
| update | `docs/ops/scheduler-parity-report.md` | Operator usage, report interpretation, and no-mutation guarantee. |
| update | `config/scheduled-tasks/schedule-tasks.yaml` | Optionally add the parity report schedule only if approved; otherwise document manual invocation. |
| update | `docs/plans/README.md` | Index this plan. |

## TDD Test List

| Test | Verification | Input | Expected Output |
|---|---|---|---|
| `test_parses_setup_cron_dry_run` | Feed representative `setup-cron.sh --dry-run` output. | Dry-run fixture | System cron job rows |
| `test_parses_hermes_cron_list` | Feed representative `hermes cron list` output. | Hermes list fixture | Gateway job rows |
| `test_detects_duplicate_logical_job_across_planes` | Same logical ID appears in system cron and Hermes list. | Combined fixtures | Duplicate warning |
| `test_report_is_read_only` | Monkeypatch subprocess runner so mutating commands fail if called. | CLI invocation | Only list/dry-run commands called |
| `test_native_provider_ai_bypass_is_highlighted` | Fixture with `gsd-researcher` native Claude task. | Schedule fixture | Bypass/migration warning linking #2763 |

## Acceptance Criteria

- [ ] Report reads all four surfaces or records unavailable surfaces explicitly.
- [ ] Output separates system cron and Hermes Gateway cron.
- [ ] Native-provider AI bypasses are highlighted with related issue links.
- [ ] No scheduler mutation occurs.
- [ ] Tests cover parsers, duplicate detection, and read-only behavior.
- [ ] Adversarial plan review artifacts are saved under `scripts/review/results/`.
- [ ] GitHub issue is moved only to `status:plan-review` after review has no unresolved MAJOR findings.
- [ ] Implementation remains blocked until the user applies `status:plan-approved`.

## Adversarial Review Summary

Round 1 adversarial review complete: Claude MAJOR, Codex MAJOR, Gemini MAJOR. Do not move to status:plan-review. Blocking themes: duplicate logical-job mapping is undefined, YAML and unavailable-surface parser tests are missing, freshness/last-run evidence from issue scope is dropped, read-only subprocess whitelist is under-specified, and required harness/control-plane retrieval is incomplete. Next action is revise plan and re-review.

Review artifacts:
- `scripts/review/results/2026-05-20-plan-2765-claude.md`
- `scripts/review/results/2026-05-20-plan-2765-codex.md`
- `scripts/review/results/2026-05-20-plan-2765-gemini.md`
- `scripts/review/results/2026-05-20-plan-2765-disagreement.md`

## Risks and Open Questions

- Parsing human CLI output is brittle; keep fixture contract narrow and allow JSON output if Hermes CLI supports it later.
- Report could be mistaken for scheduler authority; docs must state it is read-only evidence, not a mutator.
- Live crontab may contain unrelated user entries; report must distinguish workspace-hub-managed entries from external cron lines.

## Implementation Notes for Future Approved Work

- Write tests first and confirm RED where applicable.
- Use `uv run --no-project` for Python commands in this repository.
- Use `--body-file` for all GitHub comments/edits containing Markdown.
- Keep raw logs local-only unless redacted/tracked report policy explicitly allows them.
