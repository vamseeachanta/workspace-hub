# Archived Skill: `roadmap-anchor-issue-governance`

Original path: `/home/vamsee/.hermes/skills/coordination/roadmap-anchor-issue-governance`
Archived into: `/home/vamsee/.hermes/skills/.archive/umbrella-2026-04-29/coordination/roadmap-anchor-issue-governance`
Consolidation date: 2026-04-29

---

---
name: roadmap-anchor-issue-governance
description: Reopen and reuse the original roadmap/umbrella issue as the governance anchor; create new issues only for genuinely missing scoped work, then retarget/link all execution issues back to the anchor.
version: 1.0.0
author: Hermes Agent
license: MIT
---

# Roadmap Anchor Issue Governance

Use when a repo already has old roadmap/epic issues and you need to add a new analysis or execution wave without creating issue sprawl.

## When to use
- A prior roadmap/umbrella issue exists but is closed or stale
- New work is partly continuation of old roadmap logic and partly new scoped tasks
- You need to balance reopen/retarget vs creating fresh issues
- The user cares about work quality, traceability, and avoiding duplicate issue trees

## Core rule
Prefer this structure:
1. Reopen the original roadmap/umbrella issue if it still cleanly owns the domain
2. Keep existing active issues as the main tracks if they already own the work
3. Create new issues only for genuinely missing scoped work
4. Retarget all new child issues back to the reopened roadmap anchor
5. Close any replacement epic created during analysis if the reopened roadmap is the better long-term anchor

## Decision framework

### Reopen the old roadmap when
- It is still the natural domain umbrella
- The new work is roadmap-level analysis/sequencing, not a separate product area
- Existing active issues already point back to it or are naturally grouped under it

### Keep an existing issue instead of creating a new one when
- The existing issue already owns the same capability lane
- Only the scope framing is stale (e.g. build vs hardening/validation)
- A comment or body update can re-scope it cleanly

### Create a new issue only when
- The work is a genuinely missing scoped validation or implementation slice
- Folding it into an existing issue would overload that issue
- It needs independent closure evidence

## Recommended execution order

### 1. Audit before creating anything
- List open and closed issues for the domain
- Read the old roadmap/umbrella issue
- Read the current roadmap/operator/reconciliation docs
- Identify which issues are:
  - foundation already delivered
  - still active core tracks
  - duplicates/stale
  - genuinely missing work

### 2. Create a temporary replacement epic only if needed for thinking
If you create one during analysis, treat it as disposable until you decide whether the old roadmap should be reopened.

### 3. Reopen the original roadmap anchor
- Reopen the old roadmap issue
- Comment with the new analysis wave, updated priorities, and current artifact paths
- Make it explicit that this issue is now the sequencing/readiness anchor

### 4. Retarget new issues
For every new issue created during the analysis wave:
- Edit the body so the parent is the reopened roadmap issue
- Remove references to any temporary replacement epic
- Add links to the real active core issues it depends on

### 5. Link existing active issues back to the roadmap
Comment on the main active issues with:
- why they remain the canonical issue for that lane
- where they sit in the roadmap phase order
- whether any sibling issue should be de-duplicated or narrowed under them

### 6. De-duplicate explicitly
If two issues overlap:
- compare scope line by line
- identify whether the smaller issue has any distinct residual scope
- if not, close it as duplicate/superseded by the broader issue
- if yes, rewrite it as a narrow child issue

### 7. Add governance comments to the roadmap anchor
The roadmap anchor should contain:
- execution order
- status legend (foundation/proof/hardening/breadth/corpus/scaling)
- compact topology note showing which issues own which lanes

## Useful comment types

### On reopened roadmap issue
- Why it was reopened
- What new analysis wave it now owns
- Which issues are foundations vs active lanes vs new children
- Execution order and phase map

### On active existing issues
- "This remains the canonical issue for this lane"
- Its place in the roadmap sequence
- Whether nearby issues should be folded into it

### On duplicate candidate issue
- Scope comparison table
- Recommendation: close or narrow child
- Reference the roadmap anchor and current reconciliation docs

## Quality guardrails
- Never leave two peer issues owning the same roadmap lane
- Never let a temporary replacement epic remain open if the original roadmap is the better anchor
- Do not create new issues for work already cleanly owned by an active issue
- Do create new issues for missing scoped validation slices that need independent evidence
- Verify all final issue bodies/comments point to the same roadmap anchor

## Minimal final topology target
Aim for:
- one roadmap anchor
- one canonical issue per major active lane
- new child issues only for missing scoped work
- duplicates closed or rewritten as narrow children

## Example outcome pattern
- Reopen old roadmap issue `#A`
- Keep active proof issue `#B`
- Keep active hardening issue `#C`
- Create new family-validation issues `#D #E #F`
- Retarget `#D #E #F` to parent `#A`
- Close temporary replacement epic `#TMP`
- Close duplicate issue `#X` into `#C`

This yields a cleaner, higher-signal issue graph and better execution quality.