# Plan for #2755: throughput(workstations): activate ace-linux-2 provider/machine lane

> **Status:** plan-review — adversarial review complete; awaiting USER approval before `status:plan-approved` and implementation
> **Complexity:** T2
> **Date:** 2026-05-20
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2755
> **Review artifacts:** scripts/review/results/2026-05-20-plan-2755-claude-r1.md | scripts/review/results/2026-05-20-plan-2755-codex-r1.md | scripts/review/results/2026-05-20-plan-2755-gemini-r1.md | scripts/review/results/2026-05-20-plan-2755-claude-r2.md | scripts/review/results/2026-05-20-plan-2755-codex-r2.md | scripts/review/results/2026-05-20-plan-2755-gemini-r2.md | scripts/review/results/2026-05-20-plan-2755-claude-r3.md | scripts/review/results/2026-05-20-plan-2755-codex-r3.md | scripts/review/results/2026-05-20-plan-2755-gemini-r3.md

---

## Resource Intel

Live probes from `ace-linux-1` to `ace-linux-2` on 2026-05-20:

```text
hostname: ace-linux-2
/mnt/local-analysis: 932G total, 878G free
/mnt/dde: 2.8T total, 848G free
/mnt/remote/ace-linux-1/ace: mounted NFS view of ace-linux-1:/mnt/ace, 529G free
local tier-1 repos found: workspace-hub only at /mnt/local-analysis/workspace-hub
missing local tier-1 repos from probe: digitalmodel, assetutilities, worldenergydata, llm-wiki, assethold, aceengineer-website, aceengineer-strategy
tools found: gh, git, uv, tmux
tools not found in PATH from non-interactive SSH probe: claude, codex, gemini, hermes
```

Repo/context sources consulted:
- `config/workstations/registry.yaml`: `dev-secondary` / `ace-linux-2` has role `secondary-dev`, local storage `/mnt/dde`, workspace root `/mnt/local-analysis/workspace-hub`, declared repos `digitalmodel` and `worldenergydata`, and worker-mode Telegram/Hermes dispatch settings.
- `docs/ops/2026-05-04-multimachine-baseline-inventory.md`: ace-linux-2 is secondary dev / overflow AI worker / open-source simulation worker; should not be treated as licensed Orca/ANSYS solver host; minimum readiness calls for `workspace-hub`, `digitalmodel`, `assetutilities`, and `worldenergydata` local clones plus auth/config parity.
- `docs/ops/telegram-hermes-multimachine-control-plane.md`: `dev-secondary` is worker dispatchable after readiness; Windows machines remain status-only until separate approval.

---

## Decision

Use **ace-linux-2** as a **secondary Linux worker lane** for:

1. OSS simulation/preprocessing/post-processing work: OpenFOAM, FreeCAD, Gmsh, ParaView, CalculiX, mesh and visualization tasks.
2. Overflow implementation/test/debug work for Linux-compatible tier-1 repos after provider/runtime parity is proven.
3. Data-adjacent preprocessing that reads scoped `/mnt/remote/ace-linux-1/ace` inputs but writes derived working artifacts to local `/mnt/dde` or repo-approved outputs.

Do **not** use ace-linux-2 as:
- primary control plane;
- licensed OrcaFlex/OrcaWave/ANSYS solver host;
- canonical raw-data store;
- unrestricted mirror of all tier-1 repos;
- dispatch target before missing repo/runtime readiness is fixed.

---

## Tier-1 Repo Placement Baseline

### Required local repos before worker dispatch

| Repo | Required local path policy | Role | Rationale |
|---|---|---|---|
| `workspace-hub` | `/mnt/local-analysis/workspace-hub` | control/dispatch harness | Already present; canonical scripts, plans, registry, issue workflow. |
| `digitalmodel` | `/mnt/local-analysis/digitalmodel` unless a later approved registry schema adds exact per-repo allowed paths | primary worker repo | Engineering simulation workflows and OSS solver integration. |
| `assetutilities` | `/mnt/local-analysis/assetutilities` unless a later approved registry schema adds exact per-repo allowed paths | primary support repo | Shared utilities required by `digitalmodel` and data/report tooling. |
| `worldenergydata` | `/mnt/local-analysis/worldenergydata` unless a later approved registry schema adds exact per-repo allowed paths; `/mnt/remote/ace-linux-1/ace` is data-read input, not repo placement | primary data/energy worker repo | Data pipelines and preprocessing; must not confuse raw data NFS access with repo checkout. |
| `llm-wiki` | optional-to-required for planning/review lanes; required before local wiki maintenance dispatch | reference/knowledge repo | Useful for local planning/research; can be deferred if ace-linux-2 first role is solver preprocessing only. |

### Optional/on-demand repos

| Repo | Policy |
|---|---|
| `assethold` | Only clone/activate if finance/data tasks are routed to ace-linux-2. |
| `aceengineer-website` | Only clone/activate for website build/test overflow. |
| `aceengineer-strategy` | Avoid by default unless GTM strategy work is explicitly routed and data handling is approved. |

No clone, move, delete, sync rewrite, or path normalization is authorized by this plan until the user approves it and a TDD implementation issue/commit executes the changes.

---

## Implementation Scope After Approval

1. Extend `config/workstations/registry.yaml` for `dev-secondary` with an explicit `tier1_baseline` block.
2. Add/extend a read-only checker so `ace-linux-2` required and optional repo placement can be validated without mutating filesystems.
3. Add storage/path authority reconciliation across `workspace_root`, `dirname(workspace_root)`, `storage.local`, and `telegram_hermes.data_access_profile.storage_roots`; fail closed unless policy explicitly classifies repo roots versus data/cache roots.
4. Integrate ace-linux-2 repo/runtime readiness into the existing Telegram/Hermes readiness output, including the coordinator-side `scripts/readiness/telegram-hermes-readiness.sh --evidence-dir` path.
5. Record provider/runtime/auth gaps as `host_dispatchable=false` blockers for the selected lane, not merely provider-level warnings or silent fallback assumptions. Unknown, expired, or unverified auth state is blocked.
6. Create or link follow-on setup issues for missing local repos and missing provider CLIs/auth; do not perform those operations inline unless explicitly approved.

---

## Pseudocode

```text
function load_dev_secondary_baseline(registry):
    machine = registry.machines.dev-secondary
    require machine.hostname == "ace-linux-2"
    require machine.role == "secondary-dev"
    require storage.local and workspace_root are explicit
    require tier1_baseline classifies required, optional, and deferred repos
    reconcile tier1_baseline with existing repos and telegram_hermes.data_access_profile.repos

function reconcile_storage_path_authority(machine):
    classify workspace_root and dirname(workspace_root) as repo workspace roots
    classify storage.local as heavy local data/cache/derived-output root unless explicitly promoted for repo placement
    classify telegram_hermes.data_access_profile.storage_roots as data-access roots, not automatic repo-placement roots
    fail closed if required repo paths sit outside classified repo roots or if data/cache roots are used as repo roots without an approved schema projection

function discover_ace_linux_2_repos(machine):
    candidate_roots = registry-declared repo workspace roots only:
        dirname(workspace_root), workspace_root, and exact per-repo roots from approved schema projections
    explicitly treat /mnt/remote/ace-linux-1/ace as data input, not repo-checkout satisfaction
    for each required repo:
        pass only if exact discovered path matches registry-declared expected path
        do not accept invented alternatives such as /mnt/dde/repos/<repo> unless a later approved registry schema declares exact allowed paths
        fail if absent, remote-only, duplicate-ambiguous, dirty when dispatch requires clean, ahead/behind, or wrong remote

function collect_provider_runtime_readiness():
    probe non-interactive PATH and configured shell/profile PATH separately
    record declared capability separately from observed executable/auth status
    record found/missing: claude, codex, gemini, hermes, gh, git, uv, tmux
    record auth_state for gh/hermes/provider CLIs as valid, invalid, expired, missing, or unknown
    observed executable and auth status wins over declared registry capability for dispatch decisions
    set host_dispatchable=false if hermes, required provider CLI, required auth, or non-interactive PATH evidence is missing/invalid/expired/unknown for the selected lane

function decide_first_dispatch():
    if repo baseline and runtime gate pass:
        route a small approved Linux worker task to ace-linux-2
    else:
        leave #2755 open with exact missing repos/tools/auth as blockers
```

---

## TDD Plan

| Test | Purpose | Fixture | Expected |
|---|---|---|---|
| `test_dev_secondary_baseline_required_repos` | Registry has explicit required/optional/deferred repo baseline for ace-linux-2. | Minimal `dev-secondary` fixture. | Required repos and roles match this plan. |
| `test_workspace_hub_only_is_not_dispatchable` | Current live-like state with only `workspace-hub` cannot dispatch worker jobs. | Discovery fixture finds only `/mnt/local-analysis/workspace-hub`. | `dispatchable=false`; missing repos named. |
| `test_remote_ace_mount_not_repo_checkout` | NFS `/mnt/remote/ace-linux-1/ace` cannot satisfy required repo placement. | Repo-like names appear only under remote mount. | Failure says remote data mount is not local checkout. |
| `test_required_repo_arbitrary_local_root_fails` | Arbitrary local extra roots cannot satisfy required repos. | `digitalmodel` appears under undeclared `/mnt/dde/tmp/digitalmodel`. | Failure until exact path is registry-declared. |
| `test_duplicate_checkout_requires_primary_reference` | Duplicate checkouts require explicit primary/reference classification. | Two local `digitalmodel` paths. | Failure lists both paths unless registry declares roles. |
| `test_runtime_probe_missing_provider_clis_blocks_host_dispatch` | Missing `claude`, `codex`, `gemini`, or `hermes` in non-interactive path becomes explicit host-level blocker for any lane requiring those runtimes. | Probe fixture lacks those commands. | `host_dispatchable=false`; `gh/git/uv/tmux` still recorded. |
| `test_binary_present_auth_absent_or_expired_blocks_host_dispatch` | CLI presence alone is insufficient for dispatch. | `gh`, provider, and Hermes binaries exist but auth check returns missing, expired, invalid, or unknown. | `host_dispatchable=false`; readiness names exact auth blocker. |
| `test_open_source_solver_lane_allowed_without_licensed_solver` | OSS solver lane can be valid without Orca/ANSYS licensing. | FreeCAD/Gmsh/OpenFOAM present; licensed solver absent. | Linux OSS lane allowed; licensed solver lane blocked. |
| `test_live_probe_fixture_matches_2026_05_20_findings` | Live SSH findings are captured as evidence, not replaced by hardcoded assumptions. | Fixture records hostname, timestamp, local repos, NFS mount classification, and non-interactive PATH results from the 2026-05-20 probe. | Only `workspace-hub` is local; remote `/mnt/remote/ace-linux-1/ace` is data input; missing CLIs are blockers. |
| `test_registry_repo_lists_reconcile_dev_secondary` | `tier1_baseline`, `machines.dev-secondary.repos`, and `telegram_hermes.data_access_profile.repos` cannot drift. | Registry lists only `digitalmodel`/`worldenergydata` while baseline requires `workspace-hub`/`assetutilities`. | Failure names mismatched authorities until registry projection/classification is explicit. |
| `test_storage_path_authority_reconcile_or_fail_closed` | Repo roots and data/cache roots cannot be conflated. | `workspace_root=/mnt/local-analysis/workspace-hub`, `storage.local=/mnt/dde`, `storage_roots=[/mnt/dde]`, required repo paths under `/mnt/local-analysis`. | Pass only with explicit classification: `/mnt/local-analysis` is repo workspace root, `/mnt/dde` is data/cache/derived-output root; otherwise fail closed. |
| `test_checker_readonly_no_mutation` | Checker must not clone/move/delete/sync. | Monkeypatched filesystem/subprocess dangerous calls. | Only read-only probes occur. |
| `test_readiness_reports_ace_linux_2_blockers` | Readiness output includes repo and runtime blockers. | Stub checker failures. | JSON/text readiness names exact blockers and `host_dispatchable=false`. |
| `test_coordinator_evidence_dir_blocks_stale_or_missing_worker_evidence` | Coordinator-side readiness cannot dispatch from stale/missing ace-linux-2 host-local evidence. | `scripts/readiness/telegram-hermes-readiness.sh --evidence-dir` fixture missing or stale for dev-secondary. | Dispatch fails closed and names missing/stale evidence. |

---

## Acceptance Criteria

- [ ] ace-linux-2 role is recorded as secondary Linux worker lane, not control plane or licensed solver host.
- [ ] Required local repo baseline is explicit for `workspace-hub`, `digitalmodel`, `assetutilities`, and `worldenergydata`; `llm-wiki` is classified as required for planning/wiki lanes or explicitly deferred for solver-preprocess-only lane.
- [ ] `/mnt/remote/ace-linux-1/ace` is treated as raw/knowledge data input only, never as repo placement satisfaction.
- [ ] Missing local repos from live probe are recorded as blockers or follow-on setup issues before dispatch.
- [ ] Missing non-interactive provider/runtime commands (`claude`, `codex`, `gemini`, `hermes`) are recorded as `host_dispatchable=false` blockers or profile/PATH issues before any selected-lane dispatch that depends on them.
- [ ] Missing, expired, invalid, or unknown auth evidence for required provider/Hermes/gh paths blocks host dispatch even when binaries exist.
- [ ] Open-source solver/preprocessing capabilities are separated from licensed Windows solver capabilities.
- [ ] Read-only checker and readiness integration fail closed and do not mutate filesystem or git state.
- [ ] Registry reconciliation fails closed if `tier1_baseline`, `machines.dev-secondary.repos`, and `telegram_hermes.data_access_profile.repos` disagree without explicit projection/classification.
- [ ] Storage/path authority reconciliation fails closed unless `workspace_root`, `dirname(workspace_root)`, `storage.local`, and `telegram_hermes.data_access_profile.storage_roots` are explicitly classified as repo workspace roots versus data/cache/derived-output roots.
- [ ] Coordinator-side readiness consumes host-local ace-linux-2 evidence via `scripts/readiness/telegram-hermes-readiness.sh --evidence-dir`; stale or missing evidence blocks dispatch.
- [ ] First dispatch after approval produces a concrete artifact, issue comment, test result, review, or PR-ready change; otherwise #2755 remains open with exact blockers.
- [ ] No repo is moved, cloned, deleted, renamed, or sync-rewritten by this issue before explicit user approval and TDD implementation.

---

---

## Adversarial Review Summary

| Reviewer | Verdict | Notes |
|---|---|---|
| Claude r1 | MINOR | Requested registry-list reconciliation and coordinator evidence-dir stale/missing evidence gates; both added. |
| Codex r1 | MAJOR | Found runtime blockers too narrow, unsupported `/mnt/dde/repos` path alternatives, missing live-probe fixture, and declared-vs-observed capability drift; all patched locally. |
| Gemini r1 | APPROVE | Approved; suggested interactive vs non-interactive PATH test, covered by runtime/live-probe tests. |
| Codex r2 | APPROVE | Confirmed r1 blockers resolved. |
| Gemini r2 | APPROVE | Confirmed r1 blockers resolved; suggested explicit stale evidence age during implementation. |
| Claude r2 | MAJOR | Found missing storage/path authority reconciliation and missing auth-state tests; both patched locally. |
| Codex r3 | APPROVE | Approved r2 fixes. |
| Gemini r3 | APPROVE | Approved r2 fixes; reiterated stale-evidence threshold should be concrete during implementation. |
| Claude r3 | MINOR | Requested adding `gh` to auth-state TDD fixture; patched inline. |

**Overall result:** MINOR resolved inline — ready for `status:plan-review`; USER approval still required before `status:plan-approved` and implementation.

---

## Risks and Open Questions

- **Risk:** Live probe found only `workspace-hub` locally. Treating ace-linux-2 as ready now would create dispatch churn.
- **Risk:** `claude`, `codex`, `gemini`, and `hermes` were missing from non-interactive SSH PATH. They may exist in interactive shells, but dispatch must use the actual non-interactive command path unless profile loading is explicitly fixed/tested.
- **Risk:** Registry currently declares only `digitalmodel` and `worldenergydata`; plan requires deciding whether `assetutilities` and `llm-wiki` are required for ace-linux-2's first lane.
- **Open:** Should `llm-wiki` be required before any planning/review dispatch to ace-linux-2, or deferred until after solver/preprocessing lane readiness?

---

## Complexity: T2

T2 because this is a bounded workstation readiness/registry/checker plan with live machine probes, TDD, and dispatch gates. It is not T3 because it does not redesign cross-machine architecture or perform repo moves.
