# Plan for #2766: ops(workstations): ace-linux-1 checkout normalization and registry reconciliation

> **Status:** draft R2 — R1 adversarial review returned MAJOR; this revision addresses R1 findings; no implementation approval
> **Complexity:** T2
> **Date:** 2026-05-20
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2766
> **Review artifacts:** R1: `scripts/review/results/2026-05-20-plan-2766-claude.md`, `scripts/review/results/2026-05-20-plan-2766-codex.md`, `scripts/review/results/2026-05-20-plan-2766-gemini.md`, `scripts/review/results/2026-05-20-plan-2766-disagreement.md`; R2 re-review pending.

---

## Resource Intelligence Summary

### Existing repo code

- Found: `config/workstations/registry.yaml` is the current machine authority. `dev-primary` declares `hostname: ace-linux-1`, `workspace_root: /mnt/local-analysis/workspace-hub`, `tier1_repo_root: /mnt/local-analysis`, `repo_layout: sibling`, and a broad `repos` list.
- Found: `scripts/readiness/telegram_hermes_readiness.py` has a `--registry` option and is the existing readiness surface. This issue must extend that readiness path instead of creating another dispatch authority.
- Found: issue #2770 records the ace-linux-1 placement decision: required = `workspace-hub`, `digitalmodel`, `assetutilities`, `worldenergydata`, `llm-wiki`, `assethold`; optional = `aceengineer-website`, `aceengineer-strategy`; `OGManufacturing` is not a tier-1 decision repo unless later promoted.
- Found: issue #2766 comments record already-executed relocation steps for nested checkouts. This plan is therefore not a fresh move plan; it is a reconciliation, registry, checker, readiness, and final evidence plan for the state already reached plus future drift prevention.
- Gap: no committed `tier1_baseline` projection exists in `config/workstations/registry.yaml` for ace-linux-1.
- Gap: no read-only checker exists yet to verify required sibling checkouts, optional presence/warnings, no direct nested git repos under `workspace-hub`, and classification of non-tier-1 machine-access repos.

### Standards and policy inputs

| Governance source | Status | Use in this plan |
|---|---|---|
| `docs/plans/README.md` / hard gates | applicable | Plan + adversarial review + `status:plan-review` + user approval precede implementation. |
| `.claude/skills/coordination/issue-planning-mode/references/per-machine-repo-placement-outcome-contract.md` | applicable | First machine must leave a reusable registry-backed placement pattern for later machines. |
| Issue #2731 data/repo location contract plan | draft / not yet authoritative | Treated as related prior art only; this plan must not cite #2731 as an already-established sibling-checkout standard. |
| `config/agents/SHARED_SOUL.md` HTML artifact rule | applicable | Final human-facing report should be HTML; harness/plan files remain Markdown per existing `docs/plans/` convention. |

### Issue and document evidence consulted

- Issue #2766 body and comments, including live inventory, per-repo relocation evidence, and remaining nested-repo relocation summary.
- Issue #2770 decision comment for ace-linux-1 placement.
- `docs/plans/2026-05-19-issue-2754-ace-linux-1-throughput-lane-tier1-baseline.md` for the prior throughput-lane baseline.
- `config/workstations/registry.yaml` for current registry state.
- R1 adversarial review artifacts named above.

### Live state evidence, verified 2026-05-20T23:34Z–23:45Z on ace-linux-1

Direct nested git repos below `/mnt/local-analysis/workspace-hub` with root self-excluded: `0`.

Top-level git checkouts under `/mnt/local-analysis` include:

| repo | role for this issue | branch | ahead/behind | dirty | head | remote |
|---|---|---|---:|---:|---|---|
| `workspace-hub` | required tier-1 control plane | main | 0/0 | 85 | bad2169e | `https://github.com/vamseeachanta/workspace-hub.git` |
| `digitalmodel` | required tier-1 | main | 0/0 | 6 | 8669b0ab | `https://github.com/vamseeachanta/digitalmodel.git` |
| `assetutilities` | required tier-1 | main | 0/0 | 0 | 1122e50d | `https://github.com/vamseeachanta/assetutilities.git` |
| `worldenergydata` | required tier-1 | main | 0/0 | 0 | d647fa7e | `https://github.com/vamseeachanta/worldenergydata.git` |
| `llm-wiki` | required tier-1 | main | 1/0 | 0 | 9b3481c9 | `https://github.com/vamseeachanta/llm-wiki.git` |
| `assethold` | required tier-1 | main | 0/0 | 0 | b2b1131e | `https://github.com/vamseeachanta/assethold.git` |
| `aceengineer-website` | optional tier-1 | main | 0/0 | 0 | 39d2488d | `https://github.com/vamseeachanta/aceengineer-website.git` |
| `aceengineer-strategy` | optional tier-1 | main | 0/0 | 0 | 19a0e054 | `https://github.com/vamseeachanta/aceengineer-strategy.git` |
| `aceengineer-admin` | non-tier-1 machine-access | main | 0/0 | 0 | 0ad85b69 | `https://github.com/vamseeachanta/aceengineer-admin` |
| `achantas-data` | non-tier-1 machine-access | main | 0/0 | 3 | 764fffe1 | `https://github.com/vamseeachanta/achantas-data` |
| `achantas-media` | non-tier-1 machine-access | main | 0/0 | 0 | 0f48048e | `https://github.com/vamseeachanta/achantas-media` |
| `CAD-DEVELOPMENTS` | non-tier-1 machine-access | main | 0/0 | 0 | 641ee137 | `https://github.com/bakkiprasad5669/CAD-DEVELOPMENTS` |
| `hobbies` | non-tier-1 machine-access | main | 0/0 | 0 | 408399d3 | `https://github.com/vamseeachanta/hobbies.git` |
| `kaggle-rogii-2026` | non-tier-1 machine-access | main | 0/0 | 1 | d23e2608 | `https://github.com/vamseeachanta/kaggle-rogii-2026.git` |
| `llm-wiki-acma` | non-tier-1 machine-access | main | 0/0 | 0 | 1d813086 | `https://github.com/vamseeachanta/llm-wiki-acma.git` |
| `sabithaandkrishnaestates` | non-tier-1 machine-access | main | 0/0 | 0 | 941b96c3 | `https://github.com/vamseeachanta/sabithaandkrishnaestates` |
| `teamresumes` | non-tier-1 machine-access | main | 0/0 | 0 | e09c0eb9 | `https://github.com/vamseeachanta/teamresumes` |

Known issue-comment evidence also names additional non-tier-1 repos moved earlier (`acma-projects`, `client_projects`, `doris`, `frontierdeepwater`, `OGManufacturing`, `rock-oil-field`, `saipem`, `sd-work`, `seanation`). They were not present in the latest top-level git inventory; the implementation report must reconcile them as `historically_moved_not_currently_present` or equivalent, not ignore them.

---

## Deliverable

A registry-backed, test-covered ace-linux-1 checkout normalization contract that:

1. records the #2770 placement decision in `config/workstations/registry.yaml`,
2. verifies the current sibling checkout state without cloning, moving, deleting, or syncing repos,
3. rejects future direct nested git repos under `workspace-hub` while excluding `workspace-hub`'s own root `.git`,
4. distinguishes `.git/` directories from `.git` gitlink files,
5. classifies non-tier-1 machine-access repos affected by #2766,
6. feeds readiness output with distinct `repo_placement` findings, and
7. publishes an HTML final evidence report with inventory, runbook/rollback policy, and issue-comment reconciliation.

---

## Proposed Registry Schema

Add a concrete `tier1_baseline` mapping under `machines.dev-primary`:

```yaml
machines:
  dev-primary:
    repos:
      - workspace-hub
      - digitalmodel
      - assetutilities
      - worldenergydata
      - llm-wiki
      - assethold
      - aceengineer-website
      - aceengineer-strategy
      - OGManufacturing
    tier1_baseline:
      version: 1
      source_issue: 2770
      repo_root: /mnt/local-analysis
      workspace_root: /mnt/local-analysis/workspace-hub
      layout: sibling
      required:
        - workspace-hub
        - digitalmodel
        - assetutilities
        - worldenergydata
        - llm-wiki
        - assethold
      optional:
        - aceengineer-website
        - aceengineer-strategy
      reference_only: []
      not_planned: []
      non_tier1_machine_access:
        - OGManufacturing
        - aceengineer-admin
        - achantas-data
        - achantas-media
        - acma-projects
        - CAD-DEVELOPMENTS
        - client_projects
        - doris
        - frontierdeepwater
        - hobbies
        - kaggle-rogii-2026
        - llm-wiki-acma
        - rock-oil-field
        - sabithaandkrishnaestates
        - saipem
        - sd-work
        - seanation
        - teamresumes
      historically_moved_not_currently_present: []
      placement_rules:
        root_git_self_allowed: true
        direct_nested_git_policy: error
        optional_absence_policy: warning
        non_tier1_absence_policy: warning
        dirty_policy:
          required: warning
          optional: warning
          non_tier1_machine_access: warning
        ahead_policy:
          required: warning
          optional: warning
          non_tier1_machine_access: warning
```

Reconciliation rule: `telegram_hermes.data_access_profile.repos` must include all `required` tier-1 repos needed for dispatch data access. It may include `non_tier1_machine_access` repos such as `OGManufacturing`, but such entries must also be explicitly classified under `tier1_baseline.non_tier1_machine_access`; no unclassified overlap is allowed.

---

## Pseudocode

```text
function load_registry(path):
    machine = registry.machines.dev-primary
    assert machine.hostname == "ace-linux-1"
    assert machine.tier1_baseline.version == 1
    assert machine.tier1_baseline.layout == "sibling"
    return machine

function validate_registry_baseline(machine):
    required = set(machine.tier1_baseline.required)
    optional = set(machine.tier1_baseline.optional)
    non_tier1 = set(machine.tier1_baseline.non_tier1_machine_access)
    assert required == {workspace-hub, digitalmodel, assetutilities, worldenergydata, llm-wiki, assethold}
    assert optional == {aceengineer-website, aceengineer-strategy}
    assert required, optional, reference_only, not_planned are pairwise disjoint
    assert every data_access_profile repo appears in required ∪ optional ∪ non_tier1 ∪ reference_only
    assert no repo appears in machine.repos without classification, except explicitly ignored infrastructure dirs

function discover_top_level_git_repos(repo_root):
    for each immediate child of repo_root:
        if child/.git is directory OR child/.git is file:
            collect repo name, branch, remote, HEAD, ahead/behind if upstream exists, dirty count

function discover_direct_nested_git_repos(workspace_root):
    for each immediate child under workspace_root only:
        if child name == ".git": ignore root self metadata
        if child/.git is directory: emit nested_git_dir error
        if child/.git is file: emit nested_gitlink error
    do not recurse into .claude/worktrees or /mnt/local-analysis/agent-worktrees; those are separate worktree lanes

function evaluate(machine, inventory):
    missing_required = required - inventory.top_level_names - {workspace-hub if workspace_root is git repo}
    missing_optional = optional - inventory.top_level_names
    missing_non_tier1 = non_tier1 - inventory.top_level_names
    blockers = nested_git_errors + missing_required
    warnings = missing_optional + missing_non_tier1 + dirty/ahead states by policy
    return structured result

function readiness_projection(result):
    append readiness.repo_placement = {
      dispatchable: result.blockers.empty,
      blockers: result.blockers,
      warnings: result.warnings,
      inventory_timestamp_utc: now,
      source: "scripts/workstations/check-tier1-repo-baseline.py"
    }
    do not modify filesystems or run git pull/push/fetch/mv/rm/clone
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Modify | `config/workstations/registry.yaml` | Add concrete ace-linux-1 `tier1_baseline` schema and reconcile `repos` / `data_access_profile.repos`. |
| Create | `scripts/workstations/check-tier1-repo-baseline.py` | Read-only placement checker with JSON output. |
| Create | `tests/workstations/test_check_tier1_repo_baseline.py` | TDD coverage for schema, path, classification, gitdir/gitlink, and read-only behavior. |
| Modify | `scripts/readiness/telegram_hermes_readiness.py` | Import or subprocess checker and add `repo_placement` readiness section. |
| Create/Modify | `tests/readiness/test_telegram_hermes_readiness_tier1_baseline.py` | TDD coverage for readiness integration and blocker/warning separation. |
| Create | `docs/reports/ace-linux-1-tier1-checkout-normalization.html` | Human-facing final evidence report: live inventory, #2766 issue-comment reconciliation, per-repo runbook status, rollback policy. |
| Modify | `docs/plans/README.md` | Only refine the existing #2766 row status/notes after this plan passes review; do not add a duplicate index row. |

---

## TDD Test List

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| `test_dev_primary_tier1_baseline_schema_v1_matches_2770_decision` | Concrete schema path and required/optional sets. | Registry fixture with `machines.dev-primary.tier1_baseline.version: 1`. | Required/optional sets exactly match #2770. |
| `test_registry_repos_are_classified_or_explicitly_ignored` | No silent drift among `repos`, `data_access_profile.repos`, and baseline classification buckets. | Registry fixture including `OGManufacturing`. | `OGManufacturing` accepted only under `non_tier1_machine_access`; unclassified repo fails. |
| `test_data_access_profile_includes_required_repos_and_allows_classified_non_tier1` | Reconciliation rule for dispatch data access. | Fixture missing `llm-wiki` from `data_access_profile.repos`; fixture including classified `OGManufacturing`. | Missing required dispatch repo fails; classified `OGManufacturing` passes as non-tier-1. |
| `test_workspace_hub_root_git_is_not_reported_as_nested` | Self-exclusion boundary. | Fake filesystem with `/root/workspace-hub/.git`. | No nested-git error. |
| `test_direct_nested_git_directory_under_workspace_hub_is_blocker` | Nested repo directory rejection. | Fake filesystem with `/root/workspace-hub/digitalmodel/.git/`. | Blocker `nested_git_dir` names path. |
| `test_direct_nested_gitlink_under_workspace_hub_is_blocker` | Worktree/gitfile rejection. | Fake filesystem with `/root/workspace-hub/digitalmodel/.git` as file. | Blocker `nested_gitlink` names path. |
| `test_required_sibling_repos_present` | Required placement. | Fixture with all required repos at `/mnt/local-analysis/<repo>` plus root `workspace-hub`. | `dispatchable=true` for placement blockers, warnings allowed. |
| `test_missing_required_repo_blocks_readiness` | Missing required checkout is a blocker. | Fixture missing `llm-wiki`. | JSON contains `repo_placement.dispatchable=false` and blocker `missing_required_repo: llm-wiki`. |
| `test_optional_repo_absence_is_warning_only` | Optional absence does not block. | Fixture missing `aceengineer-website`. | JSON contains warning `missing_optional_repo: aceengineer-website`; `dispatchable` unchanged by that warning. |
| `test_non_tier1_absence_is_warning_only` | Non-tier-1 registry entries such as `OGManufacturing` may be absent without blocking. | Fixture missing `OGManufacturing`. | Warning `missing_non_tier1_machine_access: OGManufacturing`; no blocker. |
| `test_dirty_and_ahead_states_are_warnings_not_repo_placement_blockers` | Dirty/ahead policy is explicit. | Fixture with dirty `workspace-hub` and ahead `llm-wiki`. | Warnings include dirty/ahead records; placement dispatchability remains governed by missing/nested blockers. |
| `test_checker_is_readonly` | No clone/move/delete/sync/fetch/pull/push. | Monkeypatched subprocess/filesystem mutators. | Checker performs only stat/list/read-only git metadata commands. |
| `test_readiness_payload_adds_repo_placement_section` | Existing readiness script receives checker result. | Fixture checker JSON with one missing required repo. | Readiness JSON includes `repo_placement.blockers`, separate from provider/env blockers. |
| `test_html_report_includes_issue_comment_reconciliation` | Final report covers #2766 historical moves and latest inventory. | Fixture with issue-comment moved repo list and current inventory. | HTML contains current, missing/historical, required, optional, non-tier-1 tables. |

---

## Per-Repo Runbook and Rollback Policy

This plan does not authorize additional repo movement. It records the policy the final report must preserve for any future move/removal request:

1. **Preflight per repo:** record path, remote, branch, HEAD, upstream ahead/behind, dirty/untracked count, `.git` directory vs gitfile, active processes with cwd under path, target path existence, same-filesystem status.
2. **If clean duplicate and target verified:** preserve primary sibling; remove nested duplicate only after independent verification and issue comment evidence.
3. **If unique nested checkout:** move with `mv` only after target absence is proven; rollback is `mv <target> <source>` before any subsequent mutation.
4. **If dirty/untracked:** copy or commit/merge artifacts into chosen primary first; verify byte-identical preservation before delete/move.
5. **If post-move verification fails:** stop; do not continue batch; restore from source/target backup if available; comment issue with blocker and exact command/evidence.

For #2766 closeout, the HTML report must reconcile already-recorded comments against this runbook, identify any gaps as historical evidence gaps, and avoid pretending future approval can retroactively authorize prior operations.

---

## Acceptance Criteria

- [ ] `config/workstations/registry.yaml` contains `machines.dev-primary.tier1_baseline.version: 1` with the schema above.
- [ ] Required ace-linux-1 tier-1 repos are exactly: `workspace-hub`, `digitalmodel`, `assetutilities`, `worldenergydata`, `llm-wiki`, `assethold`.
- [ ] Optional ace-linux-1 tier-1 repos are exactly: `aceengineer-website`, `aceengineer-strategy`.
- [ ] `OGManufacturing` and other affected machine-access repos are explicitly classified outside the tier-1 decision set or as `historically_moved_not_currently_present`; no affected repo from #2766 comments is silently omitted.
- [ ] Checker excludes `workspace-hub` root `.git` but blocks direct nested child `.git/` directories and `.git` gitlink files under `/mnt/local-analysis/workspace-hub/<child>`.
- [ ] Missing required repos are blockers; missing optional and missing non-tier-1 machine-access repos are warnings.
- [ ] Dirty/ahead/behind required-repo states are warnings in `repo_placement` unless a later policy explicitly promotes them to blockers; they must be surfaced separately from missing/nested blockers.
- [ ] Readiness output contains a `repo_placement` section with `dispatchable`, `blockers`, `warnings`, `inventory_timestamp_utc`, and `source`.
- [ ] `docs/reports/ace-linux-1-tier1-checkout-normalization.html` contains live inventory, #2766 issue-comment reconciliation, runbook/rollback policy, and final path state evidence.
- [ ] Checker and readiness integration have tests proving read-only behavior; implementation performs no clone/move/delete/sync/fetch/pull/push.
- [ ] `docs/plans/README.md` existing #2766 row is updated only after the re-review result is known.

---

## Adversarial Review Summary

| Provider | R1 Verdict | R1 disposition in R2 |
|---|---|---|
| Claude | MAJOR | Addressed undefined schema, self `.git` exclusion, gitlink hazard, data-access reconciliation, readiness payload shape, TDD hedges, non-falsifiable ACs, stale #2731 authority claim, index drift. |
| Codex | MAJOR | Addressed issue deliverable coverage, stale already-moved state, affected repo enumeration, gitlink hazard, dirty/ahead policy, HTML report artifact. Artifact not on GitHub `main` remains a publication gap until selected plan/review files are committed/pushed. |
| Gemini | UNAVAILABLE | Quota exhausted; no signal. R2 can proceed with Claude+Codex for T2 unless the user specifically requests waiting for Gemini quota. |

**Overall R1 result:** MAJOR — no `status:plan-review` until R2 review returns no MAJOR findings and selected artifacts are published.

---

## Risks and Open Questions

- **Risk:** #2766 includes already-executed relocation commands before this R2 plan. The implementation must report them as historical facts and close evidence gaps rather than implying this plan authorized them.
- **Risk:** `workspace-hub`, `digitalmodel`, and `llm-wiki` currently have dirty/ahead states. This plan classifies those as visibility/readiness warnings, not repo-placement blockers; separate sync/dirty cleanup may still block other workflows.
- **Risk:** Some repos named in #2766 comments are absent from the latest top-level inventory. The final report must distinguish `not currently present` from `not affected`.
- **Open:** Whether #2770 should be closed as decision-captured is independent from #2766 implementation approval. Recommended handling: leave #2770 open until #2766 reaches `status:plan-review`, then close #2770 with a link to the reviewed decision-consuming plan, without adding `status:plan-approved` to #2766.

---

## Complexity: T2

T2 because implementation is bounded to registry schema, read-only checker, readiness projection, tests, and one HTML evidence report. R2 review should use two providers by default (Claude + Codex). Gemini may be added if quota is available, but unavailable Gemini should not block a T2 re-review when two independent reviews are available.
