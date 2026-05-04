---
name: issue-planning-mode
description: Mandatory planning workflow for ALL GitHub issues — plan, review, approve, then implement.
version: 3.1.0
author: Workspace Hub
category: coordination
tags: [planning, github, enforcement, workflow, onboarding]
related_skills:
  - engineering-issue-workflow
---

# Issue Planning Mode — Mandatory for ALL Issues

**ALL agents** (Codex, Codex, Gemini, Hermes) MUST follow this workflow for every GitHub issue.
Load this skill before drafting or executing any plan.

Full onboarding guide with step-by-step details: `docs/plans/README.md`

## Workflow Overview

```
Issue → Resource Intel → Draft Plan → Adversarial Review → Post to GH
  → Label status:plan-review → USER APPROVES → Label status:plan-approved
  → Implement (TDD) → Close
```

## Steps

### Step 1: Intake and Resource Intelligence

1. Read the full issue body — scope, acceptance criteria, references
2. Classify complexity: T1 (trivial), T2 (standard), T3 (complex)
3. Search existing code, standards, documents, and prior plans before writing

### Step 2: Draft Plan

Copy template and fill all sections:

```
docs/plans/_template-issue-plan.md  -->  docs/plans/YYYY-MM-DD-issue-NNN-slug.md
```

Required sections: Resource Intelligence Summary, Artifact Map, Deliverable, Pseudocode (T2/T3), Files to Change, TDD Test List, Acceptance Criteria, Risks.

Update the index table in `docs/plans/README.md` with a new row.

Execution discipline for delegated agents:
- If using Codex/Codex/Gemini in parallel worktrees, explicitly anchor the repo/worktree path in the prompt/context and verify the plan file was written in the intended checkout. Do not assume the child agent stayed in the requested worktree.
- After drafting, verify all expected artifacts exist where intended:
  - the plan file path
  - the `docs/plans/README.md` index row
  - no accidental extra rows/issues were inserted
- Keep status conservative as `draft` unless formal review artifacts actually exist under `scripts/review/results/`. GitHub comments alone are useful evidence, but they do not replace the repo’s review-artifact convention.

### Step 3: Adversarial Review

Route the plan to 2+ AI providers for review. Each gives: APPROVE | MINOR | MAJOR.
If any MAJOR: revise and re-review.

Post artifacts to `scripts/review/results/YYYY-MM-DD-plan-NNN-<agent>.md`.

**Reviewer-stance contract (mandatory framing for every review prompt):**
Every prompt sent to a reviewer MUST force an adversarial stance. "Adversarial" here means actively hunting for defects, not charitable reading. Required clauses in the prompt:
1. State explicitly: "You are an adversarial reviewer. Assume the plan has defects until proven otherwise."
2. Forbid praise and restatement: "Do not praise. Do not restate the plan. Focus only on what is wrong, missing, or risky."
3. Bias toward non-approval: "Return APPROVE only after affirmatively verifying each correctness-critical claim. When in doubt, return MINOR or MAJOR."
4. Require evidence: "Each finding must cite a specific file path, plan section, or quoted claim."
5. Treat cited sources as assertions to verify, not facts to trust.
6. Empty reviews are failures — if nothing is found, explicitly list what was checked.
7. **Prefer attested evidence over plan text (#2405).** If the review prompt carries a `## Attested Evidence` block produced by `scripts/review/attest-plan-claims.sh`, treat plan-asserted facts (issue states, file existence, commit SHAs) as **claims to verify against the attestation**, not as facts. Do not report "unverified claims" findings for facts already covered by the attestation block — they are verified by construction at the recorded commit SHA. If the plan contradicts the attestation, the contradiction is a finding; the attestation is authoritative. Cross-review dispatchers (`submit-to-codex.sh`, `submit-to-gemini.sh`) inject this block automatically for plan files under `docs/plans/`.

A review that returns APPROVE without at least one verified check-list item is suspect and should be rerun with a stronger prompt.

Rationale: user feedback 2026-04-17 on #2323 — "Make all the reviews adversarial in nature. Helps maximize productivity." Rubber-stamp reviews produce downstream rework that is more expensive than a cold review would be.

### Step 4: Post and Label

1. Post the plan as a GitHub issue comment
2. Apply label: `gh issue edit NNN --add-label "status:plan-review"`
3. **STOP** — do NOT implement. Wait for user approval.

### Step 6: User Approval

The user (never the implementing agent) approves the plan:
- `gh issue edit NNN --remove-label "status:plan-review" --add-label "status:plan-approved"`
- Creates marker: `.planning/plan-approved/NNN.md`

### Step 5: User Approval

The **user** (not the implementing agent) approves:

```bash
gh issue edit NNN --remove-label "status:plan-review" --add-label "status:plan-approved"
mkdir -p .planning/plan-approved
echo "Approved by: <user>" > .planning/plan-approved/NNN.md
```

Self-approval by the implementing agent is blocked by the plan-approval gate.

### Status authority and surfacing rule

When plan status signals disagree across artifacts, use this precedence:
1. Latest/most-advanced GitHub `status:*` label is authoritative for live issue state
2. `.planning/plan-approved/NNN.md` marker is authoritative local evidence that approval happened
3. `docs/plans/README.md` is a convenience index and may lag; update it when you notice drift, but do not let it override GitHub + approval-marker reality

Practical rules:
- If both `status:plan-review` and `status:plan-approved` appear, treat `status:plan-approved` as authoritative and clean up the stale lower-status label when possible.
- Do **not** surface a plan to the user for approval until adversarial plan review is complete and the plan is actually approval-ready.
- If a GitHub issue is already at a more advanced latest status (for example `status:plan-approved`), do not downgrade it just to match a stale local plan file or README row.

### Status precedence and stale-state handling

When issue state drifts across artifacts, use this precedence order for operational decisions:

1. `status:plan-approved` label on the GitHub issue
2. `.planning/plan-approved/NNN.md` local approval marker
3. `status:plan-review` label on the GitHub issue
4. local plan status in `docs/plans/README.md`

Rules:
- Treat the **latest / most-advanced status** as authoritative. Example: if both `status:plan-review` and `status:plan-approved` are present, treat the issue as `plan-approved` until labels are cleaned up.
- `docs/plans/README.md` can lag reality; do not rely on it alone for approval state.
- A plan should be surfaced to the user for approval only after adversarial review is complete and the plan content is actually approval-ready. Do not surface draft plans just because a stale label suggests `plan-review`.
- If you find label drift or README drift, clean it up or annotate it immediately so the queue stays trustworthy.

Important operational rule learned in live use:
- If multiple `status:*` labels are present on the same GitHub issue, treat the **latest / most-advanced status** as authoritative (for example, `status:plan-approved` outranks `status:plan-review`). Clean up stale lower-status labels when possible, but do not block execution-state interpretation on label drift alone.
- Only surface a plan to the user for approval **after adversarial plan review is complete**. Draft plans with pending review findings should not be presented as approval-ready just because a local plan file exists.
- `docs/plans/README.md` can drift from GitHub labels and `.planning/plan-approved/*.md`; when auditing readiness, reconcile all three and use the latest effective state rather than trusting the README row blindly.

### Status precedence and surfacing rules

- If a GitHub issue has multiple `status:*` labels, treat the **latest/most-advanced** state as authoritative. In practice: `status:plan-approved` outranks `status:plan-review`.
- When local plan indexes (for example `docs/plans/README.md`) disagree with newer approval markers or newer GitHub status labels, reconcile to the newer/more-advanced state before deciding whether user approval is still needed.
- Use `.planning/plan-approved/<issue>.md` as the canonical local proof that approval happened.
- Do **not** surface a plan to the user for approval until adversarial plan review is complete and the plan is actually approval-ready. Draft plans with pending/failed review should be revised first, then surfaced.

### Pending cross-review audit routine

When the user asks which plans are still pending cross-provider review, audit all five signals before answering:

1. `docs/plans/README.md` plan row/status
2. direct `docs/plans/` file search for `issue-<NNN>-*.md` (catches orphaned/unindexed local plans)
3. live GitHub issue labels/state via `gh issue view/list`
4. local approval marker `.planning/plan-approved/<issue>.md`
5. review artifacts under `scripts/review/results/`

Operational rules:
- `status:plan-review` label alone is **not** sufficient to say a plan is truly pending; verify whether the issue already advanced to `status:plan-approved` or already has a local approval marker.
- `status:plan-approved` without `.planning/plan-approved/<issue>.md` is approval-state drift; flag it as governance cleanup, not a clean approval-ready item.
- README rows can be stale in either direction. Treat them as discovery/index hints, not final authority.
- Also ignore/example-filter template rows or placeholder examples in `docs/plans/README.md` (for example the sample `1234` entry in the "Entry Format" section). Do not treat README sample rows as real pending work; always verify against a live GitHub issue and an actual plan file before classifying an item.
- For cross-provider plan review, explicitly check whether provider-specific artifacts exist for Codex and Gemini (or documented substitutes when a provider was unavailable). Files like `*-subagent.md`, `*-hermes.md`, or `*-final.md` do not by themselves prove Codex/Gemini review happened.
- Also verify that a canonical local plan file actually exists under `docs/plans/`. An open issue in `status:plan-review` with no plan file and no review artifacts is **not** a true pending cross-provider review item; it is earlier-stage governance drift / missing-plan work.
- Separate the queue into:
  - true pending review items (open, not approved, plan file exists, cross-review incomplete)
  - needs-revision items (review artifact set exists, but latest provider findings still return MAJOR / not approval-ready)
  - missing-plan items (live `status:plan-review` but no canonical `docs/plans/` artifact exists yet)
  - state-drift items (labels/README/markers disagree)
  - closed-stale-index items (issue already CLOSED or otherwise completed, but `docs/plans/README.md` and/or the local plan header still claim `plan-review` / `adversarial-reviewed`)
- Closed-stale-index remediation rule:
  1. verify the live GitHub issue is actually CLOSED (or otherwise definitively completed)
  2. verify any implementation/closeout evidence in issue comments or landed commits if needed
  3. update `docs/plans/README.md` from `plan-review`/`adversarial-reviewed` to `completed`
  4. update the local plan header status to `completed`
  5. do not treat partial historical review artifacts as pending cross-provider work once the issue itself is already complete
- In practice, audit in this order for each candidate issue: GitHub labels/state → local plan file under `docs/plans/` → local approval marker → review artifacts by provider. This prevents wasting time chasing “missing provider reviews” for items that are actually missing the plan itself.
- Missing-plan remediation sequence (important):
  1. Draft the canonical local plan under `docs/plans/` and add the `docs/plans/README.md` row with local status `draft`.
  2. Post a short governance comment on the issue explaining that the item was mislabeled as `status:plan-review` without a canonical plan artifact.
  3. If the issue truly had no local plan and no provider review artifacts yet, remove the stale live `status:plan-review` label while the plan is still only a local draft.
  4. Run the real adversarial review wave (Codex/Codex/Gemini as available).
  5. Only after provider artifacts exist, update the plan + README to `plan-review` and restore/apply the live `status:plan-review` label.
- This keeps live issue state aligned with actual plan maturity and avoids pretending a draft-only item is already in cross-provider review.
- When only the Codex review artifact is missing, a concise file-path-based `Codex -p` review prompt is often more reliable than embedding the full plan text inline. If a long inline Codex review prompt hangs or hits a turn cap, retry immediately with a shorter prompt that names the plan file path and explicitly requests the required review headings.
- For plan-review items that are being iteratively tightened after MAJOR findings, keep the `## Adversarial Review Summary` current after each wave: record the latest provider verdicts, explicitly say whether the plan is still not approval-ready, and summarize what changed in the latest patch wave. Do not leave the summary stuck at `PENDING` once real artifacts exist.
  2. add/update the `docs/plans/README.md` row with local status `draft`
  3. post a short governance comment explaining the issue was in missing-plan drift
  4. if you need labels to reflect reality strictly, remove stale `status:plan-review` until real provider review artifacts exist
  5. run the provider review wave
  6. once review artifacts exist, update local status to `plan-review`, restore/add the live `status:plan-review` label, and post the review-state update
- When only the Codex review artifact is missing, a concise file-path-based `Codex -p` review prompt is often more reliable than embedding the full plan text inline. If a long inline Codex review prompt hangs or hits a turn cap, retry immediately with a shorter prompt that names the plan file path and explicitly requests the required review headings.
- For new or recovered plan drafts, keep the local plan file status conservative as `draft` until actual provider artifacts exist. After the first real review wave lands, update the plan file/README row to `plan-review` and summarize the live blocker state in `## Adversarial Review Summary` rather than leaving placeholder `PENDING` language.
- If you launch a long-running background Codex review and then recover with a shorter fallback prompt, do not assume the first run is dead forever. Poll or inspect the original background process/log later. If it eventually completes with a fuller or sharper review, refresh the canonical repo artifact with the stronger findings and post a short GitHub follow-up comment noting that the completed long-form review supersedes or sharpens the earlier summary.
- Practical artifact rule: the repo artifact under `scripts/review/results/` should represent the best available current-review content, not merely the first usable fallback. Late-arriving stronger findings should replace the weaker stopgap artifact rather than being ignored in terminal/process logs.

This prevents falsely telling the user there are no pending plan reviews just because the live `status:plan-review` label set is empty, and it avoids misclassifying missing-plan issues as pending provider-review work.
Additional triage rule learned in live queue audits:
- For feature/intake sweeps, do not describe an issue as "pending other-provider cross-review" unless a local plan artifact already exists and at least one real provider review artifact exists. If the issue only has the live `status:plan-review` label but lacks both the local plan file and `scripts/review/results/` artifacts, classify it as earlier-stage governance drift / missing-plan work, not as a pending cross-review item.

This prevents falsely telling the user there are no pending plan reviews just because the live `status:plan-review` label set is empty, and also prevents overstating unlived/missing-plan items as if they were already in the provider review stage.

### Governance cleanup after fresh MAJOR re-review

If a plan had previously advanced to `status:plan-approved` or gained a local approval marker, and a later fresh adversarial re-review returns blocking `MAJOR` findings, treat that as **state rollback required**, not just a note in comments.

Cleanup sequence:
1. Post the new review summary/comment linking the fresh review artifacts.
2. If the GitHub issue is still open and labeled `status:plan-approved`, remove `status:plan-approved` and add `status:plan-review`.
3. If the issue has a stale local approval marker `.planning/plan-approved/<issue>.md` but the live issue is now back in `status:plan-review`, remove the stale marker.
4. Update `docs/plans/README.md` to match the rolled-back live state (`plan-review` rather than `plan-approved`).
5. Leave a governance-cleanup comment on the issue explaining that the rollback is due to fresh blocking review evidence, not arbitrary relabeling.

Practical rules:
- For **open** issues, stale approval markers should be removed once the issue is rolled back to `status:plan-review`.
- For **closed** issues, stale `status:plan-approved` labels are misleading and should be removed, but marker cleanup can be treated as historical hygiene rather than an operational blocker.
- If a provider is unavailable (for example Gemini 429 capacity exhaustion), do not stall indefinitely; record the provider failure explicitly and continue with available review evidence while keeping the issue in a non-approved state until blocking findings are resolved.
- Fresh MAJOR review evidence outranks older optimistic comments, stale README rows, and stale marker files.

### Fresh-review rollback rule (critical drift cleanup)

If a plan receives fresh external review artifacts (for example Codex/Gemini) with `MAJOR` / `not approval-ready` after the issue had already drifted to `status:plan-approved`, treat that as a governance-state regression that must be cleaned up immediately.

Required cleanup sequence:
1. Post a short GitHub comment summarizing that fresh review evidence returned `MAJOR` and link the new review artifacts.
2. Move the issue label back from `status:plan-approved` to `status:plan-review`.
3. If a local approval marker exists at `.planning/plan-approved/NNN.md`, remove it so local state no longer implies approval.
4. Update the corresponding `docs/plans/README.md` row from `plan-approved` to `plan-review`.
5. Re-verify all three signals after cleanup:
   - GitHub labels
   - local approval marker presence/absence
   - README row status

Operational rule:
- Fresh blocking review evidence outranks stale prior approval signals. Do not leave an issue in `status:plan-approved` just because it was previously approved if the newest adversarial review says it is not approval-ready.
- Closed issues with stale `status:plan-approved` but no matching local approval evidence should at minimum have the misleading label removed, even if you do not reopen the issue.

### Step 6: Implement (TDD)

When fresh external plan reviews land (especially Codex + Gemini) and they materially disagree with the current issue state, reconcile the workflow state immediately instead of leaving the queue misleading.

Required checks after a review wave:
1. live GitHub `status:*` labels
2. `.planning/plan-approved/<issue>.md` local marker
3. `docs/plans/README.md` row status
4. latest provider verdicts in `scripts/review/results/`

Remediation rules:
- If any fresh provider review returns `MAJOR`, do **not** leave the issue surfaced as effectively approval-ready. For open issues, roll the issue back to `status:plan-review` unless there is newer authoritative user approval after the reviewed plan revision.
- If an open issue is `status:plan-review` but still has a local `.planning/plan-approved/<issue>.md` marker from an older state, remove the stale marker so local state no longer implies approval.
- If an open issue is `status:plan-approved` but has no local approval marker, remove or downgrade the stale approval label unless there is other authoritative approval evidence you can point to.
- Sync `docs/plans/README.md` to the effective live state once labels/markers are corrected.
- Post a short GitHub comment when you perform governance cleanup so future readers know why approval-state signals changed.

Practical sequencing:
1. finish/post review artifacts
2. classify issues into approval-ready vs needs-revision
3. fix GitHub labels/comments
4. fix local marker drift
5. update `docs/plans/README.md`
6. verify the final open queue

This keeps the plan queue operationally trustworthy after large review waves instead of letting stale `plan-approved` signals linger.
### Governance cleanup when fresh review evidence contradicts current status

If a plan already carries `status:plan-approved` but fresh Codex/Gemini review returns `MAJOR` or otherwise says "not ready for user approval":

1. Treat the fresh review evidence as a governance problem, not as permission to continue.
2. Reconcile all four surfaces:
   - GitHub `status:*` labels
   - `.planning/plan-approved/<issue>.md` marker
   - `docs/plans/README.md` row status
   - `scripts/review/results/` artifacts
3. If the issue is still open and there is no local approval marker, remove stale `status:plan-approved` and move it back to `status:plan-review`.
4. If the issue is closed but still carries stale `status:plan-approved` without a marker, remove the stale approval label and post a cleanup note; do not silently leave misleading approval state behind.
5. Post a short GitHub comment explaining the cleanup and linking the blocking review artifacts.
6. Update `docs/plans/README.md` if it still claims `adversarial-reviewed` or `plan-approved` in a way that no longer matches the effective live state.

Practical rule:
- After fresh external review, the queue should distinguish between:
  - pending review
  - needs revision after MAJOR review
  - state drift cleaned / still needs rewrite

### Step 6: Implement (TDD)

Only after `status:plan-approved` label AND `.planning/plan-approved/NNN.md` marker exist:
1. Tests FIRST — write tests, confirm they fail
2. Implement minimum code to pass tests
3. Run full test suite — confirm no regressions
4. Self-review against approved plan

### Step 7: Close

- Commit with conventional message referencing the issue
- Push, post summary comment, close issue

## Batch / Overnight Sessions

- Draft plans and label `status:plan-review` — do NOT implement
- Only implement issues already labeled `status:plan-approved`

## Engineering-Critical Issues

Issues with `cat:engineering*` or `cat:data-pipeline` labels require the full
`engineering-issue-workflow` skill (adds cross-review after implementation).

## Enforcement

- **PreToolUse hook**: `.Codex/hooks/plan-approval-gate.sh` blocks writes without approval marker
- **Pre-commit hook**: `scripts/enforcement/require-plan-approval.sh --strict` blocks commits without approval
- **Self-approval check**: gate verifies approval was not created in the same session

### Safe paths (no approval needed)

`.planning/`, `docs/plans/`, `docs/governance/`, `docs/reports/`, `docs/standards/`,
and the four top-level agent adapter markdown files

### Emergency bypass

```bash
SKIP_PLAN_APPROVAL_GATE=1  # for Codex hook
FORCE_PLAN_GATE=1 git commit  # for pre-commit hook
```

All bypasses are logged.

## References

- Full guide: `docs/plans/README.md`
- Template: `docs/plans/_template-issue-plan.md`
- Hard-stop policy: `docs/standards/HARD-STOP-POLICY.md`
- Engineering workflow: `.Codex/skills/coordination/engineering-issue-workflow/SKILL.md`
