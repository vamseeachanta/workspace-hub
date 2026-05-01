# Archived Skill: `artifact-inline-plan-review-for-local-draft-revisions`

Original path: `/home/vamsee/.hermes/skills/workspace-hub-learned/artifact-inline-plan-review-for-local-draft-revisions`
Archived into: `/home/vamsee/.hermes/skills/.archive/umbrella-2026-04-29/workspace-hub-learned/artifact-inline-plan-review-for-local-draft-revisions`
Consolidation date: 2026-04-29

---

---
name: artifact-inline-plan-review-for-local-draft-revisions
description: Prevent false MAJOR plan-review findings when Codex/Gemini review stale remote/main artifacts instead of the revised local draft.
version: 1.0.0
category: workspace-hub-learned
tags: [plan-review, adversarial-review, codex, gemini, local-draft, artifact-packaging]
---

# Artifact-inline plan review for local draft revisions

Use when:
- a GitHub issue plan was revised locally after earlier review feedback
- the canonical file exists only in local/uncommitted state or differs from remote/main
- a provider review appears to criticize content already removed from the local draft

## Problem signature

A reviewer returns findings against stale content, for example claiming the plan still contains:
- package-root exports you already removed
- generic `metric_value` after you replaced it with typed fields
- helper APIs or broad scope you already deferred

This usually means the provider fetched the remote/main-branch artifact instead of the revised local draft.

## Correct response

Do not treat this as substantive regression yet.
Treat it as artifact-selection drift.

## Reliable recovery pattern

1. Keep the normal compact review prompt for the first rerun if it is small enough.
2. If the provider still reviews the wrong version, build an artifact-inline prompt.
3. Embed the exact revised local sections under review directly in the prompt, typically:
   - Deliverable
   - Scope Boundaries
   - Linkage Strategy
   - Downstream Integration Surface
   - Pseudocode
   - Files to Change
   - TDD Test List
   - Acceptance Criteria
4. Add an explicit instruction:
   - review ONLY the exact inline artifact below
   - do NOT substitute any remote/main-branch version
5. Save the prompt as a durable local artifact such as:
   - `.planning/quick/review-<issue>-artifact-inline-<provider>-prompt.md`
6. Rerun the provider using that prompt.
7. Save the resulting artifact separately from the stale run so governance can distinguish them.

## Why this works

Provider sandboxes or GitHub connectors may prefer remote/main copies even when your summary text describes the revised local state correctly. Inline artifact review removes that ambiguity and forces evaluation of the intended draft.

## Additional guidance

- Use a compact inline subset, not the entire conversation history.
- Include only the sections needed to decide approval readiness.
- If the rerun now returns MINOR/APPROVE and explicitly acknowledges the revised bounded scope, supersede the stale artifact in your synthesis.
- Record in the synthesis that the prior false-MAJOR was caused by stale artifact selection, not by the revised local draft itself.

## Good outcome criteria

The rerun should stop complaining about already-removed scope and instead focus only on real residual contract choices or test gaps.
