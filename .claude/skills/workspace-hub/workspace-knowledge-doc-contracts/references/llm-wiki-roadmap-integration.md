# Archived Skill: `llm-wiki-roadmap-integration`

Original path: `/home/vamsee/.hermes/skills/coordination/llm-wiki-roadmap-integration`
Archived into: `/home/vamsee/.hermes/skills/.archive/umbrella-2026-04-29/coordination/llm-wiki-roadmap-integration`
Consolidation date: 2026-04-29

---

---
name: llm-wiki-roadmap-integration
description: Integrate repo-ecosystem work into an existing llm-wiki / knowledge-roadmap issue without creating duplicate GitHub issues.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [github, llm-wiki, roadmap, issue-management, knowledge-management]
    related_skills: [github-issues, knowledge-source-recon, llm-wiki]
---

# LLM-Wiki Roadmap Integration

## Use when
- The user asks to "add what needs to be done" to an existing llm-wiki / knowledge-base issue portfolio
- The request spans both the central knowledge base and downstream repos
- There is a risk of creating duplicate umbrella issues instead of integrating existing work

## Core pattern
Do not default to creating new issues.
First determine whether the needed work already exists as:
1. an llm-wiki umbrella / roadmap issue
2. repo-specific remediation issues
3. a contract / policy issue tying the repo set together

If those already exist, integrate by editing the umbrella and cross-linking the dependency chain.

## Steps
1. Load context from the existing knowledge docs and roadmap artifacts.
   - Read the llm-wiki unified review / operating model
   - Read the latest issue-discovery handoff
   - Read any tier-1 or repo-portfolio scorecards if the request mentions ecosystem or individual repos
   - For current workspace-hub state, the highest-value docs are often:
     - `docs/handoffs/2026-04-20-llm-wiki-strengthening-issue-discovery-exit-handoff.md`
     - `docs/document-intelligence/llm-wiki-resource-doc-intelligence-operating-model.md`
     - `docs/reports/2026-04-16-llm-wiki-resource-intelligence-unified-review.md`
     - `docs/reports/llm-wiki-staged-batch-packs.md`

2. Search live GitHub issues before drafting anything.
   - Look for the knowledge umbrella/epic
   - Look for repo-specific remediation issues
   - Look for a shared contract issue
   - With `gh search issues`, prefer `--owner vamseeachanta` or explicit `repo:owner/name` qualifiers. Avoid relying on `user:vamseeachanta` inside a quoted query; the gh CLI can quote it into an invalid search string.
   - Search both exact and broad terms, then deduplicate: `llm-wiki`, `"LLM Wiki"`, `knowledge/wikis`, `wiki knowledge`, repo-specific `repo:vamseeachanta/digitalmodel` queries.

3. Build the missing-work delta.
   - Separate true gaps from already-open work
   - If the gap is only missing integration, do not create new issues
   - Inspect labels/status on the candidate issues, not just titles. `status:plan-review`, `status:plan-approved`, `wip:*`, and recent comments can change the correct next action.
   - For llm-wiki roadmap reviews, always inspect the current umbrella body for later-added work streams. In this repo, #2390 may include Work Stream G for tier-1 repo routing/retrieval surfaces, which is easy to miss if only reading the older handoff.

4. Prefer this integration sequence:
   - edit the existing umbrella/epic body to add a new work stream
   - add the existing issue numbers as a grouped dependency set
   - post a comment explaining why the new work stream belongs in the umbrella
   - update the shared contract / parent issue to backlink the umbrella when useful

5. Verify after editing or reporting.
   - re-read the umbrella body
   - re-read the related issue body
   - confirm the new section/comment actually rendered and uses the intended issue numbers
   - If only producing a review summary, include the live repo split explicitly: central knowledge work in `workspace-hub`, individual-repo consumption/remediation issues such as `digitalmodel` #503 and workspace-hub tier-1 issues #2461-#2465.

## Reusable dependency model
For cross-repo knowledge work, use this framing:
- knowledge base / llm-wiki = durable cross-repo knowledge layer
- shared routing/index contract = portfolio-wide execution contract
- repo-specific remediation issues = landing pads for correct code/docs/tests placement
- daily freshness/audit issue = sustaining governance loop

## Why this works
This avoids duplicate issue trees and keeps the llm-wiki roadmap focused on compounding knowledge value while still acknowledging that knowledge only pays off when downstream repos have trusted routing surfaces.

## Pitfalls
- Do not create a second umbrella if an active roadmap issue already exists
- Do not create repo-specific issues if the repo remediation set already exists live
- Do not claim a repo-ecosystem gap is new without checking scorecards / handoffs / live issues
- Always verify the post-edit body and the cross-link comment

## Minimal deliverable
A successful run usually produces:
- one umbrella body edit
- one explanatory roadmap comment
- one backlink edit on the contract/parent issue
- zero new issues unless a true gap remains
