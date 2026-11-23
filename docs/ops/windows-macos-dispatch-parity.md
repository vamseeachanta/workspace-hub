# Windows / macOS pull dispatch

Deckhand retired 2026-10-18 (deckhand issue 599). The Telegram venue and Hermes
gateway promotion instructions formerly on this page no longer apply.

Use the existing [pull/poll dispatch guide](pull-dispatch-no-ssh.md) and
[continuous pull-dispatch runbook](../runbooks/dispatch-pull.md). On main, those
guides already document routed-card polling, fenced Git leases, outbound Git
reporting, per-issue command bindings and explicit write gates. They do not
require a bot announcement to discover work.

Polling is not installed on Windows or macOS. The scheduled-task catalog targets
Linux workers only, and the non-Linux registry entries have dispatch disabled.
Scheduling and execution remain opt-in. A schedule or a successful poll does not
establish execution readiness or authorization.

Linux workers without SSH use the same
[pull/poll dispatch guide](pull-dispatch-no-ssh.md), with cron for scheduling.
They require a configured workspace and toolchain before promotion.

## Promotion checklist

The following checks will be completed on each proposed worker before dispatch
is enabled; this document does not install a scheduler or enable execution.

- [ ] **Authorization and readiness** — verify the authorized repository scope,
  access profile, configured workspace, toolchain and fresh equality self-report.
- [ ] **Scheduled poll registered** — register `scripts/operations/dispatch_pull.py`
  with Task Scheduler on Windows or a user launchd agent on macOS.
- [ ] **Dry-run claim proven** — run the poll against an authorized test card with
  the dry-run executor; verify the claim and outbound report, and that blocked
  cards are skipped.
- [ ] **Lease ref namespace reachable** — verify outbound fetch and push access
  to the dispatch lease refs, fencing and release without duplicate execution.
  A lease provides execution coordination; it does not grant task authority.
- [ ] **Registry enablement** — after the checks pass, an authorized operator
  will set `dispatch_enabled: true` and `telegram_mode: worker` within
  `telegram_hermes`. Verify the worker's top-level `storage` mapping and the
  `hermes_profile`, `sync_policy`, `data_access_profile` and
  `readiness_freshness_thresholds` fields within `telegram_hermes`, then run the
  schedule and dispatch validators. These fields remain required by
  `scripts/telegram_dispatch/policy.py`; retiring the gateway does not change
  the registry schema. A worker with `ssh: null` uses the pull path.

## Demotion

An authorized operator will unregister the scheduled poll and set
`dispatch_enabled: false` and `telegram_mode: desktop-status-only` within
`telegram_hermes`, then verify that no further cards are claimed.
Existing in-flight claims will be accounted for and their lease disposition
verified. Outbound Git credential rotation remains independent of scheduling.

Historical parity plans and deployment evidence remain in Git history and dated
reports. They do not establish current bot availability.
