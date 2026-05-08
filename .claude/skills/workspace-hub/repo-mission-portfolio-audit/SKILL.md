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

## Client-facing ecosystem PDF pattern

When producing a one-page, client-facing repo ecosystem PDF for engineering consulting:
1. Treat the current Tier-1 ecosystem as eight repos unless live docs say otherwise: `workspace-hub`, `digitalmodel`, `assetutilities`, `worldenergydata`, `llm-wiki`, `assethold`, `aceengineer-website`, and `aceengineer-strategy`.
2. In the flowchart itself, include the repo name inside every block, not just role labels, so reviewers can map each function to a GitHub location quickly.
3. Include a repo-links block with clickable GitHub links and three concise purpose bullets per repo.
4. Make `llm-wiki` explicit as the knowledge storehouse / public methodology corpus / retrieval-context layer feeding engineering agents and reports.
5. Verify the rendered PDF is a single landscape page, has no visual cut-off, and preserves links (for Chrome-generated PDFs, `pdfinfo`, `pdftotext`, `strings "$PDF" | grep 'https://github.com/...'`, and a browser visual check worked well).

See `references/client-facing-ecosystem-pdf.md` for the session-derived layout and verification checklist.

## Reusable conclusion pattern

A common portfolio conclusion in this ecosystem is:
- `workspace-hub` = control plane and governed work orchestration
- `digitalmodel` = engineering computation core
- `assetutilities` = shared utility substrate
- `worldenergydata` = energy data layer
- `llm-wiki` = cross-repo durable knowledge storehouse and retrieval context
- `aceengineer-website` = GTM/proof surface
- `aceengineer-strategy` = private GTM/pilot operations
- `assethold` = business/finance evidence and decision support

Use this as a hypothesis only when supported by the current docs and session evidence.