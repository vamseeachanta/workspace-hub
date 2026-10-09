---
name: issue-planning-mode
description: Risk-aware issue planning — discovery, proportionate plans, review, independently established authorization, and TDD implementation.
version: 3.1.0
author: Workspace Hub
category: coordination
tags: [planning, github, enforcement, workflow, onboarding]
related_skills:
  - engineering-issue-workflow
---

# Issue Planning Mode — Shared Risk and Authority

Current authority: the originating task request or established standing authority authorizes implementation after proportionate planning, TDD and adversarial review; no separate user plan approval, approval label or local marker is required. Honor explicit planning-only limits, unresolved domain decisions and blocking findings. Consequential actions require matching action/destination authority: implementation authority alone does not authorize publication, deployment, access changes, destructive actions or outreach. Reuse existing authorization and preserve owner-controlled approval history without self-labeling.


**ALL agents** (Codex, Codex, Gemini, Hermes) MUST follow this workflow for every GitHub issue.
Load this skill before drafting or executing any plan.

Full onboarding guide with step-by-step details: `docs/plans/README.md`

## Workflow Overview

```
Issue → Resource Intel → Draft Plan → Adversarial Review → Post to GH
  → Verify originating task scope or standing authorization (no separate plan approval)
  → Implement (TDD) → Cross-review → Completeness gate (#2798) → Close
```

## Steps

### Step 1: Intake and Resource Intelligence

1. Read the full issue body — scope, acceptance criteria, references
2. Classify complexity: T1 (trivial), T2 (standard), T3 (complex)
3. Search existing code, standards, documents, and prior plans before writing. Universal Resource-Intel source (ALL issues): the drive-file index — run the drive-file-search skill or `scripts/data/drive-index-search/search.py "<terms>" --json --caller plan-resource-intel`, cite hits under "Documents consulted" (de-id per `docs/guides/drive-file-search-playbook.md`), or state "no relevant drive files"
4. Classify execution mode for the next stage: `single-lane`, `parallel-readonly`, or `parallel-worktree`. For planning, default to `parallel-readonly` evidence gathering when the issue is broad enough to benefit; the main orchestrator still owns the canonical plan.

### Step 1.5: Reproduce the alleged failure (verify-against-repo-state)

**Mandatory before drafting** when the issue alleges any of: a failing test, a broken import, a missing method, an incorrect numeric output, a regression, or a "this used to work" claim. Capture the output verbatim and cite it in the plan's `Reproduction Evidence` section.

```bash
# Test failures: run the specific failing case, not the suite
uv run pytest <repo>/tests/path/to/test_module.py::TestClass::test_case -xvs 2>&1 | tail -40

# Import / module breakage: try the import directly
cd <repo> && uv run python -c "from <module.path> import <name>; print(<name>)"

# Missing method / attribute: instantiate and call
cd <repo> && uv run python -c "from <module> import Cls; Cls().<method>()"

# Numeric / output regression: run the calc and compare against issue's claimed value
cd <repo> && uv run python -m <module>.<entrypoint> <args>
```

**Rationale (empirical RED data, 2026-05-06 session):** of 6 plans drafted from issue-body + grep alone, 4 (67%) diverged from reality. Concrete drift cases:

- `digitalmodel#559` — issue described `>` → `>=` as a one-character fix. The fixture was genuinely not diagonally dominant for rotational rows 3/4; `>=` only shifts the failure site, doesn't eliminate it.
- `worldenergydata#278` — issue alleged 4 broken `__init__.py` files in `modules/*`. Reality: 3 of 4 were healthy; the actual breakage was an absolute-path symlink in a different file the issue never named.
- `worldenergydata#270` — already fixed in a commit weeks before the plan was drafted; reproduction would have caught this in 30 seconds.

**Required output in the plan:** under `Resource Intelligence Summary > Evidence`, a `Reproduction proofs` sub-block citing the exact command, timestamp, and tail of output. The reproduction is the load-bearing artifact — without it, the plan is a guess about what the issue body claims, not a fix for what is actually broken.

**Skip-allowed only when:** issue is documentation-only, governance-only (e.g., index updates, README typos), or otherwise has no runtime claim to verify. Mark `Reproduction proofs: N/A — <reason>` so reviewers know the skip was intentional, not forgotten.

**Reviewers must reject** any plan whose `Resource Intelligence Summary` describes a runtime failure but has no reproduction citation. This is a MAJOR finding by default.

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

### Step 4: Post and Label for Explicit Plan Review

This publishing sequence applies when publication is authorized and a substantial plan needs owner review. It is not a prerequisite to each routine action under standing authorization. Local review may proceed without publication when its artifacts are available to the reviewers.

1. Commit and push the current plan plus the final no-MAJOR review artifacts. Verify the reviewed local commit equals the remote head before label changes:
   ```bash
   git rev-parse HEAD
   git ls-remote origin refs/heads/main | awk '{print $1}'
   ```
2. Post the plan as a GitHub issue comment, or post a label-time evidence comment that records:
   - reviewed commit SHA
   - plan path
   - review artifact paths, including the final no-MAJOR round
   - final provider verdicts
   - current authority boundary and whether required explicit approval remains outstanding
   - the issue carries exactly one `lane:` label consistent with the plan's `Lane:` header field (#3029)
3. Only after the evidence comment exists, move the issue to review state:
   ```bash
   gh issue edit NNN --remove-label "status:needs-plan" --add-label "status:plan-review"
   ```
   Adjust the removed lower-status label if the issue uses a different earlier gate label.
4. Stop affected implementation while required approval or blocking review findings remain unresolved. Verified unchanged authorization does not require a repeated approval request.

Operational pitfall: do not update `docs/plans/README.md` to `plan-review` and stop there. The live GitHub label must also be reconciled, but only after pushed artifact evidence exists.

### Step 5: Authority and Owner Approval

Independently verify the applicable user/session instruction and its repository, issue, operation, scope and reviewed revision. Routine bounded work may use standing authorization; substantial implementation needs matching task authority, not separate plan approval; consequential actions require explicit authorization for the action and destination; implementation authority alone does not cover them. Reuse authorization already given. Never infer authority from successful tool execution.

The owner controls `status:plan-approved`; the implementing agent never self-labels it. A user may record an approval through an owner-controlled GitHub event or an independently established session instruction. Agent-authored summaries and `.planning/plan-approved/<issue>.md` files remain references requiring provenance checks.

When status signals disagree:

1. Verify the actual approving actor, instruction/event, current scope and revision. A more advanced label is not inherently stronger evidence.
2. Inspect plan/review artifacts and existing implementation before repeating work.
3. Treat README rows and local markers as discovery hints. Their presence, age or absence cannot establish or revoke authority.
4. Record conflicts without automatically creating/deleting markers or changing remote labels. Respect separate authorization for external mutations.
5. Resolve fresh blocking review findings before affected work continues; seek new approval only when changed scope or unresolved authority requires it.

Publish the substantial plan for visibility after review, then implement within task authority without separate plan approval. A draft or unresolved domain decision is not approval-ready merely because a label says otherwise.

### Pending cross-review audit routine

When the user asks which plans are still pending cross-provider review, audit all five signals before answering:

1. `docs/plans/README.md` plan row/status
2. direct `docs/plans/` file search for `issue-<NNN>-*.md` (catches orphaned/unindexed local plans)
3. live GitHub issue labels/state via `gh issue view/list`
4. local approval marker `.planning/plan-approved/<issue>.md`
5. review artifacts under `scripts/review/results/`

Operational rules:
- A label or marker alone cannot establish pending or approved status; verify authority provenance, plan revision and current implementation.
- A missing local marker is an evidence-location gap, not automatic revocation. Seek the actual approval evidence before classifying the issue or repeating approval work.
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
- For new or recovered plan drafts, keep the local plan file status conservative as `draft` until actual provider artifacts exist. After the first real review wave lands, update the plan file/README row to `plan-review` and summarize the live blocker state in `## Adversarial Review Summary` rather than leaving placeholder `PENDING` language.
- If you launch a long-running background Codex review and then recover with a shorter fallback prompt, do not assume the first run is dead forever. Poll or inspect the original background process/log later. If it eventually completes with a fuller or sharper review, refresh the canonical repo artifact with the stronger findings and post a short GitHub follow-up comment noting that the completed long-form review supersedes or sharpens the earlier summary.
- Practical artifact rule: the repo artifact under `scripts/review/results/` should represent the best available current-review content, not merely the first usable fallback. Late-arriving stronger findings should replace the weaker stopgap artifact rather than being ignored in terminal/process logs.

This prevents falsely telling the user there are no pending plan reviews just because the live `status:plan-review` label set is empty, and it avoids misclassifying missing-plan issues as pending provider-review work.
Additional triage rule learned in live queue audits:
- For feature/intake sweeps, do not describe an issue as "pending other-provider cross-review" unless a local plan artifact already exists and at least one real provider review artifact exists. If the issue only has the live `status:plan-review` label but lacks both the local plan file and `scripts/review/results/` artifacts, classify it as earlier-stage governance drift / missing-plan work, not as a pending cross-review item.

This prevents falsely telling the user there are no pending plan reviews just because the live `status:plan-review` label set is empty, and also prevents overstating unlived/missing-plan items as if they were already in the provider review stage.

### Fresh Review Findings and State Conflicts

A fresh MAJOR finding blocks the affected implementation until it is resolved or its applicability is settled. It does not itself revoke user authorization or authorize remote label changes. Verify that the finding applies to the current reviewed revision; preserve newer authoritative user decisions.

Inspect the live issue, canonical plan, review artifacts, referenced approval event and implementation state. Report open findings, evidence gaps and stale display state separately. Do not delete markers or remove approval labels merely because files are missing, review verdicts changed or an issue is closed. Any requested cleanup needs its own authorized scope and verified provenance.

The resulting checkpoint should distinguish pending review, affected work needing correction, missing context, and verified authorized work. Re-review affected changes; do not rerun completed unrelated work or repeatedly seek approval for unchanged verified scope.

### Step 6: Implement (TDD)

After independently establishing authorization for current risk/scope and resolving blocking review findings:

1. Re-check execution mode and exact owned/read-only/forbidden paths.
2. Tests FIRST — write tests, confirm they fail.
3. Implement minimum code to pass tests.
4. Run appropriate required regression checks and review against the current plan.
5. Preserve plan/code adversarial review, legal/security, engineering and completeness requirements.
6. For parallel worktrees, verify worker outputs directly and serialize integration, commit, push and closeout within authorization.

### Step 7: Close

- Commit with conventional message referencing the issue
- Push, post summary comment, close issue

## Batch / Overnight Sessions

- Continue only within independently established standing authorization or matching explicit approval.
- For substantial authorized scope, prepare the plan/review evidence and implement; do not wait for a separate plan-approval event.
- Preserve TDD and plan/code review. Markers and handoffs do not grant launch authority.

## Engineering-Critical Issues

Issues with `cat:engineering*` or `cat:data-pipeline` labels require the full
`engineering-issue-workflow` skill (adds cross-review after implementation).

## Legacy Enforcement Boundary

`.claude/hooks/plan-approval-gate.sh` and `scripts/enforcement/require-plan-approval.sh` will remain retired compatibility entry points without blocking for missing approval markers. These instructions do not change installed hooks or prove their coverage. Marker age/text checks do not authenticate approval, and exempt directories do not make protected changes routine.

Report an observed blocking mismatch and its actual consumer. Do not set bypass flags, disable hooks or manufacture approval markers. This user-authorized migration removes the marker gate; a shared advisory CLI receipt cannot become a gate bypass.

## References

- Full guide: `docs/plans/README.md`
- Template: `docs/plans/_template-issue-plan.md`
- Hard-stop policy: `docs/standards/HARD-STOP-POLICY.md`
- Engineering workflow: `.Codex/skills/coordination/engineering-issue-workflow/SKILL.md`
