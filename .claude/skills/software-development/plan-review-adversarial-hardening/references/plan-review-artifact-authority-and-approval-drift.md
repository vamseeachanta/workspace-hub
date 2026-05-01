# Archived Skill: `plan-review-artifact-authority-and-approval-drift`

Original path: `/home/vamsee/.hermes/skills/workspace-hub-learned/plan-review-artifact-authority-and-approval-drift`
Archived into: `/home/vamsee/.hermes/skills/.archive/umbrella-2026-04-29/workspace-hub-learned/plan-review-artifact-authority-and-approval-drift`
Consolidation date: 2026-04-29

---

---
name: plan-review-artifact-authority-and-approval-drift
description: Keep iterative plan-review artifacts truthful when external reruns overtake self-reviews or stale approval signals remain on older revisions.
version: 1.0.0
category: workspace-hub-learned
tags: [planning, review, governance, drift, github]
---

# Plan Review Artifact Authority and Approval Drift

Use when a local plan has gone through multiple adversarial review waves and any of these are true:
- a self-review artifact exists and later external Claude/Codex/Gemini reruns also exist
- the issue still carries `status:plan-approved` or `.planning/plan-approved/<issue>.md` from an older revision
- `docs/plans/README.md` status lags the current effective review state

## Rules

1. Latest external reruns are authoritative for the current draft.
   - Update the plan header `Review artifacts` line to point at the newest external rerun artifacts.
   - Update the Artifact Map to list those newest external rerun artifacts.
   - If you keep a self-review artifact, label it explicitly as historical or non-authoritative relative to the external rerun.

2. Describe approval drift precisely.
   - If `status:plan-approved` and/or `.planning/plan-approved/<issue>.md` still exist but fresh external reruns returned `MAJOR`, do not say "no approval exists".
   - Say the approval signals exist but apply to an older revision, and therefore do not approve the current draft revision.

3. Keep the review summary synchronized.
   - In `## Adversarial Review Summary`, record the latest completed external rerun verdicts.
   - Summarize exactly what changed in the newest patch wave.
   - State clearly whether the current draft is still blocked from GitHub posting.

4. Treat mutable fanout outputs as diagnostic until promoted to immutable evidence.
   - Do not cite mutable paths like `scripts/review/results/YYYY-MM-DD-plan-<issue>-claude.md` as approval evidence unless they are committed, non-empty, SHA-bound to the reviewed plan revision, and contain a parseable `## Verdict`/`## Verdicts` section.
   - Prefer timestamped or round-suffixed immutable provider artifacts for gate evidence, e.g. `scripts/review/results/YYYYMMDDTHHMMSSZ-plan-<issue>-claude.md` or `scripts/review/results/YYYY-MM-DD-plan-<issue>-claude-r2.md`.
   - Provider artifacts are authoritative over disagreement/synthesis artifacts. If a disagreement summary conflicts with the provider files, treat the conflict as a gate blocker until adjudicated; do not let the synthesis file override provider verdicts.
   - If a fanout rewrites mutable artifacts to empty/truncated files or leaves only `.err` files, mark that run as diagnostic/provider-infra evidence only and rerun or copy fresh valid artifacts before claiming review clearance.
   - If mutable canonical outputs are `0` bytes after a completed run but round-suffixed archive artifacts are populated, treat that as an inverted-routing/review-infra state: verify file sizes in the real worktree, archive the non-empty artifacts with explicit provenance, and rerun or create non-empty `UNAVAILABLE` artifacts before citing the canonical paths. Never cite empty canonical files as valid evidence.
   - If all providers are simultaneously `UNAVAILABLE`, the plan is not approval-ready by default. Escalate to the user with the attempted commands, stderr/stdout byte counts, and artifact paths; require a fresh valid provider review or explicit documented user override before implementation.
   - When a provider cannot read local files and switches to GitHub/main retrieval, commit and push the current plan first, then verify the remote path/sha or URL before treating the review as authoritative. Inline or uncommitted-plan reviews can be useful feedback, but they must not be represented as approval evidence for the canonical plan until the canonical committed plan matches the reviewed text.
   - If a provider falls back to MCP-only or remote-only retrieval because local sandboxing fails (for example `bwrap`/namespace errors), classify it as valid only when the artifact cites immutable GitHub/blob/commit evidence and states the local limitation. Otherwise classify it as `UNAVAILABLE`, not as a substantive approval signal.

5. Do not hand-wave README drift.
   - If `docs/plans/README.md` is accurate, treat it as verification-only state.
   - If it is stale relative to fresh review evidence, make the plan require explicit state-sync rather than merely saying "verify the row remains correct".

## Useful patch targets inside the plan

- Header status line
- Header review-artifacts line
- `### Documents consulted`
- `### Evidence (embedded verification)`
- `## Artifact Map`
- `## Pseudocode`
- `## TDD Test List`
- `## Acceptance Criteria`
- `## Adversarial Review Summary`

## Example wording

- "Live GitHub `status:plan-approved` and local `.planning/plan-approved/2460.md` reflect older approval-state drift, not approval of this current draft revision."
- "Historical Claude self-review (non-authoritative compared with external reruns)."
- "Verify/update `docs/plans/README.md` without re-adding the row; if stale approval drift is present, explicitly sync the row to the effective non-approved state."
