# Archived Skill: `artifact-inline-local-plan-rereview`

Original path: `/home/vamsee/.hermes/skills/workspace-hub-learned/artifact-inline-local-plan-rereview`
Archived into: `/home/vamsee/.hermes/skills/.archive/umbrella-2026-04-29/workspace-hub-learned/artifact-inline-local-plan-rereview`
Consolidation date: 2026-04-29

---

---
name: artifact-inline-local-plan-rereview
description: Prevent stale Codex/Gemini findings by rerunning plan review against the exact revised local artifact inline when summary prompts keep anchoring on remote/main plan content.
version: 1.0.0
category: workspace-hub-learned
---

# Artifact-inline local plan re-review

Use when:
- a plan was revised locally after review
- a rerun reviewer still reports findings against lines that were already removed/changed
- the repo's remote/main version lags the local draft
- a compact summary-of-changes prompt is producing stale review results

## Problem pattern
A compact rerun prompt that says "the plan was narrowed and now does X/Y/Z" may still cause Codex to fetch or anchor on the older remote/main artifact instead of the revised local draft.

Typical symptom:
- reviewer complains about deleted scope/items (for example package-root exports or generic `metric_value`) that are no longer present in the local plan
- reviewer verdict stays blocked for reasons tied to stale content rather than the current artifact

## Reliable recovery
1. Build a new rerun prompt.
2. State explicitly:
   - review ONLY the exact inline artifact below
   - do NOT substitute any remote/main-branch version
3. Inline the exact revised local sections under review, not just a summary:
   - Deliverable
   - Scope Boundaries
   - Linkage / contract sections
   - Pseudocode
   - Files to Change
   - TDD Test List
   - Acceptance Criteria
   - Risks / Open Questions
4. Rerun Codex against that artifact-inline prompt.
5. Treat the artifact-inline rerun as authoritative over earlier compact-summary reruns that anchored on stale repo state.

## Why this works
It removes ambiguity about which artifact is under review and prevents the reviewer from re-discovering or preferring the older plan text from main/GitHub.

## Notes
- This is especially useful after iterative plan hardening on GitHub issues.
- Use compact prompts first when possible, but switch to artifact-inline once the reviewer keeps citing removed content.
- If the provider reports sandbox/local retrieval failures while the exact artifact was inlined, separate true content findings from infrastructure/retrievability findings. Patch content defects, but treat missing `main` visibility or failed `sed`/`grep` retrieval as promotion-gate evidence rather than proof the inline draft is wrong.
- Do not cite uncommitted/local-only artifacts as approval evidence. Keep the issue draft-only until clean review artifacts are committed and retrievable from the required branch.
- Save the raw rerun output and replace the canonical review artifact only after the rerun succeeds.
