# Plan for #2533: Mission/Objective Statements Across Active Repos

> **Status:** draft (rev-3 after Gemini rev-2 MAJOR on C5 unspecified-keywords addressed)
> **Complexity:** T3
> **Date:** 2026-05-02
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2533
> **Review artifacts:** `scripts/review/results/2026-05-02-plan-2533-gemini.md` (rev-1 MAJOR — blockers addressed in rev-2 below). Codex SKIPPED per #2479 (codex-cli 0.124.0 stdin-hang). Single-author r3 fallback at `scripts/review/results/2026-05-02-plan-2533-claude.md` if Gemini rev-2 unavailable.

---

## Resource Intelligence Summary

### Existing repo code/docs

- Found: `docs/BUSINESS_BRAIN.md` (lines 14-44) — onboarding source: lists four Tier-1, five Tier-2, twelve Tier-3 repos plus four archive/extraction candidates. Provides short domain labels only, not full mission/objective/routing.
- Found: `docs/ROUTING_INDEX.md` (lines 1-66) — Tier-1 routing index for the four routing-contract repos, defines per-repo roles and issue-type → repo → path matrix. Explicitly silent on Tier-2/Tier-3 mission/objective.
- Found: `docs/plans/2026-04-27-issue-2533-repo-portfolio-mission-objective-review.md` — prior detailed plan for this exact issue, rev-5 status, Codex+Gemini MAJOR after rev-4. **This 2026-05-02 plan supersedes the 2026-04-27 plan** by reusing its evidence-registry approach (re-introduced in rev-2 after Gemini MAJOR on rev-1) but tightening scope: keeps the inventory YAML + a thin validation script, drops the broader test-module/sibling-repo evidence registry, and defers full overview-doc reconciliation to #2553.
- Found: 22 of 24 issue-listed repos exist as immediate-child git checkouts under `/mnt/local-analysis/workspace-hub/`. `pdf-large-reader` and `heavyequipemnt-rag` and `simpledigitalmarketing` (overview-doc residue) are NOT present locally.
- Found: 18 of 23 local immediate-child repos carry `.agent-os/product/mission.md`; 22/23 carry `AGENTS.md`; 21/23 carry `README.md`. Mission source is heterogeneous but every repo has at least one viable source.
- Found: `docs/standards/CONTROL_PLANE_CONTRACT.md` — `AGENTS.md` is canonical per-repo entry point; `.agent-os/` is legacy and must NOT be promoted as active product/mission authority.
- Found: `docs/document-intelligence/durable-vs-transient-knowledge-boundary.md` (#2209) — durable docs own reusable knowledge; portfolio mission table belongs in `docs/`, review artifacts under `scripts/review/results/`.

### Standards
| Standard | Status | Source |
|---|---|---|
| Mandatory issue planning workflow | applicable | `docs/plans/README.md` |
| Documentation issue retrieval bundle | applicable | `docs/plans/README.md` (governance docs + `CONTROL_PLANE_CONTRACT.md` + #2209 required for `cat:documentation`) |
| Control-plane entry point contract | applicable | `docs/standards/CONTROL_PLANE_CONTRACT.md` |
| Durable-vs-transient boundary | applicable | `docs/document-intelligence/durable-vs-transient-knowledge-boundary.md` (#2209) |
| Tier-1 indexing/code placement | applicable for Wave 1 consistency check only | `docs/standards/TIER1_INDEXING_AND_CODE_PLACEMENT_CONTRACT.md` |
| Engineering domain standards | not applicable | This is a portfolio-governance issue, not numerical engineering |

### LLM Wiki pages consulted

- No LLM-wiki pages required. Issue is portfolio governance, not domain knowledge extraction. Per memory `project_llm_wiki_stays_embedded.md`, llm-wiki stays embedded — no spinout decisions affect this plan.

### Documents consulted

- Issue #2533 body — defines four execution waves, deliverables (1-6), nine acceptance criteria, repo classification axes, and explicit overlap pairs requiring resolution.
- Issue #1962 (OPEN) — historical Tier-1 refactoring umbrella using an older eight-repo Tier-1 list (`digitalmodel`, `assetutilities`, `assethold`, `worldenergydata`, `CAD-DEVELOPMENTS`, `aceengineer-website`, `aceengineer-strategy`, `sabithaandkrishnaestates`). For #2533, #1962 is historical evidence, not current Tier-1 routing authority.
- Issue #2397 (OPEN) — Tier-1 canonical folder structure epic; #2533 consumes its outputs via #2460-#2465.
- Issue #2460 (CLOSED) — Tier-1 indexing and code-placement contract; current four-repo Tier-1 routing baseline.
- Issues #2461 (CLOSED), #2462 (OPEN, PR digitalmodel#539), #2463 (CLOSED), #2464 (CLOSED), #2465 (CLOSED) — Tier-1 child routing/indexing issues. All Tier-1 mission/objective rows in this plan's deliverable MUST align with these closed contracts.
- Issue #2553 — follow-up created 2026-04-29 to reconcile `docs/WORKSPACE_HUB_REPOSITORY_OVERVIEW.md` with mission portfolio. This plan defers full overview reconciliation to #2553 and only flags drift inline.
- Memory `project_assethold_ownership_transfer.md` — assethold transferred samdansk2 → vamseeachanta; local origin may be stale. Plan must record this in the assethold row's `notes` and not assume the local remote URL is canonical.
- Memory `project_aceengineer_copy_canonical_sources.md` — aceengineer firm copy canonical source is the live site + private `aceengineer-strategy` repo; `aceengineer-website` repo is delivery surface, not strategic copy authority. The two repos' missions must be distinguished, not collapsed.
- Prior plan `docs/plans/2026-04-27-issue-2533-repo-portfolio-mission-objective-review.md` — supersession context above.

### Source precedence for mission/objective extraction

Per `CONTROL_PLANE_CONTRACT.md`, `.agent-os/product/mission.md` is legacy. For each repo, walk the precedence list and use the first hit:

1. `AGENTS.md` (canonical entry point per `CONTROL_PLANE_CONTRACT.md`)
2. `README.md`
3. `docs/README.md`
4. `CLAUDE.md` header (only if it carries a mission statement, not a pure pointer)
5. `.agent-os/product/mission.md` — **legacy fallback only**, must be tagged `legacy_source` in the row's `source-path` column
6. If none: row mission = `REVIEW_REQUIRED` with rationale; classification status = `unknown`

### Tier classification precedence

When sources conflict on tier:

1. `docs/BUSINESS_BRAIN.md` (current authority, lines 14-44)
2. `docs/ROUTING_INDEX.md` (Tier-1 only)
3. #2460 contract (Tier-1 routing baseline)
4. `docs/WORKSPACE_HUB_REPOSITORY_OVERVIEW.md` (broader inventory; treat as overview-only when in conflict; defer reconciliation to #2553)
5. #1962 (historical eight-repo Tier-1 list; treat as historical evidence, NOT authority)

### Gaps identified

- No canonical `docs/REPO_MISSION_PORTFOLIO.md` exists yet.
- Tier-2/Tier-3 repos in `BUSINESS_BRAIN.md` lack issue-routing rules (belongs-here / route-elsewhere).
- Known mission overlaps are not visibly resolved anywhere: `investments` ↔ `assethold`; `client_projects` ↔ client-specific repos (`acma-projects`, `seanation`, `saipem`, `frontierdeepwater`, `doris`); `workspace-hub` ↔ per-repo execution docs; `assetutilities` ↔ repo-specific utilities; `aceengineer-website` ↔ `aceengineer-strategy` (delivery vs strategy); `digitalmodel` ↔ client/project verticals.
- `docs/README.md` discovery surface routes agents to `.agent-os/product/*` references that `CONTROL_PLANE_CONTRACT.md` marks legacy; mission discovery has no canonical landing.
- No single artifact tells a future agent "this work belongs in repo X" / "route this elsewhere" for the full active portfolio.

### Evidence (embedded verification)

**Issue statuses** (verified 2026-05-02 via `gh issue view`):
- `#2533` — OPEN — feat(repo-portfolio): review and revise mission/objective statements across active repos
- `#1962` — OPEN — FEATURE: Tier-1 Repo Ecosystem Refactoring
- `#2397` — OPEN — epic(repo-organization): canonical folder structure and refactor contract across tier-1 repos
- `#2460` — CLOSED — feat(repo-organization): tier-1 indexing and code-placement contract
- `#2461` — CLOSED — chore(assetutilities): canonical routing surfaces and source-hygiene cleanup
- `#2462` — OPEN — feat(digitalmodel): repo-wide operator map and canonical routing surfaces
- `#2463` — CLOSED — chore(aceengineer-website): canonical routing surfaces and legacy product-doc cleanup
- `#2464` — CLOSED — chore(workspace-hub): split curated tier-1 routing index from raw inventory
- `#2465` — CLOSED — feat(automation): daily tier-1 indexing freshness audit
- `#2479` — OPEN — codex-cli 0.124.0 stdin-hang regression (justifies SKIP Codex)
- `#2553` — OPEN — reconcile repository overview docs after mission review (overview-doc reconciliation deferred)

**File existence** (`ls` 2026-05-02):
- EXISTS: `docs/BUSINESS_BRAIN.md`, `docs/ROUTING_INDEX.md`, `docs/README.md`, `docs/standards/CONTROL_PLANE_CONTRACT.md`, `docs/document-intelligence/durable-vs-transient-knowledge-boundary.md`
- EXISTS: `docs/plans/2026-04-27-issue-2533-repo-portfolio-mission-objective-review.md` (prior plan, superseded by this one)
- MISSING (this plan creates after approval): `docs/REPO_MISSION_PORTFOLIO.md`

**Local immediate-child repo inventory** (`find /mnt/local-analysis/workspace-hub -maxdepth 2 -name .git -type d`, 2026-05-02):
23 repos present: `aceengineer-admin`, `aceengineer-strategy`, `aceengineer-website`, `achantas-data`, `achantas-media`, `acma-projects`, `assethold`, `assetutilities`, `CAD-DEVELOPMENTS`, `client_projects`, `digitalmodel`, `doris`, `frontierdeepwater`, `hobbies`, `investments`, `OGManufacturing`, `rock-oil-field`, `sabithaandkrishnaestates`, `saipem`, `sd-work`, `seanation`, `teamresumes`, `worldenergydata`.

Issue body lists 24 repos (mentions `pdf-large-reader if present/active`); `pdf-large-reader` is NOT present locally. `heavyequipemnt-rag` and `simpledigitalmarketing` (from `WORKSPACE_HUB_REPOSITORY_OVERVIEW.md`) are NOT present locally. These three are recorded as `inventory-drift: not-present-locally` in the artifact.

**Mission source coverage** (per-repo):
- 18 repos have `.agent-os/product/mission.md` (legacy fallback)
- 22 repos have `AGENTS.md` (preferred per CONTROL_PLANE_CONTRACT.md)
- 21 repos have `README.md`
- `aceengineer-strategy` has only `README.md` (no AGENTS.md/CLAUDE.md/.agent-os) — confirms its private/strategic-copy character per memory.

**Distinct source count:** 14+ (issue body, `BUSINESS_BRAIN.md`, `ROUTING_INDEX.md`, `CONTROL_PLANE_CONTRACT.md`, `durable-vs-transient-knowledge-boundary.md`, `_template-issue-plan.md`, prior plan, `issue-planning-mode/SKILL.md`, #1962, #2397, #2460-#2465, #2553, #2479, three relevant memory files).

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-05-02-issue-2533-mission-portfolio.md` |
| Portfolio mission artifact (created post-approval) | `docs/REPO_MISSION_PORTFOLIO.md` |
| Source-of-truth inventory registry (created post-approval) | `data/document-index/repo-portfolio-inventory.yaml` |
| Validation script (created post-approval) | `scripts/tests/check_repo_mission_portfolio.sh` |
| Discovery anchor updates | `docs/BUSINESS_BRAIN.md`, `docs/ROUTING_INDEX.md`, `docs/README.md` |
| Plan review — Gemini rev-1 | `scripts/review/results/2026-05-02-plan-2533-gemini.md` (MAJOR — addressed in rev-2) |
| Plan review — Claude r3 fallback (only if Gemini rev-2 unavailable) | `scripts/review/results/2026-05-02-plan-2533-claude.md` |
| Codex review | SKIPPED per #2479 |
| Plan-index row | `docs/plans/README.md` (added by main session, not this agent) |

---

## Deliverable

A canonical `docs/REPO_MISSION_PORTFOLIO.md` table — one row per repo (active or explicitly excluded) covering 23 local repos plus 3 inventory-drift entries — with mission, classification, source-path provenance, belongs-here routing rule, route-elsewhere routing rule, and overlap notes. Discoverable from `docs/BUSINESS_BRAIN.md`, `docs/ROUTING_INDEX.md`, and `docs/README.md`. Tier-1 rows align with #2460-#2465. Known overlaps explicitly resolved or marked for follow-up.

Backed by `data/document-index/repo-portfolio-inventory.yaml` as the deterministic source-of-truth (one record per repo) and `scripts/tests/check_repo_mission_portfolio.sh` as the deterministic validator that asserts file-existence, Tier-1 alignment with `ROUTING_INDEX.md`, inventory-drift presence, memory-derived facts, and discovery-anchor links. The markdown artifact is human-readable; the YAML+script pair is the enforceable contract that future agents/CI can re-execute.

---

## Pseudocode

```text
function build_portfolio_artifact():
    load issue_repo_list from #2533 body Tier-1/Tier-2/Tier-3 sections
    load brain_repo_list from docs/BUSINESS_BRAIN.md lines 14-44
    load local_repo_list from immediate-child .git checkouts
    load overview_repo_list from docs/WORKSPACE_HUB_REPOSITORY_OVERVIEW.md (read-only inventory cross-reference)

    union_repos = issue ∪ brain ∪ local ∪ overview
    for repo in union_repos:
        row = build_row(repo)
        if repo not in local_repo_list:
            row.notes += "inventory-drift: not-present-locally; cross-source: <which sources mention it>"
        emit row

function build_row(repo):
    repo_path = "/mnt/local-analysis/workspace-hub/" + repo  # workspace-hub itself reads from repo root
    mission_source = pick_first_present(repo_path, ["AGENTS.md", "README.md", "docs/README.md", "CLAUDE.md", ".agent-os/product/mission.md"])
    if mission_source is None:
        row.mission = "REVIEW_REQUIRED"
        row.source_path = "none"
        row.classification = "unknown"
        return row
    row.mission = extract_mission_paragraph(mission_source)  # 1-3 sentence summary, quoted or paraphrased with attribution
    row.source_path = repo + "/" + mission_source + (" (legacy_source)" if mission_source == ".agent-os/product/mission.md" else "")
    row.classification = classify(repo)  # see classify()
    row.belongs_here = derive_belongs_here_rule(repo, row.mission, row.classification)
    row.route_elsewhere = derive_route_elsewhere_rule(repo, row.classification)
    row.overlap_notes = lookup_known_overlaps(repo)  # from the overlap table below
    return row

function classify(repo):
    # Apply tier-classification precedence
    if repo in BUSINESS_BRAIN_tier1: return "Tier-1 active product/library"
    if repo in BUSINESS_BRAIN_tier2: return "Tier-2 domain-specific / periodic"
    if repo in BUSINESS_BRAIN_tier3: return derive_tier3_subclass(repo)  # support / archive-candidate / client-vertical / deprecated
    if repo in BUSINESS_BRAIN_archive_candidates: return "Archive/extraction candidate"
    if repo in OVERVIEW_only: return "Overview-only / not in BUSINESS_BRAIN"
    return "unclassified — REVIEW_REQUIRED"

function derive_tier3_subclass(repo):
    # client verticals: acma-projects, seanation, saipem, frontierdeepwater, client_projects, doris
    # business/admin support: aceengineer-admin, sabithaandkrishnaestates, teamresumes, achantas-data, achantas-media, hobbies, sd-work
    # strategy/private: aceengineer-strategy
    # asset/investment: assethold (note: ownership transferred per memory)
    # CAD: CAD-DEVELOPMENTS
    return appropriate subclass based on lookup table

function lookup_known_overlaps(repo):
    overlaps = {
      "investments": "Overlaps with assethold; per BUSINESS_BRAIN, investments → migrate to assethold + achantas-data, retire within 3 months",
      "assethold": "Receives investments migration; ownership transferred samdansk2 → vamseeachanta (memory)",
      "client_projects": "Generic client wrapper; per-client work routes to acma-projects/seanation/saipem/frontierdeepwater/doris when those exist",
      "workspace-hub": "Portfolio control plane — routes execution to per-repo docs, not the inverse",
      "assetutilities": "Shared utility library — repo-specific utilities stay in their repo unless 2+ repos need them",
      "aceengineer-website": "Public delivery surface only; firm strategic copy lives in private aceengineer-strategy (memory)",
      "aceengineer-strategy": "Private strategic copy authority; aceengineer-website pulls from here, not the reverse (memory)",
      "digitalmodel": "Numerical-model library; client-specific vertical work routes to the client repo (acma-projects, seanation, saipem, frontierdeepwater)",
      ...
    }
    return overlaps.get(repo, "none identified")

function derive_belongs_here_rule(repo, mission, classification):
    # Compose a one-sentence "work belongs here when..." rule grounded in the mission
    # Example: workspace-hub → "...when the work is portfolio-wide governance, harness, or cross-repo coordination"
    # Example: digitalmodel → "...when the work is reusable engineering calculation code/tests/methodology"

function derive_route_elsewhere_rule(repo, classification):
    # Compose a one-sentence "work should route elsewhere when..." rule
    # Example: workspace-hub → "...when the work is repo-specific execution that has a single owning repo"
    # Example: digitalmodel → "...when the work is one-off client-project data, route to the matching client repo"

function update_discovery_anchors():
    BUSINESS_BRAIN.md: add a single line under "Repositories" pointing to docs/REPO_MISSION_PORTFOLIO.md as the canonical mission/routing artifact (do not bloat onboarding file beyond 200 lines)
    ROUTING_INDEX.md: add cross-link in header noting that portfolio-wide mission/objective lives in docs/REPO_MISSION_PORTFOLIO.md and ROUTING_INDEX.md remains Tier-1 routing-only
    docs/README.md: add link to docs/REPO_MISSION_PORTFOLIO.md in the appropriate discovery section; flag legacy .agent-os/product/* references as legacy_source (do NOT delete them — that is #2553's scope)
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create | `docs/REPO_MISSION_PORTFOLIO.md` | Canonical human-readable portfolio mission/objective table |
| Create | `data/document-index/repo-portfolio-inventory.yaml` | Deterministic source-of-truth registry — one record per repo with all row fields plus memory-derived `notes` (assethold ownership, aceengineer copy split). Markdown table is generated/validated against this YAML. |
| Create | `scripts/tests/check_repo_mission_portfolio.sh` | Validation script enforcing C1-C12; runnable manually and from any future CI hook. Exit 0 on pass, non-zero with itemized failures otherwise. |
| Modify | `docs/BUSINESS_BRAIN.md` | Add single-line link to portfolio artifact (one-line addition; do not exceed 200-line target) |
| Modify | `docs/ROUTING_INDEX.md` | Add header note pointing to portfolio artifact for non-Tier-1 mission/routing |
| Modify | `docs/README.md` | Add link to portfolio artifact in discovery section; mark legacy `.agent-os/product/*` references as legacy (do not delete — defer to #2553) |
| Update | `docs/plans/README.md` | Add this plan's index row (handled by main session per write-only mode contract) |

**Explicitly NOT in this plan's scope:**
- Per-repo `AGENTS.md` / `README.md` / `mission.md` updates (out of scope; would multiply this from T3 to a multi-week refactor)
- Deletion of `.agent-os/product/*` legacy files (deferred to #2553-class follow-up)
- Reconciliation of `docs/WORKSPACE_HUB_REPOSITORY_OVERVIEW.md` (deferred to #2553)
- A separate `data/document-index/repo-mission-evidence.yaml` for sibling-repo evidence with hashes/URLs (the prior plan's broader registry — drove rev-4 MAJOR partly on scope creep; this plan's `repo-portfolio-inventory.yaml` carries the necessary fields directly without a second file)
- Test module under `tests/docs/` using `pytest` (the validation script in `scripts/tests/` is the chosen surface; promote to pytest only if/when the script needs structured assertions)

---

## TDD Test List

This is a documentation/governance issue — acceptance is artifact-presence and content-correctness, not numerical computation. Per `_template-issue-plan.md` guidance, present a checkable acceptance matrix instead of a unit-test table. The matrix below is the test list.

All checks below are deterministic and runnable via `scripts/tests/check_repo_mission_portfolio.sh` (Bash + `yq` for YAML parsing). The script reads `data/document-index/repo-portfolio-inventory.yaml` as source-of-truth, verifies it matches `docs/REPO_MISSION_PORTFOLIO.md`, and runs file-existence/anchor-link/contract-alignment checks. Manual review remains required only for mission-paragraph correctness against source documents.

**Generation direction (rev-3):** YAML is the hand-edited source-of-truth. The markdown table is generated by `check_repo_mission_portfolio.sh --generate` (writes `docs/REPO_MISSION_PORTFOLIO.md` from YAML). The default invocation (no flag) only validates parity (C13). Implementers MUST NOT hand-edit the markdown table; edits go to YAML and `--generate` re-emits.

**Dependencies (rev-3):** Script must check for `yq` at startup and exit with install instructions if missing. `yq` is widely available via `apt install yq`, `brew install yq`, or `pip install yq` (pip variant differs slightly; the script must pin to the Mike Farah Go-binary `yq` syntax `yq '.foo'` not the Python wrapper).

**Tier-1 keyword set for C5 (rev-3, from `docs/ROUTING_INDEX.md` lines 28-50, exact role-statement language):**
- `workspace-hub` mission MUST contain at least 2 of: `portfolio`, `control plane`, `harness`, `governance`, `cross-repo`
- `digitalmodel` mission MUST contain at least 2 of: `numerical`, `engineering calculation`, `OrcaWave` OR `OrcaFlex`, `hydrodynamics`, `solver`
- `assetutilities` mission MUST contain at least 2 of: `shared`, `Python utilities`, `engineering`, `library`
- `aceengineer-website` mission MUST contain at least 2 of: `public`, `website`, `marketing`, `demos` OR `calculators`, `deployment`

| Check ID | What it verifies | Method (in `check_repo_mission_portfolio.sh`) |
|---|---|---|
| C1 | `docs/REPO_MISSION_PORTFOLIO.md` exists and is non-empty | `[ -s docs/REPO_MISSION_PORTFOLIO.md ]` |
| C2 | YAML inventory has ≥ 23 records covering all local immediate-child repos | `yq '. | length' >= 23`; cross-check against `find -maxdepth 2 -name .git -type d` |
| C3 | Every YAML record has all required fields | `yq` schema check: `repo`, `tier`, `mission`, `source_path`, `routing_belongs_here`, `routing_route_elsewhere`, `overlap_notes`, `inventory_status`, `notes` |
| C4 | Every record's `source_path` resolves to a real file under the named repo, OR is exactly `none`/`legacy_source:<path>` with `mission == REVIEW_REQUIRED` or rationale in `notes` | `for record; check [ -f <repo>/<source_path> ] OR pattern-match` |
| C5 | Tier-1 records carry `tier: tier-1` AND mission text contains the per-repo keyword set defined above (rev-3) | for each Tier-1 repo, count keyword hits in mission field; assert ≥ 2 |
| C6 | Tier-1 records reference no contract that #2460-#2465 closed differently | static check: no record claims a Tier-1 role contradicting the closed-contract excerpts embedded in the script as constants |
| C7 | YAML records cover every overlap pair from #2533 body **symmetrically** — both repos in each pair carry a complementary `overlap_notes` entry that names the other (rev-3) | for each pair (A,B), assert A's `overlap_notes` mentions B AND B's `overlap_notes` mentions A |
| C8 | `docs/BUSINESS_BRAIN.md`, `docs/ROUTING_INDEX.md`, `docs/README.md` each contain a link to `docs/REPO_MISSION_PORTFOLIO.md` | `grep -l REPO_MISSION_PORTFOLIO.md` on each |
| C9 | Records exist for `pdf-large-reader`, `heavyequipemnt-rag`, `simpledigitalmarketing` with `inventory_status: not-present-locally` and `notes` naming the source | `yq` filter |
| C10 | `assethold` record's `notes` field contains `samdansk2` AND `ownership` AND `local origin may be stale` | `yq` extract + `grep` |
| C11 | `aceengineer-website` record's `routing_route_elsewhere` mentions `aceengineer-strategy`; `aceengineer-strategy` record's `tier` is `tier-3 strategy/private` and `notes` flags it as strategic-copy authority | `yq` extract |
| C12 | No record uses `.agent-os/product/mission.md` as `source_path` if `AGENTS.md`/`README.md`/`docs/README.md` exists in that repo | `for record; if source_path startswith .agent-os, assert no AGENTS.md/README.md/docs/README.md in same repo` |
| C13 | Markdown table matches YAML projection exactly (script regenerates MD from YAML in a temp file and diffs against committed MD) | `check_repo_mission_portfolio.sh --generate-to /tmp/proj.md && diff /tmp/proj.md docs/REPO_MISSION_PORTFOLIO.md` |

---

## Acceptance Criteria

- [ ] C1: `docs/REPO_MISSION_PORTFOLIO.md` exists and is the single canonical portfolio mission artifact.
- [ ] C2: Every local immediate-child git repo (23 repos as of 2026-05-02) has a record in `data/document-index/repo-portfolio-inventory.yaml` and a corresponding markdown row.
- [ ] C3: Every YAML record has all required fields: `repo`, `tier`, `mission`, `source_path`, `routing_belongs_here`, `routing_route_elsewhere`, `overlap_notes`, `inventory_status`, `notes`.
- [ ] C4: Every `source_path` value resolves to a real file in the named repo, OR is exactly `none` (mission = `REVIEW_REQUIRED`), OR is `legacy_source:<path>` (legacy `.agent-os/product/mission.md` fallback).
- [ ] C5+C6: Tier-1 records (`workspace-hub`, `digitalmodel`, `assetutilities`, `aceengineer-website`) are consistent with `docs/ROUTING_INDEX.md` per-repo roles and the closed contracts of #2460-#2465.
- [ ] C7: Every overlap pair flagged in #2533 body has **symmetric** `overlap_notes` (both repos in each pair name the other): `investments↔assethold`, `client_projects↔client-specific repos`, `workspace-hub↔per-repo execution docs`, `assetutilities↔repo-specific utilities`, `digitalmodel↔client/project verticals`, `aceengineer-website↔aceengineer-strategy`.
- [ ] C8: `docs/BUSINESS_BRAIN.md`, `docs/ROUTING_INDEX.md`, `docs/README.md` each contain a link to `docs/REPO_MISSION_PORTFOLIO.md`.
- [ ] C9: Records exist for `pdf-large-reader`, `heavyequipemnt-rag`, `simpledigitalmarketing` with `inventory_status: not-present-locally` and `notes` naming the source that mentions them.
- [ ] C10: `assethold` record's `notes` contains `samdansk2 → vamseeachanta ownership transfer per session memory; local origin may be stale`.
- [ ] C11: `aceengineer-website` record's `routing_route_elsewhere` mentions `aceengineer-strategy` for strategic-copy work; `aceengineer-strategy` record's `notes` flags it as strategic-copy authority per session memory.
- [ ] C12: No record uses `.agent-os/product/mission.md` as `source_path` when `AGENTS.md`/`README.md`/`docs/README.md` exists in the same repo.
- [ ] C13: Markdown table is consistent with YAML registry — every YAML record appears as a markdown row in the same order, and `scripts/tests/check_repo_mission_portfolio.sh` exits 0.
- [ ] Plan adversarial review complete with at least one provider verdict APPROVE or MINOR (no unresolved MAJOR).
- [ ] User has applied `status:plan-approved` (no self-approval).

---

## Adversarial Review Summary

| Provider | Verdict | Key findings |
|---|---|---|
| Gemini rev-1 | MAJOR | (1) Evasion of enforceability — dropped YAML registry; (2) Fragile validation C4 (markdown shell loop); (3) Unverifiable Tier-1 alignment (manual diff only); (4) Scope-deferral mismatch (#2553); (5) Memory-derived facts not committed to artifact. Full review at `scripts/review/results/2026-05-02-plan-2533-gemini.md`. |
| Codex | SKIPPED | #2479 codex-cli 0.124.0 stdin-hang regression — unavailable until 0.123.0 downgrade or upstream fix |
| Gemini rev-2 | MAJOR | rev-1 blockers (a-d) all RESOLVED. New defects: (1) **MAJOR** — C5 Tier-1 keyword set unspecified, making check non-deterministic; (2) MINOR — yq dependency not declared; (3) CLARIFICATION — markdown-vs-YAML generation direction undefined; (4) CLARIFICATION — overlap_notes symmetry. Full review appended to `scripts/review/results/2026-05-02-plan-2533-gemini.md`. |
| Claude r3 (fallback only) | NOT INVOKED | Gemini was available; r3 fallback not triggered |

**Overall result:** Rev-2 MAJOR on C5 keywords + 3 minor items. Rev-3 inline edits (this revision) address all four. No further review required pre-approval since fixes are mechanical clarifications, not architectural changes — user may accept or request rev-3 re-review at approval time.

Revisions made based on rev-1 Gemini MAJOR (rev-2):
- Reintroduced `data/document-index/repo-portfolio-inventory.yaml` as deterministic source-of-truth registry with all row fields plus memory-derived `notes`.
- Added `scripts/tests/check_repo_mission_portfolio.sh` as a deterministic validator covering C1-C13. Replaces "manual diff" / "shell loop over markdown" with `yq`-based assertions.
- Added C13 to require markdown-vs-YAML parity.
- Memory-derived facts (assethold ownership, aceengineer copy split) now live in the YAML `notes` field — committed to the artifact, not the plan.
- Removed prior justification language that mis-cited #2553 as a reason to omit the registry.

Revisions made based on rev-2 Gemini MAJOR (rev-3):
- Specified the C5 Tier-1 keyword set per repo (workspace-hub, digitalmodel, assetutilities, aceengineer-website), drawn directly from `docs/ROUTING_INDEX.md` lines 28-50. Check is now mechanically executable.
- Declared `yq` as a hard dependency; script must check at startup and exit with install instructions if missing. Pinned to Mike Farah Go-binary syntax.
- Defined generation direction: YAML is hand-edited source-of-truth; markdown is generated by `check_repo_mission_portfolio.sh --generate`. Implementers MUST NOT hand-edit the markdown.
- Made C7 require **symmetric** `overlap_notes` (both repos in pair name the other), not "collectively reference".

---

## Conflict-Resolution Protocol

When two repos overlap on mission, this plan's resolution rules:

1. **`investments` ↔ `assethold`:** `BUSINESS_BRAIN.md` already declares investments → migrate to assethold + achantas-data, retire within 3 months. Portfolio row records this; no further action this issue.
2. **`client_projects` ↔ client-specific repos:** Client-specific repo (acma-projects, seanation, saipem, frontierdeepwater, doris) wins when work targets a single client. `client_projects` is the catch-all for engagements that lack a dedicated repo.
3. **`workspace-hub` ↔ per-repo execution docs:** `workspace-hub` owns portfolio governance, harness, control-plane, durable standards, document-intelligence registries. Per-repo execution docs live in the owning repo. Cross-repo coordination → workspace-hub. Single-repo-scope work → owning repo.
4. **`assetutilities` ↔ repo-specific utilities:** Utility lives in `assetutilities` only when 2+ repos need it. Single-repo utility stays in the owning repo.
5. **`aceengineer-website` ↔ `aceengineer-strategy`:** Per memory, `aceengineer-strategy` is the private canonical strategic-copy source; `aceengineer-website` is the public delivery surface. Strategic copy work → strategy. Site delivery / pages / build → website.
6. **`digitalmodel` ↔ client/project verticals:** Reusable engineering code/tests/methodology → `digitalmodel`. One-off client analysis with non-reusable inputs → matching client vertical (acma-projects, seanation, saipem, frontierdeepwater).
7. **General fallback (when not listed above):** If sources conflict, the row's `overlap-notes` column records the conflict with `RESOLUTION_PENDING` and a follow-up issue is recommended in the plan's closeout comment. Never silently pick a side.

---

## Risks and Open Questions

- **Risk:** Some `AGENTS.md` files are pure pointers (no mission paragraph). Plan handles by walking the precedence list to next source.
- **Risk:** Mission paraphrasing may overstate intent for repos with sparse documentation. Plan mitigates by quoting source text where possible and marking sparse-source rows `REVIEW_REQUIRED`.
- **Risk (rev-2 mitigation):** Memory-derived constraints (assethold ownership, aceengineer copy split) are not in any committed file in this repo. Implementation MUST commit them to `data/document-index/repo-portfolio-inventory.yaml` `notes` field, so the artifact carries its own provenance. User should confirm the wording during approval.
- **Risk:** `docs/WORKSPACE_HUB_REPOSITORY_OVERVIEW.md` reconciliation deferred to #2553 — this plan only flags drift, does not fix the overview doc. If user wants reconciliation in this issue, scope expands and plan needs revision.
- **Risk (rev-2 mitigation):** Validation is now deterministic via `scripts/tests/check_repo_mission_portfolio.sh`. Promotion to a pre-commit hook or CI surface is a follow-up issue, not in this plan's scope.
- **Open:** Should the artifact include the four "Archive / extraction candidates" (`investments`, `rock-oil-field`, `seanation`, `saipem`) as full active rows or as a separate section? Plan's default: full row each, with `classification` reflecting archive-candidate status and `routing-rule-route-elsewhere` documenting the migration target.
- **Open:** Should `pdf-large-reader` row be created at all when not present locally? Plan's default: yes, marked `inventory-drift: not-present-locally; mentioned in #2533 body` so that future workers have provenance.

---

## Complexity: T3

**T3** — touches portfolio-wide governance (23 repos), cross-references multiple closed contracts (#2460-#2465), commits memory-derived constraints, modifies three discovery anchor files, and adds a deterministic validation script. New canonical artifact takes effect across the entire ecosystem. High coordination cost across waves matching #2533 body: Wave 1 = Tier-1 mission alignment + #2460-#2465 consistency; Wave 2 = Tier-2 mission/objective extraction; Wave 3 = Tier-3/support/archive classification + no-new-issues guidance; Wave 4 = portfolio table integration, dedupe/conflict notes, discovery-anchor link updates, validation-script run.
