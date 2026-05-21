Adversarial rerun review for revised Issue #2766 plan R6.
Rules: adversarial, no tools, review only the plan text below, cite exact sections, return APPROVE only if ready for status:plan-review.
Grounded facts: #2770 required repos are workspace-hub,digitalmodel,assetutilities,worldenergydata,llm-wiki,assethold; optional aceengineer-website,aceengineer-strategy. Existing readiness warnings-only behavior is status=warn, dispatchable=false, overall_status=warn. R5 blockers were fixed in R6.

Plan:
```markdown
# Plan for #2766: ace-linux-1 checkout normalization and registry reconciliation

> **Status:** draft R6 — R1/R2/R3/R4/R5 adversarial reviews returned MAJOR; this revision addresses R5 compact-review findings; no implementation approval
> **Complexity:** T2
> **Date:** 2026-05-20
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2766

---

## Resource Intelligence Summary

### Live issue and code state

- `config/workstations/registry.yaml` is the current workstation authority. `machines.dev-primary` maps to ace-linux-1 and currently declares `workspace_root: /mnt/local-analysis/workspace-hub`, `tier1_repo_root: /mnt/local-analysis`, `repo_layout: sibling`, `repos`, and `telegram_hermes.data_access_profile.repos`.
- `scripts/readiness/telegram_hermes_readiness.py` already emits top-level `overall_status`, `hosts`, and `errors`; any repo-placement readiness must attach to the relevant host entry, not create ambiguous top-level state.
- Issue #2770 is the ace-linux-1 tier-1 placement decision: required = `workspace-hub`, `digitalmodel`, `assetutilities`, `worldenergydata`, `llm-wiki`, `assethold`; optional = `aceengineer-website`, `aceengineer-strategy`.
- Issue #2766 contains historical relocation evidence for direct nested checkouts already moved out of `/mnt/local-analysis/workspace-hub`. This R5 plan does **not** retroactively authorize those moves; it reconciles and prevents drift.
- Latest live probe found `0` direct nested git repos under `/mnt/local-analysis/workspace-hub` after excluding root self metadata.
- Latest live probe found `/mnt/local-analysis/agent-worktrees` present as a non-git infrastructure directory. It must be explicitly allowed as infrastructure and must not mask git siblings.

### Live ace-linux-1 inventory, verified 2026-05-20T23:34Z-23:45Z

| repo | classification for this issue | branch | ahead/behind | dirty | head | remote |
|---|---|---|---:|---:|---|---|
| `workspace-hub` | required tier-1 control plane | main | 0/0 | 85 | bad2169e | `https://github.com/vamseeachanta/workspace-hub.git` |
| `digitalmodel` | required tier-1 | main | 0/0 | 6 | 8669b0ab | `https://github.com/vamseeachanta/digitalmodel.git` |
| `assetutilities` | required tier-1 | main | 0/0 | 0 | 1122e50d | `https://github.com/vamseeachanta/assetutilities.git` |
| `worldenergydata` | required tier-1 | main | 0/0 | 0 | d647fa7e | `https://github.com/vamseeachanta/worldenergydata.git` |
| `llm-wiki` | required tier-1 | main | 1/0 | 0 | 9b3481c9 | `https://github.com/vamseeachanta/llm-wiki.git` |
| `assethold` | required tier-1 | main | 0/0 | 0 | b2b1131e | `https://github.com/vamseeachanta/assethold.git` |
| `aceengineer-website` | optional tier-1 | main | 0/0 | 0 | 39d2488d | `https://github.com/vamseeachanta/aceengineer-website.git` |
| `aceengineer-strategy` | optional tier-1 | main | 0/0 | 0 | 19a0e054 | `https://github.com/vamseeachanta/aceengineer-strategy.git` |
| `aceengineer-admin` | non-tier-1 machine-access/current | main | 0/0 | 0 | 0ad85b69 | `https://github.com/vamseeachanta/aceengineer-admin` |
| `achantas-data` | non-tier-1 machine-access/current | main | 0/0 | 3 | 764fffe1 | `https://github.com/vamseeachanta/achantas-data` |
| `achantas-media` | non-tier-1 machine-access/current | main | 0/0 | 0 | 0f48048e | `https://github.com/vamseeachanta/achantas-media` |
| `CAD-DEVELOPMENTS` | non-tier-1 machine-access/current | main | 0/0 | 0 | 641ee137 | `https://github.com/bakkiprasad5669/CAD-DEVELOPMENTS` |
| `hobbies` | non-tier-1 machine-access/current | main | 0/0 | 0 | 408399d3 | `https://github.com/vamseeachanta/hobbies.git` |
| `kaggle-rogii-2026` | non-tier-1 machine-access/current | main | 0/0 | 1 | d23e2608 | `https://github.com/vamseeachanta/kaggle-rogii-2026.git` |
| `llm-wiki-acma` | non-tier-1 machine-access/current | main | 0/0 | 0 | 1d813086 | `https://github.com/vamseeachanta/llm-wiki-acma.git` |
| `sabithaandkrishnaestates` | non-tier-1 machine-access/current | main | 0/0 | 0 | 941b96c3 | `https://github.com/vamseeachanta/sabithaandkrishnaestates` |
| `teamresumes` | non-tier-1 machine-access/current | main | 0/0 | 0 | e09c0eb9 | `https://github.com/vamseeachanta/teamresumes` |

Issue-comment-only repos from #2766 that were earlier reported as moved-to-sibling but were absent from the latest top-level git inventory: `acma-projects`, `client_projects`, `doris`, `frontierdeepwater`, `OGManufacturing`, `rock-oil-field`, `saipem`, `sd-work`, `seanation`. This is an explicit **state contradiction/anomaly**: prior issue comments say `sibling=git`; current probe says absent. The implementation must not hide this. It must classify them under `historically_moved_not_currently_present`, preserve source-comment provenance, and emit `historical_state_changed_since_prior_comment` warnings in checker/readiness/report output. `OGManufacturing` is additionally a deliberate runtime-access cleanup: it is currently in `machines.dev-primary.repos` and `telegram_hermes.data_access_profile.repos` but absent on disk and not tier-1 per #2770; this plan removes it from current local/runtime sets only while preserving it as a historical/anomaly entry.

### R1/R2 review evidence

- R1 copies: `scripts/review/results/2026-05-20-plan-2766-r1-claude.md`, `...-r1-codex.md`, `...-r1-gemini.md`, `...-r1-disagreement.md`.
- R2 copies: `scripts/review/results/2026-05-20-plan-2766-r2-claude.md`, `...-r2-codex.md`, `...-r2-gemini.md`, `...-r2-disagreement.md`.
- Base fanout artifact names are not cited as durable evidence because `plan-review-fanout.sh` overwrites them on rerun; suffixed copies must be committed/pushed before any `status:plan-review` transition.

---

## Artifact Map

| Kind | Path |
|---|---|
| Plan | `docs/plans/2026-05-20-issue-2766-ace-linux-1-checkout-normalization.md` |
| Plan index | `docs/plans/README.md` |
| Registry implementation | `config/workstations/registry.yaml` |
| Checker implementation | `scripts/workstations/check-tier1-repo-baseline.py` |
| Readiness implementation | `scripts/readiness/telegram_hermes_readiness.py` |
| Checker tests | `tests/workstations/test_check_tier1_repo_baseline.py` |
| Readiness tests | `tests/readiness/test_telegram_hermes_readiness_tier1_baseline.py` |
| HTML final report | `docs/reports/ace-linux-1-tier1-checkout-normalization.html` |
| HTML report generation path | `scripts/workstations/check-tier1-repo-baseline.py --machine dev-primary --format html --output docs/reports/ace-linux-1-tier1-checkout-normalization.html` |
| Compact R4 prompt | `.planning/quick/review-2766-r4-compact-prompt.md` |
| Compact R5 prompt | `.planning/quick/review-2766-r5-compact-prompt.md` |
| R1/R2/R3/R4 review evidence | `scripts/review/results/2026-05-20-plan-2766-r*-*.md`, including compact R4 artifacts `...-r4-claude-compact.md` and `...-r4-codex-compact.md` |
| R5 review evidence | `scripts/review/results/2026-05-20-plan-2766-r5-claude-compact.md`, `scripts/review/results/2026-05-20-plan-2766-r5-codex-compact.md`, plus matching `.err` files if non-empty |
| Label-time checklist evidence | issue comment on #2766 containing reviewed commit SHA, artifact paths, and `git ls-remote` equality check before applying `status:plan-review` |

---

## Deliverable

Implement a **read-only**, registry-backed ace-linux-1 checkout normalization contract. The implementation must not clone, pull, fetch, push, move, delete, or sync repositories. It only reads filesystem/git metadata, updates workspace-hub registry/checker/readiness code, and emits an HTML evidence report.

---

## Proposed Registry Semantics

`tier1_baseline` is the authoritative placement contract. Existing `machines.dev-primary.repos` becomes a **derived local-checkout allowlist**: it must equal `required + optional + non_tier1_machine_access_current`, sorted or generated by the implementation rule. It must not include `historically_moved_not_currently_present`.

`telegram_hermes.data_access_profile.repos` target for this issue is exactly the required tier-1 set: `workspace-hub`, `digitalmodel`, `assetutilities`, `worldenergydata`, `llm-wiki`, `assethold`. It is a runtime-access subset of `machines.dev-primary.repos`, every entry must be classified in `tier1_baseline` and locally present, and no current non-tier-1, historical, reference-only, or absent repo is included. `OGManufacturing` is intentionally removed from runtime access because it is absent on disk and not tier-1 per #2770. Any future non-tier-1 runtime access requires a separate approved issue.

```yaml
machines:
  dev-primary:
    hostname: ace-linux-1
    repos:  # derived local-checkout allowlist
      - workspace-hub
      - digitalmodel
      - assetutilities
      - worldenergydata
      - llm-wiki
      - assethold
      - aceengineer-website
      - aceengineer-strategy
      - aceengineer-admin
      - achantas-data
      - achantas-media
      - CAD-DEVELOPMENTS
      - hobbies
      - kaggle-rogii-2026
      - llm-wiki-acma
      - sabithaandkrishnaestates
      - teamresumes
    tier1_baseline:
      version: 1
      source_issues:
        tier1_decision: 2770
        relocation_reconciliation: 2766
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
      non_tier1_machine_access_current:
        - aceengineer-admin
        - achantas-data
        - achantas-media
        - CAD-DEVELOPMENTS
        - hobbies
        - kaggle-rogii-2026
        - llm-wiki-acma
        - sabithaandkrishnaestates
        - teamresumes
      historically_moved_not_currently_present:
        acma-projects:
          source_issue: 2766
          source_comment: 4497956095
          prior_claim: sibling=git
          latest_probe: absent
          warning: historical_state_changed_since_prior_comment
        client_projects:
          source_issue: 2766
          source_comment: 4497956095
          prior_claim: sibling=git
          latest_probe: absent
          warning: historical_state_changed_since_prior_comment
        doris:
          source_issue: 2766
          source_comment: 4497956095
          prior_claim: sibling=git
          latest_probe: absent
          warning: historical_state_changed_since_prior_comment
        frontierdeepwater:
          source_issue: 2766
          source_comment: 4497956095
          prior_claim: sibling=git
          latest_probe: absent
          warning: historical_state_changed_since_prior_comment
        OGManufacturing:
          source_issue: 2766
          source_comment: 4497956095
          prior_claim: sibling=git and registry-runtime-access
          latest_probe: absent
          warning: historical_state_changed_since_prior_comment
          runtime_access_change: remove_from_data_access_profile
        rock-oil-field:
          source_issue: 2766
          source_comment: 4497956095
          prior_claim: sibling=git
          latest_probe: absent
          warning: historical_state_changed_since_prior_comment
        saipem:
          source_issue: 2766
          source_comment: 4497956095
          prior_claim: sibling=git
          latest_probe: absent
          warning: historical_state_changed_since_prior_comment
        sd-work:
          source_issue: 2766
          source_comment: 4497956095
          prior_claim: sibling=git
          latest_probe: absent
          warning: historical_state_changed_since_prior_comment
        seanation:
          source_issue: 2766
          source_comment: 4497956095
          prior_claim: sibling=git
          latest_probe: absent
          warning: historical_state_changed_since_prior_comment
      infrastructure_dirs:
        - agent-worktrees
      placement_rules:
        root_git_self_allowed: true
        direct_nested_git_policy: error
        required_absence_policy: error
        optional_absence_policy: warning
        non_tier1_absence_policy: warning
        historical_absence_policy: warning
        historical_state_changed_since_prior_comment_policy: warning
        unknown_sibling_git_policy: warning
        dirty_policy:
          required: warning
          optional: warning
          non_tier1_machine_access_current: warning
        ahead_policy:
          required: warning
          optional: warning
          non_tier1_machine_access_current: warning
```

---

## Pseudocode

```text
parse CLI args: --machine dev-primary (default), --registry config/workstations/registry.yaml, --repo-root optional override, --now optional ISO timestamp for deterministic tests
load registry and machine = machines[args.machine]
if args.machine != "dev-primary": raise ValueError("#2766 checker scope is dev-primary/ace-linux-1 only")
if machine.hostname != "ace-linux-1": raise ValueError("machines.dev-primary.hostname must be ace-linux-1")
if baseline.version != 1: raise ValueError("tier1_baseline.version must be 1")

classification_sets = [
  required,
  optional,
  reference_only,
  not_planned,
  non_tier1_machine_access_current,
  historically_moved_not_currently_present.keys(),
]
if any classification bucket keys overlap: raise ValueError with the overlapping repo names and bucket names
assert machine.repos == required + optional + non_tier1_machine_access_current  # order normalized
assert every data_access_profile repo is in machine.repos
assert every data_access_profile repo is in required ∪ optional ∪ non_tier1_machine_access_current
assert required ⊆ data_access_profile.repos
assert data_access_profile.repos == required
assert historically_moved_not_currently_present.keys() ∩ data_access_profile.repos == ∅

inventory = immediate child git repos under repo_root, treating both child/.git directory and child/.git file as git repos
infra_dirs = baseline.infrastructure_dirs, currently [agent-worktrees]
assert every infra dir either absent or present as a non-git directory at exactly repo_root/<infra_dir>; if repo_root/<infra_dir> itself contains a .git file/dir, warn/error per unknown_sibling_git_policy; do not recurse into child worktrees under agent-worktrees for this issue
nested = immediate children under workspace_root where child/.git directory or child/.git file exists
ignore workspace_root/.git only; do not recurse below immediate children

blockers = []
warnings = []
apply baseline.placement_rules table, not hardcoded severities:
  required absence => severity from required_absence_policy
  optional absence => severity from optional_absence_policy
  current non-tier-1 absence => severity from non_tier1_absence_policy
  historical/anomaly entries are not current-checkout expectations and never produce `missing_current` warnings; they produce only `historical_state_changed_since_prior_comment` warnings when `latest_probe=absent` conflicts with prior_claim=sibling=git
  unknown sibling git repo => severity from unknown_sibling_git_policy unless name in infra_dirs and is non-git directory
  direct nested git dir/gitlink => severity from direct_nested_git_policy
  dirty/ahead state => severity from dirty_policy/ahead_policy by classification
append blockers for severity=error; append warnings for severity=warning

readiness integration:
  host_entry = readiness["hosts"]["dev-primary"]
  host_entry["repo_placement"] = {
    "dispatchable": blockers.empty,
    "blockers": blockers,
    "warnings": warnings,
    "inventory_timestamp_utc": args.now or injected_clock.now_utc(),
    "source": "scripts/workstations/check-tier1-repo-baseline.py",
  }
  if repo_placement.blockers:
    host_entry["failures"].append(repo_placement.blockers_summary)
    host_entry["status"] = "fail"
    host_entry["dispatchable"] = False
  elif repo_placement.warnings:
    host_entry["warnings"].append(repo_placement.warnings_summary)
  # Existing readiness policy verified in scripts/readiness/telegram_hermes_readiness.py lines 407-419:
  # failures => status=fail, dispatchable=false, overall_status=fail; warnings-only => status=warn, dispatchable=false, overall_status=warn.
  # This implementation must preserve that behavior exactly.
  if host_entry["failures"]:
    host_entry["status"] = "fail"
    host_entry["dispatchable"] = False
  elif host_entry["warnings"]:
    host_entry["status"] = "warn"
    host_entry["dispatchable"] = False
  else:
    host_entry["status"] = "pass"
    host_entry["dispatchable"] = True
  recompute overall_status from all host statuses using the existing readiness aggregation rule:
    overall_status = "fail" if any host.status == "fail"
    else "warn" if any host.status in {"warn", "status-only", "not-onboarded"}
    else "pass"
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Modify | `config/workstations/registry.yaml` | Add `hostname: ace-linux-1` if absent; add `tier1_baseline`; update `repos`; set `telegram_hermes.data_access_profile.repos` to exactly the required tier-1 set and remove `OGManufacturing` plus all non-tier-1 runtime access. |
| Create | `scripts/workstations/check-tier1-repo-baseline.py` | Read-only checker with JSON and HTML output. |
| Create | `tests/workstations/test_check_tier1_repo_baseline.py` | TDD coverage for schema, classification, read-only behavior, nested gitdir/gitlink, unknown sibling drift, and historical bucket semantics. |
| Modify | `scripts/readiness/telegram_hermes_readiness.py` | Add host-scoped `repo_placement` and merge its dispatchability into the existing host dispatchability. |
| Create | `tests/readiness/test_telegram_hermes_readiness_tier1_baseline.py` | TDD coverage for host-scoped readiness integration. |
| Create | `docs/reports/ace-linux-1-tier1-checkout-normalization.html` | Human-facing final report. |
| Modify | `docs/plans/README.md` | Upsert one #2766 row; after R3 review, row status must be `plan-review` only if no MAJOR remains. |

---

## TDD Test List

All filesystem and git inputs below are synthetic fixtures unless a test explicitly states it uses the live registry file.

| Test name | Verifies |
|---|---|
| `test_dev_primary_tier1_baseline_schema_v1_matches_2770_decision` | Required/optional sets match #2770. |
| `test_all_classification_buckets_are_pairwise_disjoint_including_non_tier1_and_historical` | No repo can appear in multiple buckets, including non-tier-1 and historical buckets. |
| `test_machine_repos_equals_required_optional_current_non_tier1` | `machines.dev-primary.repos` is the derived local-checkout allowlist and excludes historical entries. |
| `test_data_access_profile_exact_required_set` | `data_access_profile.repos` equals exactly `workspace-hub`, `digitalmodel`, `assetutilities`, `worldenergydata`, `llm-wiki`, `assethold`; it contains no optional, non-tier-1, reference-only, historical, absent, or unclassified repo. |
| `test_historical_entries_have_provenance_schema_and_state_changed_warning` | Every historical entry is a mapping with `source_issue`, `source_comment`, `prior_claim`, `latest_probe`, and `warning`; absent historical entries produce `historical_state_changed_since_prior_comment`, not `missing_current`. |
| `test_workspace_hub_root_git_is_not_reported_as_nested` | Root self `.git` is excluded. |
| `test_direct_nested_git_directory_under_workspace_hub_is_blocker` | Immediate child `.git/` under workspace root blocks. |
| `test_direct_nested_gitlink_under_workspace_hub_is_blocker` | Immediate child `.git` file under workspace root blocks. |
| `test_required_sibling_repos_present` | Required sibling checkouts pass placement blockers. |
| `test_missing_required_repo_blocks_readiness` | Missing required checkout blocks. |
| `test_optional_repo_absence_is_warning_only` | Optional absence warns only. |
| `test_current_non_tier1_absence_is_warning_only` | Missing current non-tier-1 checkout warns only. |
| `test_ogmanufacturing_current_runtime_removal_is_explicit_historical_anomaly` | `OGManufacturing` is removed from current `repos`/data access but preserved under historical/anomaly with source-comment provenance. |
| `test_agent_worktrees_is_allowed_only_as_non_git_infrastructure_dir` | `/mnt/local-analysis/agent-worktrees` is ignored only when non-git; git metadata there is surfaced. |
| `test_unknown_top_level_sibling_git_repo_warns` | Unexpected `/mnt/local-analysis/<repo>` git checkout is surfaced as drift. |
| `test_dirty_and_ahead_states_are_synthetic_warnings_not_blockers` | Synthetic dirty/ahead metadata is reported as warning by policy. |
| `test_checker_is_readonly` | Monkeypatch `subprocess.run`, `subprocess.Popen`, `os.rename`, `os.remove`, `os.unlink`, `shutil.move`, `shutil.rmtree`, `pathlib.Path.unlink`, `pathlib.Path.rename`, and `pathlib.Path.replace`; combine with before/after fixture tree snapshots to prove no clone/fetch/pull/push/mv/rm/delete/sync invocation or filesystem mutation. |
| `test_readiness_payload_adds_host_scoped_repo_placement` | Missing-required blocker appends host failure, sets host status fail, sets host dispatchable false, and recomputes overall status. |
| `test_warning_only_repo_placement_matches_existing_readiness_policy` | With repo-placement warnings only: `status=warn`, `dispatchable=false`, top-level `overall_status=warn`, no `failures`; this matches existing readiness lines 407-419. |
| `test_inventory_timestamp_is_injected_for_deterministic_readiness_payload` | `--now`/injected clock makes readiness output deterministic. |
| `test_html_report_sections_and_data_attributes` | Run checker `--format html` against deterministic synthetic fixture inventory; parse HTML structurally and verify required semantic sections/machine-readable data attributes. |
| `test_plan_index_row_is_upserted_once` | README contains exactly one #2766 row with current status and plan path. |

---

## HTML Report Contract

`docs/reports/ace-linux-1-tier1-checkout-normalization.html` must be self-contained and include semantic sections with stable IDs/data attributes:

- `<section id="summary" data-machine="ace-linux-1">`
- `<section id="required-tier1">` table of required repos and status
- `<section id="optional-tier1">` table of optional repos and status
- `<section id="current-non-tier1-machine-access">` table of current non-tier-1 repos
- `<section id="historical-reconciliation">` table of issue-comment-only historical entries with source issue/comment references
- `<section id="nested-git-check">` nested gitdir/gitlink result
- `<section id="readiness-projection">` JSON snippet or table for host-scoped `repo_placement`
- `<section id="runbook-rollback-policy">` future movement guardrails

Tests must parse HTML structurally, not only grep substrings.

---

## Per-Repo Runbook and Rollback Policy

This issue's implementation does not move repos. The report must preserve this future-move policy:

1. Preflight path, remote, branch, HEAD, upstream ahead/behind, dirty/untracked count, `.git` directory vs gitfile, active cwd processes, target existence, and same-filesystem status.
2. If duplicate and clean: preserve primary sibling and remove duplicate only after independent verification.
3. If unique nested checkout: move only after target absence is proven; rollback before mutation is `mv <target> <source>`.
4. If dirty/untracked: copy or commit artifacts into chosen primary first; verify byte-identical preservation before delete/move.
5. If verification fails: stop, do not continue batch, restore if possible, and comment exact evidence.

---

## Acceptance Criteria

- [ ] Registry contains `machines.dev-primary.tier1_baseline.version: 1` with `source_issues.tier1_decision: 2770` and `source_issues.relocation_reconciliation: 2766`.
- [ ] Required ace-linux-1 tier-1 repos exactly equal `workspace-hub`, `digitalmodel`, `assetutilities`, `worldenergydata`, `llm-wiki`, `assethold`.
- [ ] Optional ace-linux-1 tier-1 repos exactly equal `aceengineer-website`, `aceengineer-strategy`.
- [ ] `machines.dev-primary.repos` equals `required + optional + non_tier1_machine_access_current` and excludes `historically_moved_not_currently_present`.
- [ ] `telegram_hermes.data_access_profile.repos` equals exactly the required tier-1 set: `workspace-hub`, `digitalmodel`, `assetutilities`, `worldenergydata`, `llm-wiki`, `assethold`; it excludes optional, current non-tier-1, reference-only, historical, and absent repos including `OGManufacturing`.
- [ ] Historical issue-comment-only repos absent from live inventory are classified under `historically_moved_not_currently_present` as per-repo provenance mappings (`source_issue`, `source_comment`, `prior_claim`, `latest_probe`, `warning`) and emit `historical_state_changed_since_prior_comment`; no repo is silently dropped.
- [ ] Checker excludes workspace root `.git` but blocks immediate child `.git/` directories and `.git` gitlink files under `/mnt/local-analysis/workspace-hub/<child>`.
- [ ] Severity is driven by `placement_rules`; missing required and direct nested git metadata are blockers by default; missing optional/current-non-tier-1/historical anomaly/unknown sibling/dirty/ahead states are warnings by default.
- [ ] Readiness output contains `hosts.dev-primary.repo_placement`; blockers append host failures, set host status `fail`, dispatchable false, and top-level `overall_status=fail`; warnings-only set host status `warn`, dispatchable false, and top-level `overall_status=warn` with no failures, matching existing readiness lines 407-419.
- [ ] HTML report satisfies the structural section contract above.
- [ ] All tests in the TDD list are written before implementation and pass after implementation.
- [ ] `docs/plans/README.md` contains exactly one #2766 row with this plan path and current gate status.
- [ ] R4/R5 adversarial review artifacts are copied to durable suffixed filenames and committed/pushed before any `status:plan-review` label is applied; label-time operator checklist must verify `git ls-remote` HEAD contains the reviewed plan and review artifacts.

---

## Review Disposition

| Review | Verdict | R3 response |
|---|---|---|
| R1 Claude/Codex | MAJOR | Preserved as `r1-*`; R2 incorporated schema, gitlink, readiness, and historical-state concerns. |
| R2 Claude | MAJOR | Fixed durable review artifact naming, data-access AC, `repos` semantics, disjointness including non-tier-1/historical, historical bucket population, source issue split, synthetic fixture language, falsifiable README AC, HTML structural contract. |
| R2 Codex | MAJOR | Added Artifact Map, changed README action to upsert, fixed historical bucket contradiction, specified host-scoped readiness merge, defined `repos` semantics, added unknown sibling drift test. |
| R3 Claude/Codex | MAJOR | R4 response: classify `OGManufacturing` as explicit historical/runtime-access removal, define machine binding via `--machine dev-primary`, make placement rules table-driven, pin readiness status/failures/overall-status updates, define `agent-worktrees` infrastructure handling, make read-only/timestamp tests falsifiable, and require commit/push before plan-review. |
| R4 compact Claude/Codex | MAJOR | R5 response: exact data-access target set, explicit warning-only readiness outcome, concrete historical provenance schema, distinct historical anomaly warning, HTML generation command, and R4/R5 artifact map cleanup. |
| R5 compact Claude/Codex | MAJOR | R6 response: fixed data-access contradiction, added hostname field, explicit overall_status aggregation, historical mapping-key disjointness, concrete R5 artifact/checklist paths, infra-dir non-recursive scope, readonly monkeypatch surface, and JSON+HTML checker output. |
| Gemini | UNAVAILABLE | Quota/API unavailable; R3 can proceed with Claude+Codex for T2 unless user requests waiting. |

---

## Risks and Open Questions

- Some live repos are dirty or ahead (`workspace-hub`, `digitalmodel`, `llm-wiki`). This plan surfaces that state; it does not clean or sync those repos.
- Historical entries came from #2766 comments, not from current live inventory. The report must clearly label their provenance.
- Closing #2770 is separate. Recommended sequence: #2766 reaches `status:plan-review`, user approves, implementation lands, then #2770 can be closed as consumed by #2766.




```

Required output:
## Verdict
APPROVE | MINOR | MAJOR
## Retrieval adequacy
adequate | inadequate
## Findings
- ...
## Blockers
1. ...
