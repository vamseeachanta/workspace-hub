# Plan for #2291: fix(cron-health): harden failure detection and align task evidence contracts

> **Status:** draft
> **Complexity:** T2
> **Date:** 2026-04-26
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2291
> **Review artifacts (planned):** scripts/review/results/2026-04-26-plan-2291-claude.md | scripts/review/results/2026-04-26-plan-2291-codex.md | scripts/review/results/2026-04-26-plan-2291-gemini.md

---

## Resource Intelligence Summary

### Existing repo code

- **Verified existing:** `scripts/monitoring/cron-health-check.sh` (308 lines).
  - Loads `config/scheduled-tasks/schedule-tasks.yaml`, iterates `tasks[]`, resolves the newest file matching the declared `log:` glob under `${WS_HUB}/`, then classifies each task using:
    - presence of any matching log file (`MISSING` if none),
    - mtime age vs. heuristic interval derived from the cron schedule string (`STALE`),
    - case-insensitive substring scan over the latest log for the hard-coded `ERROR_PATTERNS` list (lines 83-91): `ERROR:`, `fatal:`, `ModuleNotFoundError`, `Permission denied`, `Traceback`, `command not found`, `No such file or directory`.
  - Writes JSON to `.claude/state/cron-health/${DATE}.json` and prints a `[STATUS] task-id details` table to stdout.
  - **Defect surface confirmed in code:** the bootstrap-error string `/bin/sh: 1: uv: not found` does **not** match any anchored pattern. `command not found` requires literal substring match, which is absent from the BusyBox/dash style `<shell>: <line>: <prog>: not found` form. This is the mechanism that produces the false `[OK]` on `memory-health-check`.
  - **Defect surface confirmed in code:** when the `cron-health` task itself processes its own latest log, the body is scanned for `ERROR:` etc., which is exactly the substring it prints on every problem task. So a single sick downstream task will infect the cron-health self-row with a self-`ERROR` reading on the next run.

- **Verified existing:** `config/scheduled-tasks/schedule-tasks.yaml` (624 lines).
  - `memory-health-check` (lines 292-306): `log: logs/quality/memory-health-*.md`, schedule `50 5 * * *`. Command runs `uv run --no-project python scripts/memory/eval-memory-quality.py ... >> logs/quality/memory-health-$(date +\%Y\%m\%d).md 2>&1`. `uv` is invoked unqualified, no `PATH=$HOME/.local/bin:$PATH` prefix → exposes the cron-PATH bootstrap failure mode reported in the issue.
  - `weekly-hermes-parity-review` (lines 222-238): `log: logs/weekly-parity/cron-*.log`, schedule `30 4 * * 1`. Cron command appends to `logs/weekly-parity/cron-$(date +\%Y-\%m-\%d).log`. The wrapper script writes a separate dated markdown report to `logs/weekly-parity/parity-review-$(date +\%Y-\%m-\%d).md`.
  - `queue-refresh-weekly` (lines 530-547): `log: logs/queue-refresh/*.log`, schedule `30 22 * * 0`. Cron command appends to `logs/queue-refresh/$(date +\%Y-\%m-\%d).log`. Wrapper does its own `mkdir -p` of `logs/queue-refresh/`, but cron's shell evaluates the `>>` redirection target *before* any wrapper code runs.
  - `cron-health` itself (lines 309-320): `log: logs/quality/cron-health-*.log`, schedule `45 5 * * *`. Cron command appends echoed status output to that file, so any future generic error-pattern scan over the same file will trip on its own emitted `[ERROR]` lines unless the self-log rule is explicit.

- **Verified existing:** `scripts/cron/weekly-hermes-parity-review.sh`. Reads workstation evidence and writes the dated markdown report to `${WORKSPACE_HUB}/logs/weekly-parity/parity-review-${DATE_STAMP}.md`. It does `mkdir -p "$OUTPUT_DIR"` for the markdown directory, but it does NOT control where cron's `>> ...cron-YYYY-MM-DD.log` redirection lands — that is set by the YAML command and evaluated by cron's `/bin/sh` before this script ever starts.

- **Verified existing:** `scripts/cron/queue-refresh-weekly.sh`. Begins with `mkdir -p "$LOG_DIR"` for `logs/queue-refresh/`, then appends to `${LOG_FILE}`. Same caveat: this `mkdir -p` runs only after the wrapper begins executing, which is after cron has already opened the redirection target from the YAML command.

- **Verified existing:** `scripts/monitoring/tests/test_cron_health_check.sh`. Canonical bash regression suite for the monitor.

- **Verified existing:** `scripts/cron/setup-cron.sh` (`--dry-run` flag confirmed at line 26-31). This is the surface where YAML command strings get materialized into actual cron lines — the right place to assert generated-line shape in tests.

- **Verified existing:** `scripts/cron/validate-schedule.py` and `scripts/cron/tests/test_validate_schedule.py`. Existing schedule-validation suite that any contract change must keep green.

- **Gap (verified by inspection of `cron-health-check.sh`):** there is no exit-code propagation channel. The monitor only sees what wrappers wrote into log files; it has no opinion-of-record on whether the underlying `uv run`/script exited 0.
- **Gap (verified):** there is no contract checker that asserts each task's declared `log:` glob is consistent with (a) the redirection target embedded in `command:` and (b) the path family the wrapper actually emits.
- **Gap (verified):** the `ERROR_PATTERNS` list is closed; every new failure shape requires a code edit.

### Standards

| Standard | Status | Source |
|---|---|---|
| Not applicable — repo harness/operations issue, not engineering domain | n/a | issue body labels (`cat:harness`, `cat:operations`) |

### LLM Wiki pages consulted

- No relevant wiki pages — this is harness infrastructure, not domain knowledge content. (Contract per `.claude/rules/calc-citation-contract.md`: do not cite when constants/formulas are not standards-derived.)

### Documents consulted

- **Issue #2291 body** — defines three concrete failure cases: (1) `memory-health-check` reported `[OK]` while latest artifact contains only `/bin/sh: 1: uv: not found`; (2) `weekly-hermes-parity-review` reported `[MISSING]` despite a `parity-review-2026-04-12.md` artifact existing; (3) `queue-refresh-weekly` reported `[MISSING]` with no logs at all despite a scheduled task and wrapper script existing. Plus three desired outcomes: classify shell/dependency failures, align scheduler `log` contracts with actual outputs, reduce false greens / false missings.
- **Issue thread comments (verified via `gh issue view 2291 --comments`)** — five planning-mode comments document the iterative tightening from 2026-04-15 and 2026-04-16: locked `cron-*.log` as authoritative execution-evidence, parity markdown as secondary domain output; clarified shell-redirection-before-wrapper-startup failure mode; promoted bash test suite to canonical; current adversarial state is Claude=MINOR, Gemini=APPROVE, Codex=MAJOR, with Codex's three remaining blockers itemized.
- **`docs/plans/2026-04-15-issue-2291-cron-health-hardening-and-task-evidence-contracts.md`** — prior in-repo draft that this plan supersedes/sharpens. Acceptance criteria, TDD list, and bounded-invariant rule (declared `log:` glob == generated cron redirection family == wrapper-log destination family for the two named tasks) are inherited and tightened below.
- **`scripts/review/results/2026-04-15-plan-2291-{claude,codex,gemini}.md` plus `2026-04-16-plan-2291-claude-overnight.md`** — confirmed exist; their findings drove the inherited revisions.
- **Evidence artifacts** (all confirmed present):
  - `logs/quality/cron-health-20260415.log`
  - `.claude/state/cron-health/2026-04-15.json`
  - `logs/quality/memory-health-20260415.md`
  - `logs/weekly-parity/parity-review-2026-04-12.md`
- **Related issues** — #1985 (broader system-health umbrella, intentionally left out of scope), #2089 (weekly ecosystem review parent, the consumer of parity evidence), #2292 (queue-refresh-specific follow-up, scoped *out* of #2291), #2293 (wiki-ingest follow-up, also scoped out).

### Gaps identified

- **G1.** No anchored shell/bootstrap-failure pattern — current grep cannot match `/bin/sh: 1: uv: not found`-shaped lines.
- **G2.** No self-log rule for the `cron-health` task; it can self-poison its own status by re-grepping the body it just wrote.
- **G3.** No bounded contract check that ties together the YAML `log:` glob, the YAML `command:` redirection target, and the wrapper's emitted artifact path family for the two tasks named in the issue.
- **G4.** Cron's `/bin/sh` evaluates `>>` redirection before the wrapper runs; if `logs/queue-refresh/` or `logs/weekly-parity/` does not yet exist on a fresh checkout/machine, the wrapper never gets a chance to `mkdir -p`.
- **G5.** No machine-readable assertion in tests that `.claude/state/cron-health/*.json` reports the corrected statuses (current suite only inspects shell output).
- **G6.** No hermetic clean-temp execution test that proves the generated cron line works under real shell-redirection semantics with stub downstream commands.

### Evidence (embedded verification)

**Issue status** (verified 2026-04-26 via `gh issue view 2291`):
- `#2291` — OPEN — `fix(cron-health): harden failure detection and align task evidence contracts`. Labels: `bug, cat:harness, cat:operations, priority:high`.

**File existence** (verified 2026-04-26 via `ls`):
- EXISTS: `scripts/monitoring/cron-health-check.sh`
- EXISTS: `scripts/monitoring/tests/test_cron_health_check.sh`
- EXISTS: `config/scheduled-tasks/schedule-tasks.yaml`
- EXISTS: `scripts/cron/weekly-hermes-parity-review.sh`
- EXISTS: `scripts/cron/queue-refresh-weekly.sh`
- EXISTS: `scripts/cron/setup-cron.sh`
- EXISTS: `scripts/cron/validate-schedule.py`
- EXISTS: `scripts/cron/tests/test_validate_schedule.py`
- EXISTS: `logs/quality/cron-health-20260415.log`
- EXISTS: `.claude/state/cron-health/2026-04-15.json`
- EXISTS: `logs/quality/memory-health-20260415.md`
- EXISTS: `logs/weekly-parity/parity-review-2026-04-12.md`
- EXISTS: `docs/plans/2026-04-15-issue-2291-cron-health-hardening-and-task-evidence-contracts.md` (prior in-repo plan)
- EXISTS: `scripts/review/results/2026-04-15-plan-2291-claude.md`, `...-codex.md`, `...-gemini.md`, `2026-04-16-plan-2291-claude-overnight.md`
- MISSING (this plan creates new tests in repo `tests/cron/`): `tests/cron/test_setup_cron.py`

**Line excerpts of defect surface** (from `scripts/monitoring/cron-health-check.sh`, lines 83-91):
```
ERROR_PATTERNS=(
    "ERROR:"
    "fatal:"
    "ModuleNotFoundError"
    "Permission denied"
    "Traceback"
    "command not found"
    "No such file or directory"
)
```
None of these substring patterns matches the dash-style `<shell>: <lineno>: <prog>: not found` form actually emitted by cron's `/bin/sh`.

**Source count** (counted across sub-sections above): 8 distinct sources cited (issue body + 4 evidence artifacts + prior plan + 4 prior review artifacts + 4 related issues + 5 verified script files). Minimum 3 satisfied per #2208.

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan (overnight wave-2 draft) | `/tmp/overnight-plans/wave-2/issue-2291-plan.md` |
| In-repo plan (final landing path) | `docs/plans/2026-04-26-issue-2291-2026-04-26-issue-2291-cron-health-failure-detection.md` |
| Planning index update | `docs/plans/README.md` |
| Implementation | `scripts/monitoring/cron-health-check.sh` |
| Implementation | `config/scheduled-tasks/schedule-tasks.yaml` |
| Verification surface | `scripts/cron/setup-cron.sh` (no source edit; tests assert dry-run output) |
| Tests (extend existing canonical bash suite) | `scripts/monitoring/tests/test_cron_health_check.sh` |
| Tests (existing schedule validator suite — must stay green) | `scripts/cron/tests/test_validate_schedule.py` |
| Tests (new setup-cron dry-run + clean-runtime coverage) | `tests/cron/test_setup_cron.py` |
| Plan review — Claude | `scripts/review/results/2026-04-26-plan-2291-claude.md` |
| Plan review — Codex | `scripts/review/results/2026-04-26-plan-2291-codex.md` |
| Plan review — Gemini | `scripts/review/results/2026-04-26-plan-2291-gemini.md` |

---

## Deliverable

A bounded cron-health hardening change that will (1) classify `<shell>: <lineno>: <prog>: not found` bootstrap failures as `ERROR` rather than `OK`, (2) keep `weekly-hermes-parity-review`'s `cron-*.log` as the authoritative execution-evidence artifact while leaving the markdown parity report as a secondary domain output, (3) ensure both `weekly-hermes-parity-review` and `queue-refresh-weekly` cron lines pre-create their log directories before shell `>>` redirection so that fresh-checkout machines emit deterministic evidence, (4) make `cron-health`'s self-row classification immune to its own emitted error strings, and (5) prove all of the above end-to-end via the existing bash suite plus a hermetic clean-temp runtime test against `setup-cron.sh --dry-run` output.

---

## Pseudocode

```text
# Phase A — capture defects with failing tests first
A1. add fixture: dash-style "/bin/sh: 1: uv: not found" log → assert ERROR (currently OK)
A2. add fixture: benign "config key timeout: not found, using default" → assert NOT ERROR (false-positive guard)
A3. add fixture: cron-health task's own log echoing other tasks' [ERROR] lines → assert self stays OK if presence/staleness fine
A4. add hermetic test: rm -rf TMP/logs/queue-refresh and run the YAML-emitted cron command line for queue-refresh under stub `uv` → assert log file is created
A5. add hermetic test: rm -rf TMP/logs/weekly-parity and run the YAML-emitted cron command line for parity under stub wrapper → assert cron-*.log is created
A6. add JSON assertion: .claude/state/cron-health/<date>.json has the expected status value for each fixture above

# Phase B — implement bounded fix
B1. broaden ERROR_PATTERNS in cron-health-check.sh with one anchored regex per shell-bootstrap shape:
       ^[^:]+: [0-9]+: [^:]+: not found$
       ^[^:]+: command not found$
    use grep -E with anchored regex (NOT plain substring) to avoid the benign-prose false positive
B2. add self-log rule: when tid == "cron-health", skip generic ERROR_PATTERNS body scan;
    classify only by artifact presence + staleness; preserve real self-failure detection by still
    flagging missing artifact, stale artifact, and exit-code != 0 when surfaced
B3. patch ONLY two YAML command strings in schedule-tasks.yaml:
       weekly-hermes-parity-review: "mkdir -p $WORKSPACE_HUB/logs/weekly-parity && cd $WORKSPACE_HUB && bash scripts/cron/weekly-hermes-parity-review.sh >> $WORKSPACE_HUB/logs/weekly-parity/cron-$(date +\%Y-\%m-\%d).log 2>&1"
       queue-refresh-weekly:        "PATH=$HOME/.local/bin:$PATH; mkdir -p $WORKSPACE_HUB/logs/queue-refresh && cd $WORKSPACE_HUB && bash scripts/cron/queue-refresh-weekly.sh >> $WORKSPACE_HUB/logs/queue-refresh/$(date +\%Y-\%m-\%d).log 2>&1"
    keep declared log: globs unchanged so the bounded invariant holds:
       declared log: glob ≡ command redirection family ≡ wrapper emission family

# Phase C — verify
C1. run scripts/monitoring/tests/test_cron_health_check.sh — all green
C2. run scripts/cron/tests/test_validate_schedule.py — still green (no schema change)
C3. run tests/cron/test_setup_cron.py — dry-run lines for the two affected tasks contain "mkdir -p" before ">>"
C4. run hermetic clean-temp execution of those generated lines with stub downstreams — log files exist
C5. inspect .claude/state/cron-health/<date>.json — corrected statuses present
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Modify | `scripts/monitoring/cron-health-check.sh` | broaden anchored bootstrap-failure patterns (regex, not substring); add self-log rule for `cron-health`; preserve all existing classifications |
| Modify | `config/scheduled-tasks/schedule-tasks.yaml` | prepend `mkdir -p <log-dir> &&` to the two affected `command:` strings; declared `log:` globs unchanged |
| Modify | `scripts/monitoring/tests/test_cron_health_check.sh` | extend canonical bash suite with the six new fixtures (A1-A6 above) |
| Create | `tests/cron/test_setup_cron.py` | end-to-end dry-run shape assertions + hermetic clean-temp runtime test for the two generated cron lines |
| Update | `docs/plans/README.md` | add this plan's row to the index when the plan lands in `docs/plans/` |

No edits to `scripts/cron/setup-cron.sh`, `scripts/cron/validate-schedule.py`, the parity wrapper, or the queue-refresh wrapper — the fix is bounded to monitor logic + two YAML command strings + tests.

---

## TDD Test List

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| `test_cron_health_flags_dash_style_program_not_found_as_error` | dash/BusyBox `<shell>: <lineno>: <prog>: not found` is classified ERROR | log fixture containing `/bin/sh: 1: uv: not found` plus `python3: not found` variant | task status `ERROR` |
| `test_cron_health_anchored_pattern_avoids_benign_not_found_prose` | anchored regex does not flag informational prose containing `not found` | log fixture with `config key timeout: not found, using default` | task status remains non-ERROR |
| `test_cron_health_self_log_uses_presence_and_staleness_only` | `cron-health` self-row skips generic body grep | synthetic cron-health log echoing `[ERROR] xyz` for downstream tasks, fresh mtime | self-row status remains `OK` |
| `test_cron_health_self_failure_still_detected_on_missing_or_stale` | self-log rule does not mask real cron-health self-failures | (a) absent self-log → MISSING; (b) self-log older than expected interval → STALE | classifications hold |
| `test_cron_health_handles_weekly_tasks_without_daily_bias` | weekly-cadence tasks not classified STALE solely from daily bias | weekly schedule + 5-day-old fresh log | within threshold |
| `test_validate_schedule_still_passes_after_yaml_command_edit` | schedule-validator suite green after the bounded YAML change | repo state with patched commands | exit 0 |
| `test_setup_cron_dry_run_emits_mkdir_before_redirection_for_parity` | generated cron line for `weekly-hermes-parity-review` contains `mkdir -p ... &&` before `>>` and still targets `cron-*.log` family | `setup-cron.sh --dry-run` on patched YAML | regex match: `mkdir -p .*logs/weekly-parity.*&&.*>> .*cron-.*\.log` |
| `test_setup_cron_dry_run_emits_mkdir_before_redirection_for_queue_refresh` | generated cron line for `queue-refresh-weekly` contains `mkdir -p ... &&` before `>>` and still targets `logs/queue-refresh/*.log` family | `setup-cron.sh --dry-run` on patched YAML | regex match: `mkdir -p .*logs/queue-refresh.*&&.*>> .*queue-refresh.*\.log` |
| `test_generated_parity_command_runs_in_clean_temp_env_with_stub_wrapper` | hermetic clean-temp execution under stub wrapper proves redirection works when log dir is initially absent | TMPDIR with empty `logs/`, stub `weekly-hermes-parity-review.sh` exiting 0 with one stdout line | `logs/weekly-parity/cron-<date>.log` is created and non-empty |
| `test_generated_queue_refresh_command_runs_in_clean_temp_env_with_stub_uv` | same hermetic test for queue-refresh path | TMPDIR with empty `logs/`, stub `uv` on PATH | `logs/queue-refresh/<date>.log` is created and non-empty |
| `test_parity_execution_health_uses_cron_log_not_md_artifact` | parity markdown alone does not satisfy execution health | `parity-review-<date>.md` present, `cron-<date>.log` absent | execution status remains `MISSING` |
| `test_cron_health_json_report_reflects_corrected_statuses` | `.claude/state/cron-health/<date>.json` matches corrected classifications | full fixture run | JSON contains expected `status` per task |
| `test_latest_artifact_selection_prefers_fresh_success_over_stale_error` | when stale-error and fresh-success artifacts coexist, fresh governs classification | mixed-age artifact fixtures | `OK` for the fresh artifact |

### TDD sequencing

1. Extend `scripts/monitoring/tests/test_cron_health_check.sh` first to lock the failure surface (rows 1-5, 11-13). Confirm rows 1, 3, 11 fail on current code before any implementation edit.
2. Add `tests/cron/test_setup_cron.py` (rows 7-10). Confirm rows 7-10 fail on current YAML before edits.
3. Implement `cron-health-check.sh` regex broadening + self-log rule (B1, B2). Re-run row 1 → green; row 3 → green; row 4 stays green by construction.
4. Implement YAML `mkdir -p` prepend (B3). Re-run rows 6-10 → green.
5. Run row 12 JSON assertion last after both implementation phases land.
6. Final sweep: `scripts/cron/tests/test_validate_schedule.py` plus the full bash suite plus the new pytest module.

---

## Acceptance Criteria

- [ ] Dash-style `<shell>: <lineno>: <prog>: not found` fixtures classify as `ERROR`, including the exact `/bin/sh: 1: uv: not found` shape from the issue body.
- [ ] Anchored regex does not produce a benign-`not found` false positive on informational prose.
- [ ] `cron-health` self-row classification skips generic body grep and uses artifact presence/staleness only; real self-failures (missing/stale) remain detected.
- [ ] `weekly-hermes-parity-review` execution health stays tied to `logs/weekly-parity/cron-*.log`; a manual `.md` artifact alone does not satisfy execution success.
- [ ] Both `weekly-hermes-parity-review` and `queue-refresh-weekly` YAML commands pre-create their log directories before `>>` redirection.
- [ ] `scripts/cron/tests/test_validate_schedule.py` continues to pass after the YAML command-string edits.
- [ ] `setup-cron.sh --dry-run` output for the two patched tasks matches the expected `mkdir -p ... && ... >> ...` regex shape and still targets the declared `log:` glob family.
- [ ] Hermetic clean-temp execution of the generated cron lines (with stub downstream commands and empty `logs/`) creates the expected log file.
- [ ] `.claude/state/cron-health/<date>.json` machine-readable report reflects the corrected statuses.
- [ ] No unrelated scheduled-task contracts are regressed (run-the-suite check).
- [ ] Non-goals enforced: no scheduler redesign, no auto-remediation, no fix bundling for `claude-plugin-audit`/`wiki-ingest-nightly`/`gtm-job-market-scan`.
- [ ] Plan review artifacts under `scripts/review/results/2026-04-26-plan-2291-{claude,codex,gemini}.md` exist before requesting `status:plan-review` label.

---

## Adversarial Review Summary

<!-- To be filled after the 2026-04-26 review wave runs. Inherited prior-wave verdicts from the 2026-04-15 plan are recorded below as starting reference; this plan's own review pass must populate the table fresh. -->

| Provider | Verdict (this wave) | Key findings |
|---|---|---|
| Claude | _pending_ | _to be filled by 2026-04-26 review_ |
| Codex | _pending_ | _to be filled by 2026-04-26 review (prior-wave Codex MAJOR blockers were itemized; this draft addresses each: bounded YAML invariant explicit; pre-fix runtime reproduction now hermetic; self-log rule preserves real self-failure detection)_ |
| Gemini | _pending_ | _to be filled by 2026-04-26 review_ |

**Overall result (current draft):** _pending review_ — not approval-ready until ≥2 fresh provider artifacts exist on 2026-04-26.

Revisions made versus the 2026-04-15 in-repo draft:
- Replaced substring `ERROR_PATTERNS` with anchored regex per Codex's bounded-rule blocker; added explicit benign-prose false-positive test.
- Made the bounded invariant testable, not just stated: dry-run regex assertions in `tests/cron/test_setup_cron.py` enforce `declared log: ≡ redirection family`.
- Added an explicit "self-log rule does not mask real self-failure" test row addressing Codex's third blocker.
- Hermetic clean-temp runtime tests are now first-class TDD rows, not "considerations."

---

## Risks and Open Questions

- **Risk:** anchored regex must stay specific. If a reviewer presents a real-world failure shape that doesn't match the proposed two-line regex set, we will need to extend the pattern list. Mitigation: keep the false-positive guard test; document the shape catalog in a comment block above `ERROR_PATTERNS`.
- **Risk:** YAML command-string changes can affect downstream consumers (`setup-cron.sh`, `validate-schedule.py`, `workstation-dispatch.sh`, compliance scripts). Mitigation: row 6 keeps the validator green; row 7-8 verify generated lines; no schema fields change.
- **Risk:** the underlying `uv: not found` cause for `memory-health-check` is a *cron PATH* problem; this plan only commits to making the monitor classify it correctly. Real remediation (adding `PATH=$HOME/.local/bin:$PATH;` to the `memory-health-check` command) is **out of scope** for #2291 — it should be filed as a follow-up so that the classification fix and the runtime fix are independently auditable. Note this explicitly in the closeout comment.
- **Open:** should `cron-health` parse only structured `[STATUS] tid details` lines when self-monitoring, instead of just skipping body grep? Current direction: skip generic grep, rely on presence/staleness; defer structured-parse to a future ticket if real self-failures slip through.
- **Open:** should we add a third anchored shape for bash's `bash: <prog>: command not found` to cover users who set `SHELL=/bin/bash` in cron? Current direction: yes — include both `/bin/sh:`-style and `<shell>: command not found`-style as two distinct patterns. Confirm during implementation.
- **Non-goals:** no first-class execution-vs-domain artifact abstraction repo-wide; no host-level cron repair workflow; no exit-code propagation channel (would require wrapper edits across many tasks); no fix for `queue-refresh-weekly` *content* problems beyond the redirection-target fix (#2292 owns the queue-refresh content problem).

---

## Complexity: T2

**T2** — bounded harness/operations fix touching one monitor script, two YAML command strings, one canonical bash test suite, and one new pytest module. No architecture redesign, no schema changes, no cross-repo edits.
