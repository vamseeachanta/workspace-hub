# Plan for #2740: Formalize Linux cron orchestration readiness evidence and registry gates

> **Status:** draft
> **Complexity:** T2
> **Date:** 2026-05-18
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2740
> **Review artifacts:** pending

---

## Resource Intelligence Summary

### Existing repo code
- `scripts/readiness/telegram_hermes_readiness.py` already implements fail-closed host readiness and host-local evidence validation.
- `tests/readiness/test_telegram_hermes_readiness.py` already validates malformed/stale evidence rejection and output redaction.
- GitHub labels already exist for machine assignment and provider assignment:
  - `machine:ace-linux-1`, `machine:ace-linux-2`
  - `agent:claude`, `agent:codex`, `agent:gemini`
  - `wip:ace-linux-1`, `wip:ace-linux-2`
- Gap: no repo-owned contract connects machine/provider labels, daily priorities, readiness evidence, and local cron worker behavior.

### Standards
- Not applicable — workflow/readiness evidence, not engineering standards.

### Documents consulted
- `docs/ops/telegram-hermes-multimachine-control-plane.md`
- `docs/runbooks/telegram-hermes-mobile.md`
- `config/workstations/registry.yaml`
- Issues #2737–#2742 live labels/status.

### Evidence

Verified 2026-05-18T09:17:25Z:
```text
#2738 OPEN status:needs-plan machine labels absent before this background pass
#2739 OPEN status:needs-plan machine labels absent before this background pass
Existing labels include machine:ace-linux-1, machine:ace-linux-2, agent:claude, agent:codex, agent:gemini, wip:ace-linux-1, wip:ace-linux-2
```

Readiness behavior from `scripts/readiness/telegram_hermes_readiness.py`:
```text
Remote hosts require host-local readiness evidence via --evidence-dir.
Local dispatch hosts fail on unsafe GATEWAY_ALLOW_ALL_USERS, missing env keys, dirty/ahead/behind repo state, missing roots, and missing data access.
```

---

## Deliverable

A repo-owned orchestration contract for Linux background work:

1. The control surface ranks issues daily.
2. Issues get explicit `machine:*` and `agent:*` labels.
3. Local cron workers on `ace-linux-1` / `ace-linux-2` poll GitHub for their own machine label.
4. Workers report planning candidates for `status:needs-plan` / `status:plan-review` without running providers; detailed planning happens on the control surface.
5. Workers run implementation only for `status:plan-approved` plus local approval marker.
6. Workers post progress/evidence comments back to GitHub.
7. Telegram/Hermes remains notification/status surface, not direct dispatch MVP.

### Canonical queue contract

| Issue state | Cron behavior | Provider execution? |
|---|---|---|
| `status:needs-plan` | Report as planning candidate to GitHub/control-surface digest | No |
| `status:plan-review` | Report as review/approval candidate | No |
| `status:plan-approved` + `.planning/plan-approved/<issue>.md` | Eligible for implementation after readiness + lease | Yes |
| Missing/multiple `machine:*` labels | Block and comment routing ambiguity | No |
| Missing/multiple `agent:*` labels | Block and comment provider ambiguity | No |
| Dirty/ahead/behind shared checkout | Block unless a clean disposable per-issue worktree is created | No in shared checkout |

Priority ordering: `priority:critical` > `priority:P1` > `priority:high` > `priority:medium` > `priority:low` > unlabeled. Tie-breaker: oldest updated issue first, then lowest issue number. Daily control-surface review may change labels before cron runs.

### Lease / timer / isolation contract

- `machine:*`, `agent:*`, and `wip:*` labels are advisory metadata, not locks.
- Cross-host mutual exclusion uses a git remote lease ref: `refs/heads/dispatch/leases/<issue>-<mode>`.
- Lease acquisition is a non-force push; rejection means another worker owns the issue.
- Lease commits include host id, issue number, mode, provider, generated timestamp, and expiry.
- Each host uses `flock` or systemd no-overlap semantics before attempting a remote lease.
- Provider execution runs only in a clean disposable per-issue worktree/session.
- Production execution is disabled by default until dry-run output and readiness evidence are approved.

---

## Pseudocode

```text
for each cron tick on host:
    host_id = registry.resolve_local_host()
    readiness = collect_host_local_readiness(host_id)
    write evidence JSON locally
    if readiness not pass:
        update issue/status comment with blocker summary
        stop

    queue = gh issue list --label machine:<host> --state open
    queue = filter by status labels and daily priority order
    for issue in queue:
        provider = issue.labels intersect agent:*
        require exactly one machine:* and exactly one agent:* label
        if status:needs-plan or status:plan-review:
            post/report candidate only; do not run provider
            continue
        require status:plan-approved and .planning/plan-approved/<issue>.md
        acquire git remote lease ref by non-force push
        create clean disposable worktree/session
        run bounded provider prompt
        post progress/comment artifact path
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create | `docs/ops/linux-cron-issue-orchestration.md` | Canonical machine/provider label and cron behavior contract. |
| Create | `tests/operations/test_linux_cron_issue_orchestration.py` | TDD for label selection, approval gates, provider routing, comment redaction. |
| Create | `scripts/operations/linux-cron-issue-orchestrator.py` | Dry-run-first worker tick. |
| Modify | `docs/ops/telegram-hermes-multimachine-control-plane.md` | Pivot direct Telegram dispatch to future phase; cron/GitHub labels are MVP. |
| Modify | `config/workstations/registry.yaml` | Add non-secret cron/evidence fields only if tests require machine-local metadata. |

---

## TDD Test List

| Test name | What it verifies |
|---|---|
| `test_queue_selects_by_machine_label` | Host only sees its assigned issues. |
| `test_queue_requires_agent_label` | No provider label means no run. |
| `test_needs_plan_report_only_no_provider_execution` | Planning candidates are surfaced to the control surface without provider execution. |
| `test_implementation_requires_plan_approved_and_marker` | Implementation hard gate preserved. |
| `test_status_comment_redacts_secrets` | Token/chat/allowlist values redacted. |
| `test_dirty_readiness_blocks_worker` | Cron exits before work if host readiness fails. |
| `test_needs_plan_is_report_only` | `status:needs-plan` produces digest/comment, not provider execution. |
| `test_exactly_one_machine_and_agent_required` | Missing/multiple labels fail closed. |
| `test_remote_ref_lease_is_required_before_execution` | Provider run only after successful non-force lease push. |
| `test_local_no_overlap_lock_blocks_second_tick` | Duplicate cron tick exits before work. |
| `test_priority_ordering_is_deterministic` | Priority and tie-break rules are stable. |

---

## Acceptance Criteria

- [ ] Machine/provider routing contract exists in `docs/ops/linux-cron-issue-orchestration.md`.
- [ ] Tests prove queue selection, provider routing, approval gates, leases/deduplication, and redacted comments.
- [ ] Dry-run orchestrator can list eligible issues for `ace-linux-1` and `ace-linux-2` without executing providers.
- [ ] `status:needs-plan` and `status:plan-review` issues are report-only for cron workers.
- [ ] Runnable implementation issues require exactly one `machine:*`, exactly one `agent:*`, GitHub `status:plan-approved`, and local approval marker.
- [ ] Cross-host lease uses git remote ref non-force push; `wip:*` labels/comments are advisory only.
- [ ] Local cron/systemd timer has no-overlap guard, max runtime, and operator-safe disable path.
- [ ] Execution uses clean disposable per-issue worktrees or fails closed.
- [ ] Remote-worker host-local readiness evidence is generated locally on the worker host and consumed by coordinator-side `--evidence-dir` checks.
- [ ] Missing, stale, malformed, wrong-host, or unredacted readiness evidence fails closed and never makes a worker eligible.
- [ ] Readiness evidence comments/logs/artifacts include only redacted key presence/status, never raw env values or secret-bearing command lines.
- [ ] Direct Telegram dispatch is explicitly documented as deferred/future, not MVP.
- [ ] Existing readiness tests continue passing.
- [ ] Issues #2738 and #2739 have machine/provider labels applied for the Linux MVP planning lane.

---

## Adversarial Review Summary

Initial review found MAJOR issues: the contract allowed planning-provider execution before approval, lease/deduplication was not concrete, timer/no-overlap safety was underspecified, and readiness-evidence acceptance was too implicit. The plan was hardened with a canonical queue contract, report-only behavior for non-approved issues, remote git lease refs, no-overlap timer guards, clean disposable worktrees, deterministic priority ordering, and explicit host-local readiness evidence fail-closed criteria.

Final narrow re-review after patching the remaining TDD contradiction and evidence criteria: **APPROVE** for plan-review readiness.

---

## Risks and Open Questions

- **Risk:** Without a lease, cron on both machines could duplicate work. Lease/idempotency must be included before provider execution.
- **Risk:** Cron jobs can burn credits if issue filters are too broad. Default mode must be dry-run/status-only until explicitly enabled.
- **Open:** Provider choice can be static labels initially; later daily priority review can update labels based on quota/readiness.

---

## Complexity: T2

**T2** — introduces a repo contract and dry-run worker behavior, but keeps implementation bounded and fail-closed.
