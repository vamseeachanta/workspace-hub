# Plan for #2775: Restore workspace-hub SSoT Flow Across Sibling Repos

> **Status:** draft-needs-revision
> **Complexity:** T3
> **Date:** 2026-05-21
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2775
> **Review artifacts:** scripts/review/results/2026-05-21-plan-2775-claude.md | scripts/review/results/2026-05-21-plan-2775-codex.md | scripts/review/results/2026-05-21-plan-2775-gemini.md | scripts/review/results/2026-05-21-plan-2775-disagreement.md
> **Review state:** MAJOR findings received; not approval-ready until revised and re-reviewed.

---

## Resource Intelligence Summary

### Existing repo code

- Found: `config/workstations/registry.yaml` — declares `dev-primary` as `hostname: ace-linux-1`, `workspace_root: /mnt/local-analysis/workspace-hub`, `tier1_repo_root: /mnt/local-analysis`, and `repo_layout: sibling`. This is the right existing authority for machine/repo topology on dev-primary. **However, `dev-secondary` has `workspace_root: /mnt/local-analysis/workspace-hub` but no `tier1_repo_root` and no `repo_layout` field.** Registry is not internally complete for sibling-checking on dev-secondary; this is a gap, not a usable authoritative source until field-completeness is added and live-verified.
- Found: `scripts/readiness/harness-config.yaml` — declares a harness readiness SSoT. Its `workstations.dev-secondary.ws_hub_path: /mnt/workspace-hub` diverges from registry's `/mnt/local-analysis/workspace-hub`. Neither value has been live-verified against an ace-linux-2 checkout. The plan must capture ground truth on ace-linux-2 before declaring either value authoritative; assuming `/mnt/local-analysis` is correct without verification would lock in a different but equally untested value.
- Found: `config/agents/hermes/config.yaml.template` — currently renders external skill dirs as nested children of `__WS_HUB_PATH__`, e.g. `__WS_HUB_PATH__/digitalmodel/.claude/skills`, which is wrong for the live sibling layout.
- Found: `scripts/_core/sync-agent-configs.sh` — current resolver `resolve_ws_hub_path()` (lines ~896-952) reads ONLY from `harness-config.yaml`; it never consults `registry.yaml`. Flags are `--force` / `--dry-run` only; there is no `--machine` selector. The render path replaces only `__WS_HUB_PATH__`. This means the "add `__TIER1_REPO_ROOT__`" framing in earlier drafts understated the scope: this plan changes the **authoritative resolver source** (harness-config → registry-first), adds a `--machine` flag, adds a new render token, and adds post-render token/path scans. Not a one-line addition.
- Found: `.claude/skills/devops/hermes-ecosystem-integration/references/sibling-repo-sso-topology.md` — already documents the sibling-topology verification checklist: repo topology, Hermes external roots, Codex/Gemini skill symlinks, AGENTS pointers, and memory drift.
- Found: `docs/standards/CONTROL_PLANE_CONTRACT.md` lines 67-72 — convergence table currently declares all four starter repos "Fully converged" while live state shows `.codex/skills` / `.gemini/skills` broken on `worldenergydata` / `assetutilities` / `assethold` and `IntxLNK`-corrupted on `digitalmodel`. The contract documentation contradicts live state and is a required update for this plan, not an optional one.
- Gap: no single repo-owned health check currently verifies all three SSoT flows together: memory bridge, skill root resolution for Hermes/Codex/Gemini, and sibling `AGENTS.md` inheritance target resolution.
- Gap: `digitalmodel/.codex/skills` and `digitalmodel/.gemini/skills` are regular 48-byte `IntxLNK` data files, not symlinks/directories. **Root cause:** per memory `feedback_ntfs3_symlink_intxlnk`, the in-kernel Linux `ntfs3` driver reads symlinks created by the FUSE `ntfs-3g` driver as raw `IntxLNK` byte blobs. The `digitalmodel` checkout originated from an ntfs-3g-created symlink that was later read by ntfs3 or copied across filesystems carrying the `IntxLNK` payload as plain bytes. The checker and repair manifest must (a) classify these as `corrupted_ntfs_symlink`, (b) refuse to repair when the mount filesystem is `ntfs3`, and (c) verify post-repair via `file` + `readlink` that the result is an actual symbolic link.

### Standards

| Standard | Status | Source |
|---|---|---|
| Control-plane contract | existing but stale against live sibling layout | `docs/standards/CONTROL_PLANE_CONTRACT.md` requires repo-root `AGENTS.md` and provider adapters but still reports starter repo convergence as OK; current live symlink and `../AGENTS.md` probes contradict that after sibling migration. |
| Issue planning workflow | applicable | `docs/plans/README.md` requires Resource Intel → Plan → adversarial review → `status:plan-review` → user approval before implementation. |
| Sibling repo topology reference | applicable | `.claude/skills/devops/hermes-ecosystem-integration/references/sibling-repo-sso-topology.md` states sibling Hermes external dirs must not render as `workspace-hub/<repo>/.claude/skills`, provider symlinks must resolve, and AGENTS pointers must target an existing canonical contract. |

### LLM Wiki pages consulted

- N/A — this is harness/config topology work, not public or private domain-knowledge extraction. The relevant durable knowledge source is the repo-owned control-plane/harness documentation listed above.

### Documents consulted

- Related issue #2775 — defines the live failure: memory is in sync, but Hermes skill paths, provider skill symlinks, and sibling `AGENTS.md` pointers are stale/broken.
- Related issue #2758 — folder/runtime architecture clarification, overlaps at the architecture-doc layer but does not itself repair live sibling SSoT flow.
- Related issue #1583 — Hermes config parity work, already `status:plan-approved`; this issue must not duplicate its broad parity scope. #2775 narrows to sibling-layout SSoT resolution and health checks.
- Related issue #2766 — ace-linux-1 physical repo relocation, already `status:plan-approved`; #2775 handles the follow-on harness/config consequences of sibling placement.
- Related issue #2751 — cross-platform harness setup, already `status:plan-approved`; #2775 adds sibling SSoT verification to the harness surface rather than changing machine setup scope.
- `coordination/issue-planning-mode` reference `repo-location-contract-planning.md` — requires adjacent sibling checkout modeling and blocks repo moves/deletes during planning.
- `coordination/issue-planning-mode` reference `per-machine-repo-placement-outcome-contract.md` — requires repo harness/file ecosystem handling through one repo-tracked authority.

### Gaps identified

- No failing test currently catches stale nested Hermes skill roots such as `__WS_HUB_PATH__/digitalmodel/.claude/skills`.
- No failing test currently catches provider skill symlinks in sibling repos resolving to missing `/mnt/local-analysis/.claude/skills`.
- No failing test currently catches sibling repo `AGENTS.md` contract lines that point to missing `/mnt/local-analysis/AGENTS.md`.
- No machine-readable scope (registry.repos) is consulted by `sync-agent-configs.sh` or by any current readiness check when distinguishing the canonical workspace-hub skill root from sibling repo skill roots.
- No dry-run remediation command currently reports exactly what symlinks/templates/contracts would change without mutating sibling repos.
- No live ground-truth probe currently exists for ace-linux-2 (dev-secondary); both `registry.yaml` and `harness-config.yaml` carry guesses, neither verified.

### Evidence (embedded verification)

**Issue statuses** (verified 2026-05-21T09:38:43Z via `gh issue list` / `gh issue view`):

- `#2775` — OPEN — `fix(harness): restore workspace-hub SSoT flow across sibling repos` — labels include `status:needs-plan`.
- `#2758` — OPEN — `Clarify agent/runtime folder architecture to reduce human and agent confusion`.
- `#1583` — OPEN — `Hermes config parity via repo ecosystem templates` — labels include `status:plan-approved`.
- `#2766` — OPEN — `ops(workstations): physically relocate ace-linux-1 tier-1 repo checkouts` — labels include `status:plan-approved`.
- `#2751` — OPEN — `Cross-platform harness setup...` — labels include `status:plan-approved`.

**File existence / path state** (verified 2026-05-21T09:38:43Z):

- EXISTS: `/mnt/local-analysis/workspace-hub/AGENTS.md`
- MISSING: `/mnt/local-analysis/AGENTS.md`
- EXISTS: `/mnt/local-analysis/workspace-hub/.claude/skills`
- MISSING: `/mnt/local-analysis/.claude/skills`
- CORRUPT: `/mnt/local-analysis/digitalmodel/.codex/skills` and `/mnt/local-analysis/digitalmodel/.gemini/skills` are `IntxLNK` regular files encoding `../../.claude/skills`.
- EXISTS: `config/workstations/registry.yaml`
- EXISTS: `scripts/readiness/harness-config.yaml`
- EXISTS: `config/agents/hermes/config.yaml.template`
- EXISTS: `.claude/skills/devops/hermes-ecosystem-integration/references/sibling-repo-sso-topology.md`

**Repo topology proof** (`find /mnt/local-analysis -maxdepth 2 -name .git -type d -printf '%h\n' | sort`):

```text
/mnt/local-analysis/aceengineer-admin
/mnt/local-analysis/aceengineer-strategy
/mnt/local-analysis/aceengineer-website
/mnt/local-analysis/achantas-data
/mnt/local-analysis/achantas-media
/mnt/local-analysis/acma-projects-freeze-work
/mnt/local-analysis/assethold
/mnt/local-analysis/assetutilities
/mnt/local-analysis/CAD-DEVELOPMENTS
/mnt/local-analysis/digitalmodel
/mnt/local-analysis/hobbies
/mnt/local-analysis/kaggle-rogii-2026
/mnt/local-analysis/llm-wiki
/mnt/local-analysis/llm-wiki-acma
/mnt/local-analysis/sabithaandkrishnaestates
/mnt/local-analysis/teamresumes
/mnt/local-analysis/workspace-hub
/mnt/local-analysis/worldenergydata
/mnt/local-analysis/worldenergydata-wiki
```

**Memory bridge proof** (`bash scripts/memory/check-memory-drift.sh`):

```text
=== Memory Drift Check ===
  Hermes MEMORY.md : /home/vamsee/.hermes/memories/MEMORY.md
  Repo agents.md   : /mnt/local-analysis/workspace-hub/.claude/memory/agents.md

✅  In sync — no drift detected.
```

**Hermes template stale-path proof** (`grep -n "external_dirs\|/mnt/local-analysis" -A20 -B5 config/agents/hermes/config.yaml.template`):

```text
35-# Skills: wire workspace-hub ecosystem skills into Hermes as read-only external dirs.
36-# __WS_HUB_PATH__ is resolved per-machine by sync-agent-configs.sh using harness-config.yaml.
37-# Includes workspace-hub root + nested repos with their own skill libraries.
38-skills:
39:  external_dirs:
40-    - __WS_HUB_PATH__/.claude/skills
41-    - __WS_HUB_PATH__/CAD-DEVELOPMENTS/.claude/skills
42-    - __WS_HUB_PATH__/worldenergydata/.claude/skills
43-    - __WS_HUB_PATH__/achantas-data/.claude/skills
44-    - __WS_HUB_PATH__/assetutilities/.claude/skills
45-    - __WS_HUB_PATH__/digitalmodel/.claude/skills
```

**Provider symlink proof** (representative sibling repos):

Correct central relative target from inside `<repo>/.codex/skills` or `<repo>/.gemini/skills` is `../../workspace-hub/.claude/skills`, not `../workspace-hub/.claude/skills`.

```text
workspace-hub .codex/skills -> ../.claude/skills ; real=/mnt/local-analysis/workspace-hub/.claude/skills ; exists=yes
workspace-hub .gemini/skills -> ../.claude/skills ; real=/mnt/local-analysis/workspace-hub/.claude/skills ; exists=yes
worldenergydata .codex/skills -> ../../.claude/skills ; real=/mnt/local-analysis/.claude/skills ; exists=no
worldenergydata .gemini/skills -> ../../.claude/skills ; real=/mnt/local-analysis/.claude/skills ; exists=no
assetutilities .codex/skills -> ../../.claude/skills ; real=/mnt/local-analysis/.claude/skills ; exists=no
assetutilities .gemini/skills -> ../../.claude/skills ; real=/mnt/local-analysis/.claude/skills ; exists=no
assethold .codex/skills -> ../../.claude/skills ; real=/mnt/local-analysis/.claude/skills ; exists=no
assethold .gemini/skills -> ../../.claude/skills ; real=/mnt/local-analysis/.claude/skills ; exists=no
```

**AGENTS pointer proof** (representative sibling repos):

```text
# digitalmodel
Contract: ../AGENTS.md | Source: src/digitalmodel/

# worldenergydata
Contract: ../AGENTS.md | Source: src/worldenergydata/

# assetutilities
Contract: ../AGENTS.md | Source: src/assetutilities/

# assethold
Contract: ../AGENTS.md | Source: src/assethold/
```

`ls -ld /mnt/local-analysis/AGENTS.md /mnt/local-analysis/workspace-hub/AGENTS.md`:

```text
ls: cannot access '/mnt/local-analysis/AGENTS.md': No such file or directory
-rwxrwxrwx 1 vamsee vamsee 2414 May 18 14:46 /mnt/local-analysis/workspace-hub/AGENTS.md
```

**Reproduction proofs** (runtime failure class: broken provider/harness resolution):

```text
$ bash scripts/memory/check-memory-drift.sh
✅  In sync — no drift detected.

$ test -e /mnt/local-analysis/worldenergydata/.codex/skills; echo $?
1

$ test -e /mnt/local-analysis/assetutilities/.gemini/skills; echo $?
1

$ test -e /mnt/local-analysis/AGENTS.md; echo $?
1
```

- Reproduced at: 2026-05-21T09:38:43Z
- Failure mode observed matches issue claim: YES — memory is healthy; skill and harness/contract resolution are not.

**Additional live probe after first review** (`file`/`xxd`, 2026-05-21):

```text
/mnt/local-analysis/digitalmodel/.codex/skills: data
00000000: 49 6e 74 78 4c 4e 4b 01 2e 00 2e 00 2f 00 2e 00  IntxLNK...../...
/mnt/local-analysis/digitalmodel/.gemini/skills: data
00000000: 49 6e 74 78 4c 4e 4b 01 2e 00 2e 00 2f 00 2e 00  IntxLNK...../...
```

**Distinct source count:** 10+ distinct sources: issue #2775, issues #2758/#1583/#2766/#2751, `config/workstations/registry.yaml`, `scripts/readiness/harness-config.yaml`, `config/agents/hermes/config.yaml.template`, `docs/standards/CONTROL_PLANE_CONTRACT.md`, `docs/plans/README.md`, sibling topology reference skill doc, live filesystem probes, and first-round review artifacts.

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-05-21-issue-2775-workspace-hub-sibling-sso-flow.md` |
| Plan index row | `docs/plans/README.md` |
| Tests — sibling SSoT topology | `tests/readiness/test_sibling_sso_topology.py` |
| Tests — sync template rendering | `tests/readiness/test_hermes_config_sibling_paths.py` |
| Tests — sync resolver and tokens | `tests/readiness/test_sync_agent_configs_sso.py` |
| Tests — registry SSoT completeness | `tests/readiness/test_registry_sso_completeness.py` |
| Tests — sibling AGENTS contract | `tests/readiness/test_sibling_agents_contract.py` |
| Tests — dry-run + apply remediation | `tests/readiness/test_sibling_sso_repair_dry_run.py` |
| Tests — workstation registry probes | `tests/workstations/test_dev_secondary_ground_truth.py` |
| Implementation — health checker (Python) | `scripts/readiness/check-sibling-sso-flow.py` |
| Implementation — health checker (shell entry, required) | `scripts/readiness/check-sibling-sso-flow.sh` |
| Implementation — dry-run/apply repair helper | `scripts/readiness/repair-sibling-sso-flow.py` |
| Implementation — Hermes template | `config/agents/hermes/config.yaml.template` |
| Implementation — sync script resolver + flags | `scripts/_core/sync-agent-configs.sh` |
| Implementation — readiness config/schema | `scripts/readiness/harness-config.yaml`, `config/workstations/registry.yaml` |
| Implementation — control plane contract | `docs/standards/CONTROL_PLANE_CONTRACT.md` (REQUIRED, not optional) |
| Plan revision notes | `.planning/active/2775/plan-revision-notes.md` |
| Per-sibling state captures (apply-time only) | `.planning/active/2775/sibling-state/<repo>.json` |
| Pending-push queue (apply-time only) | `.planning/active/2775/pending-push.txt` |
| Review artifacts | `scripts/review/results/2026-05-21-plan-2775-*.md` |

---

## Deliverable

A repo-owned sibling SSoT health/repair workflow that makes `workspace-hub` the canonical control-plane for memory, skills, and harness contracts across sibling repos, with TDD checks that fail on the current stale paths and pass only when Hermes/Codex/Gemini skills and `AGENTS.md` inheritance resolve correctly.

---

## SSoT Strategy Decision

Choose **central-authority plus registry-derived sibling allowlist**. No overlay concept derived from stale templates. Sibling repos that own a populated `.claude/skills` with ≥1 `SKILL.md` AND appear in `registry.machines.<m>.repos` are eligible sibling sources; everything else is rejected.

Authoritative source split for this issue:

- `config/workstations/registry.yaml` is authoritative for machine identity, `workspace_root`, `tier1_repo_root`, `repo_layout`, and per-machine required repo list. Plan must add `tier1_repo_root` and `repo_layout` to any machine entry declared `sibling` (currently missing on `dev-secondary`), AFTER live ground-truth capture on that host.
- `scripts/readiness/harness-config.yaml` may carry readiness-check knobs but MUST NOT redefine machine roots. Where it currently duplicates roots (e.g., `dev-secondary.ws_hub_path`), this plan reconciles by either deleting the duplicated field or requiring exact agreement with registry. Reconciliation is gated on ground-truth verification, not unilateral lock-in to the registry guess.
- `config/agents/hermes/config.yaml.template` may use only defined render tokens. This plan requires (a) a new `__TIER1_REPO_ROOT__` token, (b) a resolver-source change in `scripts/_core/sync-agent-configs.sh` from `harness-config.yaml` to `registry.yaml`-first with a `--machine` flag, (c) post-render scans for unresolved `__[A-Z_]+__` tokens and for stale nested `workspace-hub/<repo>` patterns. See §`sync-agent-configs.sh delta` below for the discrete deliverable list.

1. `workspace-hub` remains the canonical control-plane authority for:
   - memory bridge state,
   - shared agent skills,
   - harness/readiness scripts,
   - provider adapter contract docs,
   - workstation/repo topology registry.
2. Sibling repos are NOT treated as "overlays" in this plan. The default Hermes external_dirs list contains only `__WS_HUB_PATH__/.claude/skills`. A sibling repo enters Hermes `external_dirs` ONLY when all of: (a) the repo appears in `registry.machines.<m>.repos` for the resolving machine, (b) the resolved sibling path `__TIER1_REPO_ROOT__/<repo>/.claude/skills` exists on disk, and (c) the directory contains ≥1 `SKILL.md`. This is enforced by the resolver/checker; no candidate list is hand-maintained in the template against a stale snapshot. The template author commits a union derived from registry; the resolver filters per machine at runtime. The previous candidate list (`CAD-DEVELOPMENTS`, `achantas-data`, etc.) is dropped — neither is in `registry.machines.dev-primary.repos`.
3. Codex/Gemini skill links in sibling repos should resolve to the canonical `workspace-hub/.claude/skills`. From inside a sibling `<repo>/.codex/skills` or `<repo>/.gemini/skills`, the correct relative symlink target is `../../workspace-hub/.claude/skills`. **Special case:** `workspace-hub` itself has `<repo>/.codex/skills -> ../.claude/skills` (it is its own parent); the checker must branch on `repo == workspace-hub` and apply the self-case rule rather than the sibling rule.
4. Sibling repo `AGENTS.md` files should point to `../workspace-hub/AGENTS.md` or carry an explicit local contract that names `workspace-hub/AGENTS.md` as the canonical shared governance source.
5. No parent-level `/mnt/local-analysis/AGENTS.md` or `/mnt/local-analysis/.claude/skills` shim should be created as the primary fix. Such shims would hide stale pointers and create a second apparent SSoT outside git-tracked `workspace-hub`.

---

## Pseudocode

```text
function load_registry(machine):
    read config/workstations/registry.yaml as the authority for machine roots and required repos
    read scripts/readiness/harness-config.yaml only for readiness knobs (NOT for machine roots)
    identify target machine by explicit --machine flag, else by socket.gethostname()
    require workspace_root, tier1_repo_root, repo_layout=sibling for sibling checks
    if any of those three fields is missing on the resolved machine: fail closed with named missing field
    if harness-config defines a workstations.<m>.ws_hub_path AND registry defines workspace_root:
        require exact agreement OR refuse with named-value error (do NOT silently prefer one source)
    return required repo set from registry.yaml.machines[machine].repos
    classify absent entries as status: not_present unless registry marks required_on_host: true (new optional field)

function check_memory_flow(workspace_root):
    run scripts/memory/check-memory-drift.sh
    require exit 0 and no drift marker
    record evidence in JSON/text report

function expected_skill_roots(repo, registry, machine):
    # No "overlay" concept. Registry membership + on-disk reality decides eligibility.
    if repo == workspace-hub:
        return workspace_root/.claude/skills           # canonical central root
    sibling_path = tier1_repo_root/<repo>/.claude/skills
    if sibling_path exists AND contains >=1 SKILL.md:
        return sibling_path                            # registry-derived sibling
    return None                                        # repo not eligible — emit status: not_present (not fail)

function check_hermes_template():
    parse config/agents/hermes/config.yaml.template
    fail if any external_dirs entry matches __WS_HUB_PATH__/<repo>/.claude/skills for <repo> != ".claude" (i.e., the central root)
    require canonical workspace-hub skill root entry: __WS_HUB_PATH__/.claude/skills
    require all sibling entries use the __TIER1_REPO_ROOT__/<repo>/.claude/skills form
    invoke scripts/_core/sync-agent-configs.sh --machine <m> --dry-run
    fail on:
      - any unresolved __[A-Z_][A-Z0-9_]*__ token in render output
      - any rendered external_dir matching <workspace_root>/(?!\.claude/)[^/]+/\.claude/skills
      - any rendered sibling path that does not exist on disk for the target machine (when --strict)

function check_provider_symlinks(repo):
    for provider_dir in [.codex, .gemini]:
        path = <repo>/<provider_dir>/skills
        if path is a regular file:
            if file_head_4_bytes == b"IntxLNK":
                classify as corrupted_ntfs_symlink
                emit repair_action: unlink_then_recreate
            else:
                fail with kind=unexpected_regular_file
        elif path is a symlink:
            target = readlink(path)
            real = realpath(path)
            # Property-broad failure: target must exist AND be inside the allow-set,
            # which is {workspace_root/.claude/skills} ∪ {registry-derived sibling skill dirs}.
            # Do NOT hard-code the stale realpath /mnt/local-analysis/.claude/skills here —
            # any nonexistent target or out-of-allow-set realpath fails.
            if not exists(real): fail kind=broken_symlink reason="target nonexistent" realpath=real
            if real not in allow_set: fail kind=symlink_outside_allowset realpath=real
            # workspace-hub self case: <repo>/.codex/skills -> ../.claude/skills is valid because the repo IS workspace-hub
            if repo == "workspace-hub":
                require target == "../.claude/skills"
            else:
                require target == "../../workspace-hub/.claude/skills"  OR registry-registered sibling target
        elif path is a directory:
            # Repo-local override: only valid if repo == workspace-hub OR (repo in registry.repos AND dir has >=1 SKILL.md)
            require valid per expected_skill_roots()
        else:
            emit status: not_present (path missing entirely is treated as absent, not failure)

function check_agents_contract(repo):
    read <repo>/AGENTS.md
    fail if it references ../AGENTS.md and tier1_repo_root/AGENTS.md is missing
    pass if it references ../workspace-hub/AGENTS.md and target exists, or has explicit local contract with canonical workspace-hub reference

function require_user_approval(issue_number):
    # Live GitHub label is the SOLE authoritative gate.
    # Local approval markers are explicitly NOT consulted.
    # Rationale: memory `feedback_dispatch_local_marker_rationalization` —
    # a dispatch lane can synthesize .planning/plan-approved/<n>.md as
    # retry-loop rationalization. Requiring the marker in addition to the
    # label adds a forgeable second gate without strengthening the real one.
    # The live label requires the user; that is the ONLY gate.
    cmd = ["gh", "issue", "view", str(issue_number), "--json", "labels",
           "--jq", '.labels[].name']
    try:
        labels = run_with_timeout(cmd, timeout_sec=15).splitlines()
    except (TimeoutExpired, CalledProcessError, OSError, FileNotFoundError) as e:
        raise ApprovalUnavailableError(
            f"gh query failed ({type(e).__name__}); refusing --apply (fail closed)")
    if "status:plan-approved" not in labels:
        raise ApprovalMissingError(
            f"issue #{issue_number} not labelled status:plan-approved; refusing --apply")
    # Explicitly do NOT read .planning/plan-approved/<n>.md anywhere in this flow.
    return True

function preflight_sibling_repo(repo_path):
    # All checks must pass before --apply is allowed for this repo.
    fs_type = run("findmnt", "-no", "FSTYPE", realpath(repo_path))
    if fs_type == "ntfs3":
        block(reason="ntfs3 mount — IntxLNK repair would re-corrupt; remount as ntfs-3g first")
    if run("git", "-C", repo_path, "status", "--porcelain") != "":
        block(reason="dirty working tree", files=...)
    if run("git", "-C", repo_path, "symbolic-ref", "--short", "HEAD") fails:
        block(reason="detached HEAD")
    ahead, behind = parse(run("git", "-C", repo_path, "rev-list", "--left-right", "--count", "@{u}...HEAD"))
    if ahead > 0:
        block(reason="local commits ahead of upstream — refuse to pile on")
    if untracked_files_in(repo_path, [".codex/skills", ".gemini/skills", "AGENTS.md"]):
        block(reason="untracked files in touched paths")
    if nested_worktrees_overlap_touched_paths(repo_path):
        block(reason="nested worktrees overlap")
    record state to .planning/active/2775/sibling-state/<repo>.json

function repair_dry_run():
    compute proposed changes for Hermes template, provider symlinks, AGENTS pointers
    print manifest only by default
    do NOT mutate anything in dry-run mode
    record per-repo proposed actions and preflight predictions

function repair_apply(issue_number, manifest):
    require_user_approval(issue_number)             # live GH label only, fail closed on gh error
    for repo in manifest.repos:
        preflight_sibling_repo(repo.path)           # block on dirty/detached/ntfs3/ahead/untracked
        for action in repo.actions:
            if action.kind == "unlink_then_recreate_intxlnk":
                os.unlink(action.path)
                os.symlink(action.target, action.path)
                # Post-write verification — refuses to mark success otherwise.
                assert file_type(action.path) == "symbolic link"
                assert readlink(action.path) == action.target
                assert exists(action.path + "/SKILL.md") or has_any_skill_md(action.path)
            elif action.kind == "rewrite_symlink":
                ...similar with post-write verify...
            elif action.kind == "rewrite_agents_pointer":
                ...
        # On any post-write failure, git reset --hard <pre-apply-sha> for that repo only.
        # Record rollback in state file. Do NOT auto-retry. Manual investigation only.
    # Cross-repo serialization: one repo at a time. No bulk commit. No auto-push.
    # Each repo gets its own branch `harness/2775-sibling-sso-flow` and per-file commits.
    # Push status is collected to .planning/active/2775/pending-push.txt for human review.
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create | `tests/readiness/test_sibling_sso_topology.py` | TDD suite for memory/skill/AGENTS sibling topology health (includes IntxLNK classification, workspace-hub self case, registry-absent `not_present`). |
| Create | `tests/readiness/test_hermes_config_sibling_paths.py` | Failing tests for stale nested `__WS_HUB_PATH__/<repo>/.claude/skills` template paths and sibling-aware rendering. |
| Create | `tests/readiness/test_sync_agent_configs_sso.py` | Coverage for `--machine` flag, `__TIER1_REPO_ROOT__` rendering, post-render unresolved-token scan, registry-vs-harness divergence, missing-`tier1_repo_root` fail-closed. |
| Create | `tests/readiness/test_registry_sso_completeness.py` | Sibling-machine field completeness; registry-vs-harness divergence detection. |
| Create | `tests/readiness/test_sibling_agents_contract.py` | Sibling `AGENTS.md` pointer resolution. |
| Create | `tests/readiness/test_sibling_sso_repair_dry_run.py` | Dry-run + `--apply` gate tests: live-label-only gate, marker-ignored, gh fail-closed, ntfs3 refusal, dirty-repo block, detached-HEAD block, post-write `file`/`readlink` verification. |
| Create | `tests/workstations/test_dev_secondary_ground_truth.py` | Probes that ace-linux-2 ground truth has been captured before registry mutation; skipped on dev-primary. Records the verified path in test fixture for cross-check. |
| Create | `scripts/readiness/check-sibling-sso-flow.py` | Machine-readable health checker. Branches `repo == workspace-hub` (self case) vs sibling rule. Emits structured `{memory, skills, harness_contracts, registry}` per-key with `pass/fail/not_present` + evidence paths. |
| Create | `scripts/readiness/check-sibling-sso-flow.sh` | REQUIRED stable shell entry point referenced by acceptance criteria, cron, and hooks. Wraps the Python checker via `uv run`. Not optional. |
| Create | `scripts/readiness/repair-sibling-sso-flow.py` | Dry-run-first remediation helper. `--apply` calls `gh issue view 2775 --json labels` for live-label gate, runs preflight (ntfs3, dirty, detached, ahead, untracked, nested-worktree), unlink+ln+verify for IntxLNK, post-write `file`/`readlink` checks, no auto-push. |
| Modify | `config/agents/hermes/config.yaml.template` | Remove nested sibling repo assumptions. New layout: `__WS_HUB_PATH__/.claude/skills` plus union of `__TIER1_REPO_ROOT__/<sibling>/.claude/skills` rendered from registry. Resolver filters per machine at runtime. |
| Modify | `scripts/_core/sync-agent-configs.sh` | **Structural change to authoritative resolver, not a token-add.** Discrete deliverables: (1) new `resolve_machine_roots(machine)` reading `registry.yaml` first, harness-config only as transitional fallback; (2) `--machine <name>` flag; (3) new `__TIER1_REPO_ROOT__` render token; (4) post-render unresolved-token scan `__[A-Z_][A-Z0-9_]*__`; (5) post-render stale-nested-path scan; (6) fail-closed when template uses `__TIER1_REPO_ROOT__` and registry resolves empty; (7) registry-vs-harness divergence error; (8) backup prior `~/.hermes/config.yaml` skills block to `~/.hermes/.backup/config.yaml.<ts>` before overwrite; (9) `--force`/`--dry-run` semantics unchanged (additive). |
| Modify | `scripts/readiness/harness-config.yaml` | Reconcile or remove duplicated machine roots (`workstations.<m>.ws_hub_path`). Do NOT lock in registry values without ground-truth verification on the target host. Where registry is incomplete (dev-secondary), this plan defers reconciliation until the workstation ground-truth test passes. |
| Modify | `config/workstations/registry.yaml` | Add `tier1_repo_root` and `repo_layout` to every machine declared sibling. Add optional `required_on_host: true` field so registry-listed-but-absent repos can be distinguished from `not_present`. Mutations to dev-secondary blocked until `tests/workstations/test_dev_secondary_ground_truth.py` passes on ace-linux-2. |
| Modify | Target sibling repo `AGENTS.md` files derived from `registry.machines.<m>.repos` | After approval only: replace stale `../AGENTS.md` contract pointers with `../workspace-hub/AGENTS.md` or explicit local contract language. Repos absent on disk: `status: not_present`, no write. |
| Modify | Target sibling repo `.codex/skills` / `.gemini/skills` derived from `registry.machines.<m>.repos` | After approval only: repair symlinks to canonical `../../workspace-hub/.claude/skills`. Classify `IntxLNK` regular files as `corrupted_ntfs_symlink`, refuse on `ntfs3` mounts, unlink+symlink+verify on ext4. `workspace-hub` itself uses `../.claude/skills` self-case. |
| Modify | `docs/standards/CONTROL_PLANE_CONTRACT.md` | **REQUIRED (not optional).** Convergence table currently lies — it declares all four starter repos "Fully converged" while live state shows broken/IntxLNK on `digitalmodel`, `worldenergydata`, `assetutilities`, `assethold`. Either rewrite the table by hand or replace it with a generated section sourced from `check-sibling-sso-flow.py --json`. |
| Update | `docs/plans/README.md` | Update plan index row to reflect live-label-only approval gate (no marker requirement); commit and push BEFORE next adversarial review dispatch (reviewers fetch from main). |
| Create | `.planning/active/2775/plan-revision-notes.md` | This revision summary — what changed since first review wave and remaining gate state. |

---

## TDD Test List

All tests live under `tests/readiness/` (natural home — `scripts/readiness/` owns the checker) or `tests/workstations/` (host-bound ground-truth probes). Pytest collection is verified: `pyproject.toml` has `testpaths = ["tests"]` so new top-level subdirs are auto-discovered.

| # | Test name | Property under test | Location |
|---|---|---|---|
| 1 | `test_memory_bridge_drift_check_green` | `scripts/memory/check-memory-drift.sh` exit 0 + no drift. | `tests/readiness/test_sibling_sso_topology.py` |
| 2 | `test_hermes_template_rejects_nested_repo_skill_paths` | Template contains no `__WS_HUB_PATH__/<repo>/.claude/skills` for any `<repo>` ≠ workspace-hub. | `tests/readiness/test_hermes_config_sibling_paths.py` |
| 3 | `test_hermes_template_accepts_central_workspace_hub_root` | `__WS_HUB_PATH__/.claude/skills` resolves to a dir with ≥1 `SKILL.md`. | same |
| 4 | `test_registry_machine_fields_complete_for_sibling_machines` | Any `repo_layout: sibling` machine has non-empty `tier1_repo_root` AND `workspace_root`. Today: dev-secondary fails until migration. | `tests/readiness/test_registry_sso_completeness.py` |
| 5 | `test_registry_authoritative_for_machine_roots` | When both `registry.workspace_root` and `harness-config.<m>.ws_hub_path` are defined, they must match exactly OR harness value is absent. Today: dev-secondary fails (`/mnt/workspace-hub` vs `/mnt/local-analysis/workspace-hub`) until host-verified reconciliation. | same |
| 6 | `test_intxlnk_classified_as_corrupted_symlink` | Regular file whose first 7 bytes are `49 6e 74 78 4c 4e 4b` reports `kind=corrupted_ntfs_symlink` with `repair_action=unlink_then_recreate`. | `tests/readiness/test_sibling_sso_topology.py` |
| 7 | `test_provider_symlink_broken_target_fails` (property-broad, parametrized) | Symlink whose target does not exist OR realpath is outside `{workspace_root/.claude/skills} ∪ registry-derived siblings` → fail. Parametrize across ≥3 stale realpaths (`/mnt/local-analysis/.claude/skills`, `/mnt/dde/.claude/skills`, `$HOME/workspace-hub/.claude/skills`). | same |
| 8 | `test_provider_symlink_canonical_sibling_target_passes` | `<repo>/.codex/skills -> ../../workspace-hub/.claude/skills` resolves to a real directory with ≥1 `SKILL.md`. | same |
| 9 | `test_workspace_hub_self_skill_symlink_pass` | `workspace-hub/.codex/skills -> ../.claude/skills` is treated as the self-case and passes. Iterating sibling rule over `workspace-hub` must NOT mark it broken. | same |
| 10 | `test_agents_pointer_to_missing_parent_fails` | `Contract: ../AGENTS.md` fails when `tier1_repo_root/AGENTS.md` is missing. | `tests/readiness/test_sibling_agents_contract.py` |
| 11 | `test_agents_pointer_to_workspace_hub_passes` | `Contract: ../workspace-hub/AGENTS.md` and target exists → pass. | same |
| 12 | `test_registry_repo_absent_on_disk_reports_not_present` | Registry-listed repo without an on-disk checkout (e.g., `OGManufacturing` per dev-primary registry today) emits `status: not_present`, NOT `fail`, unless registry marks `required_on_host: true`. | `tests/readiness/test_sibling_sso_topology.py` |
| 13 | `test_repair_dry_run_outputs_manifest_no_writes` | `repair-sibling-sso-flow.py --dry-run` mutates nothing on the filesystem; manifest lists proposed actions only. | `tests/readiness/test_sibling_sso_repair_dry_run.py` |
| 14 | `test_repair_apply_blocked_when_live_label_missing` | Mock `gh issue view 2775 --json labels` returning labels WITHOUT `status:plan-approved` → nonzero exit, no writes, named-label error. | same |
| 15 | `test_repair_apply_ignores_local_marker_when_label_missing` | `.planning/plan-approved/2775.md` exists on disk AND `gh` returns no live label → still blocked. Asserts the local marker is explicitly NOT consulted. | same |
| 16 | `test_repair_apply_fails_closed_on_gh_error` | Mock `gh` exit nonzero OR timeout OR `FileNotFoundError` → blocked with `ApprovalUnavailableError`. | same |
| 17 | `test_repair_refuses_when_fs_is_ntfs3` | `findmnt -no FSTYPE <repo>` returns `ntfs3` → refuse with mount-fs guidance citing `feedback_ntfs3_symlink_intxlnk`. | same |
| 18 | `test_repair_post_write_verifies_symbolic_link` | After unlink + ln -s + chmod, `file <path>` returns `symbolic link` and `readlink <path>` equals expected target; otherwise rollback. | same |
| 19 | `test_repair_dirty_repo_blocks_apply` | `git status --porcelain` non-empty for the target repo → refuse with named files listed. | same |
| 20 | `test_repair_detached_head_blocks_apply` | Detached HEAD on target repo → refuse; suggest branch creation. | same |
| 21 | `test_sync_dry_run_resolves_tier1_repo_root_token` | `sync-agent-configs.sh --machine dev-primary --dry-run` produces rendered output with no `__TIER1_REPO_ROOT__` token remaining. | `tests/readiness/test_sync_agent_configs_sso.py` |
| 22 | `test_sync_fails_closed_on_missing_tier1_repo_root_for_template_token` | Registry entry lacks `tier1_repo_root` AND template uses `__TIER1_REPO_ROOT__` → nonzero exit naming the machine. | same |
| 23 | `test_sync_fails_closed_on_unresolved_render_token` | Any remaining `__[A-Z_][A-Z0-9_]*__` pattern in post-render output → nonzero exit naming the token. | same |
| 24 | `test_sync_fails_closed_on_registry_harness_root_divergence` | `registry.workspace_root` ≠ `harness-config.<m>.ws_hub_path` (both defined) → nonzero exit naming both files and values. | same |
| 25 | `test_checker_json_report_has_four_flow_statuses` | `check-sibling-sso-flow.py --json` emits `{memory, skills, harness_contracts, registry}` with per-key `status ∈ {pass, fail, not_present}` and `evidence_paths`. | `tests/readiness/test_sibling_sso_topology.py` |
| 26 | `test_dev_secondary_ground_truth_captured_before_registry_mutation` | When run on ace-linux-2 hostname, this records and asserts the live `/mnt/<path>/workspace-hub` actually contains the repo. When run elsewhere, skipped with a clear `pytest.skip` message. Blocks the `tier1_repo_root` registry add for dev-secondary until satisfied. | `tests/workstations/test_dev_secondary_ground_truth.py` |

---

## Acceptance Criteria

- [ ] All new tests are written before implementation and initially fail on at least one current stale-path/broken-symlink fixture.
- [ ] `uv run pytest tests/readiness/ tests/workstations/ -v` passes after implementation. (Tests live under `tests/readiness/` and `tests/workstations/`; no `tests/harness/` convention introduced.)
- [ ] `scripts/readiness/check-sibling-sso-flow.sh --machine dev-primary --json` reports:
  - [ ] memory: PASS,
  - [ ] skills: PASS for configured Hermes/Codex/Gemini roots,
  - [ ] harness_contracts: PASS for sibling `AGENTS.md` targets,
  - [ ] registry: PASS for machine field completeness and registry-vs-harness agreement.
- [ ] `config/agents/hermes/config.yaml.template` no longer contains `__WS_HUB_PATH__/<repo>/.claude/skills` for any `<repo>` other than the central root.
- [ ] `scripts/_core/sync-agent-configs.sh --machine dev-primary --dry-run` produces/validates Hermes config with `__TIER1_REPO_ROOT__` expanded, no unresolved `__[A-Z_]+__` tokens, no stale nested skill paths, and emits a backup of the prior `~/.hermes/config.yaml` skills block before any overwrite.
- [ ] `config/workstations/registry.yaml` is the authoritative source for machine roots AND has `tier1_repo_root` + `repo_layout` populated on every sibling-declared machine (today: dev-secondary gains both, AFTER ground-truth capture). Any duplicated `scripts/readiness/harness-config.yaml` root either matches or is removed.
- [ ] Sibling repo eligibility is registry-derived: a repo enters Hermes `external_dirs` only when it appears in `registry.machines.<m>.repos` AND its `tier1_repo_root/<repo>/.claude/skills` exists on disk with ≥1 `SKILL.md`. No standalone overlay list is maintained.
- [ ] Target sibling repo `.codex/skills` and `.gemini/skills` resolve to existing canonical roots; `IntxLNK` regular files are detected, refused on `ntfs3` mounts, and unlinked+symlinked+verified on ext4. `workspace-hub` itself is checked as a self-case (`../.claude/skills`), not as a sibling.
- [ ] Target sibling repo `AGENTS.md` contract pointers resolve to existing `workspace-hub/AGENTS.md` or carry an explicit local contract referencing it.
- [ ] No parent-level `/mnt/local-analysis/AGENTS.md` or `/mnt/local-analysis/.claude/skills` shim is introduced as the main fix unless the plan is amended and re-reviewed.
- [ ] **Approval gate is live GitHub label only.** `repair-sibling-sso-flow.py --apply` queries `gh issue view 2775 --json labels --jq '.labels[].name'` at apply-time. It explicitly does NOT read `.planning/plan-approved/`. Any `gh` failure (network, auth, parse, timeout, missing binary) is treated as unapproved and blocks `--apply` with a named error. Per memory `feedback_dispatch_local_marker_rationalization`: forbid markers AND label as a pair; the live label is the only gate.
- [ ] Per-sibling preflight passes before any write: ntfs3 mount refused, dirty working tree refused, detached HEAD refused, ahead-of-upstream refused, untracked-in-touched-paths refused, nested-worktree-overlap refused. Each refusal records to `.planning/active/2775/sibling-state/<repo>.json`.
- [ ] Per-touched-symlink post-write verification passes: `file <path>` returns `symbolic link`, `readlink <path>` equals expected target, and target dir contains at least one `SKILL.md`. Any verification miss triggers rollback via `git reset --hard <pre-apply-sha>` for that repo only.
- [ ] `docs/standards/CONTROL_PLANE_CONTRACT.md` convergence table is rewritten (REQUIRED, not "if needed") to reflect live state or replaced by a generated section sourced from `check-sibling-sso-flow.py --json`. The current "Fully converged" claim for all four starter repos is removed.
- [ ] `docs/plans/README.md` index row for #2775 reflects live-label-only approval gate (no marker requirement) and is committed and pushed to `main` BEFORE the next adversarial review dispatch (Codex/Gemini fetch from main; cached or out-of-tree artifacts produce false-MAJOR findings — see memories `feedback_codex_needs_pushed_artifact` and `feedback_reviewer_dispatch_refetch_live_body`).
- [ ] After all repairs, `bash scripts/memory/check-memory-drift.sh` remains green.
- [ ] Post-implementation code/adversarial review (T3 — Claude + Codex + Gemini) is complete and any required legal/security/no-secrets scan is recorded before closeout.
- [ ] Final closeout comment on #2775 includes checker output, tests, changed paths per sibling repo (with branch names + commit shas + push status), and confirmation that no secrets/auth files were touched.

---

## Adversarial Review Summary

| Provider | Verdict (round 1) | Key findings |
|---|---|---|
| Claude | MAJOR | Local-marker approval reintroduces a defect class memory already flagged; overlay candidates derived from the stale template being fixed (circular); registry self-consistency unverified on dev-secondary; `tests/harness/` is a net-new convention; shell wrapper "optional" but acceptance-load-bearing; symlink test was path-narrow not class-broad; registry-listed-absent path had no `not_present` test; sync-script delta unsized; workspace-hub self-symlink not handled; no IntxLNK root-cause and no post-repair guard. |
| Codex | MAJOR | Plan/index not retrievable from remote `main` during review; target repo scope inconsistent (`CAD-DEVELOPMENTS`/`achantas-data` not in registry); `load_registry` requires `tier1_repo_root` on dev-secondary which doesn't define it; sync-script integration underspecified — current resolver reads harness-config not registry, no `--machine` flag; cross-repo source-control strategy too vague (no per-sibling-repo dirty/branch/ahead/behind capture). |
| Gemini | MAJOR | Sandbox could not see referenced files at HEAD (overlay artifact — same files exist at HEAD on this checkout per memory `feedback_gemini_sandbox_overlay_blindness`); `test_rejects_missing_external_skill_root` fixture conflated nested-rejected and missing-valid into the same path; live-label query implementation not specified; dirty-repo preflight missing from `repair_dry_run` pseudocode; IntxLNK `--apply` behavior unspecified. |

**Overall result (round 1):** MAJOR — not approval-ready.

**Revisions in this revision pass (responding to all three round-1 reviewers):**

- **Approval gate is now live GitHub label ONLY.** Local approval markers are explicitly NOT consulted by `--apply`. The previous belt-and-suspenders requirement (label + marker) is removed per memory `feedback_dispatch_local_marker_rationalization`; a dispatch lane can synthesize the marker, so stacking it as a gate adds a forgeable second factor without strengthening the load-bearing one. Pseudocode now spells out `gh issue view 2775 --json labels --jq '.labels[].name'` with fail-closed semantics on any gh error.
- **Overlay-from-template list eliminated.** Sibling eligibility is now registry-derived only: `registry.machines.<m>.repos` ∩ on-disk-`.claude/skills`-with-≥1-SKILL.md. The previously hard-coded list (`CAD-DEVELOPMENTS`, `achantas-data`, etc.) is dropped because it did not match `registry.machines.dev-primary.repos`.
- **Resolver-source change in `sync-agent-configs.sh` is now correctly scoped as structural.** Discrete deliverables enumerated: new `resolve_machine_roots(machine)` reading registry-first, `--machine` flag, `__TIER1_REPO_ROOT__` render token, post-render unresolved-token scan, post-render stale-nested-path scan, fail-closed on missing registry fields, divergence detector, prior-config backup. No longer framed as a one-line token-add.
- **dev-secondary handled as a gap, not silently locked in.** Registry mutations to dev-secondary are blocked behind `tests/workstations/test_dev_secondary_ground_truth.py` running on ace-linux-2 and recording the live `/mnt/<path>` value. The plan no longer assumes `/mnt/local-analysis` is correct without verification.
- **IntxLNK root cause documented** per memory `feedback_ntfs3_symlink_intxlnk` (in-kernel ntfs3 reading ntfs-3g symlinks as raw byte blobs). Repair `--apply` semantics specified: unlink + ln -s + post-write `file`/`readlink` verification. Mount-fs guard: refuse on ntfs3.
- **Property-broad broken-symlink test** replaces the path-narrow original (parametrized across 3 stale realpaths, not just `/mnt/local-analysis/.claude/skills`).
- **workspace-hub self-case** added: `<repo>/.codex/skills -> ../.claude/skills` is valid when `repo == workspace-hub`.
- **Registry-absent `not_present` test** added for repos like `OGManufacturing` (in registry, not on disk).
- **Test paths corrected** from `tests/harness/` (net-new convention) to `tests/readiness/` (natural co-owner with `scripts/readiness/`) and `tests/workstations/` (host-bound probes).
- **`docs/standards/CONTROL_PLANE_CONTRACT.md` update is REQUIRED.** Previously "if needed"; now explicitly required because the current convergence table contradicts live state.
- **Pre-review push requirement** added: plan + `docs/plans/README.md` index row must be committed and pushed to `main` BEFORE Codex/Gemini are re-invoked (they fetch from main; an out-of-tree plan reproduces the round-1 Codex "404 from main" finding).
- **Shell wrapper status corrected**: `check-sibling-sso-flow.sh` is now marked REQUIRED in the artifact map and files-to-change, matching its load-bearing role in the acceptance criteria.
- **Cross-repo source-control contract** added: per-sibling preflight (ntfs3 / dirty / detached / ahead / untracked / nested-worktree), per-repair branch policy (one branch per repo, conventional commits, no squash, no auto-push), post-write verification, rollback semantics.

**Re-review plan:** T3 (Claude + Codex + Gemini) per `feedback_always_adversarial_review_scale_depth`. Dispatch ONLY after the revised plan and README row are pushed to `main`; verify via `gh api repos/vamseeachanta/workspace-hub/contents/docs/plans/2026-05-21-issue-2775-workspace-hub-sibling-sso-flow.md?ref=main` returns 200.

---

## Risks and Open Questions

- **Risk:** Some sibling repos may intentionally own repo-local skills. Mitigation: require explicit registry/overlay registration before treating repo-local skills as a source; do not delete/dedupe repo-local skills in this issue.
- **Risk:** Fixing provider symlinks across sibling repos can dirty multiple repos. Mitigation: dry-run manifest first; `--apply` requires ONLY live GitHub `status:plan-approved`, ignores local approval markers, serializes writes, blocks dirty/detached/ahead/untracked/ntfs3/nested-worktree targets, and verifies each repo's git state before/after.
- **Risk:** Updating live `~/.hermes/config.yaml` can affect the current agent runtime. Mitigation: patch repo template first, dry-run sync, then update live config only after plan approval and with backup/rollback.
- **Risk:** Parent-level shim files would make broken pointers appear healthy while bypassing the repo-tracked control plane. Mitigation: explicitly reject `/mnt/local-analysis/AGENTS.md` and `/mnt/local-analysis/.claude/skills` as the primary solution.
- **Risk:** `config/workstations/registry.yaml` and `scripts/readiness/harness-config.yaml` currently overlap. Mitigation: make `registry.yaml` authoritative for topology and make harness-config reference or validate against it, not redefine it; dev-secondary reconciliation is blocked until host ground-truth is captured on ace-linux-2.
- **Resolved by first review:** Exact target repo list for first repair wave follows `config/workstations/registry.yaml` for the selected machine. Live absent entries are reported `not_present` unless the registry/check schema marks them required-on-host. Hermes sibling skill roots are registry-derived and on-disk-validated; no standalone overlay list is inferred from live git checkouts or stale Hermes template entries.
- **Resolved by first review:** `digitalmodel` `.codex/skills` / `.gemini/skills` are `IntxLNK` regular files and must be classified as corrupted NTFS symlink artifacts. Root cause and apply semantics are explicit: refuse on `ntfs3`, unlink+symlink+verify only after approval and clean-state gates.

---

## Complexity: T3

**T3** — this is cross-repo, cross-provider harness work that affects Hermes, Codex, Gemini, workstation registry semantics, global live config rendering, sibling repo provider adapters, and `AGENTS.md` contract inheritance. It requires tests before implementation, dry-run/apply safety gates, rollback, and adversarial review before `status:plan-review`. Implementation remains blocked until explicit user approval applies `status:plan-approved`.
