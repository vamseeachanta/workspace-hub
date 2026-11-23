# Archived Skill: `preserved-plan-refile-with-attested-review-wave`

Original path: `/home/vamsee/.hermes/skills/workspace-hub-learned/preserved-plan-refile-with-attested-review-wave`
Archived into: `/home/vamsee/.hermes/skills/.archive/umbrella-2026-04-29/workspace-hub-learned/preserved-plan-refile-with-attested-review-wave`
Consolidation date: 2026-04-29

---

---
name: preserved-plan-refile-with-attested-review-wave
description: Reopen a previously closed GitHub issue with a preserved local plan, rewrite it into a conservative draft, and drive iterative attested adversarial review waves until it is truly approval-ready.
version: 1.0.0
category: workspace-hub-learned
tags: [github, planning, adversarial-review, attestation, refiling, governance]
---

# Preserved Plan Re-file With Attested Review Wave

Use when:
- an issue was previously closed or rolled back
- the repo still has a preserved `docs/plans/...` artifact
- #2405-style attested review infrastructure is available
- you need to reopen/re-file the issue without pretending the old plan is still valid

## Why this exists
A preserved plan that survived a closed issue often contains stale workflow state, stale review-history claims, and assumptions that were never revalidated against live repo state. Simply reopening the issue and relabeling it wastes cycles. The reliable path is:
1. convert the plan back to `draft`
2. reopen the issue with a governance comment
3. run fresh attested adversarial review
4. tighten only the still-live blockers
5. do not advance to `status:plan-review` until reviewers stop returning MAJOR

## Workflow

### 1. Verify live state first
Always check before editing:
- `gh issue view <n> --json state,labels,title`
- required healthcheck / test command for the infrastructure you rely on
- current `origin/main` tip
- existence of the preserved plan file

If the issue is closed, do not keep `plan-review` wording in the plan header.

### 2. Rewrite the preserved plan into a conservative draft
Update the plan file to:
- set `Status: draft`
- clearly mark it as a re-file draft, not approval-ready
- remove stale review-artifact claims unless the files still exist
- distinguish:
  - required inputs
  - optional/reporting-only inputs
  - degraded/fail-closed behavior
- make identity and matching contracts explicit
- make scheduler/publication behavior explicit if the plan mentions automation

Important: if a reviewer found a contradiction, rewrite the contract itself — do not just add commentary around the contradiction.

### 3. Reopen the issue with a scoped governance comment
Use `gh issue reopen <n> -c "..."` and explain:
- why the issue is being reopened
- that the plan is now back in draft/revision mode
- that fresh adversarial review follows

Do not add `status:plan-review` yet.

### 4. Run fresh attested adversarial review immediately
Use the standard adversarial prompt with the attestation-aware clause. Save canonical artifacts under `scripts/review/results/`.

Recommended naming:
- `YYYY-MM-DD-vN-plan-<issue>-codex.md`
- `YYYY-MM-DD-vN-plan-<issue>-gemini.md`

### 5. Tighten by converging on live blocker themes
After each wave, summarize the remaining blockers into a short list and edit only those.

Common blocker buckets seen in preserved-plan refiles:
- stale workflow state (`closed` issue but plan claims `plan-review`)
- missing or stale review artifact references
- undefined identity/matching contract
- undefined degraded-vs-fail-closed behavior
- scheduler/publishing semantics not specified tightly enough
- duplicate/deduplication behavior undefined
- output schema mismatches across plan sections
- source-surface deduplication missing for multi-inventory detectors (`index.jsonl` + ledgers/manifests + registries)
- cross-domain coverage semantics left implicit (`doc_key` match in wrong wiki/domain should not silently count as covered)
- exit-code contract missing even though the plan talks about dry-run, degraded runs, or scheduled publication
- publication mode ambiguous (CLI flag vs config-driven mode), which lets reviewers reject the plan for mismatched runtime vs scheduler behavior
- locking specified at two layers (shell + Python) without one authoritative owner, creating deadlock/ambiguity risk
- heterogeneous source schemas described with vague phrases like "field or equivalent" instead of concrete field names + fallback order

### 6. Keep GitHub and repo state aligned
After each major revision wave:
- post a short GitHub comment summarizing new artifacts and remaining blockers
- update `docs/plans/README.md` to reflect `draft` / re-file-in-progress state
- do not label `status:plan-review` while reviews are still MAJOR

### 7. Commit docs-only progress incrementally
Safe commit pattern:
- plan draft rewrite + first review wave
- later revision-wave tightening + new review artifacts

This preserves the tightening history and avoids losing learning between waves.

## Operational rules
- A preserved plan is not approval-ready just because it already exists.
- Fresh MAJOR review evidence outranks older optimistic review history.
- Remove unverified or irrelevant live-state claims unless attestation covers them.
- If a blocker list narrows, keep the issue open and still in draft; do not prematurely advance labels.
- Approval readiness requires both plan quality and governance-state cleanliness.

## Suggested commit messages
- `docs(plans): reopen #NNNN with v4 review wave`
- `docs(plans): continue #NNNN adversarial revision wave`
- `docs(plans): tighten #NNNN review contracts`

## Exit condition
The issue is ready to move to `status:plan-review` only when:
- the plan header/readme row say draft -> plan-review consistently
- latest external review wave is no worse than MINOR
- GitHub comment history links the current canonical review artifacts
- no stale closed-issue or stale-approval contradictions remain
