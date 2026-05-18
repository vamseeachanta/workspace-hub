# Linux cron issue orchestration

> Issue: [#2740](https://github.com/vamseeachanta/workspace-hub/issues/2740)  
> Status: approved MVP contract for dry-run-first GitHub-label + local-cron orchestration.

## Scope

Linux cron/GitHub-label orchestration is the MVP for unattended Linux background work. Telegram/Hermes remains the operator-facing status and notification surface; it is not the direct job-dispatch surface for this MVP.

Direct Telegram-to-machine dispatch is deferred until a separate plan proves safe host-local execution, approval posture, and gateway parity on each target machine.

## Queue contract

Local workers poll GitHub issues assigned to their canonical machine labels from `config/workstations/registry.yaml` and fail closed on ambiguity. Use stable registry IDs such as `machine:dev-primary`, not physical hostnames such as `machine:ace-linux-1`, unless the registry explicitly defines that hostname as the canonical dispatch ID.

| Issue state | Worker behavior | Provider execution |
|---|---|---|
| `status:needs-plan` and `status:plan-review` are report-only | Emit planning/review candidate status to GitHub/control-surface digest | No |
| `status:plan-approved` plus `.planning/plan-approved/<issue>.md` | Eligible after readiness, remote lease, and clean disposable worktree checks | Yes |
| Missing/multiple `machine:*` labels | Block and report routing ambiguity | No |
| Missing/multiple `agent:*` labels | Block and report provider ambiguity | No |
| Dirty/ahead/behind shared checkout | Block shared-checkout execution | No |

Runnable implementation issues require exactly one `machine:*`, exactly one `agent:*`, GitHub `status:plan-approved`, and a committed local approval marker at `.planning/plan-approved/<issue>.md` in the executing checkout.

Priority order is deterministic:

1. `priority:critical`
2. `priority:P1`
3. `priority:high`
4. `priority:medium`
5. `priority:low`
6. unlabeled

Ties sort by oldest update timestamp, then lowest issue number.

## Lease and no-overlap contract

`machine:*`, `agent:*`, and `wip:*` labels are advisory metadata, not locks.

Cross-host mutual exclusion uses git remote lease refs:

```text
refs/heads/dispatch/leases/<issue>-<mode>
```

Lease acquisition is a non-force push. Push rejection means another worker owns the issue. Lease commits should include host id, issue number, mode, provider, generated timestamp, and expiry.

Each host must also use a local no-overlap guard before attempting a remote lease. The approved implementation uses `flock` semantics for a cron tick; a systemd timer may use equivalent no-overlap semantics. Duplicate local ticks exit before queue processing.

## Execution isolation

Provider execution runs only in a clean disposable per-issue worktree. If the shared checkout is dirty, ahead, behind, missing policy files, or otherwise unsafe, the worker reports a blocker and does not run a provider from that checkout.

dry-run is the default. Production provider execution remains disabled unless all of these gates pass:

1. host readiness is `pass`;
2. exactly one matching machine label and exactly one provider label exist;
3. issue has `status:plan-approved`;
4. local approval marker exists;
5. remote lease is acquired;
6. local no-overlap lock is held;
7. clean disposable worktree/session is available.

## Readiness evidence

Remote-worker readiness must be generated on the worker host. Coordinator-side checks consume host-local readiness evidence through the existing readiness tooling and `--evidence-dir` path.

Missing, stale, malformed, wrong-host, or unredacted readiness evidence fails closed and never makes a worker eligible.

Readiness evidence comments, logs, and artifacts include only redacted key presence/status. raw environment values, chat IDs, allowlists, and bot tokens must never be written to GitHub comments, repo artifacts, or cron logs.

## Status comments

Workers may post concise status comments for blockers, report-only candidates, lease loss, dry-run output, and validation evidence. Comments mirror state for humans; GitHub labels and git lease refs remain the canonical state.

Status comments must redact:

- bot tokens and API keys;
- raw Telegram chat IDs;
- allowlists/user IDs;
- credential-bearing command lines;
- local secret file contents.

## Operator-safe disable path

Disable a host by setting its registry dispatch posture to disabled/status-only, committing the change, and rotating local secrets if there is any compromise risk. Existing lease refs should be preserved as evidence unless incident response explicitly decides otherwise.

## Current implementation artifact

The repo-owned dry-run worker is:

```bash
uv run python scripts/operations/linux-cron-issue-orchestrator.py \
  --host-machine-label machine:dev-primary \
  --plan-marker-dir .planning/plan-approved \
  --issues-json /path/to/issues.json \
  --readiness-json /path/to/host-readiness.json \
  --repo-root /path/to/clean/execution-checkout \
  --lock-path /tmp/workspace-hub-cron-issue-orchestrator.lock
```

The CLI defaults to dry-run. Dry-run output lists decisions and never executes providers unless the caller explicitly supplies `--execute` plus the later execution gates. This makes cron wiring testable without burning provider quota or bypassing the plan-approval gate.
