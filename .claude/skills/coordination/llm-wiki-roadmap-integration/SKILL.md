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

2. Search live GitHub issues before drafting anything.
   - Look for the knowledge umbrella/epic
   - Look for repo-specific remediation issues
   - Look for a shared contract issue

3. Build the missing-work delta.
   - Separate true gaps from already-open work
   - If the gap is only missing integration, do not create new issues

4. Prefer this integration sequence:
   - edit the existing umbrella/epic body to add a new work stream
   - add the existing issue numbers as a grouped dependency set
   - post a comment explaining why the new work stream belongs in the umbrella
   - update the shared contract / parent issue to backlink the umbrella when useful

5. Verify after editing.
   - re-read the umbrella body
   - re-read the related issue body
   - confirm the new section/comment actually rendered and uses the intended issue numbers

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
