# Archived Skill: `roadmap-to-github-issue-wave`

Original path: `/home/vamsee/.hermes/skills/coordination/roadmap-to-github-issue-wave`
Archived into: `/home/vamsee/.hermes/skills/.archive/umbrella-2026-04-29/coordination/roadmap-to-github-issue-wave`
Consolidation date: 2026-04-29

---

---
name: roadmap-to-github-issue-wave
description: Turn a roadmap/readiness review into a de-duplicated GitHub epic + child issue set with verification and explicit scope boundaries.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [github, roadmap, issue-creation, triage, de-duplication, planning]
    related_skills: [github-issues, issue-tree-decomposition, writing-plans]
---

# Roadmap -> GitHub Issue Wave

Use when you have already produced a roadmap, readiness matrix, or gap analysis and the next step is to create the missing GitHub issues without duplicating existing work.

## When to use
- A roadmap identifies future work and the user wants issues created
- The user names a new domain/career lane and asks to research practices, create GitHub features/issues, or build job-ready capability; first create a lightweight roadmap artifact, then turn it into an issue wave
- You have an issue/review/readiness summary and need to convert only the missing items into GitHub issues
- You need one umbrella issue plus a small set of focused child issues

## Core pattern
0. If the roadmap does not exist yet, create a lightweight roadmap first
   - Put it under `docs/roadmaps/<domain>-<purpose>-roadmap.md` when it is durable product/career direction
   - Mine local job-market scans or strategy docs for existing demand signals before fresh web research
   - Check current external practice/tool anchors just enough to avoid stale framing
   - Include a capability-wave sequence and an initial issue set in the roadmap
   - Commit/push the roadmap before or immediately after creating the issue wave when repo policy permits docs-only commits

1. Ground on the roadmap artifact first
   - Read the roadmap/review doc that defines the future work
   - Extract the exact candidate issues to create

2. Audit existing issues before drafting anything
   - Search GitHub by the key nouns/phrases for each candidate
   - Check both open and closed issues
   - Classify each candidate as:
     - already open -> do not recreate
     - already closed/delivered -> do not recreate
     - adjacent but not duplicate -> reference it
     - missing -> eligible to create

3. Reuse existing labels exactly
   - Audit repo labels before creation
   - Only use labels that actually exist
   - Prefer the smallest stable label set needed for routing

4. Create one epic first
   - The epic should explain why the wave exists, list the intended child issues, and link the grounding artifacts
   - Create the epic before the children so child bodies can reference the parent issue number

5. Create child issues only for truly missing work
   - Each child should cover one validation/proof/workstream, not a mixed bundle
   - Include:
     - summary
     - why
     - scope
     - deliverables
     - success criteria
     - parent issue number
     - related existing issues

6. Verify every created issue
   - Immediately `gh issue view` each issue
   - Confirm title, labels, URL, and rendered body
   - Fix any parent references/placeholders immediately if wrong

## Good issue-shaping heuristics
- Prefer one epic + 3-6 children for a tightly related wave
- Use children for family-level proofs/examples, not for already-open infrastructure work
- Do not recreate broad infra issues if they already exist; reference them from the new epic
- If an issue is really a duplicate/sub-scope of an existing open issue, fold it into the existing issue rather than create a new one

## Domain / career-lane issue wave pattern

When the user names a new technical domain or career lane and asks to build knowledge, demos, and job-readiness:
- Start with a bounded research/docs taxonomy issue before implementation-heavy demos.
- Use that first issue to inventory current practices, tools, role taxonomy, and job-skill mapping.
- Sequence downstream child issues from lower-risk proof to public portfolio packet, for example:
  1. knowledge base + job taxonomy
  2. solver/benchmark proof in the domain
  3. CAD/layout/process automation demo
  4. full tool-flow demo/report
  5. portfolio/job-application packet
- Keep each child issue one artifact family wide. Do not let the knowledge-base issue absorb downstream benchmark code, CAD automation, full tool-flow execution, or resume/portfolio writing.
- In the first issue plan, explicitly list downstream issue numbers as non-goals / follow-ups so adversarial review can verify scope discipline.
- Lock the first issue to durable artifacts that can guide later execution, such as a report plus a machine-readable taxonomy/skill matrix and a test that verifies required sections/entries.

## Recommended body skeleton

### Epic
- Summary
- Why now
- Grounding
- Scope
- Deliverables
- Related existing issues

### Child
- Summary
- Why
- Scope
- Deliverables
- Success criteria
- Parent
- Related

## Commands

```bash
# Search for duplicates first
gh issue list --state all --limit 200 --search "<key phrase>"

# Check label existence
gh label list --limit 300

# Create epic
gh issue create --title "epic(...): ..." --body-file /tmp/epic.md --label enhancement --label priority:high

# Create child
gh issue create --title "feat(...): ..." --body-file /tmp/child.md --label enhancement --label priority:medium

# Verify
gh issue view <num> --json number,title,url,labels,body
```

## Pitfalls
- Do not create issues directly from a roadmap without searching for existing open/closed issues first
- Do not recreate issues for already-delivered foundations just because the roadmap mentions them
- Do not assume labels exist; verify them first
- Do not create children before the epic if the child body should reference the parent number
- Do not stop after creation without verification

## Learned example pattern
For OrcaWave/OrcaFlex canonical spec-contract work:
- Keep existing infrastructure issues (#1652, #1586, #1637, #1591, #1594) as references when they already cover the area
- Create a new epic only for the genuinely missing validation wave
- Create children for specific structure-family proofs (e.g. FPSO, jumper, riser variants, benchmark promotion) when those are absent from the tracker
- Verify all created issues immediately after creation
