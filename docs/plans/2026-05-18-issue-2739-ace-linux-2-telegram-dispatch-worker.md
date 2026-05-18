# Plan for #2739: Promote ace-linux-2 as first Linux cron/Hermes worker

> **Status:** draft
> **Complexity:** T2
> **Date:** 2026-05-18
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2739
> **Review artifacts:** pending

---

## Resource Intelligence Summary

### Existing repo code
- Found: `config/workstations/registry.yaml` — `dev-secondary` maps to hostname `ace-linux-2`, `dispatch_enabled: true`, `telegram_mode: worker`, and data-access roots under `/mnt/local-analysis`.
- Found: `scripts/readiness/telegram_hermes_readiness.py` — remote dispatch hosts intentionally fail closed unless host-local readiness evidence is supplied via `--evidence-dir`.
- Found: `tests/readiness/test_telegram_hermes_readiness.py` — covers host-local readiness evidence shape, freshness, redaction, and remote evidence rejection.
- Gap: There is no host-local cron worker wrapper for `ace-linux-2` that polls GitHub issues by `machine:ace-linux-2` + `agent:*`, checks plan gates, runs only bounded approved tasks, and posts progress evidence back to GitHub.

### Standards
- Not applicable — operational machine orchestration issue, not engineering-calculation standards.

### LLM Wiki pages consulted
- No relevant wiki pages required; repo docs/runbooks are canonical for this operational scope.

### Documents consulted
- Issue #2739 — scopes `ace-linux-2` as first Linux worker.
- Parent #2737 — umbrella for approved-machine Hermes orchestration.
- `docs/ops/telegram-hermes-multimachine-control-plane.md` — current document says `dev-secondary` is worker dispatchable after readiness; user guidance pivots implementation toward cron/GitHub metadata instead of direct chat dispatch.
- `docs/runbooks/telegram-hermes-mobile.md` — token hygiene and approval boundaries; do not expose env values.
- `operations/telegram-hermes-bot` skill — local/secret-only credentials, allowlist enforcement, status before action.

### Gaps identified
- Need a clean/synced `workspace-hub` on `ace-linux-2`.
- Need verified Hermes CLI availability and version parity/update posture on `ace-linux-2`.
- Need host-local readiness evidence generated on `ace-linux-2` and consumable by `ace-linux-1`.
- Need a cron-safe queue contract: GitHub issue labels assign machine/provider; cron picks up only approved/eligible issues; progress is written back to GitHub.
- Need failure behavior that does not run unapproved implementation or destructive commands.

### Evidence (embedded verification)

**Issue statuses** (verified 2026-05-18T09:17:25Z via `gh issue view`):
- `#2739` — OPEN — `feat(hermes): promote ace-linux-2 as first Telegram/Hermes dispatch worker`; labels include `status:needs-plan`.
- Parent `#2737` — OPEN — active Linux orchestration umbrella; labels include `status:needs-plan`.

**Live host evidence** (verified 2026-05-18T09:17:25Z; secrets not printed):
```text
ssh ace-linux-2 succeeds
Hermes Agent v0.14.0 (2026.5.16)
hermes-gateway service: inactive / not installed as active unit
workspace-hub on ace-linux-2: dirty/untracked from prior probe
.env permissions: 600 vamsee:vamsee
Telegram/Gateway env keys on ace-linux-2: not configured in observed grep
```

**Coordinator-side readiness reproduction:**
```text
$ bash scripts/readiness/telegram-hermes-readiness.sh --host ace-linux-2
hosts.dev-secondary.status = fail
hosts.dev-secondary.dispatchable = false
missing_data includes host-local-readiness-evidence
failure includes host-local readiness evidence missing for remote dispatch host
```

**Line excerpts:**
```text
scripts/readiness/telegram_hermes_readiness.py:357-361
remote_evidence = _load_host_local_evidence(evidence_dir, hid, raw)
if remote_evidence is None:
    entry["warnings"].append("remote dispatch host; env gates require host-local readiness evidence")
    entry["missing_data"].append("host-local-readiness-evidence")
    entry["failures"].append("host-local readiness evidence missing for remote dispatch host")
```

```text
docs/ops/telegram-hermes-multimachine-control-plane.md:154-158
Worker (`dev-secondary`):
- Sync workspace-hub to a revision that includes readiness scripts and runbook.
- Install Hermes CLI/gateway if missing; keep approval mode safe.
- Configure env-name contract locally without committing values.
- Generate host-local readiness evidence and make it available to the coordinator via --evidence-dir.
```

**Reproduction proofs:**
- Reproduced at: 2026-05-18T09:17:25Z
- Failure mode observed matches issue claim: YES — `ace-linux-2` is reachable and has Hermes, but is not yet a safe worker because it lacks clean repo state, active host-local evidence, and cron/approval contract.

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-05-18-issue-2739-ace-linux-2-telegram-dispatch-worker.md` |
| Existing readiness implementation | `scripts/readiness/telegram_hermes_readiness.py` |
| Existing readiness tests | `tests/readiness/test_telegram_hermes_readiness.py` |
| Proposed cron worker wrapper | `scripts/operations/hermes-linux-worker-cron.sh` or `scripts/operations/hermes-linux-worker-cron.py` |
| Proposed host evidence path | `.local/readiness/telegram-hermes/dev-secondary.json` or an explicitly configured non-committed evidence dir |
| Host-local secret file | `/home/vamsee/.hermes/.env` on `ace-linux-2` — do not commit/print |

---

## Deliverable

`ace-linux-2` becomes a verified Linux worker for **GitHub-label-driven local cron orchestration**: it can poll issues assigned to `machine:ace-linux-2`, select an `agent:*` route, refuse all implementation work unless approved, post progress/evidence to GitHub, and publish host-local readiness evidence consumed by `ace-linux-1`.

Direct Telegram dispatch is not part of the MVP; Telegram remains a status/notification surface while cron + GitHub issue metadata carry the work assignment.

### Plan-review hardening: exact MVP boundaries

- Cron workers **do not perform substantive planning** for `status:needs-plan` / `status:plan-review` issues. They may report candidates and blockers only. Detailed planning happens on the control surface.
- Cron workers may perform implementation only when both gates pass:
  1. GitHub issue has `status:plan-approved`.
  2. Local repo has `.planning/plan-approved/<issue>.md`.
- Labels are routing metadata, not locks. `machine:*`, `agent:*`, and `wip:*` are advisory and auditable; the lock source of truth is the git remote lease ref.
- The cross-host lease is `refs/heads/dispatch/leases/<issue>-<mode>`, created by non-force push. Push rejection means another host owns the work.
- Cron/timer execution must use a local `flock`/systemd no-overlap guard before attempting a remote lease.
- Execution must use a clean disposable per-issue worktree or hard fail; never mutate the shared dirty checkout.

---

## Pseudocode

```text
function worker_cron_tick(host_id="dev-secondary"):
    assert current hostname matches registry host_id/hostname
    run readiness locally with --host dev-secondary --evidence-dir <local-evidence-dir>
    if readiness not pass:
        post/update GitHub status comment only if state changed
        exit 0

    issues = gh issue list with labels machine:ace-linux-2
    for issue in daily-priority order:
        read labels agent:claude/agent:codex/agent:gemini and priority
        if issue is status:needs-plan or status:plan-review:
            post/report planning candidate only; do not run provider
            continue
        require status:plan-approved and .planning/plan-approved/<issue>.md
        require exactly one machine:* label and exactly one agent:* label
        acquire git remote lease ref refs/heads/dispatch/leases/<issue>-implementation via non-force push
        create clean disposable per-issue worktree
        run bounded provider command using self-contained prompt
        write progress comment with artifact paths and verification result
        release/expire lease safely
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create | `tests/operations/test_hermes_linux_worker_cron.py` | TDD for issue selection, gate refusal, label/provider routing, and progress-comment rendering. |
| Create | `scripts/operations/hermes-linux-worker-cron.py` | Cron-safe worker tick for Linux hosts. |
| Modify | `scripts/readiness/telegram_hermes_readiness.py` | Only if needed to add a first-class host-local evidence output path or machine/provider assignment fields. |
| Modify | `docs/ops/telegram-hermes-multimachine-control-plane.md` | Document pivot: cron/GitHub-label orchestration first; direct Telegram dispatch deferred. |
| Modify | `config/workstations/registry.yaml` | Add non-secret cron/evidence metadata if needed; do not add secret values. |
| Host-local | `ace-linux-2` crontab/systemd timer | Start worker tick only after user approves implementation and host readiness passes. |

---

## TDD Test List

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| `test_worker_selects_only_matching_machine_label` | `ace-linux-2` ignores issues for other machines | issues labeled `machine:ace-linux-1`, `machine:ace-linux-2` | only `ace-linux-2` issue selected |
| `test_worker_refuses_unapproved_implementation` | Hard gate blocks implementation without approval | issue lacks `status:plan-approved` | no provider run; blocked status comment rendered |
| `test_worker_reports_needs_plan_without_provider_run` | Non-approved planning candidates are reported but not executed | issue has `status:needs-plan` | status comment prepared; no provider command |
| `test_worker_routes_provider_label` | provider labels map to command route | `agent:codex`, `agent:claude`, `agent:gemini` | route object contains expected provider |
| `test_worker_redacts_status_comments` | no secrets/private Telegram metadata leak | result with token-like string | comment body contains `[REDACTED]` |
| `test_worker_requires_clean_readiness` | no work runs when host evidence fails | readiness `status=fail` | queue tick exits with status-only report |
| `test_worker_requires_exactly_one_machine_and_agent_label` | fail-closed on ambiguous routing | zero/multiple labels | no provider command; blocked comment |
| `test_worker_uses_remote_ref_lease` | cross-host mutual exclusion | lease push accepted/rejected | only accepted pusher proceeds |
| `test_worker_timer_uses_local_no_overlap_lock` | no duplicate cron tick on same host | second tick while first active | second tick exits status-only |

---

## Acceptance Criteria

- [ ] `ace-linux-2` is clean/synced enough for readiness evidence generation.
- [ ] `uv run pytest tests/readiness/test_telegram_hermes_readiness.py -v` passes before and after changes.
- [ ] New worker-selection tests pass with `uv run pytest tests/operations/test_hermes_linux_worker_cron.py -v`.
- [ ] Host-local evidence generated on `ace-linux-2` is accepted by coordinator-side readiness with `--evidence-dir`.
- [ ] Worker cron dry run lists candidates without running providers by default.
- [ ] Cron reports `status:needs-plan` / `status:plan-review` candidates only; it does not run planning providers for them.
- [ ] Implementation-mode cron refuses issues without both GitHub `status:plan-approved` and `.planning/plan-approved/<issue>.md`.
- [ ] Runnable issues must have exactly one `machine:*` label and exactly one `agent:*` label.
- [ ] Cross-host execution requires successful non-force push of `refs/heads/dispatch/leases/<issue>-implementation`; labels/comments are not locks.
- [ ] Local timer/cron uses a no-overlap lock (`flock` or systemd equivalent) before lease acquisition.
- [ ] Execution uses a clean disposable worktree or fails closed on dirty/ahead/behind state.
- [ ] Progress comment output is redacted and includes machine, provider, issue, artifact path, and verification status.
- [ ] No Telegram token, allowlist, chat id, phone, or credential-like value appears in logs/comments/artifacts.

---

## Adversarial Review Summary

Initial review found MAJOR issues: cron workers were allowed to act on non-approved issues, lease/deduplication was underspecified, dry-run defaults were weak, and dirty checkout/isolation was too vague. The plan was hardened so `status:needs-plan` / `status:plan-review` are report-only, implementation requires both GitHub `status:plan-approved` and local `.planning/plan-approved/<issue>.md`, cross-host locking uses a git remote lease ref, local timers use a no-overlap guard, and execution uses clean disposable worktrees or fails closed.

Follow-up ops/security review: **APPROVE** for plan-review readiness.

---

## Risks and Open Questions

- **Risk:** Cron workers can create duplicate runs if lease/idempotency is weak; require a lease before provider execution.
- **Risk:** Dirty worktrees can corrupt local issue execution; worker must fail closed until clean or explicitly isolated in a worktree.
- **Risk:** Direct Telegram dispatch remains over-complex for MVP; keep it deferred and use Telegram for status only.
- **Open:** Should the worker use cron, systemd timers, or Hermes cronjob? Recommended: local systemd timer/cron wrapper first, because it survives Hermes gateway instability and keeps work assignment GitHub-centric.

---

## Complexity: T2

**T2** — one Linux worker path plus queue/gate tests; operationally important but bounded to metadata-driven cron orchestration and readiness evidence.
