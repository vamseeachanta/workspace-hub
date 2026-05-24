# Claude plan-hardening memo — issue #2775

> Scope: resolve every MAJOR finding in `scripts/review/results/2026-05-21-plan-2775-disagreement.md` against the **live** repo state inspected 2026-05-21. Read-only analysis; no code/config writes outside this memo. Plan stays at `status:needs-plan` until the changes below land and a fresh adversarial wave clears.

---

## 1. Live-state corrections (things the plan or reviewers got wrong)

These are corrections to the *current plan text*, derived from reading the source files referenced in the disagreement report.

| # | Plan/reviewer claim | Live state | Correction needed |
|---|---|---|---|
| L1 | Plan implies `__TIER1_REPO_ROOT__` is a 1-line token add to `sync-agent-configs.sh`. | `scripts/_core/sync-agent-configs.sh:899-952` resolves `__WS_HUB_PATH__` from `harness-config.yaml`, **not** `registry.yaml`. There is no `--machine` flag; matching is by `socket.gethostname()`. There is no current resolver path that consults `registry.yaml` at all. | The plan is not adding a token. It is changing the **authoritative resolver source**. That is a structural change to one of three render paths (lines 73-105 `render_hermes_template`, lines 896-952 `resolve_ws_hub_path`, lines 954-1141 `sync_hermes_yaml_config`). Scope must reflect that. |
| L2 | Plan §SSoT Strategy §2 lists overlay candidates `CAD-DEVELOPMENTS, worldenergydata, achantas-data, assetutilities, digitalmodel`. | `registry.yaml.machines.dev-primary.repos` = `[worldenergydata, digitalmodel, assetutilities, assethold, workspace-hub, OGManufacturing]`. `CAD-DEVELOPMENTS` and `achantas-data` are **not** in the registry. `assethold` and `OGManufacturing` are in registry but not in the overlay list. | Overlay candidates are derived from the *stale template* the plan is fixing — circular. Either (a) define overlays as a registry-typed field per machine, or (b) drop the overlay list and treat every non-`workspace-hub` repo as a sibling resolved via `__TIER1_REPO_ROOT__/<repo>/.claude/skills`, with explicit on-disk check that the dir exists with ≥1 `SKILL.md`. |
| L3 | Plan asserts `registry.yaml` is authoritative for machine roots. | `registry.yaml.machines.dev-secondary` defines `workspace_root: /mnt/local-analysis/workspace-hub` and `storage.local: /mnt/dde`, but has **no `tier1_repo_root`** and **no `repo_layout`** fields. `harness-config.yaml.workstations.dev-secondary.ws_hub_path: /mnt/workspace-hub` is a *third* value. | Registry is not internally complete for dev-secondary. The plan's `test_registry_is_authoritative_for_machine_roots` would lock in whichever value the plan picks, with no host-side ground truth. Required: (a) capture ground truth from ace-linux-2 (host where dev-secondary lives) before declaring authoritative value; (b) add `tier1_repo_root` and `repo_layout` to dev-secondary; (c) only after that, fail-closed on harness-config divergence. |
| L4 | Plan TDD `test_provider_symlink_to_missing_parent_skills_fails` is keyed to realpath `/mnt/local-analysis/.claude/skills`. | Pseudocode line 275: `fail if realpath is /mnt/local-analysis/.claude/skills and target missing`. | Test the **property** (`symlink target does not exist`), not the specific stale value. A future drift to `/mnt/dde/.claude/skills` or `~/workspace-hub/.claude/skills` would silently pass under the current spec. |
| L5 | Plan iterates `registry.repos` and applies sibling rule `../../workspace-hub/.claude/skills`. | `workspace-hub/.codex/skills -> ../.claude/skills` — that is the **correct** target for workspace-hub itself, because it is its own parent. | The checker must branch on `repo == workspace-hub`. Sibling rule does not apply. |
| L6 | Plan `repair_dry_run` says "classify as `corrupted_ntfs_symlink` and propose delete+recreate **only in dry-run manifest**". | Gemini #6 caught: no `--apply` semantics. | Define `--apply` behavior explicitly: unlink the `IntxLNK` regular file and `ln -s` the canonical relative target, with post-write `file` + `readlink` verification. Refuse to repair when host fs is `ntfs3` per memory `feedback_ntfs3_symlink_intxlnk` — root-cause is the mount driver, not on-disk corruption. |
| L7 | Plan §Resource Intel calls `IntxLNK` files "corrupted NTFS symlink artifacts" with no cause. | `feedback_ntfs3_symlink_intxlnk` documents the cause: in-kernel `ntfs3` reads `ntfs-3g`-created symlinks as raw `IntxLNK` byte blobs. Today's host is ext4 (`/mnt/local-analysis`), but the files were created on a Windows/ntfs origin and copied across. | The plan must run `findmnt -no FSTYPE /mnt/local-analysis` at apply time, record it in the per-repair manifest, and refuse to repair on any `ntfs3` mount. |
| L8 | Plan does not mention CONTROL_PLANE_CONTRACT.md table at lines 67-72. | `docs/standards/CONTROL_PLANE_CONTRACT.md:67-72` declares all 4 starter repos "Fully converged" — but live state shows `.codex/skills`/`.gemini/skills` broken on `worldenergydata`/`assetutilities`/`assethold` and `IntxLNK`-corrupted on `digitalmodel`. The contract table lies. | The contract update is not optional ("if needed", as Files-to-Change line 308 hedges). The convergence table must be rewritten or replaced by a generated section sourced from `check-sibling-sso-flow.py --json`. List as required, not conditional. |
| L9 | `tests/harness/` does not exist. | Confirmed via `ls tests/` — no `harness/` subdir; 40+ peer subdirs exist. `pyproject.toml` has `testpaths = ["tests"]` with `python_files = ["test_*.py"]`, so a new subdir *would* be discovered. | Discovery is not at risk, but convention-break is real. Move tests to `tests/readiness/` (the natural home — `scripts/readiness/` owns the checker). Eliminates a new subdir for free. |
| L10 | Plan's first-round Codex finding "Plan/index not on remote `main` during review" is unaddressed. | Plan §Adversarial Review Summary line 363 cites the finding; "Revisions made" lines 368-373 do not address it. Memory: `feedback_codex_needs_pushed_artifact`, `feedback_reviewer_dispatch_refetch_live_body`. | Add explicit pre-review-dispatch step: commit + push plan file + add to `docs/plans/README.md` index before any provider invocation. This is operational, not a plan-body fix, but the plan must state it. |
| L11 | Gemini claims `config/workstations/registry.yaml`, `scripts/readiness/harness-config.yaml`, `config/agents/hermes/config.yaml.template`, `scripts/_core/sync-agent-configs.sh`, `scripts/memory/check-memory-drift.sh` do not exist at HEAD. | All five files exist at HEAD on this checkout. | This is a Gemini sandbox/overlay artifact per memory `feedback_gemini_sandbox_overlay_blindness`. The plan does not need to be revised for this — but the next dispatch must add the `Pre-review evidence stamp` documented in that memory: include `git ls-files <path>` output for each cited path inline in the plan, so a sandboxed reviewer can verify presence without filesystem access. |

---

## 2. Per-finding resolution table

Each row maps a reviewer MAJOR to the exact plan change required.

### Claude reviewer (10 findings)

| # | Finding (compressed) | Resolution in revised plan |
|---|---|---|
| C1 | Local-marker approval reintroduces defect class. | **Remove the local-marker requirement entirely.** Approval gate = live GitHub `status:plan-approved` only, queried at apply-time via `gh issue view 2775 --json labels`. Drop pseudocode line 286, drop TDD `test_repair_apply_requires_live_label_and_approval_marker`, replace with `test_repair_apply_blocked_when_live_label_missing` and `test_repair_apply_ignores_local_marker_when_present`. Cite `feedback_dispatch_local_marker_rationalization` explicitly. |
| C2 | Overlay candidate list is sourced from the artifact being fixed. | Per L2: either define overlays as a typed registry field (`registry.machines.<m>.skill_overlays: [...]`) with explicit on-disk validation, or eliminate the overlay concept and resolve every non-`workspace-hub` repo via `__TIER1_REPO_ROOT__/<repo>/.claude/skills`. Recommended: eliminate. The current overlay list is empty in practice — none of the cited repos has a populated `.claude/skills` outside workspace-hub (re-verify before lock-in). |
| C3 | Registry self-consistency unverified for dev-secondary. | Per L3: add a ground-truth capture step on ace-linux-2 BEFORE any registry mutation. Add `tier1_repo_root` and `repo_layout` to dev-secondary entry. Add TDD `test_registry_machine_fields_complete_for_sibling_machines` that fails when `repo_layout: sibling` is declared without `tier1_repo_root`. |
| C4 | `tests/harness/` is a net-new convention. | Per L9: move all three test files to `tests/readiness/`. No new subdir. No conftest change. |
| C5 | Shell wrapper "optional" but acceptance criterion requires it. | Drop "optional" from Artifact Map line 205. Mark required in Files-to-Change. Either delete the `.sh` wrapper from acceptance criterion and call the Python directly, or commit to the shell wrapper as required. Recommend the shell wrapper stays required (humans/cron expect a stable path). |
| C6 | Symlink failure test is path-narrow not class-broad. | Per L4. Rewrite `test_provider_symlink_to_missing_parent_skills_fails` to assert the *property* `symlink target nonexistent OR outside allow-set`. Add a parametrized fixture covering 3 distinct stale realpaths. |
| C7 | `OGManufacturing` (registry-listed but absent on disk) has no `not_present` test. | Add TDD `test_registry_repo_absent_on_disk_reports_not_present`. Fixture: registry lists a repo; sibling root has no checkout. Expected: checker emits `status: not_present` (not `fail`), unless `required_on_host: true` (a new field). |
| C8 | `sync-agent-configs.sh --dry-run` delta is unsized. | Per L1. Plan must enumerate the resolver-source change, the `__TIER1_REPO_ROOT__` render path, the `--machine` flag addition, the post-render unresolved-token scan, and the post-render stale-nested-path scan. Each as a discrete deliverable. |
| C9 | `workspace-hub`-self symlink not covered. | Per L5. Add TDD `test_workspace_hub_self_skill_symlink_pass`. Checker must special-case `repo == workspace-hub` and expect `<repo>/.codex/skills -> ../.claude/skills`. |
| C10 | No reproduction proof for IntxLNK cause; no post-repair guard. | Per L6 + L7. Add cause-statement in §Resource Intel citing `feedback_ntfs3_symlink_intxlnk`. Add TDD `test_repair_refuses_when_fs_is_ntfs3` and `test_repair_post_write_verifies_symbolic_link`. |

(Claude #11 — "first-review Codex push finding unaddressed" — see L10.)
(Claude #12 — "no test for `__TIER1_REPO_ROOT__` resolution failure" — add TDD `test_sync_fails_closed_on_missing_tier1_repo_root_for_template_token`.)

### Codex reviewer (5 findings)

| # | Finding | Resolution |
|---|---|---|
| K1 | Plan not retrievable at `main`. | Per L10. Commit and push the plan file + `docs/plans/README.md` index row before next adversarial dispatch. Verify with `gh api repos/vamseeachanta/workspace-hub/contents/docs/plans/2026-05-21-issue-2775-workspace-hub-sibling-sso-flow.md?ref=main`. |
| K2 | Repo scope inconsistent; CAD-DEVELOPMENTS/achantas-data not in registry. | Per L2 / C2. Eliminate overlay list; derive scope from `registry.machines.<m>.repos` only. |
| K3 | `load_registry` requires `tier1_repo_root` and `repo_layout=sibling`, but dev-secondary has neither. | Per L3 / C3. Required plan delta: registry migration for every machine validated, not just a divergence test. List the exact field additions per machine in Files-to-Change. |
| K4 | Sync-script integration underspecified; current resolver reads harness-config not registry. | Per L1 / C8. Explicit deliverable: replace `resolve_ws_hub_path()` with `resolve_machine_roots(machine)` that reads registry first, validates harness-config matches OR is absent, returns `(workspace_root, tier1_repo_root, repo_layout)`. Add `--machine` flag. Acceptance criterion must require the new flag in the dry-run invocation. |
| K5 | Cross-repo source-control strategy too vague. | See §5 below for the exact strategy. Plan §Risks must be replaced by a concrete `Cross-repo write safety contract` section listing each preflight check and each post-write artifact. |

### Gemini reviewer (6 findings)

| # | Finding | Resolution |
|---|---|---|
| G1 | Cited files do not exist at HEAD. | Per L11. Sandbox artifact; no plan-body change, but plan must embed `git ls-files` output for each cited path. |
| G2 | Same for sync script and memory-drift script. | Same as G1. |
| G3 | `test_rejects_missing_external_skill_root` uses nested path that contradicts other test. | Rewrite fixture to use sibling path `/mnt/local-analysis/<repo>/.claude/skills` (where repo is sibling-resolved). Drop the nested-path fixture from this test; that case is covered by `test_detects_nested_workspace_hub_skill_paths`. |
| G4 | No implementation logic specified for live label query. | Pseudocode must contain the literal command form: `gh issue view 2775 --json labels --jq '.labels[].name' \| grep -Fx status:plan-approved`. Plus error semantics: network failure → fail closed (treat as unapproved). Plus auth scope: requires `gh auth status` to succeed. |
| G5 | Dirty-repo check missing from `repair_dry_run` pseudocode. | See §5. Add explicit `git -C <repo> status --porcelain` preflight; non-empty output → refuse apply for that repo; record in manifest. |
| G6 | IntxLNK `--apply` behavior unspecified. | Per L6 / C10. Spell out unlink + ln -s + verification, with mount-fs guard. |

---

## 3. Revised approval-gate semantics (exact)

Replace plan §Pseudocode `repair_dry_run` clause about approval with:

```text
function require_user_approval(issue_number):
    # Live GitHub label is the only gate. Local markers are NOT consulted.
    # Per memory feedback_dispatch_local_marker_rationalization: forbid markers
    # AND label as a pair. A dispatch lane can synthesize the marker; the live
    # label requires the user.
    cmd = ["gh", "issue", "view", str(issue_number), "--json", "labels",
           "--jq", '.labels[].name']
    try:
        labels = run_with_timeout(cmd, timeout_sec=15).splitlines()
    except (subprocess.TimeoutExpired, subprocess.CalledProcessError, OSError):
        raise ApprovalUnavailableError(
            "could not query live label; refusing --apply (fail closed)")
    if "status:plan-approved" not in labels:
        raise ApprovalMissingError(
            f"issue #{issue_number} not labelled status:plan-approved")
    return True

function repair_apply(plan_state, issue_number):
    require_user_approval(issue_number)
    # explicit: do NOT read .planning/plan-approved/<n>.md
    # explicit: do NOT write any marker before, during, or after apply
    ...
```

Acceptance criterion text replacement:

- OLD (line 350): "Dry-run repair manifest is reviewed before any cross-repo write, and `--apply` refuses to run unless both live GitHub `status:plan-approved` and `.planning/plan-approved/2775.md` exist."
- NEW: "Dry-run repair manifest is reviewed before any cross-repo write. `--apply` queries the live `status:plan-approved` label via `gh issue view`. Local approval markers are explicitly not consulted; the apply script must not read `.planning/plan-approved/`. Fail-closed semantics: any `gh` failure (network, auth, parse) blocks apply with a named error."

TDD test list updates:
- DELETE: `test_repair_apply_requires_live_label_and_approval_marker`
- ADD: `test_repair_apply_blocked_when_live_label_missing` (mock `gh` returning labels without `status:plan-approved` → nonzero exit, no writes)
- ADD: `test_repair_apply_ignores_local_marker_when_label_missing` (fixture creates `.planning/plan-approved/2775.md` AND `gh` returns no label → still blocked)
- ADD: `test_repair_apply_fails_closed_on_gh_error` (mock `gh` exit nonzero or timeout → blocked, no writes)

---

## 4. Revised TDD test list (final)

Final list, all under `tests/readiness/` (not `tests/harness/`). Each name unambiguously names the property under test.

| # | Test | Property | Location |
|---|---|---|---|
| 1 | `test_memory_bridge_drift_check_green` | `scripts/memory/check-memory-drift.sh` exit 0 + no drift. | `tests/readiness/test_sibling_sso_topology.py` |
| 2 | `test_hermes_template_rejects_nested_repo_skill_paths` | Template contains no `__WS_HUB_PATH__/<repo>/.claude/skills` for `<repo>` ≠ workspace-hub. | `tests/readiness/test_hermes_config_sibling_paths.py` |
| 3 | `test_hermes_template_accepts_central_workspace_hub_root` | `__WS_HUB_PATH__/.claude/skills` resolves to dir with ≥1 `SKILL.md`. | same |
| 4 | `test_registry_machine_fields_complete_for_sibling_machines` | Any `repo_layout: sibling` machine has non-empty `tier1_repo_root` and `workspace_root`. | `tests/readiness/test_registry_sso_completeness.py` |
| 5 | `test_registry_authoritative_for_machine_roots` | `harness-config.yaml.workstations.<m>.ws_hub_path` either matches `registry.machines.<m>.workspace_root` or is absent. Fails on dev-secondary today (`/mnt/workspace-hub` vs `/mnt/local-analysis/workspace-hub`). | same |
| 6 | `test_intxlnk_classified_as_corrupted_symlink` | Regular file beginning with bytes `49 6e 74 78 4c 4e 4b` reports `kind=corrupted_ntfs_symlink`. | `tests/readiness/test_sibling_sso_topology.py` |
| 7 | `test_provider_symlink_broken_target_fails` (property-broad) | Symlink whose target does not exist OR is outside `{workspace_root/.claude/skills} ∪ registered_overlays` → fail. Parametrize across 3 stale-target fixtures. | same |
| 8 | `test_provider_symlink_canonical_target_passes` | `<repo>/.codex/skills -> ../../workspace-hub/.claude/skills` resolves to real dir. | same |
| 9 | `test_workspace_hub_self_skill_symlink_pass` | `workspace-hub/.codex/skills -> ../.claude/skills` (special case). | same |
| 10 | `test_agents_pointer_to_missing_parent_fails` | `Contract: ../AGENTS.md` fails when `tier1_repo_root/AGENTS.md` is missing. | `tests/readiness/test_sibling_agents_contract.py` |
| 11 | `test_agents_pointer_to_workspace_hub_passes` | `Contract: ../workspace-hub/AGENTS.md` + target exists → pass. | same |
| 12 | `test_registry_repo_absent_on_disk_reports_not_present` | Registry lists repo; sibling root has no checkout → `status: not_present`, not `fail`. | `tests/readiness/test_sibling_sso_topology.py` |
| 13 | `test_repair_dry_run_outputs_manifest_no_writes` | `repair-sibling-sso-flow.py --dry-run` mutates nothing. | `tests/readiness/test_sibling_sso_repair_dry_run.py` |
| 14 | `test_repair_apply_blocked_when_live_label_missing` | `gh` returns no `status:plan-approved` → block apply. | same |
| 15 | `test_repair_apply_ignores_local_marker_when_label_missing` | Marker file present + no live label → still blocked. | same |
| 16 | `test_repair_apply_fails_closed_on_gh_error` | `gh` nonzero/timeout → blocked. | same |
| 17 | `test_repair_refuses_when_fs_is_ntfs3` | `findmnt -no FSTYPE` returns `ntfs3` → refuse repair with mount-fs guidance. | same |
| 18 | `test_repair_post_write_verifies_symbolic_link` | After unlink + ln -s, `file` returns `symbolic link` and `readlink` equals expected target. | same |
| 19 | `test_repair_dirty_repo_blocks_apply` | `git status --porcelain` non-empty for target repo → refuse with named files. | same |
| 20 | `test_repair_detached_head_blocks_apply` | Detached HEAD → refuse; suggest branch creation. | same |
| 21 | `test_sync_dry_run_resolves_tier1_repo_root_token` | `sync-agent-configs.sh --machine dev-primary --dry-run` produces rendered output with no `__TIER1_REPO_ROOT__` token remaining. | `tests/readiness/test_sync_agent_configs_sso.py` |
| 22 | `test_sync_fails_closed_on_missing_tier1_repo_root_for_template_token` | Registry entry missing `tier1_repo_root` + template uses `__TIER1_REPO_ROOT__` → nonzero exit with named machine. | same |
| 23 | `test_sync_fails_closed_on_unresolved_render_token` | Any remaining `__[A-Z_]+__` post-render → nonzero exit naming the token. | same |
| 24 | `test_sync_fails_closed_on_registry_harness_root_divergence` | `registry.machines.<m>.workspace_root` ≠ `harness-config.workstations.<m>.ws_hub_path` (and both defined) → nonzero exit naming both files and values. | same |
| 25 | `test_checker_json_report_has_four_flow_statuses` | `check-sibling-sso-flow.py --json` emits `{memory, skills, harness_contracts, registry}` with per-key pass/fail/not_present + evidence_paths. | `tests/readiness/test_sibling_sso_topology.py` |

Existing tests count goes from 14 → 25; subdirectory count goes from +1 (new) → 0 (reuses `tests/readiness/`).

---

## 5. Cross-repo source-control strategy (exact)

Replace plan §Risks bullet 2 ("Fixing provider symlinks across sibling repos can dirty multiple repos. Mitigation: dry-run manifest first, ...") with a discrete contract section.

### Pre-apply preflight per sibling repo

For every `<repo>` in `registry.machines.<m>.repos` selected for repair, capture **before** any write:

```bash
# Recorded to .planning/active/2775/sibling-state/<repo>.json
git -C <repo> remote get-url origin
git -C <repo> symbolic-ref --short HEAD                  # branch or fail if detached
git -C <repo> rev-list --left-right --count "@{u}"...HEAD  # ahead/behind
git -C <repo> status --porcelain                         # tracked dirty
git -C <repo> ls-files --others --exclude-standard       # untracked
git -C <repo> worktree list                              # nested worktrees
findmnt -no FSTYPE "$(realpath <repo>)"                  # mount fs type
```

### Hard blocks (refuse `--apply` for that repo)

1. `git status --porcelain` non-empty (tracked dirty) → block.
2. Untracked files inside the paths the repair touches (`.codex/skills`, `.gemini/skills`, `AGENTS.md`) → block.
3. Detached HEAD → block.
4. `ahead > 0` on current branch → block (don't pile on unpushed work).
5. Mount fs type is `ntfs3` → block (per L7).
6. Repo has nested `.git/worktrees` listing a worktree under the touched paths → block.
7. `gh issue view 2775 --json labels` does not contain `status:plan-approved` → block (per §3).

### Per-repair branch and commit policy

- For every sibling repo that passes preflight, the apply step creates branch `harness/2775-sibling-sso-flow` (idempotent — checkout if exists).
- One commit per touched file, conventional-commit form, body references `vamseeachanta/workspace-hub#2775`. No squash, no bulk commit.
- **No automatic push.** The apply step writes `.planning/active/2775/pending-push.txt` listing `<repo> <branch> <commit-shas>` for human review.
- Each per-repo state file (`.planning/active/2775/sibling-state/<repo>.json`) is updated post-write with the new HEAD sha and `before/after` diff stats.

### Post-apply per-repo verification

For each touched repo, post-write:

```bash
file <touched-symlink>           # must be "symbolic link"
readlink <touched-symlink>       # must equal expected target
ls -L <touched-symlink>/SKILL.md # must exist (proves target dir is real)
git -C <repo> status --porcelain # must show only the expected new files
```

Failure on any check → unwind the branch (`git reset --hard <pre-apply-sha>`) and record `rollback: true` in that repo's state file. Manual investigation, not auto-retry.

### Cross-repo closeout

The close comment on `vamseeachanta/workspace-hub#2775` must list every touched sibling repo with: branch name, commit shas, push status (pushed/pending). No sibling-repo issue comments are created by this issue (the parent issue tracks the cross-repo work).

---

## 6. `sync-agent-configs.sh` behavior delta (exact)

### Current state (verified by reading `scripts/_core/sync-agent-configs.sh`)

- Flags: `--force`, `--dry-run`, `--help`. No `--machine`.
- Resolver `resolve_ws_hub_path` (lines 896-952) reads `harness-config.yaml`, **not** `registry.yaml`. Match order: `workstations.<m>.hostname` → `hostname_aliases` → substring of key.
- Single render token: `__WS_HUB_PATH__`. Replaced via `str.replace` in `render_hermes_template` (lines 73-105).
- No post-render token-validation scan.
- No post-render stale-pattern scan.
- No registry consultation anywhere.

### Required delta

1. **New resolver source.** Add `resolve_machine_roots(machine)` that reads `registry.yaml`. Returns `(workspace_root, tier1_repo_root, repo_layout)`. Falls back to `harness-config.yaml` only when registry is absent (transitional). When both exist, registry wins and harness divergence raises a named error.

2. **`--machine <name>` flag.** Explicit machine selection overriding hostname lookup. Required for CI / cross-machine validation. Defaults to hostname.

3. **New render token `__TIER1_REPO_ROOT__`.** Added to the `render_hermes_template` Python helper alongside `__WS_HUB_PATH__`. Resolves from `resolve_machine_roots(machine).tier1_repo_root`.

4. **Post-render unresolved-token scan.** After render, `grep -E '__[A-Z_][A-Z0-9_]*__'` on rendered output. Non-empty → exit 1 with named tokens.

5. **Post-render stale-nested-path scan.** After render, scan `skills.external_dirs` for entries matching `<workspace_root>/(?!\.claude/)[^/]+/\.claude/skills` — i.e., a nested-repo skill path under workspace-hub root that is not `workspace-hub/.claude/skills` itself. Non-empty → exit 1 with offending lines.

6. **Required-on-host gate for `__TIER1_REPO_ROOT__`.** If template references `__TIER1_REPO_ROOT__` but resolver returns empty for that machine → exit 1 naming the machine and the registry field. Tested by `test_sync_fails_closed_on_missing_tier1_repo_root_for_template_token`.

7. **Template revision.** `config/agents/hermes/config.yaml.template` becomes (current line 38 onward):

   ```yaml
   skills:
     external_dirs:
       - __WS_HUB_PATH__/.claude/skills
       # Sibling repo skill libraries; resolved per-machine via tier1_repo_root.
       # Empty by default — populate only when a sibling repo owns a populated
       # .claude/skills with ≥1 SKILL.md, AND the repo is in registry.repos for
       # this machine. Verified by check-sibling-sso-flow.py.
       - __TIER1_REPO_ROOT__/digitalmodel/.claude/skills
       - __TIER1_REPO_ROOT__/worldenergydata/.claude/skills
       - __TIER1_REPO_ROOT__/assetutilities/.claude/skills
       - __TIER1_REPO_ROOT__/assethold/.claude/skills
   ```

   (The exact list comes from `registry.machines.<m>.repos` minus `workspace-hub` minus repos not present on disk. The template author commits the union; the resolver / checker filters per machine at runtime. `CAD-DEVELOPMENTS` and `achantas-data` are dropped because they are not in registry. `OGManufacturing` is in registry but has no `.claude/skills`; either drop it or test-skip when empty.)

8. **No silent overwrite of existing `~/.hermes/config.yaml` `skills` block.** Current `sync_hermes_yaml_config` (lines 1010-1019) lists `skills` in `MANAGED_KEYS` — meaning template wins on merge. Keep that, but log the prior `skills.external_dirs` content to `~/.hermes/.backup/config.yaml.<ts>` before overwrite. Tested by `test_sync_backs_up_prior_hermes_skills_block`.

9. **No change to `--force` / `--dry-run` semantics.** Both keep current meaning. The new flag set is additive.

### Out of scope (explicitly)

- Live `~/.hermes/config.yaml` mutation outside of `sync-agent-configs.sh` itself.
- Provider config beyond Hermes (`.codex/config.toml`, `.gemini/settings.json`, `.claude/settings.json`) is unchanged by this issue.
- Memory snapshots restoration (lines 1230-1330) is unchanged.

---

## 7. Other plan-body corrections

| Plan line(s) | Issue | Fix |
|---|---|---|
| 16 | "Found: `config/workstations/registry.yaml` — already declares `dev-primary` as ... `repo_layout: sibling`." | True for dev-primary. Plan must also note dev-secondary lacks `tier1_repo_root` and `repo_layout`. |
| 17 | "`scripts/readiness/harness-config.yaml` already declares a harness readiness SSoT" | Add: harness-config also lacks per-machine `tier1_repo_root`. Divergence with registry is documented as `dev-secondary.ws_hub_path: /mnt/workspace-hub` vs registry `/mnt/local-analysis/workspace-hub`; the third value `storage.local: /mnt/dde` is the real partition root and is not consulted by either. |
| 21 | "no machine-readable SSoT policy currently distinguishes central workspace-hub skill roots from intentionally retained repo-local skill roots" | Drop the "intentionally retained" framing — none have been observed on disk. Replace with: "no machine-readable scope (registry.repos) is consulted by `sync-agent-configs.sh`". |
| 191 | "Distinct source count: 10+" | Add live-state probes from this memo as additional source #11 (cross-cutting): `scripts/_core/sync-agent-configs.sh:899-952` resolver-source proof; `registry.dev-secondary` field gap proof; harness-config `dev-secondary` divergence proof. |
| 236 | Overlay candidate list. | Per L2 / C2: eliminate, or convert to typed registry field. |
| 275 | `fail if realpath is /mnt/local-analysis/.claude/skills and target missing` | Replace: `fail if symlink target does not exist OR target is outside expected allow-set`. |
| 286 | Approval gate text. | Replace per §3 above. |
| 305 | "Required: support `__TIER1_REPO_ROOT__`, expose/render a dry-run candidate, ..." | Replace with the §6 deliverable list. |
| 308 | "`docs/standards/CONTROL_PLANE_CONTRACT.md` ... if needed" | Drop "if needed". Required. Convergence table either rewritten or replaced by `check-sibling-sso-flow.py --json` generated section. |
| 323 | `test_rejects_missing_external_skill_root` fixture path | Replace nested path with sibling path per G3. |
| 329 | TDD apply gate. | Replace per §3. |
| 330 | `test_sync_agent_config_dry_run_renders_no_nested_paths` | Add `--machine dev-primary` to the invocation example. Add `test_sync_fails_closed_on_*` variants per §6 #4/#5/#6. |
| 339-345 | Acceptance criteria. | Replace block per §3 (drop marker) and add: registry completeness, registry-vs-harness divergence test, post-render scans pass, per-sibling preflight passes. |
| 363 | "Plan/index not on remote `main` during review" Codex finding. | Add Revisions-made bullet: "Plan and `docs/plans/README.md` index row committed and pushed before re-review dispatch." |
| 384 | "Resolved by first review: ... `digitalmodel` `.codex/skills` / `.gemini/skills` are `IntxLNK`" | Add cause statement per L7 (`feedback_ntfs3_symlink_intxlnk`) and the mount-fs guard test. |

---

## 8. Optional unified diff snippets

The plan file itself is at `docs/plans/2026-05-21-issue-2775-workspace-hub-sibling-sso-flow.md`. The user/owner can apply these directly; I am not patching them.

### Diff 1: replace the approval-gate text

```diff
--- a/docs/plans/2026-05-21-issue-2775-workspace-hub-sibling-sso-flow.md
+++ b/docs/plans/2026-05-21-issue-2775-workspace-hub-sibling-sso-flow.md
@@ -283,9 +283,12 @@ function repair_dry_run():
     compute proposed changes for Hermes template, provider symlinks, AGENTS pointers
     print manifest only by default
-    require --apply plus live GitHub label status:plan-approved plus local approval marker before writes to sibling repos; marker is evidence only, never a substitute for the live label
+    require --apply plus live GitHub label status:plan-approved before writes to sibling repos
+    explicitly do NOT read or write .planning/plan-approved/<n>.md (per memory feedback_dispatch_local_marker_rationalization: forbid markers AND label as a pair)
+    label query is `gh issue view 2775 --json labels --jq '.labels[].name' | grep -Fx status:plan-approved`
+    any gh failure (network, auth, parse, timeout) blocks --apply with a named error (fail closed)
     serialize one repo at a time; do not auto-commit sibling repos unless explicitly requested in a reviewed plan amendment
```

### Diff 2: replace the symlink stale-target test description

```diff
@@ -322,7 +322,7 @@
-| `test_provider_symlink_to_missing_parent_skills_fails` | Broken `.codex/skills` / `.gemini/skills -> ../../.claude/skills` in sibling repos is detected. | Fixture repo with symlink resolving to missing parent `.claude/skills`. | Failure naming provider, repo, realpath. |
+| `test_provider_symlink_broken_target_fails` | Property: symlink target does not exist OR is outside `{workspace_root/.claude/skills} ∪ registered_overlays`. Parametrized across 3 stale realpaths (e.g., `/mnt/local-analysis/.claude/skills`, `/mnt/dde/.claude/skills`, `~/workspace-hub/.claude/skills`). | Each parametrized fixture. | Failure naming provider, repo, realpath, and which allow-set check failed. |
```

### Diff 3: replace the marker-requirement test

```diff
@@ -328,7 +328,9 @@
-| `test_repair_apply_requires_live_label_and_approval_marker` | Cross-repo writes are blocked unless issue has both live `status:plan-approved` and local marker evidence. | `--apply` with missing label or missing `.planning/plan-approved/2775.md`. | Nonzero exit; no writes; message says marker is not a substitute for label. |
+| `test_repair_apply_blocked_when_live_label_missing` | Live label is the only gate. | Mock `gh` returning labels without `status:plan-approved`. | Nonzero exit; no writes; named-label error. |
+| `test_repair_apply_ignores_local_marker_when_label_missing` | Local marker must not satisfy the gate. | `.planning/plan-approved/2775.md` exists + `gh` returns no label. | Nonzero exit; no writes; marker explicitly ignored. |
+| `test_repair_apply_fails_closed_on_gh_error` | gh failure is treated as unapproved. | Mock `gh` nonzero / timeout. | Nonzero exit; no writes; fail-closed error. |
```

---

## 9. Memory citations used in this memo

For traceability — every reviewer-affecting decision above traces back to a feedback memory or live file:

- `feedback_dispatch_local_marker_rationalization` — §3, C1, K1-adjacent.
- `feedback_never_offer_to_self_label_plan_approved` — §3 fail-closed semantics.
- `feedback_ntfs3_symlink_intxlnk` — L7, C10, G6.
- `feedback_gemini_sandbox_overlay_blindness` — L11, G1, G2.
- `feedback_codex_needs_pushed_artifact` + `feedback_reviewer_dispatch_refetch_live_body` — L10, K1.
- `feedback_r1_review_trust_hazard` — applied throughout (verified every reviewer claim against live files before accepting).
- `feedback_always_adversarial_review_scale_depth` — re-review at T3 (3 providers) is required after plan body lands.

---

## 10. Approval-readiness checklist (post-revision)

The plan is ready for re-review when **all** of the following are true:

- [ ] Plan body reflects every §2 / §7 row.
- [ ] §3 (approval gate) text replaced; no local-marker requirement remains anywhere in the plan.
- [ ] §4 (TDD list, 25 tests) replaces the current 14-test list; all under `tests/readiness/`.
- [ ] §5 (cross-repo source-control contract) replaces the §Risks bullet; preflight checks 1-7 enumerated.
- [ ] §6 (sync-agent-configs.sh delta, 9 deliverables) replaces the one-line note in Files-to-Change.
- [ ] `docs/standards/CONTROL_PLANE_CONTRACT.md` convergence-table fix listed as required, not "if needed".
- [ ] Plan file + `docs/plans/README.md` index row committed and pushed to `main` before re-review dispatch.
- [ ] Re-review dispatched at T3 (Claude + Codex + Gemini) per the always-adversarial-review rule.
- [ ] Adversarial result returns ≤ MINOR from all three providers.

Until then: `status:needs-plan`. No `status:plan-review` label flip. No `status:plan-approved` self-label.
