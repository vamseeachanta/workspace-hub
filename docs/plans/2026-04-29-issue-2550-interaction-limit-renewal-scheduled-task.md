# Plan for #2550: Codify public repo interaction-limit renewal in scheduled tasks

> **Status:** plan-review (2026-05-02 nightly batch 2 patch: fresh Codex/Claude MAJOR findings partially addressed; still not approval-ready)
> **Complexity:** T2
> **Date:** 2026-04-29
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2550
> **Review artifacts:** `scripts/review/results/2026-04-29-plan-2550-claude.md`; `scripts/review/results/2026-04-30-plan-2550-codex-final.md`; `scripts/review/results/2026-04-30-plan-2550-gemini-final.md`; `scripts/review/results/2026-05-02-plan-2550-{codex,claude}.md` (nightly batch 2 fresh re-review attempts)

---

## Resource Intelligence Summary

### Existing repo code

- Found: `config/scheduled-tasks/schedule-tasks.yaml` — canonical task registry. Schema: `id`, `label`, `schedule` (cron string), `machines` (list), `requires` (capability list), `prefer` (machine hint), `command` (shell), `log`, `is_claude_task`, `description`. No entry for interaction-limit renewal exists.
- Found: `scripts/security/secrets-scan.sh` — closest script pattern. Uses `set -euo pipefail`, `SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"`, `REPO_ROOT`, CLI arg parsing (`--repo`), structured header comment, exit 0/1. This is the pattern for `renew-interaction-limits.sh`.
- Found: `docs/ops/scheduled-tasks.md` — human-readable inventory of all scheduled tasks. Table format: `| Time | ID | Description | Log |`. Needs a new row after implementation.
- Gap: `scripts/security/renew-interaction-limits.sh` — does not exist.
- Gap: `tests/security/` directory does not exist; test must be created alongside the script.
- Gap: No task entry in `schedule-tasks.yaml` for interaction-limit renewal.

### Standards

| Standard | Status | Source |
|---|---|---|
| Plan approval hard stop | applies | `docs/standards/HARD-STOP-POLICY.md` — implementation remains blocked until user approval. |
| AI review routing | applies | `docs/standards/AI_REVIEW_ROUTING_POLICY.md` — plan needs adversarial review evidence before approval. |
| Scheduled-task governance | applies | `config/scheduled-tasks/schedule-tasks.yaml` + `docs/ops/scheduled-tasks.md` define the registry and human-readable inventory that this issue changes. |

### LLM Wiki pages consulted

No relevant wiki pages for GitHub interaction-limit renewal automation.

### Documents consulted

- `docs/handoffs/github-collaborator-only-lockdown-2026-04-29.md` — records the 2026-04-29 emergency lockdown: 10 public repos set to `collaborators_only` with `six_months` expiry (expires 2026-10-29). Hermes cron job `d9b2d1c2270d` (`renew-github-collaborator-only-interaction-limits`) created locally but NOT repo-tracked. API shape confirmed: `gh api -X PUT repos/{owner}/{repo}/interaction-limits -f limit=collaborators_only -f expiry=six_months`. Private repos return 405 — renewal is public-only.
- Issue #2546 (CLOSED/completed) — `chore(security): restrict public repo interactions to collaborators only`. Verified all 10 public repos at `collaborators_only`. Confirms 10-repo universe and GitHub's requirement that limits expire (no permanent setting).
- Issue #2550 (OPEN) — defines scope: deterministic script, dry-run mode, failure-on-non-compliant, schedule-task registration every ~150 days.

### Gaps identified

- No `scripts/security/renew-interaction-limits.sh` — must be built from scratch.
- No `tests/security/` directory or test for this script.
- No `schedule-tasks.yaml` entry for renewal — must be added.
- `docs/ops/scheduled-tasks.md` table will be stale after task is registered.

### Evidence (embedded verification)

**Issue statuses** (verified 2026-04-29T04:30Z):
- `#2546` — CLOSED (completed) — `chore(security): restrict public repo interactions to collaborators only`
- `#2550` — OPEN — `chore(security): codify public repo interaction-limit renewal in scheduled tasks`

**File existence** (`ls` 2026-04-29T04:30Z):
- EXISTS: `config/scheduled-tasks/schedule-tasks.yaml`
- EXISTS: `scripts/security/secrets-scan.sh`
- EXISTS: `docs/ops/scheduled-tasks.md`
- EXISTS: `docs/handoffs/github-collaborator-only-lockdown-2026-04-29.md`
- MISSING (new — this plan creates): `scripts/security/renew-interaction-limits.sh`
- MISSING (new — this plan creates): `tests/security/test_renew_interaction_limits.py`

**Line excerpts** (`scripts/security/secrets-scan.sh:1-18`):
```bash
#!/usr/bin/env bash
# ============================================================
# Secrets Scanner (gitleaks)
# ...
# Exit codes:
#   0  All repos pass
#   1  One or more repos fail
# ============================================================
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
```

**Gap proofs**:
- `ls scripts/security/` → `secrets-scan.sh` only — confirms `renew-interaction-limits.sh` does not exist.
- `grep -i "interaction" config/scheduled-tasks/schedule-tasks.yaml` → no output — confirms no renewal task registered.
- `ls tests/security/ 2>&1` → `tests/security does not exist yet` — confirms test directory must be created.

<!-- Verification: count distinct sources: (1) issue body #2550 + (2) schedule-tasks.yaml content + (3) secrets-scan.sh pattern + (4) handoff doc + (5) #2546 issue. Count: 5 → satisfies ≥3 -->

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-04-29-issue-2550-interaction-limit-renewal-scheduled-task.md` |
| Script | `scripts/security/renew-interaction-limits.sh` |
| Tests | `tests/security/test_renew_interaction_limits.py` |
| Schedule config | `config/scheduled-tasks/schedule-tasks.yaml` |
| Ops docs | `docs/ops/scheduled-tasks.md` |
| Plan review — Claude | `scripts/review/results/2026-04-29-plan-2550-claude.md`; refreshed attempt `scripts/review/results/2026-05-02-plan-2550-claude.md` |
| Plan review — Codex | `scripts/review/results/2026-04-30-plan-2550-codex-final.md`; refreshed attempt `scripts/review/results/2026-05-02-plan-2550-codex.md` |
| Plan review — Gemini | `scripts/review/results/2026-04-30-plan-2550-gemini-final.md`; if unavailable, rerun prompt artifact `scripts/review/prompts/2026-05-02-plan-2550-gemini-rerun.md` |

---

## Deliverable

A `scripts/security/renew-interaction-limits.sh` script with dry-run mode, full-pass verification, and non-zero exit on any non-compliant repo, registered in `config/scheduled-tasks/schedule-tasks.yaml` so the interaction-limit renewal runs automatically every ~150 days without Hermes-local cron dependency.

---

## Pseudocode

```
renew-interaction-limits.sh [--dry-run | --check]

  OWNER = "vamseeachanta"
  PUBLIC_REPOS = gh repo list $OWNER --json name,isPrivate,isArchived --paginate
                 | filter isPrivate=false
                 | extract {name,isArchived} list

  # Fail-closed empty-list guard (resolves F3 from
  # docs/plans/overnight-prompts/2026-04-29-next-wave-autofeed/results/nextwave-followup-plan-review-2550-20260429-1246.md):
  # zero public repos can ONLY mean auth/API/network failure — never a normal "everything passed" condition.
  if PUBLIC_REPOS is empty or null:
    print "FAIL: gh repo list returned no public repos — likely auth, API, or network failure"
    exit 1

  mkdir -p "$REPO_ROOT/logs/security"
  REPORT_PATH="$REPO_ROOT/logs/security/interaction-limit-renewal-$(date -u +%Y%m%dT%H%M%SZ).md"

  for each repo in PUBLIC_REPOS:
    if --dry-run or --check:
      current = gh api repos/$OWNER/$repo/interaction-limits OR 404 => {limit: "unset", expires_at: null}
      print "DRY-RUN/CHECK | $repo | archived=$(repo.isArchived) | current limit=$(current.limit) | expires=$(current.expires_at)"
    else:
      gh api -X PUT repos/$OWNER/$repo/interaction-limits
             -f limit=collaborators_only -f expiry=six_months
      if PUT fails for archived repo with 403/unsupported-state:
        record explicit failure; do not silently skip; do not remove Hermes cron until owner decides archived-repo policy

  # Dry-run is report-only by design: no PUT and no compliance failure.
  # --check is verification-only by design: no PUT and non-zero on any non-compliant public repo.
  if --dry-run:
    write local report to REPORT_PATH referencing #2546 and exit 0

  for each repo in PUBLIC_REPOS:
    verify = gh api repos/$OWNER/$repo/interaction-limits OR 404 => {limit: "unset", expires_at: null}
    if verify.limit != "collaborators_only":
      print "FAIL: $repo not collaborators_only after renewal"
      FAIL_COUNT++
    else:
      print "OK | $repo | expires=$(verify.expires_at)"

  write local verification report to REPORT_PATH referencing #2546
  if FAIL_COUNT > 0: exit 1
  else: exit 0
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create | `scripts/security/renew-interaction-limits.sh` | main renewal script with dry-run + verification + fail-closed empty-list guard |
| Create | `tests/security/test_renew_interaction_limits.py` | pytest tests that execute the real Bash script with a stubbed `gh` on `$PATH`; do NOT rely on Python mocks of Bash child-process internals. Keep this as the single required test framework unless an existing repo dependency proves `bats` is already available. |
| Modify | `config/scheduled-tasks/schedule-tasks.yaml` | add `github-interaction-limit-renewal` task entry pinned to `machines: [ace-linux-1]` (single runner — avoids double-PUT race); the scheduled command must pre-create `logs/security/` *before* any shell/task log redirection, e.g. `mkdir -p logs/security && scripts/security/renew-interaction-limits.sh ...` |
| Modify | `docs/ops/scheduled-tasks.md` | add row to task schedule table |
| Decommission | Hermes cron `d9b2d1c2270d` (`renew-github-collaborator-only-interaction-limits`) | retire local-only renewal during implementation after manual `--dry-run`, live, and follow-up `--check` verification succeed; record removal in a follow-up handoff under `docs/handoffs/` |
| Update | `docs/plans/README.md` | add this plan to index (executor step) |

---

## TDD Test List

**Pytest wrapper tests** (`tests/security/test_renew_interaction_limits.py` — execute the real Bash script with a stubbed `gh` on `$PATH`; no Python-only mocks of Bash internals; no new `bats` dependency):

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| `test_dry_run_does_not_call_put` | `--dry-run` calls GET only, no PUT | `--dry-run`, mocked gh responses | stdout contains "DRY-RUN", no PUT call made |
| `test_all_compliant_exits_zero` | all repos return `collaborators_only` after renewal | mocked PUT success + GET returns `collaborators_only` | exit code 0, no FAIL lines |
| `test_noncompliant_repo_exits_nonzero` | one repo fails verification | mocked GET returns `limit=null` for one repo | exit code 1, "FAIL" in stdout for that repo |
| `test_report_includes_all_public_repos` | all public repos appear in output, including archived public repos already protected by #2546 | stubbed `gh repo list` returning public/private/archived repos | public repo names in stdout/report; private absent; archived public marked `archived=true` rather than skipped |
| `test_dry_run_live_call_pattern` | live `bash renew-interaction-limits.sh --dry-run` invokes only GET, no PUT | stub `gh` writes invoked args to `/tmp/gh-trace`; assert no PUT lines | `gh-trace` contains only `api repos/.../interaction-limits` GETs |
| `test_malformed_gh_json_propagates_parse_failure` | malformed `gh` JSON does not silently exit 0 when parsed through `gh --jq` / shell parsing (no standalone `jq` binary required) | stub `gh` returns invalid JSON; run script | exit code != 0; stderr mentions JSON parse failure |
| `test_empty_repo_list_fails_closed` | empty `gh repo list` does not produce a "0 failures" success (resolves F3) | stub `gh repo list` returns `[]`; run script | exit code 1; stderr mentions empty-repo-list condition |
| `test_archived_public_repo_put_failure_blocks_cutover` | archived public repo renewal failure is visible and prevents decommissioning old renewal path | stub archived repo PUT returns 403 | exit code 1; report says archived repo requires owner/manual renewal decision |

---

## Acceptance Criteria

- [ ] `scripts/security/renew-interaction-limits.sh --dry-run` exits 0 and prints current limit status without calling PUT; dry-run is report-only and does not fail on non-compliant current state
- [ ] `scripts/security/renew-interaction-limits.sh --check` exits 0 only when all public repos already report `collaborators_only`; it calls GET only and exits 1 for any non-compliant repo
- [ ] `scripts/security/renew-interaction-limits.sh` (live mode) exits 0 when all public repos confirm `collaborators_only`
- [ ] Script exits 1 when any public repo does not report `collaborators_only` after renewal attempt
- [ ] When `gh repo list` returns empty/null (auth, network, or API failure), script exits 1 with explicit error message — verified by `test_empty_repo_list_fails_closed` (resolves F3)
- [ ] Repository discovery includes every public repository (`isPrivate=false`), including archived public repos such as `aceengineercode` that #2546 verified as protected. Archived public repos are marked in the report; if GitHub rejects PUT renewal for an archived repo, the script exits non-zero and records a manual owner decision/cutover blocker rather than silently letting the limit expire.
- [ ] Dry-run and verification GET calls handle GitHub `404 Not Found` as an explicit `unset` interaction-limit state rather than crashing under `set -euo pipefail`.
- [ ] All pytest unit tests pass: `uv run pytest tests/security/test_renew_interaction_limits.py -v`
- [ ] Live-invocation pytest subprocess checks pass inside `tests/security/test_renew_interaction_limits.py`; no `bats` dependency is introduced unless separately added to the repo dependency matrix and scheduled-task requirements.
- [ ] No regression: `uv run pytest tests/` passes (run from repo root; avoid non-existent nested `workspace-hub/tests/` path)
- [ ] `config/scheduled-tasks/schedule-tasks.yaml` contains a `github-interaction-limit-renewal` task entry with the full canonical schema: `id`, `label`, `schedule`, `machines: [ace-linux-1]` (single runner — see operational note below for why dual-machine fan-out is rejected), `requires: [bash, gh]`, `command`, `log`, `is_claude_task: false`, and `description` (resolves F4 schema completeness + F6 single-machine race). The implementation must use `gh --jq` or shell parsing rather than requiring a standalone `jq` binary; if standalone `jq` is introduced, this AC must change to `requires: [bash, gh, jq]`.
- [ ] Scheduled cadence is `0 2 1 1,6,11 *` — fires at 02:00 UTC on the 1st of January, June, and November (max gap 153 days < 183-day `six_months` expiry; min gap 61 days due to month-boundary spacing — over-renewal is safe and idempotent) (resolves F7 concrete cron syntax)
- [ ] `docs/ops/scheduled-tasks.md` table row added (Time / ID / Description / Log columns populated to match existing rows)
- [ ] Script creates `logs/security/` before writing reports/reports-internal logs, and the scheduled-task `command` also pre-creates `logs/security/` before invoking the script (for example, `mkdir -p logs/security && scripts/security/renew-interaction-limits.sh ...`) so scheduler-managed log handling is not dependent on an in-script directory creation that may happen too late
- [ ] Script writes a local dated verification report under `logs/security/` referencing [#2546](https://github.com/vamseeachanta/workspace-hub/issues/2546); automatic GitHub issue comments are explicitly out of scope for this tranche unless the user separately requests them
- [ ] During implementation, after the canonical scheduler entry is installed/reloaded on ace-linux-1, and after manual `--dry-run`, live, and follow-up `--check` verification all succeed for every public repo (including archived public repos or an explicit owner-approved archived-repo exception), remove the Hermes cron `d9b2d1c2270d` from ace-linux-1 with `hermes cron remove d9b2d1c2270d` (or pause/remove via the Hermes UI if CLI access is unavailable) and record the cutover in a new `docs/handoffs/` artifact citing this plan and the verification log path; do not defer this acceptance criterion to the first future scheduled run

---

## Adversarial Review Summary

<!-- Single-author Claude review applied 2026-04-29; Codex/Gemini fanout NOT run by this lane (sandbox / permission-gate constraints — see provider-coverage note). -->

| Provider | Verdict | Key findings |
|---|---|---|
| Claude | MINOR_PATCH_NEEDED → patches applied | F1 Hermes cron decommission gap (MAJOR), F2 mock-vs-live test divergence (MAJOR), F3 silent-failure on empty `gh repo list` (MAJOR), F4 incomplete `schedule-tasks.yaml` schema (MINOR), F5 orphan `--output FILE` flag (MINOR), F6 single-machine spec missing (MINOR — folded into F4 patch), F7 imprecise cron cadence (MINOR), F8 pagination future-proofing (LOW), F9 failure-escalation path (LOW), F10/F11 review-summary placeholder (LOW). Patches F1–F8 landed in this revision. F9 retained as Open question for user. Full review at `docs/plans/overnight-prompts/2026-04-29-next-wave-autofeed/results/nextwave-followup-plan-review-2550-20260429-1246.md`. |
| Codex | MAJOR (2026-05-02 fresh attempt) | `scripts/review/results/2026-05-02-plan-2550-codex.md` found archived public repos must not be silently skipped and scheduler installation/cutover must be explicit. This revision includes all public repos, treats archived PUT failure as a blocker, and requires scheduler reload before Hermes cron removal. |
| Gemini | MAJOR (2026-04-30 batch2 fanout) | `scripts/review/results/2026-04-30-plan-2550-gemini-final.md` found unresolved requirements, missing jq/log-dir guards, and cutover ambiguity; these are patched, but Gemini rerun remains unavailable/pending. |
| Claude | MAJOR (2026-05-02 fresh attempt) | `scripts/review/results/2026-05-02-plan-2550-claude.md` found `--check` semantics and fresh-artifact bookkeeping defects; this revision clarifies `--check` is GET-only verification and records current MAJOR evidence honestly. |

**Overall result:** NEEDS FRESH RE-REVIEW after 2026-05-02 hardening. The plan is not approval-ready while fresh Codex/Claude verdicts remain MAJOR. This revision addresses the archived-public-repo skip defect, report-delivery decision, `jq`/dependency ambiguity, missing log-directory guard, scheduler reload + Hermes-cron cutover specificity, and removes the undeclared `bats` dependency by consolidating live Bash invocation checks into pytest subprocess tests. Approval should wait for a clean rerun or explicit user override.

**Provider-coverage honesty note:** Historical Codex/Gemini artifacts exist but include MAJOR findings against older plan revisions. Nightly batch 2 is producing refreshed review attempts under `scripts/review/results/2026-05-02-plan-2550-*`; if a provider is unavailable, the prompt artifact is preserved and the issue remains `status:plan-review`. This plan does NOT self-approve; only the user can flip to `status:plan-approved`.

Revisions made based on review:
- Pseudocode: dropped `[--output FILE]` flag (F5); switched `--limit 100` → `--paginate` (F8); inserted fail-closed empty-list guard (F3).
- Files to Change: consolidated live Bash invocation coverage into `tests/security/test_renew_interaction_limits.py` to avoid an undeclared `bats` dependency; added Decommission row for Hermes cron `d9b2d1c2270d` (F1).
- TDD Test List: uses pytest subprocess tests for the real Bash script with a stubbed `gh`; added `test_dry_run_live_call_pattern`, `test_malformed_gh_json_propagates_parse_failure`, `test_empty_repo_list_fails_closed` (F2 + F3), and clarified that parsing must use `gh --jq`/shell parsing unless `jq` is explicitly added to scheduled-task requirements.
- Acceptance Criteria: enumerated full `schedule-tasks.yaml` schema including `id`, `label`, `log`, `is_claude_task: false`, and `machines: [ace-linux-1]` (F4 + F6); replaced `0 2 1 */5 *` with `0 2 1 1,6,11 *` and documented max/min gaps (F7); added empty-list-fail AC (F3); added Hermes cron decommission AC (F1).
- Risks and Open Questions: replaced pagination risk with resolution note (F8); added Hermes cron cutover sequence (F1); added Open question on `notify.sh` failure escalation vs log-only audit trail (F9).
- Front-matter: `Status` flipped from `draft` to `plan-review` to match live GitHub label state; `Review artifacts` line now points to the actual single-author review file path with explicit Codex/Gemini-not-run disclosure.

---

## Risks and Open Questions

- **Resolved (F8):** `gh repo list` pagination — pseudocode now uses `--paginate` instead of `--limit 100`, removing the >100-repo brittleness class entirely (cost: zero — one-flag change). Original verified counts: 10 public + 17 private = 27 total as of 2026-04-29.
- **Risk:** GitHub API returns 405 for private repos (confirmed in #2546 comment). Script must skip private repos before calling PUT, not after a 405. The filter on `isPrivate=false` handles this.
- **Risk / blocker:** Archived public repositories can already have interaction limits from #2546, but renewal semantics may differ. The script must include archived public repos in discovery/reporting and fail loudly if renewal or verification cannot keep them protected; do not silently skip them or remove the Hermes renewal cron until the owner accepts the archived-repo policy.
- **Operational gap / cutover (F1):** Until the Hermes cron `d9b2d1c2270d` is removed, two renewal paths run concurrently every ~150 days. Cutover sequence inside this implementation tranche: (a) install new task; (b) execute one manual `--dry-run` cycle and verify it reports the expected repo set without PUT calls; (c) execute one manual live cycle and verify all public repos confirm `collaborators_only` with refreshed expiry; (d) execute a follow-up manual `--check` cycle; (e) remove the Hermes cron with `hermes cron remove d9b2d1c2270d`; (f) record the removal in a new `docs/handoffs/` artifact. This cutover is intentionally not deferred to the first future scheduled run; the schedule entry remains validated by config/docs review plus the manual invocation evidence.
- **Decision:** Failure visibility is local-log/report only for this bounded tranche. `scripts/notify.sh` integration is a useful follow-up if the first cycle shows silent-failure risk, but it is not required for approval of this issue.
- **Decision:** The script prepares a local dated verification report referencing #2546. It does not post GitHub issue comments automatically in this tranche.
- **Decision:** Do not create `tests/security/__init__.py` or `tests/security/conftest.py` unless pytest collection fails without them; the initial implementation should keep the new test directory minimal.

---

## Complexity: T2

New script with argument parsing, multiple files, TDD required, config entry, and docs update. More than one file modified/created; full workflow applies.
