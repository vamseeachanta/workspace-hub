# Plan for #2533: Repo Portfolio Mission/Objective Review

> **Status:** draft
> **Complexity:** T2
> **Date:** 2026-04-27
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2533
> **Review artifacts:** scripts/review/results/2026-04-27-plan-2533-claude.md | scripts/review/results/2026-04-27-plan-2533-codex.md | scripts/review/results/2026-04-27-plan-2533-gemini.md

---

## Resource Intelligence Summary

### Existing repo code/docs
- Found: `docs/BUSINESS_BRAIN.md` — existing single-file ecosystem context with Tier-1, Tier-2, and Tier-3 repo groups, but only short domain labels rather than mission/objective/routing rules.
- Found: `docs/ROUTING_INDEX.md` — current Tier-1 routing index with per-repo roles and issue-type placement rules; it does not cover Tier-2/Tier-3 repo mission/objective classification.
- Found: `docs/WORKSPACE_HUB_REPOSITORY_OVERVIEW.md` — workspace repository overview exists and should be reconciled with the new portfolio mission table rather than duplicated blindly.
- Found: `docs/standards/TIER1_INDEXING_AND_CODE_PLACEMENT_CONTRACT.md` and `docs/standards/TIER1_INDEXING_CHECKLIST.md` — Tier-1 routing/indexing contract exists and should remain the authority for code-placement checks.

### Standards
| Standard | Status | Source |
|---|---|---|
| Mandatory issue planning workflow | applicable | `docs/plans/README.md` |
| Tier-1 indexing/code placement | applicable for Wave 1 | `docs/standards/TIER1_INDEXING_AND_CODE_PLACEMENT_CONTRACT.md` |
| Tier-1 indexing checklist | applicable for Wave 1 consistency checks | `docs/standards/TIER1_INDEXING_CHECKLIST.md` |
| Engineering domain standards | not directly applicable | This is a repo-portfolio/docs-governance issue, not a numerical engineering calculation. |

### LLM Wiki pages consulted
- No LLM-wiki pages are required for this planning slice. The issue is portfolio governance, not domain knowledge extraction.
- Related issue #2390 remains context for LLM-wiki strengthening, but this plan should not expand into wiki content work.

### Documents consulted
- Related issue #1962 — open Tier-1 repo ecosystem refactoring umbrella; #2533 should link to it but not replace its Tier-1 execution scope.
- Related issue #2397 — open Tier-1 canonical folder structure/refactor contract epic; #2533 should consume Tier-1 outputs and extend mission/objective coverage across the broader portfolio.
- Related issue #2460 — closed Tier-1 indexing and code-placement contract; authoritative for Tier-1 routing baseline.
- Related issues #2461, #2463, #2464, #2465 — closed Tier-1 child routing/indexing issues; use as already-completed evidence rather than creating duplicates.
- Related issue #2462 — open digitalmodel routing child; now has PR https://github.com/vamseeachanta/digitalmodel/pull/539 and should remain open until landed/closed.

### Gaps identified
- No canonical `docs/REPO_MISSION_PORTFOLIO.md` exists yet.
- No single table currently records mission/objective, tier/status, source path, and routing rule for every active repo.
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
- EXISTS: `docs/ROUTING_INDEX.md`, lines 24-50 define Tier-1 per-repo routing roles.
- EXISTS: `docs/plans/README.md`, lines 15-27 define the issue planning gate.
- MISSING (new — this issue creates): `docs/REPO_MISSION_PORTFOLIO.md`.

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
```

**Gap proofs:**
- `docs/REPO_MISSION_PORTFOLIO.md` is absent and must be created by this issue.
- The current Tier-1 routing index is explicitly titled `# Tier-1 Routing Index`; it is not a portfolio-wide mission/objective artifact.

Current distinct source count: 9+ (`#2533`, `#1962`, `#2397`, `#2390`, `#2460-#2465`, `docs/BUSINESS_BRAIN.md`, `docs/ROUTING_INDEX.md`, `docs/standards/TIER1_INDEXING_AND_CODE_PLACEMENT_CONTRACT.md`, `docs/standards/TIER1_INDEXING_CHECKLIST.md`, `docs/plans/README.md`).

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-04-27-issue-2533-repo-portfolio-mission-objective-review.md` |
| Portfolio mission artifact | `docs/REPO_MISSION_PORTFOLIO.md` |
| Discovery links | `docs/BUSINESS_BRAIN.md`, `docs/ROUTING_INDEX.md`, optionally `docs/README.md` |
| Validation tests | `tests/docs/test_repo_mission_portfolio.py` |
| Plan review — Claude | `scripts/review/results/2026-04-27-plan-2533-claude.md` |
| Plan review — Codex | `scripts/review/results/2026-04-27-plan-2533-codex.md` |
| Plan review — Gemini | `scripts/review/results/2026-04-27-plan-2533-gemini.md` |

---

## Deliverable

A canonical `docs/REPO_MISSION_PORTFOLIO.md` table that records each active repo's mission, objectives, activity/tier classification, source evidence, and issue-routing guidance, linked from the workspace discovery surfaces.

---

## Pseudocode

```text
function collect_repo_inventory():
    read docs/BUSINESS_BRAIN.md repo sections
    enumerate immediate child git repos under /mnt/local-analysis/workspace-hub or configured workspace root
    merge known repos from overview docs
    mark repos as listed, unlisted, missing, or excluded

function derive_repo_mission(repo):
    check strongest source order: .agent-os/product/mission.md, README.md, AGENTS.md, docs/README.md, workspace docs
    extract concise mission and objectives with source path
    preserve uncertainty as REVIEW_REQUIRED instead of guessing

function classify_repo(repo):
    assign Tier-1, Tier-2, Tier-3/support/archive/deprecated/no-new-issues
    record rationale and conflict/dedupe notes

function write_portfolio_artifact():
    emit table with repo, tier/status, mission, objectives, belongs-here routing, route-elsewhere rule, evidence source, notes
    include overlap/conflict section
    include update rules for future agents

function validate_artifact():
    assert every BUSINESS_BRAIN active repo has a row
    assert every immediate-child git repo is represented or explicitly excluded
    assert each row has non-empty mission/objective/source/routing fields
    assert Tier-1 rows reference or align with the Tier-1 routing contract
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create | `docs/REPO_MISSION_PORTFOLIO.md` | Canonical portfolio mission/objective table and overlap-resolution notes |
| Modify | `docs/BUSINESS_BRAIN.md` | Link the canonical portfolio mission artifact without bloating the onboarding file |
| Modify | `docs/ROUTING_INDEX.md` | Cross-link from Tier-1 routing to portfolio-level mission/objective context |
| Modify | `docs/README.md` | Optional discoverability link if docs index lacks a portfolio-governance entry |
| Create | `tests/docs/test_repo_mission_portfolio.py` | Regression checks for required rows, fields, links, and Tier-1 alignment |
| Update | `docs/plans/README.md` | Add this plan to the planning index |

---

## TDD Test List

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| `test_portfolio_artifact_exists_and_is_linked` | New artifact exists and is discoverable from at least one canonical docs surface | repo checkout | artifact exists; BUSINESS_BRAIN or ROUTING_INDEX links it |
| `test_business_brain_repos_have_portfolio_rows` | Every repo named in BUSINESS_BRAIN active tiers has a row | BUSINESS_BRAIN + mission artifact | no missing repo rows |
| `test_immediate_child_git_repos_are_represented_or_excluded` | Local git repos are either represented or explicitly excluded/inventory-drift | local workspace inventory | no silent omissions |
| `test_required_columns_present` | Table has mission/objectives/status/source/routing fields | mission artifact markdown | all required columns found |
| `test_tier1_rows_align_with_routing_index` | Tier-1 repos align with existing routing index roles and do not contradict #2460 | mission artifact + ROUTING_INDEX | no contradictions for workspace-hub, digitalmodel, assetutilities, aceengineer-website |
| `test_overlap_notes_cover_known_conflicts` | Known repo mission overlaps are explicitly addressed | mission artifact | overlap section includes expected repo pairs |

---

## Acceptance Criteria

- [ ] `docs/REPO_MISSION_PORTFOLIO.md` exists and is linked from `docs/BUSINESS_BRAIN.md` and/or `docs/ROUTING_INDEX.md`.
- [ ] Every active repo in `docs/BUSINESS_BRAIN.md` has a mission/objective row or explicit exclusion rationale.
- [ ] Every immediate-child local git repo not listed in `docs/BUSINESS_BRAIN.md` is added, explicitly excluded, or marked as inventory drift.
- [ ] Each row has source evidence: exact repo/path used for mission/objective derivation.
- [ ] Each row has a tier/status classification and issue-routing guidance.
- [ ] Known overlapping repo missions are called out with a resolution or follow-up recommendation.
- [ ] Tier-1 rows are consistent with `docs/ROUTING_INDEX.md`, #2460, and the relevant child issue outputs (#2461-#2465).
- [ ] TDD tests in `tests/docs/test_repo_mission_portfolio.py` pass with `uv run pytest tests/docs/test_repo_mission_portfolio.py -q`.
- [ ] No implementation proceeds until adversarial plan review is complete and user approval applies `status:plan-approved`.

---

## Adversarial Review Summary

| Provider | Verdict | Key findings |
|---|---|---|
| Claude | PENDING | Not yet run |
| Codex | PENDING | Not yet run |
| Gemini | PENDING | Not yet run |

**Overall result:** PENDING (review required before posting as plan-review / implementation)

Revisions made based on review:
- None yet.

---

## Risks and Open Questions

- **Risk:** Some local child directories may be dirty, missing remotes, or intentionally not active repos; implementation must classify drift explicitly rather than forcing rows.
- **Risk:** Mission extraction from sparse READMEs may overstate intent; mark uncertain missions as `REVIEW_REQUIRED` and cite the source.
- **Risk:** This issue could creep into repo refactors; keep it to mission/objective/routing documentation plus validation tests.
- **Open:** Whether `CAD-DEVELOPMENTS` belongs in the active portfolio list should be resolved during inventory, not assumed from memory.

---

## Complexity: T2

**T2** — multi-file documentation/governance change with a new validation test module and cross-repo inventory evidence, but no production-code architecture changes.
