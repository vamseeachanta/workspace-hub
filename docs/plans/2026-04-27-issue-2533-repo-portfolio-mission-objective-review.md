# Plan for #2533: Repo Portfolio Mission/Objective Review

> **Status:** draft — rev-3 after Codex rev-2 MAJOR review
> **Complexity:** T2
> **Date:** 2026-04-27
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2533
> **Review artifacts:** scripts/review/results/2026-04-28-plan-2533-codex.md | scripts/review/results/2026-04-28-plan-2533-gemini.md | scripts/review/results/2026-04-28-plan-2533-disagreement.md

---

## Resource Intelligence Summary

### Existing repo code/docs
- Found: `docs/BUSINESS_BRAIN.md` — current onboarding source lists four Tier-1 repos (`workspace-hub`, `digitalmodel`, `assetutilities`, `aceengineer-website`), seven Tier-2 repos, and Tier-3/support/archive candidates. It has only short domain labels, not full mission/objective/routing rules.
- Found: `docs/ROUTING_INDEX.md` — current Tier-1 routing index for the four active routing-contract repos. It defines per-repo roles and issue-type placement rules, but intentionally does not cover Tier-2/Tier-3 mission/objective classification.
- Found: `docs/WORKSPACE_HUB_REPOSITORY_OVERVIEW.md` — broader legacy/overview inventory claims 25 managed repositories and lists additional repos absent from `docs/BUSINESS_BRAIN.md`, including `CAD-DEVELOPMENTS`, `heavyequipemnt-rag`, and `simpledigitalmarketing`. The implementation must treat these as inventory-source conflicts or overview-only candidates, not silently omit them.
- Found: `docs/README.md` — docs landing page contains workspace discovery links and repo-count/context claims that must be reconciled because current lines still reference `26+` repos and legacy `.agent-os/product/mission.md` as “Mission & Vision”; implementation must update this discovery surface so it points to `docs/REPO_MISSION_PORTFOLIO.md` and does not route agents to legacy mission authority.
- Found: `docs/standards/TIER1_INDEXING_AND_CODE_PLACEMENT_CONTRACT.md` and `docs/standards/TIER1_INDEXING_CHECKLIST.md` — Tier-1 routing/indexing contract exists and remains authority for Tier-1 code-placement checks.
- Found: `docs/standards/CONTROL_PLANE_CONTRACT.md` — documentation/control-plane issues must preserve `AGENTS.md` as canonical per-repo entry point and avoid reviving `.agent-os/` as an authority; `.agent-os` is legacy content only.
- Found: `docs/document-intelligence/durable-vs-transient-knowledge-boundary.md` (#2209) — durable docs should own reusable knowledge, while issues/plans/review artifacts are execution-state evidence. Therefore the portfolio mission table belongs in durable docs, while review artifacts remain under `scripts/review/results/`.

### Standards
| Standard | Status | Source |
|---|---|---|
| Mandatory issue planning workflow | applicable | `docs/plans/README.md` |
| Documentation issue retrieval bundle | applicable and now satisfied | `docs/plans/README.md` requires governance docs, `CONTROL_PLANE_CONTRACT.md`, and #2209 for `cat:documentation` work |
| Control-plane entry point contract | applicable | `docs/standards/CONTROL_PLANE_CONTRACT.md` |
| Durable-vs-transient boundary | applicable | `docs/document-intelligence/durable-vs-transient-knowledge-boundary.md` (#2209) |
| Tier-1 indexing/code placement | applicable for Wave 1 consistency checks | `docs/standards/TIER1_INDEXING_AND_CODE_PLACEMENT_CONTRACT.md` |
| Tier-1 indexing checklist | applicable for Wave 1 consistency checks | `docs/standards/TIER1_INDEXING_CHECKLIST.md` |
| Engineering domain standards | not directly applicable | This is a repo-portfolio/docs-governance issue, not a numerical engineering calculation. |

### LLM Wiki pages consulted
- No LLM-wiki pages are required for this planning slice. The issue is portfolio governance, not domain knowledge extraction.
- Related issue #2390 remains context for LLM-wiki strengthening, but this plan must not expand into wiki implementation work.

### Documents consulted
- Related issue #1962 — open Tier-1 repo ecosystem refactoring umbrella. **Important conflict:** #1962 uses an older/eight-repo Tier-1 refactor-priority list (`digitalmodel`, `assetutilities`, `assethold`, `worldenergydata`, `CAD-DEVELOPMENTS`, `aceengineer-website`, `aceengineer-strategy`, `sabithaandkrishnaestates`). For this issue, #1962 is historical umbrella/refactor evidence, not the current Tier-1 routing authority.
- Related issue #2397 — open Tier-1 canonical folder structure/refactor contract epic; #2533 should consume Tier-1 outputs and extend mission/objective coverage across the broader portfolio.
- Related issue #2460 — closed Tier-1 indexing and code-placement contract; authoritative for the current four-repo Tier-1 routing baseline alongside `docs/BUSINESS_BRAIN.md` and `docs/ROUTING_INDEX.md`.
- Related issues #2461, #2463, #2464, #2465 — closed Tier-1 child routing/indexing issues; use as already-completed evidence rather than creating duplicates.
- Related issue #2462 — open digitalmodel routing child; now has PR https://github.com/vamseeachanta/digitalmodel/pull/539 and should remain open until landed/closed.

### Source precedence for classification conflicts
When repo-tier sources conflict, implementation must record the conflict and use this precedence for the initial artifact:

1. `docs/BUSINESS_BRAIN.md` + `docs/ROUTING_INDEX.md` + #2460 contract for current Tier-1 routing classification.
2. `docs/WORKSPACE_HUB_REPOSITORY_OVERVIEW.md` for broader managed-repo inventory and overview-only candidates.
3. #1962 for historical/refactor-priority context, not current routing-tier authority.
4. Per-repo `AGENTS.md`, `README.md`, and `docs/README.md` for mission/objective evidence.
5. `.agent-os/product/mission.md` only as legacy evidence where present; it must not override `AGENTS.md` per `CONTROL_PLANE_CONTRACT.md`.

### Gaps identified
- No canonical `docs/REPO_MISSION_PORTFOLIO.md` exists yet.
- No deterministic committed inventory file currently reconciles `BUSINESS_BRAIN`, repository overview, and live/local repo inventory.
- No single table currently records mission/objective, tier/status, source path, and routing rule for every active or explicitly excluded repo.
- Tier-2/Tier-3 repos have short domain labels but no explicit issue-routing guidance.
- Known overlaps are not resolved in one visible place: `investments` vs `assethold`, `client_projects` vs client-specific repos, `workspace-hub` vs per-repo execution docs, and `assetutilities` vs repo-specific utilities.

### Evidence (embedded verification)

**Issue statuses** (verified 2026-04-28T03:41:23Z via `gh issue view`):
- `#1962` — OPEN — FEATURE: Tier-1 Repo Ecosystem Refactoring — audit, plan, execute with Claude Code plan mode
- `#2397` — OPEN — epic(repo-organization): canonical folder structure and refactor contract across tier-1 repos
- `#2390` — OPEN — epic(knowledge): llm-wiki strengthening roadmap and execution waves
- `#2460` — CLOSED — feat(repo-organization): tier-1 indexing and code-placement contract
- `#2461` — CLOSED — chore(assetutilities): canonical routing surfaces and source-hygiene cleanup for tier-1 issue work
- `#2462` — OPEN — feat(digitalmodel): repo-wide operator map and canonical routing surfaces beyond OrcaWave/OrcaFlex
- `#2463` — CLOSED — chore(aceengineer-website): canonical routing surfaces and legacy product-doc reference cleanup
- `#2464` — CLOSED — chore(workspace-hub): split curated tier-1 routing index from raw inventory and clean routing noise
- `#2465` — CLOSED — feat(automation): daily tier-1 indexing freshness audit and scorecard refresh

**File existence / source excerpts:**
- EXISTS: `docs/BUSINESS_BRAIN.md`, lines 14-38 list Tier-1/Tier-2/Tier-3 repos.
- EXISTS: `docs/ROUTING_INDEX.md`, lines 24-50 define current four-repo Tier-1 routing roles.
- EXISTS: `docs/WORKSPACE_HUB_REPOSITORY_OVERVIEW.md`, lines 53-87 list broader work/personal repo inventory, including overview-only repos not in `BUSINESS_BRAIN`.
- EXISTS: `docs/standards/CONTROL_PLANE_CONTRACT.md`, lines 9-17 establish `AGENTS.md` as canonical entry point and lines 37-47 mark `.agent-os/` legacy.
- EXISTS: `docs/document-intelligence/durable-vs-transient-knowledge-boundary.md`, lines 17-27 define durable/transient classification and promotion guardrails.
- EXISTS: `docs/README.md`, lines 7 and 206 reference `26+` repositories; lines 263-264 and 298-302 reference `.agent-os/product/*` mission/product docs. These stale discovery links must be replaced or clearly marked legacy as part of this issue.
- MISSING (new — this issue creates): `docs/REPO_MISSION_PORTFOLIO.md`.
- MISSING (new — this issue creates): `docs/registry/repo-portfolio-inventory.yaml`.

**Line excerpts:**
```text
# docs/BUSINESS_BRAIN.md
14: ## Repositories (24 active, GitHub: vamseeachanta)
16: ### Tier-1 (actively developed, cross-repo dependencies)
24: ### Tier-2 (domain-specific, periodic work)
35: ### Tier-3 (low-frequency, reference, or archival)

# docs/ROUTING_INDEX.md
24: ## Per-Repo Routing
28: - Role: portfolio control plane, issue planning, agent harness, durable standards, and document-intelligence registries.
35: - Role: numerical models, offshore engineering calculation pipelines, OrcaWave, OrcaFlex, hydrodynamics, and solver workflows.
42: - Role: shared Python utilities used by engineering repositories.
48: - Role: public website, marketing content, demos, calculators, and deployment assets.

# docs/WORKSPACE_HUB_REPOSITORY_OVERVIEW.md
53: ### Work Repositories (Professional/Client Projects)
70: | **CAD-DEVELOPMENTS** | CAD development work and documentation | Engineering/CAD |
71: | **heavyequipemnt-rag** | Heavy equipment RAG (retrieval-augmented generation) | AI/Engineering |
72: | **simpledigitalmarketing** | Digital marketing content and tools | Marketing |
```

**Gap proofs:**
- `docs/REPO_MISSION_PORTFOLIO.md` is absent and must be created by this issue.
- `docs/registry/repo-portfolio-inventory.yaml` is absent and must be created to make inventory tests deterministic.
- The current Tier-1 routing index is explicitly titled `# Tier-1 Routing Index`; it is not a portfolio-wide mission/objective artifact.

Current distinct source count: 12+ (`#2533`, `#1962`, `#2397`, `#2390`, `#2460-#2465`, `docs/BUSINESS_BRAIN.md`, `docs/ROUTING_INDEX.md`, `docs/WORKSPACE_HUB_REPOSITORY_OVERVIEW.md`, `docs/README.md`, `docs/standards/CONTROL_PLANE_CONTRACT.md`, `docs/document-intelligence/durable-vs-transient-knowledge-boundary.md`, `docs/standards/TIER1_INDEXING_AND_CODE_PLACEMENT_CONTRACT.md`, `docs/standards/TIER1_INDEXING_CHECKLIST.md`, `docs/plans/README.md`).

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-04-27-issue-2533-repo-portfolio-mission-objective-review.md` |
| Portfolio mission artifact | `docs/REPO_MISSION_PORTFOLIO.md` |
| Deterministic inventory registry | `docs/registry/repo-portfolio-inventory.yaml` |
| Discovery links | `docs/BUSINESS_BRAIN.md`, `docs/ROUTING_INDEX.md`, optionally `docs/README.md` |
| Validation tests | `tests/docs/test_repo_mission_portfolio.py` |
| Plan review — Codex | `scripts/review/results/2026-04-28-plan-2533-codex.md` |
| Plan review — Gemini | `scripts/review/results/2026-04-28-plan-2533-gemini.md` |
| Plan review disagreement/summary | `scripts/review/results/2026-04-28-plan-2533-disagreement.md` |

---

## Deliverable

A canonical `docs/REPO_MISSION_PORTFOLIO.md` table plus `docs/registry/repo-portfolio-inventory.yaml` inventory registry that record each active/candidate repo's mission, objectives, activity/tier classification, source evidence, conflict notes, and issue-routing guidance, linked from workspace discovery surfaces.

---

## Pseudocode

```text
function collect_repo_inventory():
    parse docs/BUSINESS_BRAIN.md repo sections
    parse docs/WORKSPACE_HUB_REPOSITORY_OVERVIEW.md work/personal repo tables
    optionally enumerate local immediate-child git repos at an explicit implementation-time workspace root
    write docs/registry/repo-portfolio-inventory.yaml with repo, seen_in sources, local_path_status, source_conflicts
    never make tests depend on the current machine's live filesystem unless WORKSPACE_HUB_PORTFOLIO_ROOT is explicitly set

function derive_repo_mission(repo):
    use source precedence: AGENTS.md, README.md, docs/README.md, workspace docs, then legacy .agent-os mission if present
    extract concise mission and 2-5 objectives with exact source path(s)
    preserve uncertainty as REVIEW_REQUIRED instead of guessing

function classify_repo(repo):
    apply classification precedence: BUSINESS_BRAIN/ROUTING_INDEX/#2460 for current Tier-1; overview for broader managed inventory; #1962 as historical refactor evidence
    assign one status: Tier-1 active, Tier-2 active/periodic, Tier-3 support/archive, overview-only candidate, deprecated/no-new-issues, or excluded
    record rationale and any conflicting source claims

function write_portfolio_artifact():
    emit a table with repo, status, mission, objectives, belongs-here routing, route-elsewhere rule, evidence source, conflict notes
    include explicit conflict-resolution section for #1962 vs current Tier-1 sources and known overlap pairs
    include update rules for future agents and a link to the inventory registry

function validate_artifact():
    assert every BUSINESS_BRAIN active repo has a portfolio row
    assert every overview-table repo has a portfolio row or explicit excluded/overview-only status
    assert every repo in committed inventory registry is represented or excluded
    assert each row has non-empty mission/objective/source/routing/conflict-status fields
    assert every row source path exists in the repo checkout or is explicitly marked external/legacy with a rationale
    assert source evidence paths are tied to the row's mission/objective fields, not generic repo roots
    assert Tier-1 rows align with ROUTING_INDEX and #2460 current four-repo routing baseline
    assert docs/README.md links the new mission portfolio and no longer promotes .agent-os/product/mission.md as active mission authority
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create | `docs/REPO_MISSION_PORTFOLIO.md` | Canonical portfolio mission/objective table, classification precedence, and overlap-resolution notes |
| Create | `docs/registry/repo-portfolio-inventory.yaml` | Deterministic inventory source-of-truth for tests; reconciles BUSINESS_BRAIN, overview docs, and optional local inventory snapshot |
| Modify | `docs/BUSINESS_BRAIN.md` | Link the canonical portfolio mission artifact without bloating the onboarding file |
| Modify | `docs/ROUTING_INDEX.md` | Cross-link from Tier-1 routing to portfolio-level mission/objective context and clarify Tier-1 routing precedence |
| Modify | `docs/README.md` | Required discoverability cleanup: link `docs/REPO_MISSION_PORTFOLIO.md`, reconcile repo-count language with the new inventory registry, and remove or clearly mark legacy `.agent-os/product/mission.md` references so agents do not treat `.agent-os` as active mission authority |
| Create | `tests/docs/test_repo_mission_portfolio.py` | Regression checks for required rows, inventory registry coverage, fields, links, source precedence, and Tier-1 alignment |
| Update | `docs/plans/README.md` | Verify/update the existing #2533 plan-index row status only; do not duplicate the row |

---

## TDD Test List

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| `test_portfolio_artifact_exists_and_is_linked` | New artifact exists and is discoverable from canonical docs surfaces | repo checkout | artifact exists; BUSINESS_BRAIN and/or ROUTING_INDEX links it |
| `test_inventory_registry_exists_and_has_source_sets` | Deterministic inventory registry exists and records which sources saw each repo | inventory YAML | each repo has `seen_in`, `status`, and `evidence` fields |
| `test_business_brain_repos_have_portfolio_rows` | Every repo named in BUSINESS_BRAIN active tiers has a row | BUSINESS_BRAIN + mission artifact | no missing repo rows |
| `test_overview_repos_are_represented_or_explicitly_excluded` | Overview-only repos such as `CAD-DEVELOPMENTS`, `heavyequipemnt-rag`, and `simpledigitalmarketing` cannot disappear silently | overview doc + inventory registry + mission artifact | every overview repo has a row or explicit excluded/overview-only status |
| `test_inventory_registry_repos_are_represented_or_excluded` | Tests use committed inventory, not ambient local filesystem, for deterministic CI behavior | inventory YAML + mission artifact | no silent omissions |
| `test_required_columns_present` | Table has mission/objectives/status/source/routing/conflict fields | mission artifact markdown | all required columns found |
| `test_row_source_paths_exist_or_are_explicitly_external` | Source evidence is correctness-critical, not just non-empty prose | mission artifact + repo checkout | every source path exists, or row marks source as external/legacy with rationale |
| `test_row_source_paths_are_specific` | Rows cannot use generic repo roots as evidence for detailed mission/objectives | mission artifact | source paths include a file path and, where practical, line/range or section marker |
| `test_docs_readme_points_to_portfolio_not_legacy_agent_os` | Docs landing page routes mission discovery to the new artifact and not active `.agent-os/product/mission.md` | docs/README.md | portfolio link present; legacy `.agent-os/product/mission.md` is absent or clearly in a legacy/deprecated section |
| `test_tier1_rows_align_with_current_routing_index` | Current Tier-1 rows align with `ROUTING_INDEX` and #2460 four-repo routing baseline | mission artifact + ROUTING_INDEX | no contradictions for workspace-hub, digitalmodel, assetutilities, aceengineer-website |
| `test_1962_tier_conflict_is_documented` | Historical eight-repo #1962 Tier-1 language is acknowledged and not silently used as current authority | mission artifact | conflict section documents #1962 vs current BUSINESS_BRAIN/#2460 precedence |
| `test_overlap_notes_cover_known_conflicts` | Known repo mission overlaps are explicitly addressed | mission artifact | overlap section includes expected repo pairs |
| `test_plan_index_has_single_2533_row` | Implementation does not duplicate the already-created plan-index row | docs/plans/README.md | exactly one row for issue 2533 |

---

## Acceptance Criteria

- [ ] `docs/REPO_MISSION_PORTFOLIO.md` exists and is linked from `docs/BUSINESS_BRAIN.md` and/or `docs/ROUTING_INDEX.md`.
- [ ] `docs/registry/repo-portfolio-inventory.yaml` exists and records source membership from `BUSINESS_BRAIN`, repository overview, and optional local inventory snapshot.
- [ ] Every active repo in `docs/BUSINESS_BRAIN.md` has a mission/objective row or explicit exclusion rationale.
- [ ] Every repo in `docs/WORKSPACE_HUB_REPOSITORY_OVERVIEW.md` is represented, explicitly excluded, or marked as overview-only/inventory drift.
- [ ] Every repo in the committed inventory registry is represented or explicitly excluded in the portfolio artifact.
- [ ] Each row has source evidence: exact repo/path used for mission/objective derivation.
- [ ] Source evidence is validated: paths exist in the checkout, or external/legacy sources are explicitly marked with rationale.
- [ ] Source evidence is specific enough to verify the mission/objective claim (file path plus section/line/range where practical).
- [ ] Each row has a tier/status classification and issue-routing guidance.
- [ ] Known overlapping repo missions are called out with a resolution or follow-up recommendation.
- [ ] The #1962 historical eight-repo Tier-1 language is documented as a source conflict, with current Tier-1 routing precedence assigned to `BUSINESS_BRAIN` + `ROUTING_INDEX` + #2460.
- [ ] Tier-1 rows are consistent with `docs/ROUTING_INDEX.md`, #2460, and the relevant child issue outputs (#2461-#2465).
- [ ] `docs/README.md` links to the portfolio mission artifact and no longer promotes `.agent-os/product/mission.md` as active mission authority.
- [ ] TDD tests in `tests/docs/test_repo_mission_portfolio.py` pass with `uv run pytest tests/docs/test_repo_mission_portfolio.py -q`.
- [ ] `docs/plans/README.md` has exactly one #2533 row with current status; no duplicate index row is added.
- [ ] No implementation proceeds until adversarial plan review is complete and user approval applies `status:plan-approved`.

---

## Adversarial Review Summary

| Provider | Verdict | Key findings |
|---|---|---|
| Codex | MAJOR | Rev-1 missed documentation-class retrieval (`CONTROL_PLANE_CONTRACT.md`, #2209), did not resolve #1962 vs current Tier-1 conflict, missed overview-only repos in tests, made inventory test environment-dependent, and risked duplicating the #2533 plan-index row. |
| Gemini | UNAVAILABLE | `gemini-3.1-pro-preview` returned repeated `429 RESOURCE_EXHAUSTED / MODEL_CAPACITY_EXHAUSTED`; no substantive verdict produced. |

**Overall result:** REVISION REQUIRED after rev-2; rev-3 addresses Codex rev-2 blockers and should be rerun before `status:plan-review`.

Revisions made based on review:
- Added documentation-class required sources: `CONTROL_PLANE_CONTRACT.md` and #2209 durable/transient boundary.
- Added explicit source-precedence rules for #1962's historical eight-repo Tier-1 language vs current four-repo Tier-1 routing contract.
- Added deterministic inventory registry deliverable: `docs/registry/repo-portfolio-inventory.yaml`.
- Added overview-repo coverage tests for `docs/WORKSPACE_HUB_REPOSITORY_OVERVIEW.md` entries, including overview-only candidates.
- Changed local filesystem inventory from direct CI test dependency to optional implementation-time snapshot captured in the registry.
- Changed `docs/plans/README.md` action from “add row” to “verify/update existing row only”.
- Rev-3 added source-path existence/specificity tests to make evidence verifiable, not just non-empty.
- Rev-3 made `docs/README.md` cleanup mandatory so mission discovery points to the new portfolio artifact instead of active-looking `.agent-os/product/mission.md` references.
- Rev-3 was committed and pushed before rerun so reviewers bind to the durable on-`main` plan and artifacts rather than a local-only inline copy.

---

## Risks and Open Questions

- **Risk:** Some local child directories may be dirty, missing remotes, or intentionally not active repos; implementation must classify drift explicitly in the inventory registry rather than forcing active rows.
- **Risk:** Mission extraction from sparse READMEs may overstate intent; mark uncertain missions as `REVIEW_REQUIRED` and cite the source.
- **Risk:** This issue could creep into repo refactors; keep it to mission/objective/routing documentation plus validation tests.
- **Risk:** `docs/WORKSPACE_HUB_REPOSITORY_OVERVIEW.md` may be stale; implementation should preserve its entries as source evidence/conflicts, not blindly promote them to active status.
- **Open:** Whether `CAD-DEVELOPMENTS`, `heavyequipemnt-rag`, and `simpledigitalmarketing` belong in the active portfolio list should be resolved during inventory classification, not assumed.

---

## Complexity: T2

**T2** — multi-file documentation/governance change with a new deterministic inventory registry, a new validation test module, and cross-source inventory evidence, but no production-code architecture changes.
