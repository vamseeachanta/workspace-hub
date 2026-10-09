# Status Label Mapping

This standard records the Card E04 cleanup decision: sparse `status:*` labels
that described dispatch state move to the `dispatch:*` axis. Status labels that
remain part of plan, review, blocking, data, and completeness gates are not
retired by this migration.

## Automation Inventory

The migration grep covered `scripts/`, `config/`, `.github/`, and `.claude/`.
Active code and config read the following retained status labels:

| Label | Reader | Reason retained |
| --- | --- | --- |
| `status:needs-plan` | `scripts/operations/linux-cron-issue-orchestrator.py` | Planning candidate gate. |
| `status:plan-review` | `scripts/operations/linux-cron-issue-orchestrator.py`, `.github/workflows/autoapply-completeness-label.yml` | Plan review and completeness enrollment gate. |
| `status:plan-approved` | `scripts/operations/linux-cron-issue-orchestrator.py`, `.github/workflows/autoapply-completeness-label.yml` | Implementation authorization gate. |
| `status:blocked` | `scripts/ai/build-orca-kanban.py` | Blocking state on the Orca kanban. |
| `status:completeness-verified` | `.github/workflows/completeness-gate.yml` | Completeness closeout gate. |
| `status:needs-data` | `.claude` guidance and memory surfaces | Data-readiness state, not dispatch state. |
| `status:icebox` | Config snapshots | Backlog parking state, not dispatch state. |
| `status:unreachable` | Config snapshots | Source/access state, not dispatch state. |

The sparse dispatch-like labels below are retired. Active readers were adjusted
where needed so dispatch state is read from `dispatch:*` instead of these
`status:*` labels.

## Retired Mapping

| Retired label | Replacement label | Rationale |
| --- | --- | --- |
| `status:done` | `dispatch:done` | Completion of a dispatched lane belongs on the dispatch axis. |
| `status:closed` | `dispatch:done` | Closed terminal dispatch state is equivalent to done for routing. |
| `status:implemented` | `dispatch:done` | Implemented terminal dispatch state is equivalent to done for routing. |
| `status:working` | `dispatch:active` | Active execution is dispatch state, not plan/governance state. |
| `status:in-progress` | `dispatch:active` | In-progress execution is dispatch state, not plan/governance state. |
| `status:pending` | `dispatch:ready` | Pending dispatch work is ready queue state. |

## Migration Operation

Use `scripts/operations/relabel-status-to-dispatch.sh` to perform the live
cleanup. The script is dry-run by default. With `--apply`, it relabels issues
and PRs across all non-archived repositories for the owner, then deletes each
retired `status:*` label only in repositories where both issue and PR probes
return zero remaining uses.

```bash
scripts/operations/relabel-status-to-dispatch.sh
scripts/operations/relabel-status-to-dispatch.sh --apply
```

The apply form is intentionally not run as part of this change.

Relabeling legacy active issues to `dispatch:active` fires the
`autoapply-completeness-label` workflow because that workflow treats
`dispatch:active` as a work-state transition. That enrollment is intentional for
new active work and is a known side effect of applying the migration to old
active labels.
