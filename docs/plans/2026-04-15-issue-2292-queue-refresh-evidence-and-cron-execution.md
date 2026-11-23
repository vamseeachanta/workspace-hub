# Plan for #2292: fix(queue-refresh): restore weekly queue refresh evidence and cron execution

> **Status:** draft
> **Complexity:** T2
> **Date:** 2026-04-15
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2292
> **Review artifacts:** scripts/review/results/2026-04-15-plan-2292-claude.md | scripts/review/results/2026-04-15-plan-2292-codex.md | scripts/review/results/2026-04-15-plan-2292-gemini.md

---

## Resource Intelligence Summary

### Existing repo code
- Found: `scripts/cron/queue-refresh-weekly.sh` — weekly wrapper that sets `LOG_DIR`, writes queue-refresh progress lines, sources workstation/git helpers, runs `uv run scripts/refresh-agent-work-queue.py`, and writes to `logs/queue-refresh/YYYY-MM-DD.log` only after the script itself starts.
- Found: `scripts/refresh-agent-work-queue.py` — canonical queue generator that writes `notes/agent-work-queue.md` and supports dry-run / staleness / parity-check modes.
- Found: `scripts/refresh-agent-work-queue.sh` — thin convenience wrapper around the Python generator.
- Found: `logs/queue-refresh/.gitkeep` — the queue-refresh directory already exists in the repo checkout, so missing-directory-before-redirection is not yet proven as the live root cause on this machine.
- Gap: the scheduled command in `config/scheduled-tasks/schedule-tasks.yaml` still uses outer shell redirection to `logs/queue-refresh/*.log`, which remains a brittle bootstrap surface even if the directory currently exists.
- Gap: there is no current direct evidence in `logs/queue-refresh/` beyond `.gitkeep`, so installed-cron absence vs cron-not-firing vs pre-wrapper bootstrap failure vs later runtime failure is not yet separated by artifact evidence.

### Standards
| Standard | Status | Source |
|---|---|---|
| Not applicable | n/a | Non-engineering operations issue |

### LLM Wiki pages consulted
- No relevant wiki pages; this is scheduler/work-queue infrastructure, not domain knowledge content.

### Documents consulted
- Issue #2292 body — states the problem as missing evidence logs and asks to determine whether the cron entry is not installed, not firing, or failing before log creation.
- `config/scheduled-tasks/schedule-tasks.yaml` — defines `queue-refresh-weekly` with `bash scripts/cron/queue-refresh-weekly.sh >> $WORKSPACE_HUB/logs/queue-refresh/$(date ...).log 2>&1` and `log: logs/queue-refresh/*.log`.
- `logs/quality/cron-health-20260415.log` — marks `queue-refresh-weekly` as `[MISSING]` with no matching logs.
- `scripts/cron/queue-refresh-weekly.sh` — confirms the wrapper itself creates `LOG_DIR`, but only after the shell has already processed the outer cron redirection; also confirms the wrapper depends on `scripts/lib/workstation-lib.sh` and `scripts/cron/lib/git-safe.sh` plus a full-variant hostname gate.
- `logs/queue-refresh/.gitkeep` — confirms the queue-refresh log directory exists in the checkout, weakening the assumption that directory absence alone explains the live failure.
- `scripts/cron/setup-cron.sh` — installer/dry-run path that expands the YAML command into actual cron lines and is therefore the authoritative place to inspect generated cron command shape.
- Live probe artifact: `docs/reports/2026-04-15-issue-2292-installed-crontab-probe.md` — confirms `queue-refresh-weekly` is currently installed in the live crontab on `ace-linux-1`, eliminating the `not-installed` branch for this host.
- Related issue #1985 — broader system-health context; #2292 should stay bounded to queue refresh rather than reopening general cron observability.
- Related issue #2291 — adjacent cron-health contract hardening effort; #2292 should integrate with it but remain focused on queue-refresh execution/evidence restoration.

### Gaps identified
- On `ace-linux-1`, the installed-crontab probe has already eliminated the `not-installed` branch; the remaining ambiguity is whether the installed weekly job has not fired in practice yet or is failing after cron launch.
- No regression coverage around the generated cron command shape for queue-refresh.
- No hermetic runtime test proving queue-refresh’s scheduled command can emit evidence on a clean directory when downstream work and sourced helper seams are stubbed.
- No explicit verification yet that the wrapper’s full-variant gate / git helper initialization can be controlled cleanly in tests.
- Current schedule / wrapper logging uses two time bases (`$(date +%Y-%m-%d)` in the outer cron redirect vs `date -u` inside the wrapper), which can split evidence across files near midnight and must be normalized or explicitly accepted.

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-04-15-issue-2292-queue-refresh-evidence-and-cron-execution.md` |
| Planning index update | `docs/plans/README.md` |
| Implementation | `config/scheduled-tasks/schedule-tasks.yaml` |
| Implementation | `scripts/cron/queue-refresh-weekly.sh` |
| Verification path | `scripts/cron/setup-cron.sh` |
| Tests (existing schedule validator suite) | `scripts/cron/tests/test_validate_schedule.py` |
| Tests (new queue-refresh setup/cron runtime coverage) | `tests/cron/test_setup_cron.py` |
| Tests (new queue-refresh wrapper coverage if needed) | `tests/cron/test_queue_refresh_weekly.py` |
| Plan review — Claude | `scripts/review/results/2026-04-15-plan-2292-claude.md` |
| Plan review — Codex | `scripts/review/results/2026-04-15-plan-2292-codex.md` |
| Plan review — Gemini | `scripts/review/results/2026-04-15-plan-2292-gemini.md` |

---

## Deliverable

A bounded queue-refresh plan with an explicit stop condition:
1. if the live problem classifies as `installed-but-not-firing` and hermetic reproduction does not show a repo-owned defect, this issue ends as diagnosis + operator guidance with no repo code changes;
2. if hermetic reproduction confirms a repo-owned launch/evidence defect, the fix lands with a single logging owner: `queue-refresh-weekly.sh` owns queue-refresh evidence under `logs/queue-refresh/*.log` and outer cron redirection is removed.

---

## Pseudocode

```text
capture and preserve the live-state artifact first:
    use the installed-crontab probe artifact for `ace-linux-1` to prove the task is installed on this host
    narrow the remaining live states to:
        installed-but-not-firing in practice
        installed-and-failing-after-launch

use hermetic `/bin/sh` reproduction to choose the branch:
    derive the exact generated queue-refresh command via setup-cron dry-run
    execute the current behavior in a clean temp environment with stubbed workstation/git/downstream seams
    if no repo-owned failure reproduces:
        stop here
        classify as operational/not-firing
        post operator guidance or create a follow-up operational issue
        do not change repo code in this issue
    if repo-owned failure reproduces:
        continue into bounded remediation

for the repo-owned remediation branch, choose one logging owner explicitly:
    queue-refresh evidence is owned by `queue-refresh-weekly.sh`
    wrapper writes the canonical `logs/queue-refresh/*.log` file family using one canonical time basis (UTC)
    outer cron redirection is removed from the scheduled command so there is no double-write ambiguity
    declared `log:` glob in schedule-tasks.yaml continues to point at the wrapper-owned queue-refresh log family

implement bounded changes only in the repo-owned branch:
    patch schedule-tasks.yaml to call the wrapper without outer log redirection
    patch queue-refresh-weekly.sh only as needed to make wrapper-owned logging deterministic from startup onward under `/bin/sh`
    add only minimal wrapper seams/stubs needed for hermetic testability

verify end-to-end:
    setup-cron dry-run emits the expected no-outer-redirection command shape
    hermetic clean-temp execution under `/bin/sh` creates the wrapper-owned evidence log
    runtime-failure branch produces evidence distinguishing later failure from missing startup
    machine-readable health reporting still classifies the task truthfully against the same log family
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Modify | `config/scheduled-tasks/schedule-tasks.yaml` | only in the repo-owned failure branch: remove outer queue-refresh log redirection and let the wrapper remain the single logging owner while preserving the declared log family |
| Modify | `scripts/cron/queue-refresh-weekly.sh` | only in the repo-owned failure branch: make wrapper-owned logging deterministic from startup onward under `/bin/sh` |
| Create/Modify | `tests/cron/test_setup_cron.py` | verify generated queue-refresh command shape, no-outer-redirection contract, preserved date behavior, and `/bin/sh` runtime behavior |
| Create/Modify | `tests/cron/test_queue_refresh_weekly.py` | verify wrapper-owned logging behavior only if script-level changes are actually needed |
| Update | `docs/plans/README.md` | add this plan to the index |

---

## TDD Test List

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| `test_setup_cron_dry_run_emits_current_queue_refresh_command` | current generated queue-refresh command is captured exactly for diagnosis | `setup-cron.sh --dry-run` fixture | emitted line matches current queue-refresh command |
| `test_generated_queue_refresh_command_fails_pre_fix_on_clean_dir_under_sh` | current generated command fails before wrapper startup under `/bin/sh` hermetic conditions when that branch is reproducible | pre-fix command + clean temp env + stubbed seams | no evidence log created |
| `test_generated_queue_refresh_command_runs_post_fix_on_clean_dir_under_sh` | final chosen repo-owned fix succeeds in hermetic `/bin/sh` environment | fixed command + clean temp env + stubbed workstation/git/downstream seams | wrapper-owned evidence log created |
| `test_queue_refresh_wrapper_runtime_failure_still_writes_evidence` | later runtime failure after wrapper start is distinguishable from missing startup | stubbed downstream failure after wrapper starts | wrapper-owned evidence log exists with failure details |
| `test_queue_refresh_log_family_matches_schedule_contract` | declared `log:` glob and wrapper-owned log destination stay aligned after the final chosen contract | schedule fixture + wrapper fixture | same queue-refresh log family |
| `test_queue_refresh_log_time_basis_is_consistent` | final chosen logging contract does not split evidence across local-vs-UTC date bases | wrapper-owned logging fixture | single canonical date family |
| `test_setup_cron_replace_preserves_queue_refresh_entry` | queue-refresh fix does not break `setup-cron.sh --replace` behavior | replace-mode fixture | valid emitted crontab entry |

### TDD sequencing
1. Capture and save the installed-crontab probe artifact for the target full-variant host.
2. Use `setup-cron.sh --dry-run` to derive the exact current queue-refresh command for this repo state.
3. Prove the current generated command’s behavior under `/bin/sh` hermetic conditions with stubbed workstation/git/downstream seams.
4. If hermetic reproduction shows no repo-owned defect, stop: classify the issue as operational/not-firing and do not change repo code in this issue.
5. If hermetic reproduction shows a repo-owned defect, implement the bounded fix with wrapper-owned logging as the single source of truth, then rerun runtime checks.
6. Re-run queue-refresh health expectations only after the branch outcome is explicit.

---

## Acceptance Criteria

- [ ] A reviewable installed-crontab probe artifact is captured and the live failure on `ace-linux-1` is narrowed explicitly to `installed-but-not-firing` or `installed-and-failing-after-launch`
- [ ] `queue-refresh-weekly` declared `log:` glob remains `logs/queue-refresh/*.log`
- [ ] If hermetic reproduction shows no repo-owned defect, the issue stops as diagnosis-only and records `installed-but-not-firing` / operational drift explicitly with no repo code changes claimed
- [ ] If the failure branch is repo-side, queue-refresh adopts a single logging owner: `queue-refresh-weekly.sh` writes the canonical `logs/queue-refresh/*.log` evidence family and outer cron redirection is removed
- [ ] Hermetic `/bin/sh` clean-temp execution proves the relevant pre-fix branch and the post-fix branch under controlled workstation/git/downstream seams
- [ ] If wrapper-level failure occurs after startup, the wrapper-owned log distinguishes runtime failure from missing startup
- [ ] `scripts/cron/tests/test_validate_schedule.py` still passes after any targeted command changes
- [ ] `setup-cron.sh --dry-run` verification confirms the final generated cron line matches the declared queue-refresh log family and preserves expected date expansion
- [ ] `setup-cron.sh --replace` behavior is not regressed for the queue-refresh entry
- [ ] No unrelated scheduled-task contracts are regressed
- [ ] Plan review artifacts are posted under `scripts/review/results/`

---

## Adversarial Review Summary

| Provider | Verdict | Key findings |
|---|---|---|
| Claude | MINOR | Strong bounded diagnosis-first plan; it asked for tighter stop conditions, explicit operator-probe framing, and date/time-basis clarity. |
| Codex | MAJOR | Main blocker remains the decision boundary between operational diagnosis and repo-owned remediation, plus explicit logging ownership and cleaner separation of operator evidence from repo behavior. |
| Gemini | MINOR | Bounded approach is sound; it pushed toward wrapper-owned logging and highlighted local-vs-UTC filename mismatch and cron-shell realism. |

**Overall result:** FAIL (re-draft required before plan-review)

Revisions made based on review:
- Captured and recorded the installed-crontab probe artifact proving `queue-refresh-weekly` is installed on `ace-linux-1`.
- Narrowed the live ambiguity to `installed-but-not-firing` vs `installed-and-failing-after-launch`.
- Added an explicit stop condition: if hermetic reproduction does not reveal a repo-owned defect, this issue ends as diagnosis-only with operator guidance and no repo code changes.
- Chose a single logging owner for the repo-owned fix branch: `queue-refresh-weekly.sh` owns the canonical `logs/queue-refresh/*.log` evidence family and outer cron redirection is removed.
- Tightened `/bin/sh` hermetic runtime wording and wrapper-owned log expectations.
- Remaining blocker: Codex still wants the plan to stop mixing diagnosis and remediation enough that the branch decision is obvious to a future executor before any code change is attempted.

---

## Risks and Open Questions

- **Risk:** the installed-crontab probe shows the task is present on `ace-linux-1`, so the remaining live problem may be purely operational/not-firing; if so, repo code changes alone will not make the job run on schedule.
- **Risk:** changing the queue-refresh command string can affect schedule consumers if quoting/escaping is not preserved.
- **Risk:** wrapper tests can become non-hermetic unless workstation detection, git helpers, downstream `uv` execution, and shell choice (`/bin/sh`) are stubbed explicitly.
- **Open:** if repo-side command shape is the confirmed failure path, is it safer to pre-create the directory in the generated cron command or to move logging responsibility fully inside the wrapper with `exec >> "$LOG_FILE" 2>&1` after startup?
- **Open:** if hermetic reproduction is sound and the live task simply has not fired / is operationally drifting, should this issue stop at diagnosis + operator guidance and create a separate install/fire-parity issue?
- **Non-goals:** no scheduler redesign, no repo-wide artifact-contract schema, no fix bundle for unrelated broken cron tasks.

---

## Complexity: T2

**T2** — bounded scheduled-task + wrapper/evidence repair with targeted regression tests and no broad architecture changes.