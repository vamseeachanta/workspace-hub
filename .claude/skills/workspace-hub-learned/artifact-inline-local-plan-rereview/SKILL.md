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
- Save the raw rerun output and replace the canonical review artifact only after the rerun succeeds.
