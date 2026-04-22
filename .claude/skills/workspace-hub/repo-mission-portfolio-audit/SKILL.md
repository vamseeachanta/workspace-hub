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

## Required synthesis

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