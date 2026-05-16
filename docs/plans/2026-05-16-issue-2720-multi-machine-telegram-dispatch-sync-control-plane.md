# Plan for #2720: Multi-machine Telegram dispatch and sync control plane

> **Status:** plan-review
> **Complexity:** T3
> **Date:** 2026-05-16
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2720
> **Review artifacts:** scripts/review/results/2026-05-16-plan-2720-r4-claude.md | scripts/review/results/2026-05-16-plan-2720-r4-codex.md | scripts/review/results/2026-05-16-plan-2720-r4-gemini.md | scripts/review/results/2026-05-16-plan-2720-r4-disagreement.md

---

## Resource Intelligence Summary

### Existing repo code and configuration
- Found: `config/workstations/registry.yaml` — canonical workstation registry. It states: `HARD RULE: all machine identity/capability data lives here.` The implementation will **extend this file in-place** with Telegram/Hermes dispatch metadata instead of creating a competing host registry.
- Found: `scripts/ai/provider-dispatch-loop.py` — existing provider dispatch loop with leader-host locking, lease ledger paths, lease TTL, idempotency keys, readiness gates, and plan-approval checks. The implementation will reuse or factor this lease/leader pattern rather than invent a weaker comment-only or git-file-only lease.
- Found: `scripts/ai/task-dispatcher.py` — existing provider/model task router. It scores providers by tier and keywords but is not a machine job launcher. The implementation will treat it as a routing input, not the Telegram dispatch executor.
- Found: `scripts/operations/workstation-dispatch.sh` and `scripts/coordination/routing/lib/agent_dispatcher.sh` — existing local dispatch/routing helpers. The implementation will survey these before adding any new `scripts/telegram_dispatch/` entry points.
- Found: `scripts/readiness/compare-harness-state.sh` — compares readiness across hosts, but currently hard-codes `ace2_hub="/mnt/workspace-hub"`. The implementation will migrate Telegram/Hermes readiness checks to derive host paths from `config/workstations/registry.yaml` and will fail closed on observed-vs-registered path drift.
- Found: `scripts/readiness/nightly-readiness.sh` — centralizes readiness checks and writes `.claude/state/readiness-issues.md`. The implementation will add Telegram/Hermes dispatch readiness as a bounded check without aborting unrelated nightly readiness work.
- Found: `scripts/readiness/workstation-version-check.sh` — provides Windows-oriented software readiness patterns for ANSYS/OrcaFlex. The implementation will add Windows-shaped fixtures for Hermes/Telegram/readiness reporting without assuming Linux-only commands.
- Found: `scripts/hermes/backfill-skills-to-repo.sh` — existing Hermes skill backfill/sync helper. The implementation will keep skill/config parity repo-backed and will not use Telegram message history as a sync source.
- Found: `scripts/dispatch/overnight-2026-05-13/C2-issue-2563.sh` and related lane scripts — existing issue-specific dispatch lane artifacts. The implementation will avoid duplicating these lane scripts unless a new reusable Telegram dispatch interface is justified.
- Observed but not authoritative: `.claude/skills/operations/telegram-hermes-bot/references/multi-machine-dispatch.md` exists only as a local untracked draft. The plan does **not** rely on that file for correctness claims. After user approval, implementation will either promote equivalent content into the tracked Telegram-Hermes skill/reference tree or keep the durable multi-machine contract solely in `docs/ops/telegram-hermes-multimachine-control-plane.md`.

### Standards and workflow sources
| Standard / source | Status | Finding |
|---|---|---|
| `AGENTS.md` | applicable | Requires issue → plan → adversarial review → user approval → TDD → close; implementation dispatch must not bypass this gate order. |
| `docs/plans/README.md` | applicable | Requires resource intel, plan artifact, adversarial review artifacts, GitHub comment, `status:plan-review`, then hard stop for user approval. |
| `docs/plans/_template-issue-plan.md` | applicable | Requires concrete artifact map, files-to-change list, TDD list, acceptance criteria, review summary, risks, and complexity. |
| `docs/standards/CONTROL_PLANE_CONTRACT.md` | applicable | Confirms `AGENTS.md` is the canonical context entry point and provider adapters must not contradict it. |
| `config/agents/hermes/SOUL.md` | applicable | Repeats the no-self-approval hard gate and repo-backed configuration discipline for Hermes. |
| `.claude/settings.json` | applicable | Shows local Claude hooks and permission settings; Telegram-driven access must not weaken repo governance hooks or approval gates. |
| `.claude/rules/README.md` and existing `.claude/rules/*.md` | partial | Existing repo rules include calc citation, goal invocation, patterns, and coding style. Referenced `security.md`/`legal-compliance.md` are not present on `main`; implementation will record this as a governance gap and will rely on `AGENTS.md`, `SHARED_SOUL.md`, and `scripts/legal/legal-sanity-scan.sh` until those rule paths are restored. |
| `docs/document-intelligence/data-intelligence-map.md` | consulted | Universal planning retrieval entry point exists; no document-intelligence-specific implementation dependency was found for this harness/control-plane issue. |
| `scripts/legal/legal-sanity-scan.sh` | applicable | Mandatory changed-file scan for no client identifiers/secrets; this issue will include token redaction and legal/security scan acceptance criteria. |

### Documents and issues consulted
- Issue #2720 — defines the target: multi-computer Hermes + Telegram dispatch where Telegram is a thin command/notification surface and synchronization remains repo/GitHub-backed.
- Issue #2563 — single-host Telegram mobile access for Hermes AI control is already `status:plan-approved`; #2720 will inherit findings without duplicating single-host setup.
- Issue #1885 — ace-linux-1 Telegram gateway setup issue exists and records the `GATEWAY_ALLOW_ALL_USERS` risk; #2720 will make allow-all a readiness failure unless a separate multi-user security plan is approved.
- Issue #2665 — provider-credit approval dashboard and dispatch gates is already `status:plan-approved`; #2720 will reuse dispatch/approval-gate concepts rather than create a competing scheduler.
- `docs/ops/machine-inventory.md` — current human-readable machine dispatch readiness inventory. It asks each machine to answer programs/licenses, AI-provider auth, repos, smoke/run commands, and dispatch readiness.
- `docs/ops/2026-05-04-multimachine-baseline-inventory.md` — defines roles: ace-linux-1 as control plane/source of truth, ace-linux-2 as secondary AI/OSS worker, licensed Windows hosts as solver machines, macbook as portable manual dev, and shoerack as future GPU compute.
- `docs/methodology/multi-agent-parity.md` — defines repo-backed parity: skills, memory, and agent knowledge synchronize through git-tracked files, not through agent-local memory or message history.
- `docs/reports/inventory-readiness-matrix-2026-04-25.md` — uses `READY`, `PARTIAL`, and `MISSING` stage values in its package readiness and blocked-evidence tables; #2720 will reuse the evidence-status vocabulary only where it fits machine readiness reporting.
- `scripts/readiness/harness-config.yaml` — readiness config for required plugins, tier-1 repos, workstation report paths, Hermes health checks, and prerequisites.

### Current CI and review baseline
`gh run list --branch main --limit 10` on 2026-05-16 recorded this pre-work baseline:

| Created UTC | Run | Status | Conclusion | URL |
|---|---|---|---|---|
| 2026-05-16T12:40:10Z | Claude Code | completed | skipped | https://github.com/vamseeachanta/workspace-hub/actions/runs/25962163751 |
| 2026-05-16T12:36:49Z | Claude Code | completed | skipped | https://github.com/vamseeachanta/workspace-hub/actions/runs/25962098685 |
| 2026-05-16T12:31:49Z | Claude Code | completed | skipped | https://github.com/vamseeachanta/workspace-hub/actions/runs/25961997006 |
| 2026-05-16T12:24:48Z | Claude Code | completed | skipped | https://github.com/vamseeachanta/workspace-hub/actions/runs/25961856679 |
| 2026-05-16T12:12:41Z | Baseline Testing | completed | success | https://github.com/vamseeachanta/workspace-hub/actions/runs/25961626577 |
| 2026-05-16T12:12:16Z | Claude Code | completed | skipped | https://github.com/vamseeachanta/workspace-hub/actions/runs/25961617681 |
| 2026-05-16T11:45:08Z | Claude Code | completed | skipped | https://github.com/vamseeachanta/workspace-hub/actions/runs/25961089561 |
| 2026-05-16T11:07:16Z | Baseline Testing | completed | success | https://github.com/vamseeachanta/workspace-hub/actions/runs/25960370466 |
| 2026-05-16T11:06:46Z | Claude Code | completed | skipped | https://github.com/vamseeachanta/workspace-hub/actions/runs/25960360741 |
| 2026-05-16T10:23:07Z | Claude Code | completed | skipped | https://github.com/vamseeachanta/workspace-hub/actions/runs/25959526578 |

### Evidence

Captured 2026-05-16T15:43:47Z from `/mnt/local-analysis/workspace-hub`.

**Reproduction proofs:** N/A — this is a planning/governance/control-plane design issue, not a reported runtime failure.

**Issue statuses** (`gh issue view 2720 --json number,title,state,labels,url,comments --jq ...`):
```json
{"commentCount":0,"labels":["enhancement","priority:high","cat:ai-orchestration","cat:operations","cat:harness","domain:integrations","domain:notification","status:needs-plan"],"number":2720,"state":"OPEN","title":"feat(hermes): multi-machine Telegram dispatch and sync control plane","url":"https://github.com/vamseeachanta/workspace-hub/issues/2720"}
```

**File existence** (`ls -la` on correctness-critical paths):
```text
-rwxrwxrwx 1 vamsee vamsee 39559 May 16 08:23 docs/plans/2026-05-16-issue-2720-multi-machine-telegram-dispatch-sync-control-plane.md
-rwxrwxrwx 1 vamsee vamsee 117799 May 16 07:37 docs/plans/README.md
-rwxrwxrwx 1 vamsee vamsee 4925 May 14 23:05 config/workstations/registry.yaml
-rwxrwxrwx 1 vamsee vamsee 21189 May 13 22:54 scripts/ai/provider-dispatch-loop.py
-rwxrwxrwx 1 vamsee vamsee 9234 Apr  4 21:11 scripts/ai/task-dispatcher.py
-rwxrwxrwx 1 vamsee vamsee 8559 Mar 31 06:06 scripts/operations/workstation-dispatch.sh
-rwxrwxrwx 1 vamsee vamsee 3864 Mar 31 06:06 scripts/coordination/routing/lib/agent_dispatcher.sh
-rwxrwxrwx 1 vamsee vamsee 4145 Apr 11 12:30 scripts/readiness/compare-harness-state.sh
-rwxrwxrwx 1 vamsee vamsee 2447 Apr 12 05:46 scripts/readiness/harness-config.yaml
-rwxrwxrwx 1 vamsee vamsee 42999 Apr 12 05:47 scripts/readiness/nightly-readiness.sh
-rwxrwxrwx 1 vamsee vamsee 5361 Mar 31 06:06 scripts/readiness/workstation-version-check.sh
-rwxrwxrwx 1 vamsee vamsee 8470 Apr  5 21:35 scripts/hermes/backfill-skills-to-repo.sh
-rwxrwxrwx 1 vamsee vamsee 12789 May 14 23:05 docs/ops/machine-inventory.md
-rwxrwxrwx 1 vamsee vamsee 10528 May  4 22:29 docs/ops/2026-05-04-multimachine-baseline-inventory.md
-rwxrwxrwx 1 vamsee vamsee 14914 Apr  9 15:17 docs/methodology/multi-agent-parity.md
-rwxrwxrwx 1 vamsee vamsee 5693 May  1 20:29 docs/reports/inventory-readiness-matrix-2026-04-25.md
-rwxrwxrwx 1 vamsee vamsee 4420 Apr 23 17:25 docs/standards/CONTROL_PLANE_CONTRACT.md
-rwxrwxrwx 1 vamsee vamsee 4061 May 15 17:45 config/agents/hermes/SOUL.md
-rwxrwxrwx 1 vamsee vamsee 10494 May  1 20:29 .claude/settings.json
-rwxrwxrwx 1 vamsee vamsee 10415 Apr  7 08:50 scripts/legal/legal-sanity-scan.sh
-rwxrwxrwx 1 vamsee vamsee 3075 May 16 05:23 .claude/skills/operations/telegram-hermes-bot/references/multi-machine-dispatch.md
```

**Line excerpts** proving canonical registry and readiness path drift:
```text
$ sed -n '1,8p' config/workstations/registry.yaml
# registry.yaml — Single source of truth for all workstations.
# Read by: scripts/cron/setup-cron.sh, scripts/operations/workstation-status.sh
# HARD RULE: all machine identity/capability data lives here.
...
  dev-secondary:
    hostname: ace-linux-2
    os: linux
    role: secondary-dev
    workspace_root: /mnt/local-analysis/workspace-hub

$ sed -n '38,46p' scripts/readiness/harness-config.yaml
  dev-primary:
    ws_hub_path: /mnt/local-analysis/workspace-hub
    ssh_target: null
    report_path: .claude/state/harness-readiness-dev-primary.yaml
  dev-secondary:
    ws_hub_path: /mnt/workspace-hub
    ssh_target: ace2
    report_path: .claude/state/harness-readiness-dev-secondary.yaml

$ sed -n '25,33p' scripts/readiness/compare-harness-state.sh
check_ace2() {
  local ssh_target="ace2"
  local ace2_hub="/mnt/workspace-hub"
  local ace2_report="${STATE_DIR}/harness-readiness-ace-linux-2.yaml"
```

**Gap proofs**:
```text
$ ls -d scripts/telegram_dispatch tests/telegram_dispatch 2>&1 || true
ls: cannot access 'scripts/telegram_dispatch': No such file or directory
ls: cannot access 'tests/telegram_dispatch': No such file or directory

$ grep -R "telegram.*dispatch\|/dispatch\|/jobs\|/sync\|acquire_dispatch_lease" -n scripts config tests .claude/skills/operations/telegram-hermes-bot 2>/dev/null | grep -v 'docs/plans' | head -40
scripts/ai/provider-work-queue.py:162:            # Non-truncated candidate set for downstream Kanban/dispatcher consumers (#2665).
```
These gap proofs show no existing Telegram/Hermes multi-host dispatch parser, job API, sync API, or lease implementation under the planned script/test paths; existing references are generic dispatch/sync infrastructure, not the requested Telegram control plane.

**Plan/index existence:** `docs/plans/README.md` contains the #2720 row at line 203 with status `plan-review` after adversarial review closeout.

**Durability closeout:** the #2720 plan and r4 review artifacts are committed by the closeout commit and pushed to `origin/main` before the GitHub issue label transition. This is not implementation permission; implementation remains blocked until user approval.

Initial T3 adversarial plan review artifacts for this plan returned **MAJOR** from Claude, Codex, and Gemini. Subsequent rounds drove the plan to the current patched state: duplicate host registry removed, Git remote-ref lease with expired-lease fast-forward renewal specified, approval marker gate added, harness-config path reconciliation added, embedded evidence added, allow-all fail-closed tests added, skill/reference durability corrected, and acceptance criteria tightened. No implementation may start until the user applies `status:plan-approved`.

### Gaps identified
- `config/workstations/registry.yaml` lacks Telegram/Hermes dispatch-specific keys (`telegram_mode`, `hermes_profile`, `sync_policy`, `dispatch_enabled`, `data_access_profile`, freshness thresholds). These will be added to the existing registry, not a new registry file.
- No durable multi-machine Telegram/Hermes runbook exists on `main` that answers single coordinator bot vs per-host profiles, command contract, token rotation, rollback, and cross-OS operator UX.
- No Telegram command parser currently maps `/status`, `/dispatch`, `/jobs`, and `/sync` to GitHub issue gates, registry-derived host routing, readiness reports, and an atomic lease mechanism.
- No atomic cross-host Telegram dispatch lease exists. Existing `provider-dispatch-loop.py` has a useful leader lock and JSONL ledger pattern, but Telegram dispatch will use a **Git remote-ref creation lease** as the atomic primitive: a host creates an empty lease commit and pushes it without force to `refs/heads/dispatch/leases/<issue>-<mode>`. Remote ref creation/update rejection is the cross-host winner/loser arbiter; GitHub issue comments only mirror the winning lease for human visibility.
- No machine-by-machine data-access matrix currently combines workspace roots, storage roots, knowledge roots, remote mounts, repos, and report output locations in a Telegram-consumable readiness report.
- No tests currently exercise Telegram dispatch policy: fail-closed host identity, approval-state gating, dirty-worktree blocking, duplicate/concurrent lease blocking, `GATEWAY_ALLOW_ALL_USERS=true` blocking, token redaction, and safe sync behavior.

---

## Machine-by-machine readiness and data-access scope

| Host ID | Hostname | Role | Workspace/data sources to verify | Dispatch posture for MVP |
|---|---|---|---|---|
| `dev-primary` | `ace-linux-1` | Control plane / primary dev | Workspace `/mnt/local-analysis/workspace-hub`; local `/mnt/local-analysis`; knowledge `/mnt/ace`; remote mounts `/mnt/remote/ace-linux-2/dde` and `/mnt/remote/ace-linux-2/local-analysis`; repos include workspace-hub, digitalmodel, assetutilities, worldenergydata, assethold, OGManufacturing. | Coordinator/leader candidate. May run Telegram gateway and write dispatch leases if clean, synced, approved, and allowlist-safe. |
| `dev-secondary` | `ace-linux-2` | Secondary dev / OSS simulation worker | Workspace `/mnt/local-analysis/workspace-hub`; local `/mnt/dde`; NFS client view of ace-linux-1 knowledge to be verified; repos digitalmodel and worldenergydata. | Worker candidate for approved or plan-only work after SSH/readiness path verification. Must not self-originate leases unless explicitly promoted. |
| `licensed-win-1` | `licensed-win-1` | Simulation license host | Workspace `D:\workspace-hub`; local `D:\`; no NFS/SSH; repo OGManufacturing; licensed solver outputs via Git-backed queue. | Status-only/readiness-only in MVP unless Hermes/gateway parity and safe queue execution are verified. |
| `licensed-win-2` | `licensed-win-2` | Secondary licensed solver host | Workspace `D:\workspace-hub`; local `D:\`; no NFS/SSH; repo OGManufacturing. | Status-only/readiness-only until live license/access probes confirm routing. |
| `macbook-portable` | `Vamsees-MacBook-Air` | Portable manual dev | Workspace `/Users/krishna/workspace-hub`; local `/Users/krishna`; no NFS/cron from Linux. | Manual status participant only; no unattended dispatch dependency. |
| `gali-linux-compute-1` | `shoerack` | Future GPU compute | Workspace currently null; local access TBD; CUDA/dual RTX 3090; no repos yet. | Not dispatchable. `/status` should report `not_onboarded` and required setup steps. |

The implementation will make `/status` report both AI harness readiness and data-access readiness per host: workspace root observed, GitHub auth, Hermes/gateway profile, provider auth status where non-secretly observable, repo availability, dirty/synced state, storage/knowledge mount availability, readiness report freshness, and whether the host is allowed to dispatch, execute, or report only.

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-05-16-issue-2720-multi-machine-telegram-dispatch-sync-control-plane.md` |
| Plan index | `docs/plans/README.md` |
| Existing host registry to extend | `config/workstations/registry.yaml` |
| Dispatch contract/runbook | `docs/ops/telegram-hermes-multimachine-control-plane.md` |
| Telegram bot/gateway config template | `config/agents/hermes/telegram-multihost.example.yaml` |
| Dispatch CLI / webhook helpers | `scripts/telegram_dispatch/` or a justified extension of `scripts/ai/provider-dispatch-loop.py` / `scripts/operations/workstation-dispatch.sh` |
| Readiness integration | `scripts/readiness/telegram-hermes-readiness.sh` and bounded integration in `scripts/readiness/nightly-readiness.sh` |
| Tests | `tests/telegram_dispatch/` and `tests/readiness/test_telegram_hermes_readiness.py` |
| Skill/runbook update | `.claude/skills/operations/telegram-hermes-bot/` and `docs/ops/telegram-hermes-multimachine-control-plane.md` |
| Plan review — Claude r4 | `scripts/review/results/2026-05-16-plan-2720-r4-claude.md` |
| Plan review — Codex r4 | `scripts/review/results/2026-05-16-plan-2720-r4-codex.md` |
| Plan review — Gemini r4 | `scripts/review/results/2026-05-16-plan-2720-r4-gemini.md` |
| Plan review — disagreement/final synthesis | `scripts/review/results/2026-05-16-plan-2720-r4-disagreement.md` |

---

## Deliverable

A documented, tested, repo-backed multi-machine Telegram + Hermes dispatch control plane will exist, with registry-derived per-host readiness and data-access inventory, safe `/status`/`/dispatch`/`/jobs`/`/sync` command contracts, atomic host/job lease rules, fail-closed synchronization through GitHub/git artifacts, and explicit rollback/token-rotation procedures.

---

## Pseudocode

```text
function load_registry(path=config/workstations/registry.yaml):
    parse existing machines map
    validate required existing fields: hostname, os, role, workspace_root, capabilities, storage, repos
    validate new dispatch fields when dispatch_enabled is true: telegram_mode, hermes_profile, sync_policy, dispatch_enabled, data_access_profile, readiness_freshness_thresholds
    reject secrets/tokens and unknown host roles
    return normalized host records

function collect_host_readiness(host_id):
    verify host identity matches registry hostname/aliases
    verify workspace root exists and AGENTS.md is present
    verify observed repo root equals registry workspace_root; fail closed on drift
    verify git branch/status/upstream are safe for dispatch
    verify gh/git/hermes/provider tools required by host role are present
    verify Telegram gateway/Desktop mode is configured without exposing tokens
    verify GATEWAY_ALLOW_ALL_USERS is false/unset unless a separate security issue has status:plan-approved and .planning/plan-approved/<security_issue>.md
    verify storage, knowledge roots, remote mounts, and repos declared in data_access_profile
    verify readiness report age is within registry readiness_freshness_thresholds
    return readiness report with pass/warn/fail, freshness, and evidence lines

function acquire_dispatch_lease(issue, host, mode):
    require leader host or explicit promotion handoff
    acquire local fcntl leader lock on ace-linux-1 when operating locally
    derive lease_ref = refs/heads/dispatch/leases/<issue>-<mode> and deterministic idempotency_key
    fetch origin lease_ref; if active and not expired, reject with existing lease evidence
    if lease_ref does not exist:
        create first empty lease commit whose parent is current main sha
        run: git push origin <lease_commit>:<lease_ref> without --force
    else if lease_ref exists but is expired:
        create successor empty lease commit whose parent is current lease_ref tip
        run: git push origin <successor_lease_commit>:<lease_ref> without --force
        require fast-forward update; rejection means another host renewed first
    treat push success as the only lease win; treat push rejection as duplicate/concurrent lease loss
    after successful push, mirror lease_ref and idempotency_key to a GitHub issue comment for human-visible evidence
    write local JSONL ledger only as cache/audit, never as sole source of truth
    reject concurrent duplicate claims for issue+mode unless partition key differs explicitly
    return lease_id, lease_ref URL, and durable issue comment URL

function evaluate_dispatch_request(request):
    parse Telegram command into issue_or_task, host selector, mode, dry_run flag
    resolve GitHub issue and labels via gh
    reject implementation unless both user-approved plan signals exist: GitHub status:plan-approved and .planning/plan-approved/<issue>.md marker
    allow plan-only drafting only under status:needs-plan/status:plan-review workflow rules
    choose host by selector or registry/readiness/capability score
    reject if host readiness is fail/degraded for requested capability
    reject dirty repo, unpushed commits, stale branch, unavailable host, stale readiness, or missing data access
    acquire_dispatch_lease(issue, host, mode)
    launch bounded Hermes/job runner with log sink and durable artifact contract; do not call dated issue-specific overnight lane scripts directly
    return Telegram response with host_id, job_id, issue URL, log path, lease, and next checkpoint

function safe_sync(host_id, mode):
    verify host identity and repo root from registry
    run fetch/status discovery first
    if dirty or unpushed: report blocker and stop
    if clean: pull --ff-only and refresh external skill/config paths
    run readiness smoke after sync
    report evidence to Telegram and GitHub/repo artifact when work state changes

function redact_and_emit_status(status):
    remove bot tokens, env var values, provider secrets, and sensitive path annotations
    include host_id, capability, status, issue/job URLs, non-secret diagnostics, and data-access summary
    send to Telegram and write durable repo/GitHub artifact when work state changes
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Modify | `config/workstations/registry.yaml` | Extend existing canonical workstation registry with Telegram/Hermes dispatch fields; do not create a parallel host registry. |
| Create | `docs/ops/telegram-hermes-multimachine-control-plane.md` | Human-facing architecture/runbook: single coordinator bot vs per-host profiles, command contract, sync model, data-access matrix, rollback, token rotation, and cross-OS Telegram Desktop guidance. |
| Create | `config/agents/hermes/telegram-multihost.example.yaml` | Secret-free Hermes/gateway config template documenting per-host profiles, allowlists, and environment-variable placeholders. |
| Create or extend | `scripts/telegram_dispatch/` or existing dispatch modules | Implement Telegram command translation into validated GitHub issue + registry-derived host routing + atomic lease/job records. Final implementation must justify new directory vs extending `scripts/ai/provider-dispatch-loop.py` / `scripts/operations/workstation-dispatch.sh`; dated `scripts/dispatch/overnight-2026-05-13/` lane scripts are historical issue-specific runners and must not become the Telegram dispatch API. |
| Modify/refactor | `scripts/ai/provider-dispatch-loop.py` only if needed | Reuse/factor leader-lock and lease/idempotency logic for Telegram dispatch without weakening existing provider dispatch behavior. |
| Create | `scripts/readiness/telegram-hermes-readiness.sh` | Produce per-host readiness and data-access report for Telegram/Hermes dispatch prerequisites. |
| Modify | `scripts/readiness/nightly-readiness.sh` | Add a bounded call to Telegram/Hermes readiness near the existing readiness issue aggregation, preserving non-aborting behavior for unrelated checks. |
| Modify | `scripts/readiness/compare-harness-state.sh` | Remove or quarantine hard-coded ace-linux-2 path assumptions by deriving paths from `config/workstations/registry.yaml`; this is not optional because the current hardcode is cited as a motivating risk. |
| Modify | `scripts/readiness/harness-config.yaml` | Reconcile or retire duplicated workstation workspace path fields so readiness checks cannot disagree with `config/workstations/registry.yaml`; any remaining paths must be generated/validated against the registry. |
| Create | `tests/telegram_dispatch/test_dispatch_policy.py` | TDD coverage for label gates, host routing, dirty repo rejection, duplicate/concurrent lease rejection, and fail-closed errors. |
| Create | `tests/telegram_dispatch/test_redaction.py` | TDD coverage proving token/env/secret values never appear in status/log output. |
| Create | `tests/readiness/test_telegram_hermes_readiness.py` | Verify readiness report parsing and pass/warn/fail behavior across Linux, Windows, macOS, and not-onboarded fixtures. |
| Update | `.claude/skills/operations/telegram-hermes-bot/` | This skill is tracked; update it with the final multi-machine contract and pitfalls, while keeping `docs/ops/telegram-hermes-multimachine-control-plane.md` as the human-facing runbook. |
| Update local config | `~/.hermes/.env` on ace-linux-1 (operator action, not committed) | Remove or disable any existing `GATEWAY_ALLOW_ALL_USERS=true`; implementation must document verification evidence and must not commit secrets or env values. |
| Create | `docs/ops/telegram-hermes-desktop-smoke-checklist.md` | Manual smoke checklist for Telegram Desktop ergonomics across Linux/Windows/macOS; automated tests verify the checklist exists and is linked. |
| Update | `docs/plans/README.md` | Add this plan to the plan index and update status after review. |

---

## TDD Test List

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| `test_load_registry_rejects_secret_values` | registry cannot contain bot tokens/API keys | YAML fixture with token-looking value | validation error with redacted field name |
| `test_registry_extends_existing_workstation_schema` | dispatch metadata lives under `config/workstations/registry.yaml` machines | fixture with machines + dispatch keys | parsed host records; no parallel registry required |
| `test_dispatch_blocks_unapproved_implementation_issue` | Telegram `/dispatch` cannot bypass plan approval | issue labels `status:needs-plan` or `status:plan-review`, mode=`implementation` | blocked result explaining approval gate |
| `test_dispatch_blocks_plan_approved_without_local_marker` | status label alone is insufficient for implementation | issue has `status:plan-approved` but no `.planning/plan-approved/<issue>.md` | blocked result, no lease created |
| `test_dispatch_allows_plan_only_for_needs_plan` | planning work can be queued without implementation | issue labels `status:needs-plan`, mode=`plan` | job request accepted as plan-only |
| `test_dispatch_blocks_dirty_repo` | dirty/unknown repo state fails closed | host readiness fixture with dirty worktree | blocked result, no lease created |
| `test_dispatch_blocks_unpushed_or_stale_branch` | stale/unpushed git state fails closed | host readiness fixture with ahead/behind state | blocked result, no lease created |
| `test_dispatch_blocks_missing_data_access` | requested work cannot route to host lacking required repo/storage/mount | host fixture missing required repo or mount | blocked result naming missing data surface |
| `test_dispatch_blocks_duplicate_lease` | same issue cannot launch twice by accident | existing active lease for issue+host/task | blocked result with existing job ID |
| `test_concurrent_dispatch_acquires_single_lease` | Git remote-ref lease is atomic across processes | two subprocesses push competing lease commits to the same lease ref | exactly one push succeeds; loser receives existing lease evidence |
| `test_expired_lease_renewal_is_fast_forward_cas` | expired lease renewal cannot deadlock or require force push | existing expired lease ref plus two renewal attempts parented to current lease tip | exactly one fast-forward update succeeds; loser reports concurrent renewal |
| `test_dispatch_auto_selects_capable_clean_host` | `--host auto` uses registry + readiness + capability | mixed host readiness fixtures | selected host matches requested capability and clean state |
| `test_sync_is_fetch_status_before_pull` | `/sync` performs non-destructive discovery before pull | clean vs dirty repo fixtures | clean host runs ff-only pull; dirty host stops before pull |
| `test_status_redacts_tokens_and_env_values` | Telegram status/log output contains no secrets | payload with env/token values | redacted output and failing assertion if secret leaks |
| `test_allow_all_users_is_readiness_failure` | unsafe Telegram gateway mode fails closed | env/config fixture with `GATEWAY_ALLOW_ALL_USERS=true` | readiness failure; dispatch blocked |
| `test_missing_token_or_allowlist_is_fail_closed` | missing/invalid Telegram security state cannot silently pass | missing token or missing allowlist evidence | readiness failure without printing token values |
| `test_malformed_registry_is_fail_closed` | unreadable or invalid registry does not fall back to permissive defaults | malformed `registry.yaml` fixture | readiness failure and no dispatchable hosts |
| `test_unreachable_github_api_blocks_dispatch` | dispatch cannot continue without GitHub issue/lease authority | mocked `gh`/API timeout | blocked result, no local-only lease |
| `test_unparseable_telegram_command_is_rejected` | command parser fails closed on invalid input | `/dispatch` with missing issue or unknown flags | validation error, no lease created |
| `test_expired_or_invalid_bot_token_does_not_leak` | token validation failures redact token material | expired/invalid token fixture | readiness failure with redacted diagnostic |
| `test_windows_host_uses_windows_command_profile` | Windows readiness uses Windows path/command conventions | licensed-win fixture | report uses `D:\workspace-hub` and Windows/Git-Bash profile, not Linux assumptions |
| `test_macos_host_is_manual_status_only` | portable Mac is not treated as unattended dispatch host | macbook fixture | status-only/manual result |
| `test_not_onboarded_gpu_host_is_not_dispatchable` | future GPU node is visible but blocked | shoerack fixture with null workspace | `not_onboarded`, dispatch blocked |
| `test_readiness_report_marks_missing_gateway_degraded` | missing gateway/Desktop config is visible but not confused with repo sync | host fixture missing Telegram config | degraded readiness with actionable remediation |
| `test_job_completion_writes_durable_artifact_reference` | completed jobs report durable issue/log/handoff path, not only Telegram message | job completion fixture | status includes GitHub comment URL or repo artifact path |
| `test_desktop_smoke_checklist_is_linked` | manual Telegram Desktop UX verification is not prose-only | generated runbook | checklist path exists and is linked from the runbook |

---

## Acceptance Criteria

- [ ] `config/workstations/registry.yaml` is extended in-place for dispatch metadata and remains the single source of truth for machine identity/capability data.
- [ ] Registry coverage includes at least `dev-primary`, `dev-secondary`, `licensed-win-1`, and `licensed-win-2`; `macbook-portable` and `gali-linux-compute-1` are represented as manual/status-only or not-onboarded as appropriate.
- [ ] Human-facing runbook ranks single coordinator bot vs per-host bots/profiles and recommends one MVP architecture with explicit tradeoffs.
- [ ] `/status`, `/dispatch <issue-or-task> --host <host|auto>`, `/jobs`, and `/sync` have documented input/output contracts and fail-closed behavior.
- [ ] Telegram is explicitly documented as command/notification plane only; GitHub/git/repo artifacts remain canonical synchronization state.
- [ ] Dispatch checks GitHub labels and blocks implementation unless the issue is user-approved by both required signals: `status:plan-approved` and `.planning/plan-approved/<issue>.md`.
- [ ] Dispatch can queue plan-only work for `status:needs-plan` without bypassing the user approval gate.
- [ ] Duplicate work prevention uses the concrete Git remote-ref lease `refs/heads/dispatch/leases/<issue>-<mode>` plus deterministic idempotency keys; the Git push result is the atomic arbiter, GitHub issue comments mirror the winning lease for visibility, and the local ledger is cache/audit only.
- [ ] Expired lease renewal is defined as a fast-forward compare-and-swap update: the successor empty lease commit must parent the current lease-ref tip, push without force to the same lease ref, and treat rejection as concurrent renewal/claim loss.
- [ ] Dirty worktrees, unpushed commits, stale branches, missing host identity, missing repo root, unreachable host, stale readiness reports, or missing data access block dispatch by default.
- [ ] `GATEWAY_ALLOW_ALL_USERS=true`, missing allowlist evidence, or disabled approval mode causes readiness failure and dispatch blocking unless a separate security issue has both `status:plan-approved` and `.planning/plan-approved/<security_issue>.md`, and the runbook cites that issue explicitly.
- [ ] Secrets are never written to repo files, GitHub comments, Telegram messages, or logs; redaction tests cover token-like values and env values.
- [ ] Cross-OS behavior is documented; automated tests cover Linux, Windows-shaped, macOS manual-status, and not-onboarded GPU fixtures. Telegram Desktop ergonomics are verified by `docs/ops/telegram-hermes-desktop-smoke-checklist.md`, not claimed as fully automated.
- [ ] Readiness integration produces a machine-by-machine AI harness and data-access report consumable by nightly checks and Telegram `/status`.
- [ ] `scripts/readiness/harness-config.yaml` no longer carries workstation workspace paths that conflict with `config/workstations/registry.yaml`; tests or validation fail closed on any remaining registry/readiness path drift.
- [ ] Existing dispatch infrastructure (`provider-dispatch-loop.py`, `task-dispatcher.py`, workstation dispatch helpers, overnight lane scripts) is either reused, factored, or explicitly documented as not the right integration point.
- [ ] Rollback and token-rotation procedures are documented, including how to disable one compromised host without disabling all dispatch.
- [ ] All new automated tests pass with `uv run pytest tests/telegram_dispatch tests/readiness -v`.
- [ ] Existing readiness checks still pass or document unrelated pre-existing failures, with a pre-work `gh run list --branch main` baseline recorded.
- [ ] `scripts/legal/legal-sanity-scan.sh` passes for all changed files.
- [ ] The tracked Telegram-Hermes operations skill is updated, and the durable human-facing contract lives in `docs/ops/telegram-hermes-multimachine-control-plane.md`.

---

## Adversarial Review Summary

| Provider | Latest verdict | Key findings |
|---|---|---|
| Claude r4 | MINOR | No plan-content blockers after r4; requested harness-config row, status/header cleanup, dispatch path consistency, and review-summary freshness. |
| Codex r4 | MAJOR before final closeout | Content fixes were mostly verified; blockers were non-durable artifacts, stale review-state wording, and harness-config visibility. This revision patches wording/visibility; durability is resolved by commit/push and issue comment before label transition. |
| Gemini r4 | MAJOR before final closeout | Required embedded tool-output evidence and explicit `scripts/readiness/harness-config.yaml` reconciliation. This revision embeds the required evidence and includes harness-config in Files to Change and acceptance criteria. |

**Overall result:** plan-content blockers from r4 have been patched inline. Workflow closeout is complete once this commit is pushed, the GitHub issue summary is posted, and the issue is moved to `status:plan-review`. A `status:plan-review` transition does **not** approve implementation; implementation remains blocked until the user applies `status:plan-approved`.

Revisions made based on review:
- Replaced proposed `config/workstations/telegram-hermes-hosts.yaml` with in-place extension of `config/workstations/registry.yaml`.
- Added machine-by-machine AI harness and data-access scope.
- Added existing dispatch infrastructure retrieval and integration/justification acceptance criterion.
- Specified Git remote-ref lease creation (`refs/heads/dispatch/leases/<issue>-<mode>`) as the atomic cross-host primitive, with GitHub issue comments only as human-visible mirrors.
- Added explicit `GATEWAY_ALLOW_ALL_USERS` fail-closed tests and acceptance criterion.
- Added missing harness/infrastructure retrieval sources and recorded absent rule paths as a governance gap.
- Added `scripts/readiness/harness-config.yaml` to the planned change set and acceptance criteria so registry-vs-readiness path drift is explicitly resolved, not merely documented.
- Tightened test paths to require `tests/readiness/test_telegram_hermes_readiness.py`, approval-marker enforcement, malformed-registry/unreachable-GitHub/unparseable-command failures, and an explicit manual Desktop smoke checklist artifact.

---

## Risks and Open Questions

- **Risk:** A single coordinator bot could become a central failure point and wider blast-radius token. The runbook will compare this against per-host bots/profiles and recommend a coordinator-bot MVP only if token rotation, host disablement, allowlist enforcement, and lease visibility are satisfactory.
- **Risk:** Telegram Desktop on Windows/Linux could create operator confusion if multiple hosts respond with ambiguous names. All responses will include stable `host_id`, role, repo root, job ID, and lease ID.
- **Risk:** Git-backed sync can still race if multiple machines commit concurrently. Dispatch will require pull-before-work, pathspec-limited commits, leader lease acquisition through a non-forced Git remote-ref push, GitHub-visible mirrored lease evidence, and explicit partitioning for parallel work.
- **Risk:** Existing ace-linux-2 path drift (`/mnt/workspace-hub` vs `/mnt/local-analysis/workspace-hub`) could produce false readiness. Readiness will derive expected paths from `registry.yaml` and fail closed on mismatch.
- **Risk:** Licensed Windows hosts may not support Hermes directly. The design will treat Windows as status-only/readiness-only or git-backed queue workers unless Hermes/gateway parity is explicitly verified.
- **Risk:** Provider/headroom data may be stale. `/status` will label stale provider quota/readiness data as stale instead of treating it as dispatchable.
- **Open:** Should MVP use one coordinator bot on ace-linux-1 that routes to worker hosts, or per-host bot profiles with shared GitHub-backed lease ledger? Recommended default: coordinator bot first for operator simplicity, per-host profiles reserved for isolation after MVP.
- **Open:** Which hosts should be in the first live smoke test: ace-linux-1 + ace-linux-2 only, or include licensed-win-1 as read-only/status before execution? Recommended default: ace-linux-1 + ace-linux-2 for live dispatch, licensed-win-1 status-only until Windows readiness is fresh.
- **Open:** Which GitHub primitive should represent the active lease: label, issue comment marker, issue body task list, or Projects field? Chosen default: Git remote-ref lease creation at `refs/heads/dispatch/leases/<issue>-<mode>` with deterministic idempotency key and local leader lock; GitHub issue comments are visibility mirrors, not the atomic primitive.

---

## Complexity: T3

**T3** — this is a cross-machine, cross-OS harness/control-plane design that will touch canonical workstation configuration, Hermes/gateway operations, GitHub issue gates, readiness scripts, dispatch/lease infrastructure, tests, security/redaction, and machine/data routing. It requires 3-provider adversarial plan review before user approval and implementation.
