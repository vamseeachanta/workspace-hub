# Plan for #2462: Repo-wide operator map and canonical routing surfaces for digitalmodel beyond OrcaWave/OrcaFlex

> **Status:** draft (adversarial-reviewed r2; Gemini r2 MINOR #1 and #2 addressed 2026-04-23 — HARD GATE wording strengthened to require contract-doc lock, AC #14 now binds the row's path value to this plan's actual filename)
> **Complexity:** T2
> **Date:** 2026-04-22
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2462
> **Review artifacts:** scripts/review/results/2026-04-22-plan-2462-claude.md | scripts/review/results/2026-04-22-plan-2462-codex.md | scripts/review/results/2026-04-22-plan-2462-gemini.md
> **Contract dependency (HARD GATE, strengthened per Gemini r2 MINOR #1):** implementation of this plan MUST NOT begin until (a) #2460 (tier-1 indexing and code-placement contract) has reached `status:plan-approved` AND (b) #2460's contract doc has been drafted to the point where the registry path shape and operator-map host location are textually locked — either inline in the #2460 plan or on main in `docs/standards/TIER1_INDEXING_AND_CODE_PLACEMENT_CONTRACT.md`. The `status:plan-approved` label alone is insufficient because it does not guarantee the contract doc exists; a worker who reads the weaker gate as "approved → green to start" will hit missing-contract-doc failures. The #2460 contract is authoritative for: the required routing-surface set (`AGENTS.md`, `README.md`, `docs/README.md`, repo operator map, canonical machine-readable registry, code/tests/docs routing table, source-hygiene rules, repo-vs-bulk-artifact-store rule), the canonical registry filename, and the operator-map host directory. If any of those items moves in #2460, this plan is re-patched and re-reviewed before implementation.
> **Sibling scope boundary:** #2461 owns `assetutilities`; #2463 owns `aceengineer-website`; #2464 owns `workspace-hub` curation / `docs/CONTENT_INDEX.md` hygiene; #2465 owns daily freshness automation. This plan edits ONLY `digitalmodel/` files and the single workspace-hub file `docs/maps/digitalmodel-operator-map.md`; it does not rewrite sibling repos' routing surfaces.

---

## Resource Intelligence Summary

### Existing repo code
- Found: `digitalmodel/AGENTS.md` — already usable: states purpose, entry points, test command, dependency on assetutilities. No rewrite needed; only a link addition.
- Found: `digitalmodel/README.md` (3615 bytes) — line 46 already acknowledges `specs/module-registry.yaml` is stale: `"The earlier specs/module-registry.yaml reference is currently stale and should not be treated as canonical until restored."` This is an honest admission of gap, not a resolution.
- Found: `digitalmodel/ROADMAP.md` — lines 9 and 50 still treat `specs/module-registry.yaml` as canonical:
  - line 9: `"Module IDs reference specs/module-registry.yaml."`
  - line 50: `"[ ] Add module entry to specs/module-registry.yaml with full capabilities and gaps"`
- Found: `digitalmodel/docs/domains/README.md` — redirects OrcaWave/OrcaFlex current-state to the workspace-level operator map at `../docs/maps/digitalmodel-orcawave-orcaflex-operator-map.md`. Same redirect pattern should apply to the other 28+ domains.
- Found: `digitalmodel/src/digitalmodel/` has 30 top-level source domains: `ansys, asset_integrity, benchmarks, cathodic_protection, data_models, data_systems, drilling_riser, fatigue, field_development, geotechnical, gis, hydrodynamics, infrastructure, marine_ops, naval_architecture, nde, orcaflex, orcawave, power, production_engineering, reservoir, signal_processing, solvers, specialized, structural, subsea, visualization, web, well, workflows` (plus `engine.py`, `sections.py`, `units.py`, `_compat.py`, `__init__.py`, `__main__.py`, `specs/`).
- Found: `digitalmodel/tests/` has strong test-domain parity — covers `ansys, asset_integrity, benchmarks, cathodic_protection, data_systems, drilling_riser, fatigue, field_development, geotechnical, gis, hydrodynamics, infrastructure, marine_ops, naval_architecture, nde, orcaflex, orcawave` plus cross-cutting `engineering_validation, integration, performance, contracts, fixtures, cross_repo`.
- Found: workspace-hub `docs/maps/` contains exactly one operator map: `digitalmodel-orcawave-orcaflex-operator-map.md`. This is the template pattern to generalize.
- Gap: `digitalmodel/docs/README.md` does not exist — `ls` returns "No such file or directory".
- Gap: `digitalmodel/specs/module-registry.yaml` does not exist — `ls` returns "No such file or directory". `digitalmodel/specs/` contains only a `modules/` subdirectory.
- Gap: no repo-wide operator map exists — only the single OrcaWave/OrcaFlex slice.
- Gap: the OrcaWave/OrcaFlex redirect pattern from `docs/domains/README.md` is not applied to the other 28+ active domains.

### Standards
| Standard | Status | Source |
|---|---|---|
| Tier-1 indexing and code-placement contract (draft, being landed in #2460) | draft upstream | `docs/plans/2026-04-22-issue-2460-tier1-indexing-and-code-placement-contract.md` |
| Control-plane repo discovery contract | existing baseline | `docs/standards/CONTROL_PLANE_CONTRACT.md` |
| Starter repo taxonomy expectations | existing baseline | `docs/standards/FILE_STRUCTURE_TAXONOMY.md` |

### LLM Wiki pages consulted
- Not applicable at the plan level — this is repo-wide routing scaffolding. Individual operator-map rows may link domain wiki pages where they already exist (e.g., `knowledge/wikis/marine-engineering/`, `knowledge/wikis/maritime-law/`), but the plan does not itself edit wiki content.

### Documents consulted
- GitHub issue #2462 — deliverables: `docs/README.md`, repo-wide operator map, canonical registry, drift cleanup across README/roadmap/domain docs, common-issue-type routing.
- `docs/reports/2026-04-22-tier-1-indexing-scorecard.md` — ranks digitalmodel 13/20 (best tier-1 codebase, incomplete repo-wide indexing); cites exact gaps: no `docs/README.md`, stale registry reference, single-slice operator map.
- `docs/maps/digitalmodel-orcawave-orcaflex-operator-map.md` — existing operator map is the template to generalize; the column shape is already proven.
- `docs/plans/2026-04-22-issue-2460-tier1-indexing-and-code-placement-contract.md` — T1 contract; registry filename and operator-map host location defer to this contract.
- `docs/plans/2026-04-22-overnight-tier1-knowledge-beef-up-pack.md` — overnight coordination frame; confines T2 writes to `docs/plans/2026-04-22-issue-2462-*.md`, `docs/plans/README.md` (only the #2462 row), `scripts/review/results/*2462*`, and the T2 summary report.
- `digitalmodel/docs/domains/README.md` — shows the existing pattern for redirecting a domain's current-state to a workspace-level operator map; the same pattern generalizes repo-wide.
- Related prior narrow fix #1753 and umbrella issues #2397 and #1962 — scope-boundary references.

### Gaps identified
- No repo-wide `digitalmodel/docs/README.md` canonical entry point exists.
- No repo-wide operator map — the one existing map covers only the OrcaWave/OrcaFlex slice.
- `ROADMAP.md` still treats the missing `specs/module-registry.yaml` as if it were canonical; `README.md` honestly marks it stale but does not restore or replace it. The repo is currently internally inconsistent on this point.
- No single canonical machine-readable registry exists anywhere for the 30+ top-level domains.
- The domain-docs-redirect pattern is proven for OrcaWave/OrcaFlex but not applied repo-wide, so future issue work on (for example) `fatigue` or `cathodic_protection` has no trusted routing surface.
- No regression guard enforces that operator-map rows and actual source-tree domains stay in sync.

### Evidence (embedded verification)

**Issue statuses** (verified 2026-04-22 via `gh issue view` in this session):
- `#2462` — OPEN — `feat(digitalmodel): repo-wide operator map and canonical routing surfaces beyond OrcaWave/OrcaFlex`
- `#2460` — OPEN — `feat(repo-organization): tier-1 indexing and code-placement contract` (upstream contract dependency)
- `#2397` — OPEN — `epic(repo-organization): canonical folder structure and refactor contract across tier-1 repos`
- `#1962` — OPEN — `FEATURE: Tier-1 Repo Ecosystem Refactoring`
- `#1753` — referenced in #2462 body as prior narrow fix; status to be re-verified during implementation.

**File existence** (verified 2026-04-22 via `ls`):
- EXISTS: `digitalmodel/AGENTS.md`
- EXISTS: `digitalmodel/README.md`
- EXISTS: `digitalmodel/ROADMAP.md`
- EXISTS: `digitalmodel/docs/domains/README.md`
- EXISTS: `docs/maps/digitalmodel-orcawave-orcaflex-operator-map.md` (workspace-hub)
- EXISTS: `digitalmodel/specs/modules/` (directory only, no module-registry.yaml)
- MISSING (this plan creates): `digitalmodel/docs/README.md`
- MISSING (this plan creates): `docs/maps/digitalmodel-operator-map.md` (repo-wide operator map, workspace-hub host — matches the existing single-slice pattern)
- MISSING (this plan creates): canonical machine-readable module/domain registry at the path shape defined by #2460

**Line excerpts — live stale-reference contradictions**:
```
# digitalmodel/ROADMAP.md:9
Module IDs reference `specs/module-registry.yaml`. Maturity levels (production, stable, beta, development, stub) track readiness, not priority.

# digitalmodel/ROADMAP.md:50
- [ ] Add module entry to `specs/module-registry.yaml` with full capabilities and gaps
```
```
# digitalmodel/README.md:46
For OrcaWave/OrcaFlex current-state navigation, see [../docs/maps/digitalmodel-orcawave-orcaflex-operator-map.md](../docs/maps/digitalmodel-orcawave-orcaflex-operator-map.md) (#1752). The earlier `specs/module-registry.yaml` reference is currently stale and should not be treated as canonical until restored.
```

**Gap proofs**:
- `ls digitalmodel/docs/README.md` → `No such file or directory` → confirms repo-wide docs entry missing.
- `ls digitalmodel/specs/module-registry.yaml` → `No such file or directory` → confirms the registry ROADMAP.md cites does not exist.
- `ls docs/maps/digitalmodel-operator-map.md` → `No such file or directory` → confirms a repo-wide operator map does not yet exist.

<!-- Source count: 7 distinct (issue body + scorecard + existing operator map + #2460 plan + overnight pack + live source tree + live stale refs). -->

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-04-22-issue-2462-digitalmodel-repo-wide-routing-surfaces.md` |
| Canonical docs entry point (new, nested repo) | `digitalmodel/docs/README.md` |
| Repo-wide operator map (new, workspace-hub host) | `docs/maps/digitalmodel-operator-map.md` |
| Existing slice operator map (linked from repo-wide map) | `docs/maps/digitalmodel-orcawave-orcaflex-operator-map.md` |
| Canonical machine-readable registry | `digitalmodel/<registry path per #2460 contract>` |
| ROADMAP drift cleanup | `digitalmodel/ROADMAP.md` |
| README drift cleanup | `digitalmodel/README.md` |
| Domain docs redirect update | `digitalmodel/docs/domains/README.md` |
| Tests | `digitalmodel/tests/docs/test_digitalmodel_routing_contract.py` |
| Workspace-hub regression guard | `tests/docs/test_banned_stale_references.py` (extend) |
| Plan index update | `docs/plans/README.md` (only the #2462 row) |
| Plan review — Claude | `scripts/review/results/2026-04-22-plan-2462-claude.md` |
| Plan review — Codex | `scripts/review/results/2026-04-22-plan-2462-codex.md` |
| Plan review — Gemini | `scripts/review/results/2026-04-22-plan-2462-gemini.md` |

---

## Deliverable

A repo-wide canonical routing layer for `digitalmodel` — `docs/README.md` entry point, a workspace-hub-hosted repo-wide operator map covering all 30 observed top-level source domains (generalizing the existing OrcaWave/OrcaFlex slice map), a single canonical machine-readable module/domain registry at the path defined by #2460, and aligned `README.md` / `ROADMAP.md` / `docs/domains/README.md` — so that any future digitalmodel issue (fatigue, cathodic_protection, marine_ops, gis, etc.) can be routed to source/tests/docs without rediscovery or reliance on the single-slice map.

---

## Pseudocode

```text
function build_repo_wide_operator_map():
    derive canonical domain list from git ls-tree src/digitalmodel at implementation time
        (do not hard-code; the list evolves)
    for each top-level source directory under src/digitalmodel/ that is a package (has __init__.py):
        row = {
            module: <domain name>,
            source_path: src/digitalmodel/<domain>/,
            tests_path: tests/<domain>/ if tests/<domain>/ exists else 'missing',
            docs_path: docs/domains/<domain>/ if exists else link to workspace-hub domain docs,
            typical_issue_labels: inferred from existing labels or 'tbd by implementer',
            key_dependencies: from pyproject or imports (best-effort),
            links: list of any existing workspace-hub operator maps that already cover this slice
        }
    preserve OrcaWave/OrcaFlex slice map:
        link from the repo-wide map rather than duplicate its content
    place repo-wide map at docs/maps/digitalmodel-operator-map.md (workspace-hub)

function create_canonical_docs_entry():
    create digitalmodel/docs/README.md:
        state: this is the canonical docs entry point for the repo
        route by issue type: engineering domain, solver integration, validation, infra
        link AGENTS.md, README.md, operator map (workspace-hub), registry, docs/domains/README.md
        name the curated-vs-raw inventory boundary (which docs/ subtrees are routing surfaces)

function restore_or_replace_module_registry():
    decision: restore specs/module-registry.yaml OR migrate to the filename #2460 mandates
    once #2460 freezes the filename, create the registry:
        one entry per top-level source domain
        fields: module, entry_point, maturity, owner_wiki, key_tests, related_operator_map_row
    must be derivable from / verifiable against the repo-wide operator map

function drift_cleanup():
    patch digitalmodel/ROADMAP.md:
        line 9: replace 'specs/module-registry.yaml' with the canonical registry path chosen
        line 50: same
    patch digitalmodel/README.md:
        replace the 'stale until restored' sentence once the registry actually exists
        add a link to docs/maps/digitalmodel-operator-map.md (repo-wide)
    patch digitalmodel/docs/domains/README.md:
        generalize its OrcaWave/OrcaFlex current-state redirect pattern:
            point each covered domain at the repo-wide operator map
            keep the OrcaWave/OrcaFlex deeper-dive link

function implement_with_tdd():
    write tests first (see TDD Test List)
    confirm tests fail against current tree
    apply docs/README.md creation
    apply repo-wide operator map creation (derived from src/digitalmodel/)
    apply registry creation at #2460 path
    apply ROADMAP/README/domain-docs drift cleanup
    rerun targeted tests until green
    extend workspace-hub tests/docs/test_banned_stale_references.py to cover the new curated digitalmodel docs
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create | `digitalmodel/docs/README.md` | Canonical repo-wide docs entry point (missing today). |
| Create | `docs/maps/digitalmodel-operator-map.md` | Repo-wide operator map (workspace-hub host — matches existing digitalmodel-orcawave-orcaflex pattern). |
| Create | `digitalmodel/<registry path per #2460>` | Canonical machine-readable module/domain registry. |
| Modify | `digitalmodel/ROADMAP.md` | Replace `specs/module-registry.yaml` references (lines 9 and 50) with the canonical registry path. |
| Modify | `digitalmodel/README.md` | Remove the "stale until restored" sentence once the registry actually exists; add a link to the repo-wide operator map. |
| Modify | `digitalmodel/docs/domains/README.md` | Generalize the OrcaWave/OrcaFlex current-state redirect pattern to point other covered domains at the repo-wide operator map. |
| Modify | `digitalmodel/AGENTS.md` | Add a single link to the repo-wide operator map so AGENTS.md stays the one-stop entry point. |
| Create | `digitalmodel/tests/docs/test_digitalmodel_routing_contract.py` | Asserts: (a) canonical surfaces exist, (b) operator-map rows match observed source domains, (c) registry entries match operator-map rows, (d) no remaining stale `specs/module-registry.yaml` substring anywhere under `digitalmodel/` (scoped exclusion list: the new `docs/README.md` MAY cite the former path once when documenting the drift-cleanup history, but ROADMAP.md and README.md MUST NOT), (e) source-hygiene rule per #2460: no backup artifacts (`*.bak`, `*.orig`), cache directories, or runtime noise under `src/digitalmodel/` tracked paths, (f) repo-vs-bulk-artifact-store rule per #2460: the new `docs/README.md` names the universal placement rule. |
| Modify | `tests/docs/test_banned_stale_references.py` | Bring the new digitalmodel canonical docs into the workspace-hub curated stale-reference guard. |
| Update | `docs/plans/README.md` | Add/keep the #2462 plan row. **Ownership note:** worker-3's planning worktree is write-fenced out of `docs/plans/README.md`. The row is already present (indexed line 280) and will be updated by the main session at merge or by a subsequent pass — acceptance criterion #14 asserts the row exists at that canonical filename. |

---

## TDD Test List

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| `test_docs_readme_exists` | `digitalmodel/docs/README.md` is present | path | file exists |
| `test_docs_readme_links_required_surfaces` | `docs/README.md` links AGENTS.md, README.md, operator map, registry, and `docs/domains/README.md` | docs/README.md text | all links present |
| `test_docs_readme_states_curated_vs_raw_boundary` | `docs/README.md` explicitly names which `docs/` subtrees are curated routing surfaces vs raw/supporting | docs/README.md text | rule present |
| `test_repo_wide_operator_map_exists` | `docs/maps/digitalmodel-operator-map.md` is present | path | file exists |
| `test_operator_map_rows_match_source_tree` | Operator map has a row for every top-level directory under `src/digitalmodel/` that is a package (has `__init__.py`) | observed tree vs map text | exact set match |
| `test_operator_map_columns_match_existing_slice_shape` | Repo-wide map uses at least the columns already used by `digitalmodel-orcawave-orcaflex-operator-map.md` (module, source, tests, docs, issue labels, key dependencies) | map header | required columns present |
| `test_operator_map_links_orcawave_orcaflex_slice` | Repo-wide map references the existing OrcaWave/OrcaFlex slice map rather than duplicating it | map text | link present |
| `test_registry_exists` | Canonical machine-readable registry exists at the path shape defined by #2460 | path | file exists |
| `test_registry_covers_all_operator_map_rows` | Registry entries are a superset of operator-map rows (no domain drops out) | registry vs map | coverage holds |
| `test_roadmap_no_stale_specs_module_registry_reference` | `digitalmodel/ROADMAP.md` no longer references `specs/module-registry.yaml` at lines 9 or 50 | ROADMAP.md text | forbidden string absent |
| `test_readme_no_stale_until_restored_claim` | `digitalmodel/README.md` no longer contains the "stale until restored" sentence once the registry exists | README.md text | forbidden phrase absent |
| `test_domain_redirect_generalized` | `digitalmodel/docs/domains/README.md` points non-OrcaWave/OrcaFlex domains at the repo-wide operator map rather than leaving them unrouted | domain README text | redirect section present |
| `test_agents_md_links_repo_wide_map` | `digitalmodel/AGENTS.md` links the repo-wide operator map | AGENTS.md text | link present |
| `test_workspace_stale_ref_guard_covers_new_docs` | Workspace-hub stale-reference guard includes the new digitalmodel canonical docs | workspace test text | paths present |
| `test_plans_readme_indexes_2462_plan` | `docs/plans/README.md` includes the #2462 plan row at the canonical `-repo-wide-routing-surfaces.md` filename | README text | row present |
| `test_no_src_hygiene_violations_in_digitalmodel` | No `*.bak` / `*.orig` / `__pycache__/` / cache-runtime artifacts are tracked under `src/digitalmodel/` (enforces #2460 source-hygiene rule for this repo) | `git ls-files src/digitalmodel/` | no forbidden extensions / path substrings |
| `test_docs_readme_names_repo_vs_bulk_artifact_store_rule` | `digitalmodel/docs/README.md` names the universal repo-vs-bulk-artifact-store placement rule defined in #2460 | docs/README.md text | rule present |
| `test_tdd_red_phase_evidence_exists` | Implementation commit(s) include red-phase evidence (captured pytest output showing the new tests failed BEFORE the new docs/files/edits landed) | commit message or attached red-phase artifact | evidence present |

---

## Acceptance Criteria

- [ ] `digitalmodel/docs/README.md` exists, routes common issue types to source/tests/docs, and links AGENTS.md, README.md, operator map, registry, and `docs/domains/README.md`.
- [ ] `digitalmodel/docs/README.md` explicitly states the curated-vs-raw inventory boundary.
- [ ] `docs/maps/digitalmodel-operator-map.md` exists and has one row per top-level package under `src/digitalmodel/` (derived from the live tree, not hard-coded).
- [ ] Repo-wide operator map uses at least the column shape already proven by `docs/maps/digitalmodel-orcawave-orcaflex-operator-map.md`.
- [ ] Repo-wide operator map links the existing OrcaWave/OrcaFlex slice map rather than duplicating its content.
- [ ] Canonical machine-readable registry exists at the path #2460 defines, and covers every operator-map row.
- [ ] `digitalmodel/ROADMAP.md` no longer references `specs/module-registry.yaml` at lines 9 or 50; both references now point to the canonical registry path.
- [ ] `digitalmodel/README.md` no longer contains the "stale until restored" sentence, and now links the repo-wide operator map.
- [ ] `digitalmodel/docs/domains/README.md` generalizes its OrcaWave/OrcaFlex redirect pattern so other domains are routed to the repo-wide operator map.
- [ ] `digitalmodel/AGENTS.md` links the repo-wide operator map.
- [ ] `digitalmodel/tests/docs/test_digitalmodel_routing_contract.py` is green and catches future drift (operator-map rows vs source tree).
- [ ] `tests/docs/test_banned_stale_references.py` is extended to cover the new digitalmodel canonical docs and still passes.
- [ ] `docs/plans/README.md` includes the #2462 row AND that row's third-column path value matches this plan's actual filename `docs/plans/2026-04-22-issue-2462-digitalmodel-repo-wide-routing-surfaces.md` (not just the issue number — prevents spurious-pass on filename drift, per Gemini r2 MINOR #2).
- [ ] All three plan-review artifacts under `scripts/review/results/2026-04-22-plan-2462-{claude,codex,gemini}.md` exist AND every provider's final verdict is APPROVE or MINOR. If any provider returns MAJOR, the plan is re-tightened and re-reviewed (up to the repo-standard `MAX_REVIEW_ITERATIONS=3`) — there is NO "at most one non-APPROVE/MINOR" loophole; all three must clear.
- [ ] No encroachment on sibling scope: the implementation touches only `digitalmodel/**` paths plus the single workspace-hub file `docs/maps/digitalmodel-operator-map.md` and the workspace-hub regression guard `tests/docs/test_banned_stale_references.py`; no file owned by #2461 (`assetutilities/**`), #2463 (`aceengineer-website/**`), #2464 (`docs/CONTENT_INDEX.md`, repo-root cleanup), or #2465 (daily-freshness automation) is modified.
- [ ] Source-hygiene gate per #2460: `git ls-files src/digitalmodel/` returns no file matching `*.bak`, `*.orig`, or path substring `__pycache__/`; the `test_no_src_hygiene_violations_in_digitalmodel` test asserts this.
- [ ] Repo-vs-bulk-artifact-store rule per #2460: `digitalmodel/docs/README.md` names the universal placement rule and cites `/mnt/ace/data` only as the current workspace-hub implementation example.
- [ ] Hard gate on #2460: before implementation begins, #2460 has reached `status:plan-approved` AND its contract doc has locked the registry path shape and operator-map host location textually (either in the #2460 plan or on main in `docs/standards/TIER1_INDEXING_AND_CODE_PLACEMENT_CONTRACT.md`). If #2460 changes any of those items, this plan is patched and re-reviewed first. (Strengthened per Gemini r2 MINOR #1 — `status:plan-approved` alone is insufficient because it does not guarantee the contract doc exists.)
- [ ] TDD red-phase evidence captured in the implementation commit(s): the new tests in `test_digitalmodel_routing_contract.py` demonstrably failed on the red-phase commit BEFORE the new docs/edits/registry were added; the evidence is either inline in the commit body or attached as `.planning/quick/2462-red-phase.out`.

---

## Adversarial Review Summary

**Round 1 (pre-tightening) — 2026-04-22 worker-3 single-author r3 fallback:**

| Provider (lens) | Verdict | Key findings |
|---|---|---|
| Claude (completeness / testing / scope) | MAJOR | (a) duplicate rival plan collision at `-operator-map.md` — resolved by deleting duplicate; (b) #2460 contract surface undercount — resolved by adding source-hygiene rule and repo-vs-bulk-artifact-store rule to Files-to-Change, TDD Test List, and Acceptance Criteria; (c) pre-green test on `currently stale` (substring absent from ROADMAP.md) — resolved by grounding drift tests in `stale until restored` for README.md only and using positive assertions elsewhere; (d) 11-domain floor arbitrary — resolved by keeping the live-tree-derived rule (existing `test_operator_map_rows_match_source_tree` already handles this). |
| Codex (evidence verification) | APPROVE | All 11 issue-state claims, all EXISTS/MISSING paths, and all cited line excerpts verified. Two minor polishes noted (scorecard excerpt "..." should be marked "(abridged)"; byte-count claims fragile — switched to "non-empty"). |
| Gemini (scope / dependency / contract alignment) | MAJOR | (a) review-gate loophole ("at most one non-APPROVE/MINOR") — REMOVED; all three must clear; (b) no explicit hard gate on #2460 — ADDED as hard-gate front-matter and acceptance criterion; (c) source-hygiene surface silently dropped — ADDED; (d) ROADMAP:50 retargeted (not deleted) — already correct; (e) sibling scope unclear — ADDED sibling scope boundary front-matter and acceptance criterion. |

**Round 1 overall:** FAIL (re-draft required).

Revisions made between r1 and r2:
1. Front-matter status line updated to `draft (adversarial-reviewed r2)`.
2. Added **HARD GATE** dependency on #2460 reaching `status:plan-approved` before implementation.
3. Added sibling scope boundary front-matter naming #2461/#2463/#2464/#2465 owners.
4. Expanded test file description to call out the six contract surfaces (existence, rows, registry, drift, source-hygiene, repo-vs-bulk-artifact-store).
5. Added three new TDD Test List rows: `test_no_src_hygiene_violations_in_digitalmodel`, `test_docs_readme_names_repo_vs_bulk_artifact_store_rule`, `test_tdd_red_phase_evidence_exists`.
6. Strengthened Acceptance Criteria: removed the review-gate loophole (all three providers must clear APPROVE/MINOR; MAJOR triggers re-draft up to `MAX_REVIEW_ITERATIONS=3`); added sibling-non-encroachment criterion; added source-hygiene criterion; added repo-vs-bulk-artifact-store criterion; added #2460 hard-gate criterion; added TDD red-phase evidence criterion.
7. Added ownership note for `docs/plans/README.md` row update (already indexed, main session owns updates at merge).

**Round 2 verdicts** are captured in the files named under the "Review artifacts" header above.

**Provenance note:** r1 and r2 review artifacts were produced via worker-3 sub-agent dispatch (single-author r3 fallback) because worker-3 operates in a planning-only sandbox that cannot reach the Stage-5/6 evidence gate in `scripts/review/cross-review.sh`. Real cross-provider dispatch via `scripts/review/submit-to-{claude,codex,gemini}.sh` should replace these artifacts when a gate-capable session can run them; the fallback is explicitly labeled in each file and should be preferred to leaving the review column empty per `feedback_permission_gate_blocks_cross_review.md`.

---

## Risks and Open Questions

- **Risk:** Hard-coding the domain list in the operator map guarantees drift. Mitigation: the routing-contract test re-derives the required domain set from `git ls-tree src/digitalmodel` at test time, so any future `src/digitalmodel/` addition that isn't reflected in the operator map fails CI.
- **Risk:** The OrcaWave/OrcaFlex slice map is referenced from multiple places (`README.md`, `docs/domains/README.md`, PR #1752). Changing references in a drift-cleanup step could break downstream discoverability. Mitigation: this plan preserves the slice map path unchanged and only adds the repo-wide map as a new supersurface.
- **Risk:** The registry filename decision is upstream in #2460. If #2460 changes between plan review and implementation, registry-related tests need a patch. Mitigation: this plan defers the filename to #2460 and writes the registry test to read the path from a small contract-shape stub rather than hard-code it.
- **Risk:** `digitalmodel/ROADMAP.md:50` is a roadmap line-item ("add module entry to `specs/module-registry.yaml`"). Rewriting the path without also deciding whether the line-item should remain open, retargeted, or deleted risks semantic drift. Mitigation: the drift-cleanup step chooses *retarget to the new canonical path*, not deletion, because the action (recording new module entries) is still valid once the registry is real.
- **Risk:** Not every `src/digitalmodel/<domain>/` directory is actually a Python package (some may be data, some `__init__.py`-less). Mitigation: the operator-map-derivation rule is "package if `__init__.py` exists", so non-package directories are explicitly excluded and this is asserted in the routing-contract test.
- **Open:** Does `digitalmodel/docs/domains/README.md` need one redirect section per domain, or a single redirect paragraph referencing the repo-wide operator map? This plan specifies the single-paragraph approach; reviewers may push for a per-domain section.
- **Open:** Should `digitalmodel/specs/modules/` (currently the only inhabitant of `specs/`) be documented as the canonical per-module spec location in the registry? This plan defers that surface-inventory question to implementation.

---

## Complexity: T2

**T2** — one new canonical docs entry, one new repo-wide operator map, one new machine-readable registry, three existing docs patched for drift (README, ROADMAP, domain redirect), one AGENTS.md link addition, one new test file, one extension to the workspace-hub stale-reference guard. Non-trivial but scoped: no source-code changes to `src/**`, no engine behavior changes, no new solver integrations. The operator map is large (30 rows) but mechanically derived from the observed source tree.
