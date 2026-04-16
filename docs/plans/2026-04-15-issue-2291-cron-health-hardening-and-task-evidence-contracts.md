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
- This issue will not introduce a generic repo-wide task-evidence contract layer; it will only enforce a narrow invariant for the two named tasks: the declared `log:` glob, the generated cron redirection target, and the wrapper-log destination family must all agree.

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-04-15-issue-2291-cron-health-hardening-and-task-evidence-contracts.md` |
| Planning index update | `docs/plans/README.md` |
| Implementation | `scripts/monitoring/cron-health-check.sh` |
| Implementation | `config/scheduled-tasks/schedule-tasks.yaml` |
| Verification path | `scripts/cron/setup-cron.sh` |
| Tests (existing canonical cron-health suite) | `scripts/monitoring/tests/test_cron_health_check.sh` |
| Tests (existing schedule validator suite, keep passing) | `scripts/cron/tests/test_validate_schedule.py` |
| Tests (new setup-cron dry-run + clean-runtime coverage) | `tests/cron/test_setup_cron.py` |
| Plan review — Claude | `scripts/review/results/2026-04-15-plan-2291-claude.md` |
| Plan review — Codex | `scripts/review/results/2026-04-15-plan-2291-codex.md` |
| Plan review — Gemini | `scripts/review/results/2026-04-15-plan-2291-gemini.md` |

---

## Deliverable

A bounded cron-health hardening change that (1) classifies `/bin/sh` bootstrap failures correctly, (2) keeps `weekly-hermes-parity-review`'s cron wrapper log as the authoritative execution-health artifact while treating the markdown parity report as secondary domain output, and (3) makes both `weekly-hermes-parity-review` and `queue-refresh-weekly` emit deterministic cron evidence by ensuring their log directories exist before shell redirection is evaluated.

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
    both parity and queue-refresh schedule commands pre-create their log directories before shell redirection

implement bounded changes:
    update cron-health failure taxonomy with anchored `/bin/sh`/shell bootstrap patterns and false-positive guards
    for the `cron-health` task itself, skip generic `ERROR_PATTERNS` body scanning and classify only from fresh artifact presence/staleness
    patch only the two named scheduled commands in `schedule-tasks.yaml` so pre-redirection directory creation is explicit
    enforce one narrow invariant for those two tasks only:
        declared `log:` glob == generated cron redirection family == wrapper log destination family
    verify generated cron lines through `setup-cron.sh --dry-run`
    run a hermetic clean-temp harness with stub downstream commands so shell/redirection semantics are tested without depending on real `uv`, repo state, or external services

rerun targeted tests, validator suite, setup-cron dry-run verification, hermetic clean-runtime command execution checks, and confirm JSON health output reflects corrected classifications
write JSON health report with corrected status/details for the affected tasks
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Modify | `scripts/monitoring/cron-health-check.sh` | broaden anchored bootstrap-failure detection, add false-positive guards, and make the self-log rule explicit: skip generic `ERROR_PATTERNS` scanning for the `cron-health` task and classify it only by fresh artifact presence/staleness |
| Modify | `config/scheduled-tasks/schedule-tasks.yaml` | add pre-redirection directory creation to the two named affected commands and keep authoritative execution-evidence contracts explicit |
| Modify | `scripts/monitoring/tests/test_cron_health_check.sh` | extend the existing canonical bash suite with the new failure, appended-log, and self-reference cases |
| Create/Modify | `tests/cron/test_setup_cron.py` | verify `setup-cron.sh --dry-run` emits the corrected generated cron lines and that a hermetic clean-temp harness using stub downstream commands proves the two generated command shapes work under real shell/redirection semantics |
| Update | `docs/plans/README.md` | add this plan to the index |

---

## TDD Test List

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| `test_cron_health_flags_sh_style_program_not_found_as_error` | shell/bootstrap dependency failures using `/bin/sh: ...: not found` are classified as ERROR | failing log fixture containing `/bin/sh: 1: uv: not found` and variant fixtures like `python3: not found` | status `ERROR`, not `OK` |
| `test_cron_health_not_found_guard_avoids_benign_false_positive` | anchored failure detection does not misclassify benign prose containing `not found` | fixture log with informational text like `config key timeout: not found, using default` | status remains non-ERROR |
| `test_cron_health_handles_weekly_tasks_without_daily_bias` | weekly tasks are not misclassified solely due to cadence | weekly schedule + fresh execution log fixture | within threshold |
| `test_cron_health_self_log_uses_presence_and_staleness_only` | `cron-health` does not scan its own body for generic `ERROR:` strings and instead classifies itself only by artifact presence/staleness | synthetic cron-health log containing echoed task errors | self status stays correct |
| `test_setup_cron_dry_run_preserves_validator_compatibility` | existing validator suite keeps passing while new end-to-end setup-cron tests own the command-shape regression | current repo validator suite plus dry-run verification | pass |
| `test_setup_cron_dry_run_emits_fixed_queue_refresh_command` | generated cron line for queue-refresh includes directory creation before redirection and still targets the declared log family | `setup-cron.sh --dry-run` on fixture/config or controlled environment | emitted line contains expected `mkdir -p ... && ... >> ...` shape and queue-refresh log family |
| `test_setup_cron_dry_run_emits_fixed_parity_command` | generated cron line for parity includes directory creation before wrapper-log redirection and still targets the declared log family | `setup-cron.sh --dry-run` on fixture/config or controlled environment | emitted line contains expected `mkdir -p ... && ... >> ...` shape and parity cron-log family |
| `test_generated_queue_refresh_command_runs_in_clean_temp_env_with_stub_downstream` | the generated queue-refresh command succeeds in a hermetic clean temp environment where the target log dir starts absent | emitted command + stub downstream command + clean temp workspace | evidence log is created |
| `test_generated_parity_command_runs_in_clean_temp_env_with_stub_downstream` | the generated parity command succeeds in a hermetic clean temp environment where the target log dir starts absent | emitted command + stub downstream command + clean temp workspace | wrapper log is created |
| `test_parity_execution_health_uses_wrapper_log_not_manual_md_artifact` | manual parity markdown artifacts do not satisfy cron execution health | `.md` artifact present, wrapper log absent | execution status remains `MISSING` |
| `test_cron_health_json_report_reflects_corrected_statuses` | machine-readable cron-health JSON matches the corrected classifications after the fix | fixture run producing report JSON | expected task statuses in `.claude/state/cron-health/*.json` |
| `test_latest_artifact_selection_prefers_fresh_success_over_stale_error` | monitor selects current evidence correctly when stale error and fresh success artifacts coexist in appended-log environments | mixed-age artifact fixtures | fresh success governs classification |

### TDD sequencing
1. Extend `scripts/monitoring/tests/test_cron_health_check.sh` first to reproduce the current false green and to lock the self-log rule (`cron-health` uses artifact presence/staleness only, not generic body grep).
2. Keep `scripts/cron/tests/test_validate_schedule.py` green while adding end-to-end `setup-cron.sh --dry-run` tests for the two affected commands.
3. Run the generated cron command lines in a hermetic clean temp environment with stub downstream commands so runtime redirection behavior is proven without depending on real `uv`, repo state, or external services.
4. Add JSON-output assertions so `.claude/state/cron-health/*.json` is verified alongside shell output.
5. Confirm all new tests fail on current code before any implementation edits.
6. Implement bounded code/config changes, then rerun targeted suites, validator suite, setup-cron dry-run checks, hermetic runtime checks, and JSON-report assertions.

---

## Acceptance Criteria

- [ ] `cron-health-check` classifies `/bin/sh: 1: uv: not found`-style fixtures as `ERROR` rather than `OK`
- [ ] Anchored bootstrap-failure detection does not create a benign `not found` false positive in targeted regression tests
- [ ] `cron-health-check` no longer marks itself `ERROR` solely because its own log echoes other task failures; for the `cron-health` task, generic body grep is skipped and classification uses artifact presence/staleness only
- [ ] `weekly-hermes-parity-review` execution health remains tied to `logs/weekly-parity/cron-*.log`; a manual `.md` artifact alone does not satisfy cron execution success
- [ ] Both `weekly-hermes-parity-review` and `queue-refresh-weekly` schedule commands create their log directories before shell redirection, so cron execution can emit evidence deterministically
- [ ] `scripts/cron/tests/test_validate_schedule.py` still passes after the targeted command changes
- [ ] `setup-cron.sh --dry-run` verification proves the generated cron lines for the two affected tasks create their log directories before shell redirection and still target the declared log families
- [ ] Hermetic clean-temp execution of the generated cron command lines with stub downstream commands proves the fix works under actual shell/redirection semantics, not just string inspection
- [ ] `.claude/state/cron-health/*.json` regression assertions confirm the corrected classifications appear in machine-readable output as well as shell output
- [ ] Compatibility impact of any `schedule-tasks.yaml` contract change is validated during implementation by rerunning `scripts/cron/tests/test_validate_schedule.py` plus the targeted `setup-cron.sh --dry-run` checks before closeout
- [ ] Targeted suites pass, including the existing bash cron-health suite and new schedule-validation coverage
- [ ] No unrelated scheduled-task contracts are regressed
- [ ] Non-goals remain enforced: no broad scheduler redesign, no auto-remediation, no attempt to fix unrelated broken jobs inside #2291
- [ ] Plan review artifacts are posted under `scripts/review/results/`

---

## Adversarial Review Summary

| Provider | Verdict | Key findings |
|---|---|---|
| Claude | MINOR | Keep the existing bash cron-health suite canonical, explicitly gate the self-log fix, and keep queue-refresh diagnosis front-loaded rather than assuming wrapper-only failure. |
| Codex | MAJOR | Plan still needs a sharper bounded rule for schedule validation and more concrete end-to-end validation of generated cron command shapes / appended-log behavior before it is approval-ready. |
| Gemini | APPROVE | Bounded monitor+schedule fix direction is sound; keep `cron-*.log` authoritative, keep `validate-schedule.py` checks simple, and avoid false-positive `not found` matching. |

**Overall result:** FAIL (re-draft required before plan-review)

Revisions made based on review:
- Clarified that both parity and queue-refresh can fail before wrapper startup because shell redirection happens before script execution.
- Locked the execution-evidence rule: `cron-*.log` is authoritative; markdown parity report is secondary.
- Promoted the existing bash cron-health suite to canonical status in the plan.
- Added bounded schedule-validation coverage, appended-log considerations, and stronger acceptance criteria.
- Remaining blocker: Codex still considers the validator scope and end-to-end cron-line validation insufficiently bounded/specified.

---

## Risks and Open Questions

- **Risk:** anchored shell-failure detection must stay specific enough to catch real `/bin/sh` bootstrap failures without misclassifying benign prose or tool-probe output.
- **Risk:** changing `schedule-tasks.yaml` command strings can affect current consumers (`setup-cron.sh`, `validate-schedule.py`, `workstation-dispatch.sh`, and compliance scripts) if verification coverage is incomplete.
- **Risk:** queue-refresh and parity may still have an additional install/runtime problem even after pre-redirection directory creation is fixed; this issue only commits to making scheduler evidence deterministic and classification truthful.
- **Open:** after the bounded fix, should the repo later add a first-class notion of execution log vs secondary domain artifact, or is the narrow invariant in this issue sufficient for the two named tasks: declared `log:` glob == generated cron redirection family == wrapper-log destination family?
- **Open:** should `cron-health` explicitly skip scanning its own log body, or should it parse only structured task-status lines when self-monitoring? Current planned direction: skip generic body grep for the `cron-health` task and rely on fresh artifact presence/staleness.
- **Non-goals:** no redesign of the full scheduled-task schema, no repo-wide artifact-type abstraction, no host-level cron repair workflow, and no bundling of unrelated broken jobs (`claude-plugin-audit`, `wiki-ingest-nightly`, `gtm-job-market-scan`) into #2291.

---

## Complexity: T2

**T2** — bounded harness/operations fix spanning one monitor, one scheduler contract surface, and targeted regression tests, with no major architecture redesign required.