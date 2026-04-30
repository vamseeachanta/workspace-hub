# Plan for #2550: Codify public repo interaction-limit renewal in scheduled tasks

> **Status:** plan-review (batch2 hardening applied 2026-04-30; NOT approval-ready until Gemini MAJOR findings are patched and a fresh substantive re-review returns no MAJOR)
> **Complexity:** T2
> **Date:** 2026-04-29
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2550
> **Review artifacts:** `scripts/review/results/2026-04-29-plan-2550-claude.md` (canonicalized from single-author Claude review), `scripts/review/results/2026-04-29-plan-2550-codex.md` (UNAVAILABLE timeout), `scripts/review/results/2026-04-29-plan-2550-gemini.md` (MAJOR; includes stale-workspace claims plus substantive archived-repo / 404 / Bash-test findings), `scripts/review/results/2026-04-29-plan-2550-disagreement.md`

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

Not applicable — this is an infrastructure/automation issue.

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
| Plan review — Claude | `scripts/review/results/2026-04-29-plan-2550-claude.md` |
| Plan review — Codex | `scripts/review/results/2026-04-29-plan-2550-codex.md` |
| Plan review — Gemini | `scripts/review/results/2026-04-29-plan-2550-gemini.md` |

---

## Deliverable

A `scripts/security/renew-interaction-limits.sh` script with dry-run mode, full-pass verification, and non-zero exit on any non-compliant repo, registered in `config/scheduled-tasks/schedule-tasks.yaml` so the interaction-limit renewal runs automatically every ~150 days without Hermes-local cron dependency.

---

## Pseudocode

```
renew-interaction-limits.sh [--dry-run]

  OWNER = "vamseeachanta"
  PUBLIC_REPOS = gh repo list $OWNER --json name,isPrivate,isArchived --paginate
                 | filter isPrivate=false AND isArchived=false
                 | extract name list

  # Fail-closed empty-list guard (resolves F3 from
  # docs/plans/overnight-prompts/2026-04-29-next-wave-autofeed/results/nextwave-followup-plan-review-2550-20260429-1246.md):
  # zero public repos can ONLY mean auth/API/network failure — never a normal "everything passed" condition.
  if PUBLIC_REPOS is empty or null:
    print "FAIL: gh repo list returned no public repos — likely auth, API, or network failure"
    exit 1

  for each repo in PUBLIC_REPOS:
    if --dry-run:
      current = gh api repos/$OWNER/$repo/interaction-limits OR 404 => {limit: "unset", expires_at: null}
      print "DRY-RUN | $repo | current limit=$(current.limit) | expires=$(current.expires_at)"
    else:
      gh api -X PUT repos/$OWNER/$repo/interaction-limits
             -f limit=collaborators_only -f expiry=six_months

  for each repo in PUBLIC_REPOS:
    verify = gh api repos/$OWNER/$repo/interaction-limits OR 404 => {limit: "unset", expires_at: null}
    if verify.limit != "collaborators_only":
      print "FAIL: $repo not collaborators_only after renewal"
      FAIL_COUNT++
    else:
      print "OK | $repo | expires=$(verify.expires_at)"

  if FAIL_COUNT > 0: exit 1
  else: exit 0
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create | `scripts/security/renew-interaction-limits.sh` | main renewal script with dry-run + verification + fail-closed empty-list guard |
| Create | `tests/security/test_renew_interaction_limits.py` | pytest wrapper tests that execute the real Bash script with a stubbed `gh` on `$PATH`; do NOT rely on Python mocks of Bash child-process internals |
| Create | `tests/security/test_renew_interaction_limits.bats` | bats integration test using a stubbed `gh` in `$PATH` (live-invocation coverage; resolves F2 mock-vs-live divergence per `feedback_mock_vs_live_invocation_divergence.md`) |
| Modify | `config/scheduled-tasks/schedule-tasks.yaml` | add `github-interaction-limit-renewal` task entry pinned to `machines: [ace-linux-1]` (single runner — avoids double-PUT race) |
| Modify | `docs/ops/scheduled-tasks.md` | add row to task schedule table |
| Decommission | Hermes cron `d9b2d1c2270d` (`renew-github-collaborator-only-interaction-limits`) | retire local-only renewal once the canonical task is verified live for one cycle (resolves F1 — eliminates the dual-renewal-path race documented in `docs/handoffs/github-collaborator-only-lockdown-2026-04-29.md`); record removal in a follow-up handoff under `docs/handoffs/` |
| Update | `docs/plans/README.md` | add this plan to index (executor step) |

---

## TDD Test List

**Pytest wrapper tests** (`tests/security/test_renew_interaction_limits.py` — execute the real Bash script with a stubbed `gh` on `$PATH`; no Python-only mocks of Bash internals):

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| `test_dry_run_does_not_call_put` | `--dry-run` calls GET only, no PUT | `--dry-run`, mocked gh responses | stdout contains "DRY-RUN", no PUT call made |
| `test_all_compliant_exits_zero` | all repos return `collaborators_only` after renewal | mocked PUT success + GET returns `collaborators_only` | exit code 0, no FAIL lines |
| `test_noncompliant_repo_exits_nonzero` | one repo fails verification | mocked GET returns `limit=null` for one repo | exit code 1, "FAIL" in stdout for that repo |
| `test_report_includes_all_public_repos` | all non-archived public repos appear in output while archived repos are skipped | stubbed `gh repo list` returning public/private/archived repos | non-archived public repo names in stdout; archived/private absent |

**Bats integration tests** (`tests/security/test_renew_interaction_limits.bats` — invokes the actual Bash script with a stubbed `gh` in `$PATH`; resolves F2 by exercising real `set -euo pipefail`, real shell quoting, real flag parsing):

| Test name | What it verifies | Mechanism | Expected result |
|---|---|---|---|
| `test_dry_run_live_call_pattern` | live `bash renew-interaction-limits.sh --dry-run` invokes only GET, no PUT | stub `gh` writes invoked args to `/tmp/gh-trace`; assert no PUT lines | `gh-trace` contains only `api repos/.../interaction-limits` GETs |
| `test_set_minus_e_propagates_jq_failure` | malformed `gh` JSON does not silently exit 0 | stub `gh` returns invalid JSON; run script | exit code != 0; stderr mentions JSON parse / jq failure |
| `test_empty_repo_list_fails_closed` | empty `gh repo list` does not produce a "0 failures" success (resolves F3) | stub `gh repo list` returns `[]`; run script | exit code 1; stderr mentions empty-repo-list condition |

---

## Acceptance Criteria

- [ ] `scripts/security/renew-interaction-limits.sh --dry-run` exits 0 and prints current limit status without calling PUT
- [ ] `scripts/security/renew-interaction-limits.sh` (live mode) exits 0 when all public repos confirm `collaborators_only`
- [ ] Script exits 1 when any public repo does not report `collaborators_only` after renewal attempt
- [ ] When `gh repo list` returns empty/null (auth, network, or API failure), script exits 1 with explicit error message — verified by `test_empty_repo_list_fails_closed` (resolves F3)
- [ ] Repository discovery filters to non-private AND non-archived repositories before any PUT call; archived public repositories are skipped to avoid GitHub 403 failures.
- [ ] Dry-run and verification GET calls handle GitHub `404 Not Found` as an explicit `unset` interaction-limit state rather than crashing under `set -euo pipefail`.
- [ ] All pytest unit tests pass: `uv run pytest tests/security/test_renew_interaction_limits.py -v`
- [ ] All bats integration tests pass: `bats tests/security/test_renew_interaction_limits.bats` (resolves F2 — live invocation against stubbed `gh`)
- [ ] No regression: `uv run pytest workspace-hub/tests/` passes
- [ ] `config/scheduled-tasks/schedule-tasks.yaml` contains a `github-interaction-limit-renewal` task entry with the full canonical schema: `id`, `label`, `schedule`, `machines: [ace-linux-1]` (single runner — see operational note below for why dual-machine fan-out is rejected), `requires: [bash, gh]`, `command`, `log`, `is_claude_task: false`, and `description` (resolves F4 schema completeness + F6 single-machine race)
- [ ] Scheduled cadence is `0 2 1 1,6,11 *` — fires at 02:00 UTC on the 1st of January, June, and November (max gap 153 days < 183-day `six_months` expiry; min gap 61 days due to month-boundary spacing — over-renewal is safe and idempotent) (resolves F7 concrete cron syntax)
- [ ] `docs/ops/scheduled-tasks.md` table row added (Time / ID / Description / Log columns populated to match existing rows)
- [ ] After the new `github-interaction-limit-renewal` task fires successfully on its first scheduled run AND a follow-up dry-run cycle confirms expected behavior, the Hermes cron `d9b2d1c2270d` is removed (or `disabled: true`-equivalent) and the cutover is recorded in a new `docs/handoffs/` artifact citing this plan and the verification log path (resolves F1 dual-renewal-path race)

---

## Adversarial Review Summary

<!-- Single-author Claude review applied 2026-04-29; Codex/Gemini fanout NOT run by this lane (sandbox / permission-gate constraints — see provider-coverage note). -->

| Provider | Verdict | Key findings |
|---|---|---|
| Claude | MINOR_PATCH_NEEDED → patches applied | F1 Hermes cron decommission gap (MAJOR), F2 mock-vs-live test divergence (MAJOR), F3 silent-failure on empty `gh repo list` (MAJOR), F4 incomplete `schedule-tasks.yaml` schema (MINOR), F5 orphan `--output FILE` flag (MINOR), F6 single-machine spec missing (MINOR — folded into F4 patch), F7 imprecise cron cadence (MINOR), F8 pagination future-proofing (LOW), F9 failure-escalation path (LOW), F10/F11 review-summary placeholder (LOW). Patches F1–F8 landed in this revision. F9 retained as Open question for user. Full review at `docs/plans/overnight-prompts/2026-04-29-next-wave-autofeed/results/nextwave-followup-plan-review-2550-20260429-1246.md`. |
| Codex | UNAVAILABLE (2026-04-30 batch2 fanout) | `scripts/review/results/2026-04-29-plan-2550-codex.md` timed out in Codex CLI/stdin path and contributed no substantive signal. |
| Gemini | MAJOR (2026-04-30 batch2 fanout) | `scripts/review/results/2026-04-29-plan-2550-gemini.md` includes some stale-workspace false negatives about missing files, but also raises substantive blockers now patched into this plan: skip archived public repos, handle interaction-limit GET 404 as unset, and avoid Python mocks that cannot exercise Bash child process behavior. |

**Overall result:** NEEDS FRESH RE-REVIEW after batch2 hardening. The plan is not approval-ready while the latest substantive Gemini verdict is MAJOR and Codex/Claude fanout did not return fresh usable output. The canonical Claude single-author review remains useful historical evidence, but approval should wait for a clean rerun or explicit user override.

**Provider-coverage honesty note:** Only the Claude review artifact exists today. Codex and Gemini have not produced verdicts on this plan. Per `feedback_never_offer_to_self_label_plan_approved.md`, this plan does NOT self-approve; the `status:plan-review` GitHub label remains until the user explicitly flips it.

Revisions made based on review:
- Pseudocode: dropped `[--output FILE]` flag (F5); switched `--limit 100` → `--paginate` (F8); inserted fail-closed empty-list guard (F3).
- Files to Change: added `tests/security/test_renew_interaction_limits.bats` row (F2); added Decommission row for Hermes cron `d9b2d1c2270d` (F1).
- TDD Test List: split into pytest unit table + bats integration table; added `test_dry_run_live_call_pattern`, `test_set_minus_e_propagates_jq_failure`, `test_empty_repo_list_fails_closed` (F2 + F3).
- Acceptance Criteria: enumerated full `schedule-tasks.yaml` schema including `id`, `label`, `log`, `is_claude_task: false`, and `machines: [ace-linux-1]` (F4 + F6); replaced `0 2 1 */5 *` with `0 2 1 1,6,11 *` and documented max/min gaps (F7); added empty-list-fail AC (F3); added Hermes cron decommission AC (F1).
- Risks and Open Questions: replaced pagination risk with resolution note (F8); added Hermes cron cutover sequence (F1); added Open question on `notify.sh` failure escalation vs log-only audit trail (F9).
- Front-matter: `Status` flipped from `draft` to `plan-review` to match live GitHub label state; `Review artifacts` line now points to the actual single-author review file path with explicit Codex/Gemini-not-run disclosure.

---

## Risks and Open Questions

- **Resolved (F8):** `gh repo list` pagination — pseudocode now uses `--paginate` instead of `--limit 100`, removing the >100-repo brittleness class entirely (cost: zero — one-flag change). Original verified counts: 10 public + 17 private = 27 total as of 2026-04-29.
- **Risk:** GitHub API returns 405 for private repos (confirmed in #2546 comment). Script must skip private repos before calling PUT, not after a 405. The filter on `isPrivate=false` handles this.
- **Operational gap / cutover (F1):** Until the Hermes cron `d9b2d1c2270d` is removed, two renewal paths run concurrently every ~150 days. Cutover sequence: (a) install new task; (b) execute one `--dry-run` cycle and verify cron logs match expected behavior (correct repo set, correct expiry, exit 0); (c) execute one live cycle and verify all 10 public repos confirm `collaborators_only` with refreshed expiry; (d) only then remove the Hermes cron and record the removal in a new `docs/handoffs/` artifact. Until step (d) completes, both paths racing is bounded-safe (idempotent PUTs to the same `limit=collaborators_only`/`expiry=six_months`) but is exactly the dual-source-of-truth anti-pattern this issue exists to retire.
- **Open (F9 — flag for user during approval):** On exit 1 (any failure mode — empty repo list, non-compliant verification, API blip, auth expiry), should the script invoke `scripts/notify.sh` like `research-staleness` and `compliance-daily` do, OR is a `>> $WORKSPACE_HUB/logs/security/...log` audit trail sufficient given the 5-month cadence? A security control that fails silently to a log no one reads is de-facto undefended; an `notify.sh` integration is one extra line in the cron command and removes that risk class. Recommend: yes, wire `notify.sh` on non-zero exit. Decision pending user approval.
- **Open:** Should the script post a GitHub issue comment with the renewal report (like `compliance-daily` does)? Issue body says "post or prepare a verification report referencing #2546" — option to write a local report file rather than always posting. Flag for user during approval.
- **Open:** Does the `tests/security/` directory need a `conftest.py` or `__init__.py`? Check test runner config in `pyproject.toml` before creating the directory.

---

## Complexity: T2

New script with argument parsing, multiple files, TDD required, config entry, and docs update. More than one file modified/created; full workflow applies.
