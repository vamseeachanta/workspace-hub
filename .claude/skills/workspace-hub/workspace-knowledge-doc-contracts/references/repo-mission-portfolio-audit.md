# Archived Skill: `repo-mission-portfolio-audit`

Original path: `/home/vamsee/.hermes/skills/workspace-hub/repo-mission-portfolio-audit`
Archived into: `/home/vamsee/.hermes/skills/.archive/umbrella-2026-04-29/workspace-hub/repo-mission-portfolio-audit`
Consolidation date: 2026-04-29

---

---
name: repo-mission-portfolio-audit
description: Audit the workspace-hub repo portfolio to extract each repo's mission, identify documentation gaps, and prioritize a plan/approval sequence with explicit LLM-wiki weighting for future issue triage.
version: 1.0.1
category: workspace-hub
tags: [portfolio, mission, repo-audit, llm-wiki, governance, planning]
---

# Repo Mission Portfolio Audit

Use when the user wants a portfolio-wide understanding of what each repo is for, what should be revised first, or how future GitHub issue creation should incorporate repo mission and LLM-wiki value.

## Inputs to gather

1. Cross-session context
- Run `session_search` with broad OR terms like:
  - `repo mission OR adversarial plan OR llm-wiki OR issue planning OR repo portfolio`
- Use this to recover prior conclusions, open strategy lanes, and existing planning artifacts.

2. Canonical workspace context
- Read:
  - `docs/BUSINESS_BRAIN.md`
  - `docs/WORKSPACE_HUB_REPOSITORY_OVERVIEW.md`
  - root repo overview files
  - `docs/README.md`
- These define tiering, repo roles, and the ecosystem control-plane story.

3. Relevant plan lanes
- Read active portfolio/knowledge plans when relevant, especially:
  - `docs/plans/2026-04-20-issue-2398-llm-wiki-spinout-vs-embedded-architecture.md`
  - `docs/plans/2026-04-20-issue-2420-repo-portfolio-steering-contract.md`
  - `docs/plans/2026-04-12-llm-wiki-ecosystem-strengthening-gh-stories.md`
  - recent handoffs under `docs/handoffs/` and `docs/session-handoffs/`

4. Live repo inventory
- Enumerate actual subrepos from the workspace root by checking which immediate child directories contain `.git`.
- For each repo, inspect presence of:
  - workflow contract file
  - top-level README
  - provider-specific config file
  - `.agent-os/product/mission.md`
  - `.agent-os/product/roadmap.md`
  - `.agent-os/product/decisions.md`
- Also capture git cleanliness when it matters before proposing edits.

## Practical extraction pattern

For each repo, derive the mission from the strongest available source in this order:
1. `.agent-os/product/mission.md`
2. `README.md`
3. workflow contract file
4. `docs/README.md`
5. provider-specific config file

Record:
- repo name
- tier (from `docs/BUSINESS_BRAIN.md` if available)
- mission summary
- source used for the summary
- documentation completeness gaps

## Interactive user review pattern

Use this when the user wants to review mission/objective documents directly and provide edits one file at a time.

1. Build a deterministic review queue before opening files:
   - active portfolio plan/report files first when the user is reviewing the process itself
   - repo-level mission documents next (for example `.agent-os/product/mission.md`, while treating `.agent-os` as legacy evidence unless a control-plane plan says otherwise)
   - portfolio context docs after repo mission docs when needed (`docs/BUSINESS_BRAIN.md`, `docs/WORKSPACE_HUB_REPOSITORY_OVERVIEW.md`, mission revision reports)
2. Open exactly one file at a time in the editor with `code -r <absolute-path>` and wait for the user's explicit response before moving on.
3. If the user says "no changes" for a file, do not edit it; open the next queued file.
4. If the user provides changes, apply only those changes, verify the diff for that file, and then continue the one-file-at-a-time review.
5. When mission review reveals ecosystem-health gaps, search existing GitHub issues first. Prefer commenting/updating/reopening an existing issue; create a new focused issue only when no existing issue reasonably covers the gap. Typical issue-worthy gaps: repo should be deprecated/no-new-issues, repo mission conflicts with another repo, README/control-plane/mission docs are missing or stale, repo should be merged/split, routing/indexing rules are unclear, or client/confidentiality boundaries are ambiguous.
6. If the user gives broad permission to open or reopen GitHub issues for repo-ecosystem health, treat that as authorization to act during the mission-review sweep, but still do the duplicate search first and keep changes focused. Do not create issues for every wording edit; create/reopen only for distinct ecosystem-health work that should survive beyond the current document review.
7. Keep the mission-review umbrella issue as the anchor when one exists (for example a repo-portfolio mission/objective review issue). Link any new or reopened issues back to that anchor.
8. When the review reveals that a repo should be retired/deprecated, capture it as a first-class mission outcome rather than a vague cleanup note: state the retirement timeframe, destination repos for each artifact class, the no-new-durable-work rule, and the condition that retirement happens only after migration is verified. Require a migration manifest or equivalent evidence showing what moved where, what was intentionally archived/left as a pointer, and how useful information, provenance, and progression history were preserved. Create or update a focused GitHub issue for the migration/retirement work after duplicate search.
9. For temporary/archive repos that should feed Tier-1 repos, frame the mission as **active triage only**: sanity-check every file, classify artifacts as code/data/analysis/reference/duplicate/discard candidate, migrate useful code/data/analysis to the appropriate Tier-1 destination, and retire or reduce the source repo to a minimal pointer/manifest only after verified no-loss migration. Common destination mapping in this workspace: `digitalmodel` for reusable engineering methods/calculations/workflows, `assetutilities` for reusable utility code/tooling, `worldenergydata` for energy data extraction/normalization/analysis workflows, and `workspace-hub` for coordination manifests/issues/routing decisions.
10. For client/project-context repos, distinguish project data/context from reusable engineering code. A recurring pattern is: client repo owns client/project context and GTM delivery framing, while reusable algorithms/code should be centralized in the engineering computation core repo (commonly `digitalmodel`) unless the user explicitly says the client repo should own standalone implementation. Capture whether outputs are reusable by other clients/teams and whether confidentiality/client-boundary restrictions apply. Examples seen in this workspace: ACMA and Doris are client/project-context repos for consulting delivery; OGManufacturing outcomes may be reusable by other clients/teams while reusable code should primarily centralize in `digitalmodel`.
11. For business/entity administration repos, do not force them into a pure investment/project archive pattern. Capture the dual mission when present: investment/deal tracking plus ongoing corporate administration such as finance tracking, tax filing support, entity/legal records, statements, compliance notes, and administrative task history. Add users/personas for administrators or tax preparers when the repo supports filings/admin work, and preserve auditable records rather than migrating them away unless the user identifies a better long-term home.
12. For restricted personal/professional-document repos, avoid hallucinated product/platform missions. Treat them as scoped reference archives tied to the named person's work context and only activate them for the explicit domain or opportunity the user names (for example bio/pharmacy). State what the repo is **not** (not general software/engineering/admin work), the activation trigger (specific request or explicit strategic direction), confidentiality/provenance requirements, and whether a future durable destination should be created if repeated work develops.
13. For client-specific extraction/archive repos, frame the mission around information extraction and archival rather than active delivery: identify the client/project boundary, sanity-check for sensitivity and usefulness, extract data/information/analysis worth preserving, migrate reusable artifacts only after sensitivity review, create a no-loss extraction/archive manifest, and archive/retire the repo when extraction is verified. Do not create a new issue if an existing client/archive migration issue already covers it; otherwise create a focused follow-up issue linked to the portfolio mission umbrella.
14. When the review reaches `docs/BUSINESS_BRAIN.md` or another ecosystem brain/context file, treat it as a compact source-of-truth refresh rather than a repo mission rewrite. Reconcile the user's current facts about provider accounts, machine roles, licensed-software dispatch targets, Hermes/control-plane ownership, repo classifications, and archive/retirement candidates. Keep it concise, link out to detailed issues/registries for large inventories, and create focused follow-up issues for durable work such as machine/software/auth inventory, licensed Windows OrcaFlex/AQWA dispatch, or periodic Business Brain refresh. Do not preserve stale provider-account assumptions if the user corrects them (for example, one paid Codex account rather than multiple accounts).

## Execution pattern after the audit recommendation

Use this when the user accepts the audit recommendation and asks to "execute the recommended next moves" or similar.

1. Re-check live GitHub state before acting:
   - search for an already-open portfolio mission/objective issue to avoid duplicates
   - view the recommended parent/related issues and record state/title/labels
   - if a related child issue is already implemented on a branch, check for an existing PR before creating one
2. If no suitable portfolio-wide issue exists, create one with a class-level title such as `feat(repo-portfolio): review and revise mission/objective statements across active repos`.
3. The new issue body should include:
   - Tier-1/Tier-2/Tier-3 starting inventory from `docs/BUSINESS_BRAIN.md`
   - deliverables for a canonical portfolio mission artifact, classification, source evidence, routing rules, and overlap/conflict notes
   - related links to the umbrella/structure/routing issues already found
   - explicit planning-gate language: issue -> resource intel -> plan -> adversarial review -> plan-review -> user approval -> plan-approved -> implementation
4. Immediately draft the repo-tracked plan under `docs/plans/YYYY-MM-DD-issue-NNN-<slug>.md` and update `docs/plans/README.md` if the repo uses that index.
5. Commit and push the draft plan/index update, then comment on:
   - the new portfolio issue with plan path + commit + current gate state
   - parent/related umbrella issues with the new issue link and scope boundary
   - any still-open child issue with PR/branch evidence if you touched its routing state
6. Do **not** add `status:plan-review` until adversarial review has actually run and the plan summary is populated. Draft-planned means draft only.

## Required synthesis

Before recommending new issue creation, explicitly distinguish **repo mission/objective review** from adjacent but different work classes:
- **routing/indexing/code-placement** issues answer "where should future work land and be retrieved?"
- **mission/objective** issues answer "what is this repo for, what work belongs here, and should the repo remain active, archival, merged, or no-new-issues?"

When live GitHub already has a routing/indexing issue family (for example a contract issue plus per-repo routing child issues), do not treat that as complete portfolio mission review. Instead:
1. Verify the live state of the related issues with `gh issue view/list` rather than relying on stale plan/report text.
2. Identify which children are closed, which remain open/working, and whether any freshness report is stale relative to closed issues.
3. Recommend extending an existing umbrella issue when it reasonably owns mission/objective review; otherwise recommend a new portfolio-wide issue titled at the mission/objective class level.
4. For a mission/objective issue, require each repo to be classified as active product/library, client vertical, business/admin support, archive/reference, or deprecated/no-new-issues.
5. Require each repo's output to include both "work belongs here when..." and "work does not belong here when..." rules, plus duplicate/boundary checks between similar repos.

Produce these outputs:

### 1. Ecosystem mission model
Distill the portfolio into a small set of role classes, typically:
- control plane
- engineering computation core
- shared utility substrate
- GTM / externalization layer
- domain/client verticals
- archives/support repos

### 2. Revision order
Recommend a wave-based approval order instead of a flat repo list.
Default ordering:
1. `workspace-hub`
2. Tier-1 repos
3. Tier-2 repos
4. Tier-3 repos

Explain why each wave comes before the next.

### 3. Documentation gaps
Call out missing or weak surfaces, especially:
- repos missing a workflow contract file
- repos missing a top-level README
- repos missing structured `.agent-os/product/*` mission files
- repos whose mission is only implied by a pointer file
- repos that are too dirty locally to revise safely without state triage

### 4. LLM-wiki weighting rule
When the user wants future issue creation to consider knowledge value, explicitly propose a scoring rubric that includes LLM-wiki contribution.

A good default issue score is:
- 35% repo mission / strategic alignment
- 25% execution leverage / downstream impact
- 20% LLM-wiki contribution
- 10% governance / drift reduction
- 10% implementation readiness

Define the 20% LLM-wiki component using:
- durable knowledge capture
- cross-repo usefulness
- retrieval/discoverability improvement
- promotion-readiness into wiki/docs/routing

## Good output structure

Use:
1. High-level conclusion
2. What prior sessions already established
3. Recommended mission-revision order
4. Per-repo mission snapshot by tier/wave
5. Documentation gaps
6. LLM-wiki-weighted issue triage rule
7. Concrete next-step recommendation

## Important cautions

- Do not invent repo mission text if no strong source exists; mark it as a gap.
- Do not revise files directly unless the user explicitly asks for edits; this audit is usually a planning/approval precursor.
- If the workspace root or a target repo is dirty, mention it before recommending direct changes.
- Treat unresolved architecture questions (for example LLM-wiki embedded vs spinout) as current-state constraints, not settled facts.

## Reusable conclusion pattern

A common portfolio conclusion in this ecosystem is:
- `workspace-hub` = control plane
- `digitalmodel` = engineering computation core
- `assetutilities` = shared utility substrate
- `aceengineer-website` = GTM/proof surface
- `llm-wikis` = cross-repo durable knowledge layer

Use this as a hypothesis only when supported by the current docs and session evidence.