# Windows / macOS dispatch parity (no-SSH hosts)

> Cross-platform sibling to [`telegram-hermes-multimachine-control-plane.md`](telegram-hermes-multimachine-control-plane.md).
> Issue: [#2742](https://github.com/vamseeachanta/workspace-hub/issues/2742) (WF4, epic #2998). Ties the
> F4 Telegram-venue contract (#2971) + the WF3 pull dispatch (#3000) into a promotion path for the
> hosts the Linux control plane left as status-only.

## Scope

The Linux control plane reaches workers by **SSH push**. `ace-win-1`, `ace-win-2`, `macbook-portable`
and `gali-linux-compute-1` are `ssh: null` — no inbound SSH, corporate firewall blocks inbound, only
outbound git/HTTPS works. This document is the approved parity plan that the control-surface issue-tree
gates on ("Windows/macOS stay status-only until an approved parity plan exists"). It describes how those
hosts move from `telegram_mode: desktop-status-only` to safe dispatch targets — and how they stay safe.

## 1. Recommendation — coordinator-routed PULL worker (not per-host bots)

Three host classes:

| Class | Hosts | Reach | Dispatch model |
|---|---|---|---|
| Coordinator | `dev-primary` | inbound (hermes gateway) | owns the Telegram bot + the venue; announces work |
| SSH worker | `dev-secondary` | SSH push | existing push dispatch (`workstation-dispatch.sh`) |
| **No-SSH pull worker** | `ace-win-1/2`, `macbook-portable`, `gali-linux-compute-1` | outbound git only | **pull**: a scheduled agent claims lease-arbitrated work and reports outbound |

**Decision: no-SSH hosts become coordinator-routed pull workers.** They run NO inbound bot. The single
coordinator owns the Telegram bot and the single-active venue; it announces claimable work. Each no-SSH
host runs the WF3 pull agent (`scripts/operations/dispatch_pull.py`) on a schedule, which claims work
via the F3 git-ref lease (acquire + fencing token, no double-run across hosts), executes locally, and
reports status outbound via git.

**Per-host inbound bots are rejected.** They are physically impossible on these hosts (no inbound reach)
and would scatter the bot token across physical/portable machines. Status-only remains the pre-promotion
state; `gali` stays `disabled`/not-onboarded until it has a workspace.

**Enum note.** `telegram_mode` is a closed set `{coordinator, worker, desktop-status-only, disabled}`
(`scripts/telegram_dispatch/policy.py`). A promoted no-SSH host uses the existing **`worker`** value; the
pull-vs-push distinction is **derived from `ssh: null`** (no push reach ⇒ the dispatcher uses
`dispatch_pull.py`), so no new mode is introduced.

## 2. Service model per OS

No-SSH pull workers run NO long-lived inbound daemon. The poll is a scheduled task:

| OS | Host(s) | Scheduler | Runs |
|---|---|---|---|
| Windows / Git-Bash | `ace-win-1/2` | Task Scheduler (WF2 #2815) | `dispatch_pull.py`, `equality-report.ps1` |
| macOS | `macbook-portable` | launchd user agent | `dispatch_pull.py`, equality collector |
| Linux (no-SSH) | `gali-linux-compute-1` | cron | `dispatch_pull.py`, equality collector |

The coordinator (`dev-primary`) keeps its hermes gateway; `dev-secondary` keeps SSH-push. Python on the
no-SSH hosts is the system `python` + `pyyaml` (`python -m pip install --user pyyaml`) — `uv` is not
assumed (Windows). Cadence: equality self-report weekly; dispatch poll on the cadence the work warrants
(e.g. every 15–30 min while a wave of work is queued, idle otherwise).

## 3. Secret storage & allowlist posture

- The **Telegram bot token** and `TELEGRAM_ALLOWED_USERS` live ONLY on the coordinator. No-SSH pull
  workers never receive Telegram messages, so they hold **no bot token** — a strict reduction in secret
  surface versus a per-host-bot model.
- A pull worker needs only **outbound git credentials** (`gh auth` / a fine-scoped token) to fetch the
  queue + lease refs and push results.
- **Authority** to run an item is the registry `data_access_profile` (what repos/paths the host may touch)
  plus the git-ref lease (who runs it now). The coordinator enforces the venue allowlist via the F4
  single-active gating (`venue_lease.py`); a pull worker cannot send into the venue, only claim + report.
- Env-var POINTERS (not values) stay in the registry `telegram_hermes` block, matching the Linux contract.

## 4. Readiness evidence (mirrors Linux)

A no-SSH host is **healthy** when, using the same evidence format the Linux hosts emit:

- its `equality-<machine>.yaml` self-report (WF2 #2815 / WF5 #2816) is **fresh** (within
  `readiness_freshness_thresholds.report_hours`), AND
- it **heartbeats** — a recent claim/report cycle within the freshness threshold.

Silent-stop is caught by `venue_absence_detector.py` (F4): no heartbeat + no mirrored activity raises an
unknown-telemetry alert rather than reading as healthy. The equality matrix
(`build-equality-matrix.py`) is the fleet-wide rollup; a non-reporting host grades
`MISSING-EVIDENCE`/`UNREACHABLE` (already handled), so a promoted-but-silent host is visible, not invisible.

## 5. MVP promotion checklist (per machine class)

`desktop-status-only` → pull worker. All gates operator-run on the host (no SSH):

- [ ] **Reconciler converged** — `harness_reconcile.py --apply` ran (WF1 #2999): safety deny-list present
      in `%USERPROFILE%\.claude\settings.json` (or `~/.claude` on macOS/Linux).
- [ ] **Toolchain** — `gh auth status` OK (outbound git) and `python -m pip show pyyaml` present.
- [ ] **Scheduled poll registered** — Task Scheduler / launchd / cron runs `dispatch_pull.py` (WF2 #2815).
- [ ] **Fresh equality self-report** — `equality-<machine>.yaml` committed and within freshness (WF2/WF5).
- [ ] **Dry-run claim proven** — `python scripts/operations/dispatch_pull.py --machine <id>` claims a
      sample routed card → `ran` (dry-run executor), `blocked` cards skipped.
- [ ] **Lease ref namespace reachable** — `git fetch origin 'refs/heads/dispatch-lease/*'` and push succeed.
- [ ] **Registry flip (operator)** — `dispatch_enabled: true` + `telegram_mode: worker` (existing enum;
      `ssh: null` keeps it pull). Re-run `validate-schedule.py` / dispatch-policy validator green.

`gali-linux-compute-1` additionally needs a configured `workspace_root` + onboarded `agent_clis` before
the toolchain gate applies (it is `not-onboarded` today).

## 6. Rollback & token rotation

- **Demote** = unregister the scheduled poll + flip the registry back to `dispatch_enabled: false`,
  `telegram_mode: desktop-status-only`. No daemon to stop; no in-flight inbound state.
- **Token rotation** is a **coordinator-only** concern — pull workers hold no bot token, so a rotation
  never touches the physical Windows/macOS boxes (simpler than the SSH-worker model, where each worker
  carried env pointers). Rotating the worker's outbound git credential is independent and standard.

## Dependencies & cross-references

- **WF3 #3000** `docs/ops/pull-dispatch-no-ssh.md` + `scripts/operations/dispatch_pull.py` — the pull path.
- **F4 #2971** `docs/ops/telegram-venue-contract.md` + `scripts/operations/venue_{lease,absence_detector,audit}.py`
  — the venue consistency + health substrate.
- **WF2 #2815** — Task Scheduler rendering from `schedule-tasks.yaml` (the scheduler that runs the poll).
- **WF1 #2999** — the reconciler that converges the host before promotion.
- **deckhand#179** — the venue **send-path** (the announce side), gated behind `VENUE_LEASE_ENABLED`. The
  pull-claim side works without it (the host can poll the git-ref/queue directly), so parity is **not
  blocked** on the cross-repo send-path; deckhand#179 upgrades the trigger from poll to announce-driven.
