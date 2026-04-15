# Plan for #2291: fix(cron-health): harden failure detection and align task evidence contracts

> **Status:** draft
> **Complexity:** T2
> **Date:** 2026-04-15
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2291
> **Review artifacts:** scripts/review/results/2026-04-15-plan-2291-claude.md | scripts/review/results/2026-04-15-plan-2291-codex.md | scripts/review/results/2026-04-15-plan-2291-gemini.md

---

## Resource Intelligence Summary

### Existing repo code
- Found: `scripts/monitoring/cron-health-check.sh` — current health monitor parses `schedule-tasks.yaml`, resolves latest matching log, and classifies tasks via age plus a limited error-pattern grep over log text.
- Found: `scripts/cron/weekly-hermes-parity-review.sh` — writes dated markdown artifacts to `logs/weekly-parity/parity-review-YYYY-MM-DD.md`, not `cron-*.log`.
- Found: `scripts/cron/queue-refresh-weekly.sh` — intended weekly wrapper writes to `logs/queue-refresh/YYYY-MM-DD.log` and runs `uv run scripts/refresh-agent-work-queue.py`.
- Gap: there is no contract-check layer ensuring that a scheduled task’s declared `log:` pattern matches its actual emitted artifact path.
- Gap: `cron-health-check.sh` does not capture task exit codes or robust shell/dependency failure signatures; it only sees strings present in the latest artifact.

### Standards
| Standard | Status | Source |
|---|---|---|
| Not applicable | n/a | Non-engineering harness/operations issue |

### LLM Wiki pages consulted
- No relevant wiki pages; issue is about repo scheduler/health infrastructure rather than domain knowledge content.

### Documents consulted
- Issue #2291 body — defines three concrete failure modes to address: false green on `memory-health-check`, parity monitoring/evidence ambiguity for `weekly-hermes-parity-review`, and missing evidence for `queue-refresh-weekly`.
- `config/scheduled-tasks/schedule-tasks.yaml` — declares `memory-health-check`, `weekly-hermes-parity-review`, `queue-refresh-weekly`, and `cron-health` with their expected log/output contracts; also shows multiple other consumers depend on this contract surface.
- `logs/quality/cron-health-20260415.log` — current summary reports 34 tasks, 28 healthy, 6 problematic; flags `weekly-hermes-parity-review` as MISSING and `memory-health-check` as OK.
- `.claude/state/cron-health/2026-04-15.json` — machine-readable health output confirms the same classifications and current `last_log` assumptions.
- `logs/quality/memory-health-20260415.md` and `logs/quality/memory-health-20260414.md` — both latest artifacts are only `/bin/sh: 1: uv: not found`, proving the task is persistently failing despite current OK status.
- `logs/weekly-parity/parity-review-2026-04-12.md` — parity artifact exists, but under a secondary markdown artifact path rather than the configured cron log glob, so the issue is a mixed execution-evidence / secondary-artifact problem. The authoritative cron wrapper log can also fail before script startup if `logs/weekly-parity/` is absent on a clean machine.
- `logs/maintenance/review-audit-20260415.log` — shows review/compliance automation is live, so cron-health inaccuracies directly distort broader repo-ecosystem reporting.
- Related issue #1985 — existing broader system-health umbrella issue; #2291 should be a bounded fix issue, not another broad audit bucket.
- Related issue #2089 — weekly ecosystem review parent, providing context for why parity evidence contracts matter.

### Gaps identified
- No robust failure-detection mechanism for tasks that fail before emitting one of the monitor’s narrow grep patterns.
- No deterministic validation that task output paths match the `log:` pattern declared in `schedule-tasks.yaml`.
- No bounded reconciliation path for tasks that emit non-log artifacts (`.md`) but are still monitored by log-glob assumptions.
- Both `queue-refresh-weekly` and `weekly-hermes-parity-review` can fail before wrapper startup if cron redirects into a non-existent log directory.

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-04-15-issue-2291-cron-health-hardening-and-task-evidence-contracts.md` |
| Planning index update | `docs/plans/README.md` |
| Implementation | `scripts/monitoring/cron-health-check.sh` |
| Implementation | `config/scheduled-tasks/schedule-tasks.yaml` |
| Implementation | `scripts/cron/validate-schedule.py` |
| Tests (existing canonical cron-health suite) | `scripts/monitoring/tests/test_cron_health_check.sh` |
| Tests (new/extended schedule validation coverage) | `tests/cron/test_validate_schedule.py` |
| Tests (required parity contract coverage) | `tests/cron/test_weekly_hermes_parity_review.py` |
| Plan review — Claude | `scripts/review/results/2026-04-15-plan-2291-claude.md` |
| Plan review — Codex | `scripts/review/results/2026-04-15-plan-2291-codex.md` |
| Plan review — Gemini | `scripts/review/results/2026-04-15-plan-2291-gemini.md` |

---

## Deliverable

A bounded cron-health hardening change that (1) classifies `/bin/sh` bootstrap failures correctly, (2) keeps `weekly-hermes-parity-review`'s cron wrapper log as the authoritative execution-health artifact while treating the markdown parity report as secondary domain output, and (3) makes `queue-refresh-weekly` emit deterministic cron evidence by ensuring its log directory exists before shell redirection is evaluated.

---

## Pseudocode

```text
capture failing behavior first with the existing bash cron-health test suite plus new schedule-validation fixtures:
    prove `/bin/sh: ...: not found` is currently misclassified as OK
    prove cron-health can misclassify itself from echoed ERROR lines
    prove queue-refresh schedule command can fail before wrapper start if log directory is absent before `>>` redirection

set target contract decisions in-plan before coding:
    weekly-hermes-parity-review execution health stays tied to `cron-*.log`
    parity markdown report remains secondary domain artifact, not the authoritative execution-health signal
    queue-refresh-weekly schedule command pre-creates its log directory before shell redirection

implement bounded changes:
    update cron-health failure taxonomy with anchored `/bin/sh`/shell bootstrap patterns and false-positive guards
    prevent self-log scanning from poisoning cron-health status
    patch schedule-tasks.yaml command strings where pre-redirection directory creation is required
    add/extend schedule validation coverage so these contract bugs are caught mechanically

rerun targeted tests and schedule validation
write JSON health report with corrected status/details for the affected tasks
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Modify | `scripts/monitoring/cron-health-check.sh` | broaden anchored bootstrap-failure detection, add false-positive guards, and prevent self-log poisoning |
| Modify | `config/scheduled-tasks/schedule-tasks.yaml` | add pre-redirection directory creation where required and keep authoritative execution-evidence contracts explicit |
| Modify | `scripts/cron/validate-schedule.py` | add regression coverage/checks for schedule command patterns that can fail before script startup |
| Modify | `scripts/monitoring/tests/test_cron_health_check.sh` | extend the existing canonical bash suite with the new failure and self-reference cases |
| Create/Modify | `tests/cron/test_validate_schedule.py` | verify schedule validation catches pre-redirection directory/contract problems |
| Create/Modify | `tests/cron/test_weekly_hermes_parity_review.py` | only if needed for parity-specific contract assertions beyond generic schedule validation |
| Update | `docs/plans/README.md` | add this plan to the index |

---

## TDD Test List

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| `test_cron_health_flags_sh_style_program_not_found_as_error` | shell/bootstrap dependency failures using `/bin/sh: ...: not found` are classified as ERROR | failing log fixture containing `/bin/sh: 1: uv: not found` and variant fixtures like `python3: not found` | status `ERROR`, not `OK` |
| `test_cron_health_not_found_guard_avoids_benign_false_positive` | anchored failure detection does not misclassify benign prose containing `not found` | fixture log with informational text like `config key timeout: not found, using default` | status remains non-ERROR |
| `test_cron_health_handles_weekly_tasks_without_daily_bias` | weekly tasks are not misclassified solely due to cadence | weekly schedule + fresh execution log fixture | within threshold |
| `test_cron_health_self_log_does_not_error_on_echoed_task_failures` | cron-health does not mark itself ERROR solely because its own log echoes other task error lines | synthetic cron-health log with reported task errors | self status stays correct |
| `test_schedule_validation_rejects_pre_redirection_missing_dir_pattern` | schedule validation catches commands that redirect into a directory before ensuring it exists | YAML fixture with `>> $WORKSPACE_HUB/logs/queue-refresh/...` but no preceding `mkdir -p` | validation failure |
| `test_schedule_validation_accepts_queue_refresh_after_dir_creation` | fixed queue-refresh command shape passes validation | YAML fixture with directory creation before redirection | validation pass |
| `test_parity_execution_health_uses_wrapper_log_not_manual_md_artifact` | manual parity markdown artifacts do not satisfy cron execution health | `.md` artifact present, wrapper log absent | execution status remains `MISSING` |
| `test_latest_artifact_selection_prefers_fresh_success_over_stale_error` | monitor selects current evidence correctly when stale error and fresh success artifacts coexist | mixed-age artifact fixtures | fresh success governs classification |

### TDD sequencing
1. Extend `scripts/monitoring/tests/test_cron_health_check.sh` first to reproduce the current false green and self-log poisoning.
2. Add schedule-validation fixtures/tests proving pre-redirection directory bugs are caught.
3. Capture the parity execution-health rule: wrapper log is authoritative; markdown artifact is secondary only.
4. Confirm all new tests fail on current code before any implementation edits.
5. Implement bounded code/config changes, then rerun targeted suites.

---

## Acceptance Criteria

- [ ] `cron-health-check` classifies `/bin/sh: 1: uv: not found`-style fixtures as `ERROR` rather than `OK`
- [ ] Anchored bootstrap-failure detection does not create a benign `not found` false positive in targeted regression tests
- [ ] `cron-health-check` no longer marks itself `ERROR` solely because its own log echoes other task failures
- [ ] `weekly-hermes-parity-review` execution health remains tied to `logs/weekly-parity/cron-*.log`; a manual `.md` artifact alone does not satisfy cron execution success
- [ ] `queue-refresh-weekly` schedule command creates its log directory before shell redirection, so cron execution can emit evidence deterministically
- [ ] `scripts/cron/validate-schedule.py` (plus targeted tests) catches the pre-redirection directory bug shape going forward
- [ ] Compatibility impact of any `schedule-tasks.yaml` contract change is validated by rerunning the relevant schedule consumers / validators before approval to implement
- [ ] Targeted suites pass, including the existing bash cron-health suite and new schedule-validation coverage
- [ ] No unrelated scheduled-task contracts are regressed
- [ ] Non-goals remain enforced: no broad scheduler redesign, no auto-remediation, no attempt to fix unrelated broken jobs inside #2291
- [ ] Plan review artifacts are posted under `scripts/review/results/`

---

## Adversarial Review Summary

| Provider | Verdict | Key findings |
|---|---|---|
| Claude | PENDING | review not run yet |
| Codex | PENDING | review not run yet |
| Gemini | PENDING | review not run yet |

**Overall result:** PENDING

Revisions made based on review:
- none yet

---

## Risks and Open Questions

- **Risk:** anchored shell-failure detection must stay specific enough to catch real `/bin/sh` bootstrap failures without misclassifying benign prose or tool-probe output.
- **Risk:** changing `schedule-tasks.yaml` command strings can affect current consumers (`setup-cron.sh`, `validate-schedule.py`, `workstation-dispatch.sh`, and compliance scripts) if validation coverage is incomplete.
- **Risk:** queue-refresh may still have an additional install/runtime problem even after pre-redirection directory creation is fixed; this issue only commits to making scheduler evidence deterministic and classification truthful.
- **Open:** do existing consumers need a first-class notion of execution log vs secondary domain artifact, or is the bounded `cron-*.log authoritative / .md secondary` rule sufficient for the named tasks?
- **Open:** should `cron-health` explicitly skip scanning its own log body, or should it parse only structured task-status lines when self-monitoring?
- **Non-goals:** no redesign of the full scheduled-task schema, no repo-wide artifact-type abstraction, no host-level cron repair workflow, and no bundling of unrelated broken jobs (`claude-plugin-audit`, `wiki-ingest-nightly`, `gtm-job-market-scan`) into #2291.

---

## Complexity: T2

**T2** — bounded harness/operations fix spanning one monitor, one scheduler contract surface, and targeted regression tests, with no major architecture redesign required.