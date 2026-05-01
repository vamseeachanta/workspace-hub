# Archived Skill: `github-roadmap-anchor-reuse`

Original path: `/home/vamsee/.hermes/skills/github/github-roadmap-anchor-reuse`
Archived into: `/home/vamsee/.hermes/skills/.archive/umbrella-2026-04-29/github/github-roadmap-anchor-reuse`
Consolidation date: 2026-04-29

---

---
name: github-roadmap-anchor-reuse
description: Reuse and reopen existing roadmap/epic GitHub issues instead of fragmenting work across duplicate replacement epics; retarget children and link active issues for continuity.
version: 1.0.0
author: Hermes Agent
license: MIT
---

# GitHub Roadmap Anchor Reuse

Use when a user wants roadmap-level analysis, follow-on issue creation, or execution tracking for an area that already has a closed or stale roadmap/epic issue.

## Why

Creating a fresh replacement epic is often the wrong default when a historical roadmap issue already exists. Reopening the original anchor preserves traceability, keeps prior discussion/context in one place, and avoids splitting execution across parallel umbrella issues.

## When to use

Use this skill when:
- You discover an older closed roadmap/epic issue for the same domain
- You already created a new umbrella issue, then learn the user prefers reusing the original roadmap
- You need to balance new scoped child issues with existing long-running execution issues
- The user wants the work linked so quality stays high and issue structure stays coherent

## Recommended structure

Prefer this hierarchy:
1. Reopened original roadmap/epic issue = main anchor
2. Existing active issues keep their current roles if they already cleanly cover proof/hardening/breadth/scaling work
3. New issues are created only for genuinely missing scoped analyses or deliverables
4. Any temporary replacement umbrella epic should be closed once children are retargeted to the reopened anchor

## Workflow

### 1. Audit existing anchors before creating new epics

Search for existing roadmap/sprint/capability issues first:

```bash
gh issue list --state all --limit 200 --search "roadmap OR sprint plan OR capability roadmap <domain>"
gh issue view <candidate> --json number,title,state,labels,body,url
```

Look for:
- original roadmap/capability issue
- sprint tracker issue
- existing active implementation/hardening issues
- any newly created replacement epic that duplicates the anchor role

### 2. Decide reopen vs new

Reopen the existing roadmap issue when:
- it is clearly the original umbrella for the same domain
- prior context is still relevant
- the new work is an updated analysis wave, not a separate initiative

Create a new issue only when:
- the work has no clean existing home
- it is a tightly scoped child deliverable
- reopening the old issue would blur unrelated workstreams

### 3. If a replacement epic was already created, retarget instead of keeping both

If you created a new umbrella issue and then find or choose to reuse the original roadmap:
1. Reopen the original roadmap issue
2. Comment on the original issue with the updated analysis/roadmap direction
3. Edit all new child issues so their parent/anchor references point to the reopened roadmap issue
4. Comment on active existing issues to link them back to the reopened roadmap issue
5. Close the replacement epic with a comment explaining the retargeting

### 4. Link work in both directions

Add explicit linkage comments:
- roadmap anchor -> existing active issues + new child issues
- active existing issues -> roadmap anchor
- child issues -> parent roadmap anchor

This keeps future agents from inventing parallel structures.

### 4A. Add a roadmap execution map, not just parent pointers

After reopening the anchor, add one concise roadmap comment that future agents can use immediately:
- status legend: foundation delivered / proof / hardening / breadth / corpus / scaling
- ordered phase map: proof first, then family validation, then hardening, then breadth/corpus, then scaling
- explicit note about which issue is the roadmap anchor vs which issue is only a narrow sprint tracker

This prevents later agents from flattening all issues into one backlog or creating new umbrella epics because the sequencing was implicit rather than written down.

### 4AA. Finish with a compact governance-topology note on the roadmap anchor

After reopening/retargeting/closing issues, add one short "current issue topology" summary comment on the roadmap anchor.

Include:
- roadmap anchor issue
- proof foundation lane
- family-validation lane
- hardening lane
- breadth/corpus lane
- scaling lane
- duplicate issue(s) removed or superseded
- the primary roadmap document path

Why this matters:
- it gives later agents a stable map of the final intended structure after cleanup
- it reduces the chance that someone re-creates a just-closed duplicate epic or re-opens a superseded side track
- it makes the post-cleanup state discoverable without having to read every intermediate comment

### 4B. For overlapping active issues, do a close-vs-narrow-child comparison

When two open issues appear to cover the same workstream:
1. compare their bodies line by line across deliverables/scope
2. identify exact overlap vs unique residual scope
3. post a recommendation comment on the narrower issue

Use this decision rule:
- if the narrower issue adds no meaningful unique scope, recommend closing it as duplicate/superseded by the broader issue
- if it has a small distinct residual scope, recommend rewriting it explicitly as a narrow child of the broader issue

Do not leave both issues as peer roadmap anchors when one is clearly subsumed by the other.

### 4C. Put sequencing comments on new child issues

For each new child issue, add a short comment saying:
- which roadmap phase it belongs to
- which proof/hardening issues must precede it
- whether it can run in parallel with sibling child issues
- which later breadth/scaling issues it should precede

This keeps family-specific issues from being executed out of order and makes the roadmap operational rather than just descriptive.

### 5. Verify after every structural change

After reopen/edit/comment/close actions, verify with:

```bash
gh issue view <num> --json number,state,title,url,labels,body
```

Confirm:
- correct open/closed state
- correct parent/anchor references in body text
- no stale references to superseded umbrella issues
- labels still make sense

## Practical pattern

Example balance:
- Reopen original roadmap anchor: `#1572`
- Keep existing execution issues active: `#1652`, `#1586`, `#1637`, `#1591`, `#1594`, `#1628`
- Create new child issues only for missing family-specific proof work
- Close a replacement epic such as `#2453` after retargeting its children

## Pitfalls

- Do not leave both the original roadmap issue and a duplicate replacement epic open unless they have clearly different scopes
- Do not create new child issues for work already well-covered by an active existing issue
- Do not forget to retarget child issue bodies after changing the anchor
- Do not assume comments are enough; verify the issue body and state after edits

## 6. After issue-topology cleanup, establish one proof-standard issue before family-wave execution

Once the roadmap anchor and child issue structure are stable, do not jump directly into executing every new child issue. First identify the single issue that should define the proof standard for the domain, then tighten it.

Pattern:
1. Choose the governing proof-standard issue (for example, the main real-fixture/native-fidelity issue)
2. Define its execution-ready acceptance criteria explicitly
3. Re-scope any nearby follow-on issue as a narrow child/follow-on rather than a parallel proof issue
4. Add a reusable proof-template checklist on the roadmap anchor for all family-validation issues
5. Only then sequence the family-validation wave behind that proof-standard issue

Why this matters:
- prevents each child issue from inventing a different evidence bar
- keeps proof-before-breadth discipline intact
- makes downstream family issues faster to plan and easier to review

Recommended outputs:
- proof-standard issue comment with acceptance criteria and definition of done
- child/follow-on issue comment clarifying its narrower role
- roadmap comment with reusable checklist covering canonical fixture, native generation path, evidence artifacts, allowed vs blocking diffs, test contract, doc update, and closure rule

### 6A. Turn the proof-standard issue into a concrete repo artifact/test plan before moving to family issues

After setting the proof-standard issue, convert it from abstract roadmap language into an exact file-level implementation map.

Recommended sequence:
1. inspect the repo for the real production file/test surfaces involved
2. decide exact artifact filenames to create (fixture metadata, snapshot baseline, helper modules, focused tests)
3. create the repo-ready helper/test skeletons first
4. run the focused tests and fix path/import/normalization issues immediately
5. post an evidence comment back to the proof-standard issue with:
   - exact files added
   - exact test command
   - pass/fail result
6. only then use that proven pattern to plan the first family-validation child issue

Reusable artifact pattern:
- fixture artifact directory (for committed metadata + snapshots)
- helper module for loading fixture metadata / generating report inputs
- snapshot helper module for normalization
- fixture integration test
- fixture snapshot test

Why this matters:
- it upgrades the proof-standard issue from governance-only to execution-ready
- it exposes real path/import/stability problems early
- it gives downstream child issues a concrete pattern instead of just a checklist

### 6B. For the first child issue, mine the repo for the exact source/spec/native reference set

Before executing the first family-validation child issue:
1. find the canonical spec file
2. find the native monolithic reference, if it exists
3. find the generated modular reference set, if it exists
4. find existing tests touching the same generic/typed path
5. post a grounded file map comment on the child issue

This keeps the child issue bounded and prevents vague planning like "validate FPSO family" without naming the actual spec, native reference, modular files, and target test locations.

## Success criteria

You know the structure is healthy when:
- one roadmap anchor is clearly dominant
- existing issues retain continuity where appropriate
- new issues exist only for genuinely missing scopes
- every issue points back to the roadmap anchor cleanly
- one proof-standard issue defines the evidence bar for downstream family issues
- the user can understand the execution structure at a glance
