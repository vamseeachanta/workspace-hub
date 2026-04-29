# Plan for #2550: Codify public repo interaction-limit renewal in scheduled tasks

> **Status:** draft
> **Complexity:** T2
> **Date:** 2026-04-29
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2550
> **Review artifacts:** scripts/review/results/2026-04-29-plan-2550-claude.md | ...-codex.md | ...-gemini.md

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
renew-interaction-limits.sh [--dry-run] [--output FILE]

  OWNER = "vamseeachanta"
  PUBLIC_REPOS = gh repo list $OWNER --json name,isPrivate,isArchived --limit 100
                 | filter isPrivate=false
                 | extract name list

  for each repo in PUBLIC_REPOS:
    if --dry-run:
      current = gh api repos/$OWNER/$repo/interaction-limits
      print "DRY-RUN | $repo | current limit=$(current.limit) | expires=$(current.expires_at)"
    else:
      gh api -X PUT repos/$OWNER/$repo/interaction-limits
             -f limit=collaborators_only -f expiry=six_months

  for each repo in PUBLIC_REPOS:
    verify = gh api repos/$OWNER/$repo/interaction-limits
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
| Create | `scripts/security/renew-interaction-limits.sh` | main renewal script with dry-run + verification |
| Create | `tests/security/test_renew_interaction_limits.py` | TDD test suite (mock gh subprocess) |
| Modify | `config/scheduled-tasks/schedule-tasks.yaml` | add `github-interaction-limit-renewal` task entry |
| Modify | `docs/ops/scheduled-tasks.md` | add row to task schedule table |
| Update | `docs/plans/README.md` | add this plan to index (executor step) |

---

## TDD Test List

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| `test_dry_run_does_not_call_put` | `--dry-run` calls GET only, no PUT | `--dry-run`, mocked gh responses | stdout contains "DRY-RUN", no PUT call made |
| `test_all_compliant_exits_zero` | all repos return `collaborators_only` after renewal | mocked PUT success + GET returns `collaborators_only` | exit code 0, no FAIL lines |
| `test_noncompliant_repo_exits_nonzero` | one repo fails verification | mocked GET returns `limit=null` for one repo | exit code 1, "FAIL" in stdout for that repo |
| `test_report_includes_all_public_repos` | all 10 known public repos appear in output | mocked `gh repo list` returning 10 repos | all 10 repo names in stdout |

---

## Acceptance Criteria

- [ ] `scripts/security/renew-interaction-limits.sh --dry-run` exits 0 and prints current limit status without calling PUT
- [ ] `scripts/security/renew-interaction-limits.sh` (live mode) exits 0 when all public repos confirm `collaborators_only`
- [ ] Script exits 1 when any public repo does not report `collaborators_only` after renewal attempt
- [ ] All 4 TDD tests pass: `uv run pytest tests/security/test_renew_interaction_limits.py -v`
- [ ] No regression: `uv run pytest workspace-hub/tests/` passes
- [ ] `config/scheduled-tasks/schedule-tasks.yaml` contains a `github-interaction-limit-renewal` task entry with `schedule`, `machines`, `requires: [bash, gh]`, `command`, and `description`
- [ ] Scheduled cadence is safely under 6-month expiry (every ~150 days / `0 2 1 */5 *` or equivalent)
- [ ] `docs/ops/scheduled-tasks.md` table row added

---

## Adversarial Review Summary

<!-- Filled in after Step 4 completes. Do not post to GitHub until this section is populated. -->

| Provider | Verdict | Key findings |
|---|---|---|
| Claude | — | — |
| Codex | — | — |
| Gemini | — | — |

**Overall result:** pending

---

## Risks and Open Questions

- **Risk:** `gh repo list` pagination — if the account exceeds 100 repos, the `--limit 100` default may miss some. Fix: use `--limit 200` or paginate explicitly. Low risk now (verified 10 public repos + 17 private = 27 total as of 2026-04-29).
- **Risk:** GitHub API returns 405 for private repos (confirmed in #2546 comment). Script must skip private repos before calling PUT, not after a 405. The filter on `isPrivate=false` handles this.
- **Open:** Should the script post a GitHub issue comment with the renewal report (like `compliance-daily` does)? Issue body says "post or prepare a verification report referencing #2546" — option to write a local report file rather than always posting. Flag for user during approval.
- **Open:** Does the `tests/security/` directory need a `conftest.py` or `__init__.py`? Check test runner config in `pyproject.toml` before creating the directory.

---

## Complexity: T2

New script with argument parsing, multiple files, TDD required, config entry, and docs update. More than one file modified/created; full workflow applies.
