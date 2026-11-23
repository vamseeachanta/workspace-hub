# Issue #2764 Plan — fix(operations): harden Hermes session exporter for undated session files

- **Issue**: https://github.com/vamseeachanta/workspace-hub/issues/2764
- **Status**: draft — round 1 adversarial review returned MAJOR; revision required
- **Date**: 2026-05-20
- **Complexity**: T1
- **Execution mode**: single-lane after approval; narrow script/test change.

## Resource Intelligence Summary

### Evidence
- **GitHub issue #2764** — Live issue body verified open with `status:needs-plan`; bug report includes failing command and undated filename root cause.
- **`scripts/cron/hermes-session-export.sh:1-235`** — Exporter uses `set -euo pipefail`; date extraction uses `grep -oE ... | head -1` before the empty-date guard, so no-match aborts the script.
- **Reproduction evidence** — Earlier debug trace found `/home/vamsee/.hermes/sessions/session_bg_22fe54.json` lacks an 8-digit date and trips the pipeline before skip logic.
- **`scripts/analysis/provider_session_ecosystem_audit.py`** — Audit succeeds independently on current raw logs, but export freshness remains fragile if the wrapper aborts.
- **Existing test search** — No dedicated `hermes-session-export` test was found in prior search; add one rather than relying on manual dry-runs.

### Reproduction proofs
- **Runtime failure reproduction**: Earlier live debug trace reproduced the failure: `bash scripts/cron/hermes-session-export.sh; echo EXIT:$?` returned `EXIT:1`; `bash -x scripts/cron/hermes-session-export.sh --dry-run` traced the abort to undated basename `session_bg_22fe54` and empty `session_date` before the guard could run under `set -euo pipefail`.
- **Live issue state**: `gh issue view 2764` confirmed the issue is open and labeled `status:needs-plan` before this plan was drafted.

### Gaps / assumptions
- Current planning uses previously captured `hermes cron list` evidence from issue intake; implementation should capture fresh live output in tests/report fixtures before changing runtime behavior.
- Raw provider logs may contain local/private runtime evidence and should remain local-only unless already tracked reports explicitly require redacted summaries.
- No secrets or credential values are required for this plan.

## Artifact Map

| Artifact | Path |
|---|---|
| Plan | `docs/plans/2026-05-20-issue-2764-hermes-session-export-undated-file-hardening.md` |
| Review artifacts | `scripts/review/results/2026-05-20-plan-2764-*.md` |
| GitHub issue | `https://github.com/vamseeachanta/workspace-hub/issues/2764` |

## Deliverable

A failing-then-passing exporter hardening patch so undated Hermes session filenames are skipped safely under `set -euo pipefail` without blocking provider-session audit freshness.

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
| create | `scripts/cron/tests/test_hermes_session_export.sh` | Shell tests with temp HOME and undated/datestamped session fixtures. |
| update | `scripts/cron/hermes-session-export.sh` | Make date extraction no-match safe, count/log skipped unsupported filenames, preserve fail-closed behavior for real conversion errors. |
| update | `docs/plans/README.md` | Index this plan. |

## TDD Test List

| Test | Verification | Input | Expected Output |
|---|---|---|---|
| `test_skips_undated_session_file_under_pipefail` | Temp HOME with `session_bg_22fe54.json`; run exporter dry-run under strict shell. | Undated fixture only | Exit 0 with skip message |
| `test_exports_dated_session_file` | Temp HOME with dated Hermes session JSON fixture. | Dated fixture | Output JSONL written under orchestrator Hermes log path |
| `test_conversion_error_still_fails` | Malformed dated JSON fixture. | Invalid JSON | Non-zero exit and error message |
| `test_provider_audit_runs_after_export_dry_run` | Run exporter dry-run then provider audit stdout command. | Current repo state | Both commands exit 0 |

## Acceptance Criteria

- [ ] RED test reproduces undated filename abort before patch.
- [ ] Patch skips unsupported filenames and logs/counts the skip.
- [ ] Dated valid sessions still export.
- [ ] Malformed dated sessions still fail rather than being silently ignored.
- [ ] Targeted tests plus provider audit command pass.
- [ ] Adversarial plan review artifacts are saved under `scripts/review/results/`.
- [ ] GitHub issue is moved only to `status:plan-review` after review has no unresolved MAJOR findings.
- [ ] Implementation remains blocked until the user applies `status:plan-approved`.

## Adversarial Review Summary

Round 1 adversarial review complete: Claude MAJOR, Codex MAJOR, Gemini MAJOR. Do not move to status:plan-review. Blocking themes: pseudocode/scope copied from scheduler plans, test isolation would write/delete live log paths unless env override is designed, conversion-error behavior is mischaracterized, exact safe patch shape and RED proof artifact are missing, and complexity likely T2 not T1. Next action is rewrite as a narrow exporter hardening plan and re-review.

Review artifacts:
- `scripts/review/results/2026-05-20-plan-2764-claude.md`
- `scripts/review/results/2026-05-20-plan-2764-codex.md`
- `scripts/review/results/2026-05-20-plan-2764-gemini.md`
- `scripts/review/results/2026-05-20-plan-2764-disagreement.md`

## Risks and Open Questions

- A too-broad `|| true` could hide real conversion failures; only the filename date extraction should be tolerant.
- Tests must isolate HOME/log paths to avoid mutating live `~/.hermes` sessions.
- Current later dry-run success must not mask the already-identified line-level fragility.

## Implementation Notes for Future Approved Work

- Write tests first and confirm RED where applicable.
- Use `uv run --no-project` for Python commands in this repository.
- Use `--body-file` for all GitHub comments/edits containing Markdown.
- Keep raw logs local-only unless redacted/tracked report policy explicitly allows them.
