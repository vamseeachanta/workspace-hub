# Plan for #2756: throughput(workstations): activate licensed-win-1 solver/status lane

> **Status:** draft — resource intel captured; adversarial plan review not yet run
> **Complexity:** T2
> **Date:** 2026-05-20
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2756

---

## Objective

Decide and enforce the tier-1 repo placement baseline for `licensed-win-1` without turning a licensed Windows solver host into a general-purpose repo-maintenance lane.

This issue is a planning/decision gate only. It does **not** authorize cloning, moving, deleting, syncing, or rewriting repositories on Windows.

---

## Resource Intel

### Issue intake

- Issue: [#2756](https://github.com/vamseeachanta/workspace-hub/issues/2756)
- Current labels at intake: `status:needs-plan`, `machine:licensed-win-1`, `priority:high`, `cat:operations`, `cat:ai-orchestration`, `domain:workstations`.
- Requested role: licensed Windows / solver-capable worker lane.

### Registry evidence

From `config/workstations/registry.yaml`:

- Machine key: `licensed-win-1`
- OS: `windows`
- Role: `simulation-license-host`
- Workspace root: `D:\workspace-hub`
- SSH: `null`
- Capabilities: `claude`, `codex`, `gemini`; `bash`; `orcaflex`, `ansys`, `git`
- Storage local: `D:\`
- Current repo list: `OGManufacturing`
- Telegram/Hermes: `dispatch_enabled: false`, `telegram_mode: desktop-status-only`, `sync_policy: manual-status-only`

### Ops docs evidence

From `docs/ops/2026-05-04-multimachine-baseline-inventory.md`:

- `licensed-win-1` is a licensed solver host.
- It should run OrcaWave/OrcaFlex/ANSYS through Windows Task Scheduler + Git-backed queue after bootstrap.
- Windows solver workspace is `D:\workspace-hub`; Linux should not mount/mutate Windows solver workspaces.

From `docs/ops/telegram-hermes-multimachine-control-plane.md`:

- Windows machines are desktop/status-only for MVP.
- No unattended dispatch to Windows until a separate approved plan proves Windows Hermes/gateway parity, approval posture, and safe job execution.

---

## Recommended Decision

### Required local repo baseline

| Repo | Required on `licensed-win-1`? | Role | Rationale |
|---|---:|---|---|
| `workspace-hub` | Yes | queue/control harness checkout | Required for Git-backed solver queues, readiness evidence, scripts, registry, and issue-linked artifacts. |
| `digitalmodel` | Yes, before solver job execution | solver/model execution repo | Primary source of OrcaWave/OrcaFlex workflows, specs, fixtures, reports, and solver integration code. |
| `assetutilities` | Yes, if `digitalmodel` tests/scripts import it locally | support dependency | Shared utilities used by `digitalmodel`; should be present only if local editable dependency is required. |
| `worldenergydata` | No by default | not a solver host baseline | Data pipelines belong on Linux/data lanes; Windows should consume prepared solver inputs via Git/artifacts. |
| `llm-wiki` | No by default | not a solver host baseline | Reference/wiki maintenance is not a licensed Windows lane responsibility. |
| `assethold` | No by default | confidential/on-demand | Only if a solver job explicitly needs approved private inputs. |
| `aceengineer-website` | No | GTM/web lane | Not solver-host work. |
| `aceengineer-strategy` | No | GTM/prospect lane | Not solver-host work. |

### Lane posture

`licensed-win-1` should be a **manual/status-only licensed solver lane** until Windows dispatch parity is separately approved.

Allowed before approval:

- Read-only inventory of repo presence, solver availability, and Task Scheduler readiness.
- Manual evidence capture from Telegram Desktop / Hermes status / Git Bash.
- Plan/review of a Git-backed solver queue contract.

Blocked before approval:

- Unattended Telegram/Hermes dispatch.
- Repo clone/move/delete/sync operations.
- Solver execution against unstaged/unapproved models.
- Treating `OGManufacturing` as a tier-1 placement substitute.

---

## Implementation Scope After Approval

1. Add `tier1_baseline` for `licensed-win-1` to `config/workstations/registry.yaml`.
2. Add a read-only Windows evidence schema for:
   - repo checkout presence at exact Windows paths,
   - solver executable/license checks,
   - Git Bash/non-interactive command path,
   - Task Scheduler queue readiness,
   - provider/Hermes/gh auth state if any agent lane is proposed.
3. Integrate `licensed-win-1` into readiness output as `status_only=true`, `unattended_dispatchable=false` until a later approved Windows dispatch plan changes it.
4. Create follow-on issues for missing repo checkouts or solver queue bootstrap. Do not perform setup inline.

---

## TDD Plan

| Test | Purpose | Fixture | Expected behavior |
|---|---|---|---|
| `test_licensed_win_1_required_repos_minimal_solver_baseline` | Preserve narrow repo scope. | Baseline includes `workspace-hub`, `digitalmodel`; optional `assetutilities`; excludes data/GTM repos. | Pass only for solver-focused baseline. |
| `test_windows_status_only_blocks_unattended_dispatch` | Enforce current MVP control-plane policy. | Registry has `dispatch_enabled=false`, `telegram_mode=desktop-status-only`. | Readiness reports `unattended_dispatchable=false`. |
| `test_windows_workspace_paths_are_exact_and_not_linux_mounts` | Prevent Linux path bleed-through. | Windows paths use `D:\...`; Linux `/mnt/...` appears. | Linux paths rejected for Windows repo placement. |
| `test_solver_lane_requires_task_scheduler_and_license_evidence` | Prevent fake solver readiness. | Missing Task Scheduler queue or missing Orca/ANSYS license check. | Solver job dispatch blocked; status-only evidence still recorded. |
| `test_ogmanufacturing_not_tier1_substitute` | Avoid registry drift. | Registry currently lists `OGManufacturing`. | It may remain as existing repo but cannot satisfy tier-1 baseline. |
| `test_windows_setup_actions_are_follow_on_issues_only` | Keep plan non-mutating. | Missing `digitalmodel` checkout. | Plan creates/links setup issue; does not clone/sync. |

---

## Acceptance Criteria

- [ ] `licensed-win-1` tier-1 baseline is explicit and solver-focused.
- [ ] `workspace-hub` and `digitalmodel` are required before solver queue execution; `assetutilities` is dependency-gated.
- [ ] `worldenergydata`, `llm-wiki`, `aceengineer-website`, and `aceengineer-strategy` are excluded from the default Windows solver host baseline unless a later approved plan justifies them.
- [ ] `licensed-win-1` remains status-only / manual until Windows dispatch parity is separately approved.
- [ ] Readiness evidence distinguishes repo presence, solver/license availability, Task Scheduler readiness, provider/auth state, and dispatch authorization.
- [ ] No clone/move/delete/sync operation is authorized before explicit USER approval and TDD implementation.

---

## Risks and Open Questions

- **Risk:** Current registry lists `OGManufacturing`, not tier-1 repos. Treat it as existing non-tier-1 state, not a substitute for `workspace-hub`/`digitalmodel`.
- **Risk:** No SSH or remote command path is registered. Live evidence likely requires manual/desktop capture unless another approved access path exists.
- **Open question:** whether `assetutilities` must be a local editable checkout on Windows or can be installed as a dependency for solver jobs.
- **Open question:** exact Windows Task Scheduler queue directory and artifact handoff format.

---

## Explicit Non-Goals

- Do not implement Windows unattended dispatch in this issue.
- Do not move repos between Linux and Windows.
- Do not run solver jobs.
- Do not treat licensed Windows hosts as general planning/review/data-processing machines.
