# Repo Mission Revision Sequence and Approval Packet

Date: 2026-04-21
Repo: `/mnt/local-analysis/workspace-hub`
Status: draft working report

## Purpose

Create a grounded sequence for repo-by-repo mission revision and approval across the workspace ecosystem, using current repo files, recent planning sessions, and the established adversarial review workflow.

This report is not an implementation plan for a GitHub issue. It is a steering artifact to decide the approval order and the first packet to take into formal plan/review.

## Grounding Used

### Cross-session context
- Session recall on repo mission, adversarial plan, llm-wiki, issue planning, and repo portfolio work
- Prior findings that llm-wiki is now a cross-repo durable-knowledge layer, not a side track
- Prior findings that workspace-hub currently owns most planning/governance/intelligence surfaces

### Repo-level documents
- `README.md`
- `docs/README.md`
- `docs/BUSINESS_BRAIN.md`
- `docs/WORKSPACE_HUB_REPOSITORY_OVERVIEW.md`
- `AGENTS.md`

### Current plan / handoff artifacts
- `docs/plans/2026-04-20-issue-2398-llm-wiki-spinout-vs-embedded-architecture.md`
- `docs/plans/2026-04-20-issue-2420-repo-portfolio-steering-contract.md`
- `docs/plans/2026-04-12-llm-wiki-ecosystem-strengthening-gh-stories.md`
- `docs/handoffs/2026-04-20-ecosystem-skills-planning-and-review-exit-handoff.md`

### Live repo scan inputs
For each local subrepo present under workspace-hub root:
- `AGENTS.md`
- `README.md`
- `CLAUDE.md`
- `.agent-os/product/mission.md`
- `.agent-os/product/roadmap.md`
- `.agent-os/product/decisions.md`

---

## Ecosystem Mission Model

The current ecosystem resolves into four primary layers:

1. `workspace-hub` — control plane
   - issue planning
   - adversarial review workflow
   - standards and governance
   - cross-repo orchestration
   - document intelligence and llm-wiki coordination

2. `digitalmodel` — engineering computation core
   - offshore, subsea, and marine engineering calculation library
   - standards-to-code path
   - most likely primary downstream consumer of engineering knowledge assets

3. `assetutilities` — shared utility substrate
   - reusable business, Excel, data, and automation utilities
   - common support layer for multiple repos

4. `aceengineer-website` — GTM and externalization layer
   - public-facing capability proof
   - demos, positioning, and marketing output from durable internal knowledge

Tier-2 and Tier-3 repos should be revised against this spine rather than independently.

---

## Recommended Approval Order

### Wave 1 — portfolio spine
1. `workspace-hub`
2. `digitalmodel`
3. `assetutilities`
4. `aceengineer-website`

### Wave 2 — domain and client execution repos
5. `worldenergydata`
6. `OGManufacturing`
7. `acma-projects`
8. `seanation`
9. `frontierdeepwater`
10. `rock-oil-field`
11. `investments`

### Wave 3 — operational/support/personal repos
12. `aceengineer-admin`
13. `aceengineer-strategy`
14. `client_projects`
15. `saipem`
16. `CAD-DEVELOPMENTS`
17. `doris`
18. `teamresumes`
19. `sd-work`
20. `assethold`
21. `sabithaandkrishnaestates`
22. `hobbies`
23. `achantas-data`
24. `achantas-media`

Rationale:
- Wave 1 defines the canonical ecosystem roles first
- Wave 2 aligns domain and client-delivery repos to that model
- Wave 3 cleans up supporting and lower-frequency repos after the main portfolio language is settled

---

## Repo Inventory Snapshot

| Repo | Tier | Current mission surface | Main gap to address first |
|---|---|---|---|
| `workspace-hub` | T1 | README + docs + BUSINESS_BRAIN + repository overview | Mission is split across multiple docs; needs one canonical repo mission contract |
| `digitalmodel` | T1 | README + AGENTS + CLAUDE | No structured `.agent-os/product/{mission,roadmap,decisions}.md` found |
| `assetutilities` | T1 | Strong `.agent-os` mission/roadmap/decisions | Align role to portfolio spine; local dirty state should be triaged before implementation work |
| `aceengineer-website` | T1 | README + AGENTS + CLAUDE | No structured mission/roadmap/decisions files |
| `worldenergydata` | T2 | README + AGENTS + CLAUDE | No structured `.agent-os` mission files found |
| `OGManufacturing` | T2 | Strong `.agent-os` mission/roadmap/decisions | Align wording to portfolio spine and downstream role |
| `acma-projects` | T2 | `.agent-os/product/mission.md` present | Roadmap/decisions thin or absent |
| `seanation` | T2 | Strong `.agent-os` mission/roadmap/decisions | Align to portfolio routing and llm-wiki role |
| `frontierdeepwater` | T2 | `.agent-os/product/mission.md` present | Roadmap/decisions thin or absent |
| `rock-oil-field` | T2 | `.agent-os/product/mission.md` + CLAUDE | Missing `AGENTS.md` and `README.md` |
| `investments` | T2 | Strong `.agent-os` mission/roadmap/decisions | Clarify ecosystem role vs personal/portfolio analytics |
| `aceengineer-admin` | T3 | Strong `.agent-os` mission/roadmap/decisions | Align to consulting-ops support role |
| `aceengineer-strategy` | T3 | README only | Missing `AGENTS.md`, `CLAUDE.md`, and structured mission set |
| `client_projects` | T3 | `.agent-os/product/mission.md` present | Roadmap/decisions thin or absent |
| `saipem` | T3 | Strong `.agent-os` mission/roadmap/decisions | Clarify client-delivery vs reusable knowledge ownership |
| `CAD-DEVELOPMENTS` | T3 | README + AGENTS + CLAUDE | No structured `.agent-os` mission set |
| `doris` | T3 | Strong `.agent-os` mission/roadmap/decisions | Clarify where it fits relative to data/analytics stack |
| `teamresumes` | T3 | Strong `.agent-os` mission/roadmap/decisions | Low-priority role clarification only |
| `sd-work` | T3 | `.agent-os/product/mission.md` present | Roadmap/decisions thin or absent |
| `assethold` | T3 | Strong `.agent-os` mission/roadmap/decisions | Align to investments / finance boundary |
| `sabithaandkrishnaestates` | T3 | Strong `.agent-os` mission/roadmap/decisions | Low-priority role clarification only |
| `hobbies` | T3 | Strong `.agent-os` mission/roadmap/decisions | Low-priority role clarification only |
| `achantas-data` | T3 | AGENTS contract pointer + README | Needs explicit purpose statement, not just inherited contract |
| `achantas-media` | T3 | AGENTS contract pointer + CLAUDE | Needs README and explicit purpose statement |

---

## Required Revision Packet for Every Repo

Each repo should eventually get the same review packet:

1. Mission statement
   - what the repo exists to do
   - who uses it
   - what it explicitly does not own

2. Ecosystem role
   - control plane / engineering core / utility substrate / GTM layer / domain vertical / support/archive

3. Dependency map
   - upstream inputs
   - downstream consumers
   - relationship to llm-wiki: producer / consumer / both / none

4. Canonical file set
   - `AGENTS.md`
   - `README.md`
   - `CLAUDE.md`
   - `.agent-os/product/mission.md`
   - `.agent-os/product/roadmap.md`
   - `.agent-os/product/decisions.md`
   - `docs/README.md` if repo has a docs surface

5. Review packet
   - adversarial plan review before approval
   - then later adversarial artifact/code review after implementation

---

## LLM-Wiki Weighting for Future Issue Selection

Future work issues should include a 20% llm-wiki weighting.

### Recommended issue scoring model
- 35% strategic mission alignment
- 25% execution leverage / downstream repo impact
- 20% llm-wiki contribution
- 10% governance / drift reduction
- 10% implementation readiness

### LLM-wiki contribution sub-score
Score candidate issues on:
1. knowledge capture value
2. cross-repo usefulness
3. retrieval / provenance / discoverability improvement
4. promotion readiness into durable repo knowledge

### High-scoring llm-wiki issue examples
- standards provenance and reuse contracts
- wiki promotion of curated durable knowledge
- knowledge routing metadata to downstream repos
- retrieval contracts for issue workflows
- architecture decisions for embedded vs spinout knowledge boundaries

### Low-scoring llm-wiki issue examples
- isolated presentational tweaks
- narrow refactors with no durable knowledge gain
- purely local fixes with no retrieval or cross-repo reuse consequence

---

## First Approval Packet: `workspace-hub`

### Why start here
- It is the control plane for the entire portfolio
- The repo already contains the strongest mission/governance/intelligence evidence
- It is the right place to define how llm-wiki, issue planning, repo routing, and downstream repo roles fit together
- Revising downstream repo missions before `workspace-hub` would create drift

### Current grounded state
The repo mission is spread across:
- `README.md`
- `docs/README.md`
- `docs/BUSINESS_BRAIN.md`
- `docs/WORKSPACE_HUB_REPOSITORY_OVERVIEW.md`
- `AGENTS.md`

This already implies a clear role, but the role is fragmented:
- central repo-management hub
- GSD control plane
- multi-provider AI workflow orchestrator
- cross-repo governance surface
- document-intelligence and llm-wiki host/coordinator

### Proposed workspace-hub mission statement direction
`workspace-hub` is the central control plane for the engineering repo ecosystem. It governs issue planning, adversarial review, repo orchestration, document intelligence, llm-wiki coordination, and cross-repo standards so that engineering knowledge can flow from raw sources to validated implementation and outward to GTM surfaces.

### Proposed explicit non-goals
`workspace-hub` is not:
- the main engineering calculation engine (`digitalmodel` owns that)
- the generic shared utility library (`assetutilities` owns that)
- the public marketing/delivery surface (`aceengineer-website` owns that)
- a dumping ground for every project-specific artifact

### Proposed ecosystem-role definitions to lock here
- `workspace-hub` = control plane
- `digitalmodel` = engineering computation core
- `assetutilities` = shared utility substrate
- `aceengineer-website` = GTM / externalization layer
- `worldenergydata` = domain data ingestion/analysis layer
- llm-wiki = durable cross-repo knowledge layer, with repo-boundary architecture still under evaluation per `#2398`

### Files to revise in the first workspace-hub packet
Primary:
- `README.md`
- `docs/README.md`
- `docs/BUSINESS_BRAIN.md`
- `docs/WORKSPACE_HUB_REPOSITORY_OVERVIEW.md`

Possible follow-on if needed:
- `AGENTS.md`
- `CLAUDE.md`

### Approval criteria for the first workspace-hub packet
- one canonical repo mission exists and is not contradictory across the main docs
- the repo’s control-plane role is explicit
- non-goals are explicit
- llm-wiki is described as a durable knowledge layer without prematurely freezing the spinout decision from `#2398`
- downstream repo roles are named consistently
- the language is specific enough to guide future issue triage and repo mission revisions

### Suggested formal next step
Create a dedicated GitHub issue for:
`feat(portfolio): canonicalize workspace-hub repo mission and ecosystem role contract`

Then draft the canonical issue plan under `docs/plans/` and route it through adversarial plan review before user approval.

---

## Recommended Execution Sequence After This Report

1. User approves that `workspace-hub` is the first repo to revise
2. Create the GitHub issue for the workspace-hub mission contract
3. Draft the canonical issue plan
4. Run adversarial plan review
5. User approves or requests revision
6. Only then revise repo files
7. Repeat repo-by-repo using the approved spine
8. After Wave 1 is approved, audit and rank GH issues with the 20% llm-wiki weighting rubric

---

## Immediate Recommendation

Proceed next with a formal issue + plan for `workspace-hub` mission canonicalization before touching any downstream repo mission files.
