---
name: gh-work-planning
description: Canonical GitHub issue planning route — issue intake, strengthened resource intelligence, repo-tracked plan artifact, adversarial review, GitHub progress posting, future-issue capture, explicit approval gate before execution, and execution-ready delegation packaging for Claude agent teams.
version: 1.3.0
author: Hermes Agent
category: coordination
triggers:
  - When user says "gh work planning"
  - When planning a GitHub issue before implementation
  - When an issue must move into plan-review before code changes
related_skills:
  - github-issues
  - writing-plans
  - multi-provider-adversarial-review
tags: [planning, github, issue-workflow, hard-stop, adversarial-review, tdd]
---

# GH Work Planning

This is the canonical planning route for GitHub issue work.

Use it whenever work starts from a GitHub issue and must follow:
Issue -> Plan -> User Approval -> Implement.

## Route summary

The output of this route is one artifact: an approved plan that downstream execution can follow without guessing.

## GitHub posting rule

As work progresses, post meaningful GitHub updates at each major step.
Do not wait until the end to communicate progress.

Minimum posting cadence during planning:
- after Step 1: intake / classification note
- after Step 2: resource-intelligence findings note
- after Step 3: draft-plan ready note if useful internally, or proceed directly into review
- after Step 4: review result summary
- after Step 5: final plan comment + status label update

Posts should be concise, factual, and cumulative rather than noisy.
If multiple sub-actions happen quickly, combine them into one structured update.

## Future-issue capture rule

During planning, if you discover adjacent work that should not be silently absorbed into the current issue, capture it as a future GitHub issue.

## Claude agent-team prompt packaging rule

When the work is large enough to benefit from multiple agents or multiple terminals, use Claude to package the work into self-contained prompts for agent team(s).
Use this especially when:
- the plan naturally splits into non-overlapping workstreams
- agent teams need explicit file ownership and zero git contention
- overnight or unattended execution is desired
- a licensed or external machine must execute work without Hermes context

Prompt packages should be:
- self-contained
- explicit about scope boundaries
- explicit about allowed write paths and forbidden paths
- explicit about tests, validation, and GitHub posting expectations
- explicit about commit/close or comment-only behavior

Preferred supporting skills for this packaging:
- `overnight-parallel-agent-prompts`
- `licensed-machine-prompt-orchestration`

## Agent-team decision gate

Before splitting work across Claude agent teams, explicitly decide yes/no on delegation.

Delegate only when all are true:
- work naturally splits into non-overlapping streams
- each stream can be given explicit file ownership
- dependencies between streams are known and minimal
- the orchestrator can keep GitHub status and final integration coherent

Do not delegate when:
- streams would touch the same files or branches concurrently
- ownership boundaries cannot be made explicit
- the work is small enough that orchestration overhead dominates
- a critical unknown should be resolved first in the main planning thread

If delegation is chosen, the plan must include a workstream split contract, delegated prompt pack, GitHub authority split, and execution-ready handoff per stream.

## Zero git contention rule

Zero git contention is a hard rule.

- no two delegated teams may write the same file
- no two delegated teams may own the same branch or worktree
- shared-file integration stays with the orchestrator unless one stream is explicitly designated as the sole owner
- if clean ownership cannot be enforced, do not split the work that way

Prefer additive boundaries, isolated worktrees, and orchestrator-controlled final merges.

## GitHub authority split

Default authority split:
- orchestrator owns issue intake, planning comments, labels, approval-state transitions, future-issue creation, final synthesis, and closeout decisions
- delegated teams own execution evidence inside their assigned stream packet and may draft suggested GitHub text only if requested

Delegated teams should not independently change issue-wide status labels, redefine scope, or close the parent issue unless the orchestrator explicitly grants that authority.

## Decision checkpoint rule

At the end of each major planning step, explicitly choose one:
- continue current issue
- create future issue
- stop for user decision
- stop for blocker

Do not carry ambiguity across steps.

Create a future issue when the discovered work is:
- materially out of scope
- a follow-up optimization rather than required for current acceptance
- blocked by missing data/decisions
- a separate bug/risk/remediation item
- useful institutional knowledge that should be tracked rather than buried in comments

When creating a future issue:
1. give it a precise title
2. include context, impact, and why it was split out
3. link back to the current issue
4. reference the new issue number in the current issue comment and in the plan's Risks/Open Questions or Follow-ups section

## The 5 steps

```text
STEP 1: Issue Intake          — read, classify, announce
STEP 2: Resource Intelligence — search all knowledge sources, map artifact locations, identify gaps and follow-ups
STEP 3: Draft the Plan        — pseudocode, file map, tests, acceptance criteria, follow-up issues
STEP 4: Adversarial Review    — Claude + Codex + Gemini review the plan
STEP 5: Hard Stop             — post to GitHub, label, wait for user approval
```

## STEP 1 — Issue intake

1. Read the full issue body: scope, acceptance criteria, references, labels.
2. Classify complexity:
   - T1: trivial change, abbreviated plan still required
   - T2: standard multi-file work with tests
   - T3: complex or architectural change
3. Announce that planning is underway before any implementation starts.
4. Post a short GitHub comment that planning has started, with complexity and any immediate scope notes.

## Blocker protocol

If planning is blocked, post a GitHub update immediately with:
- blocker summary
- impact on scope, plan quality, or approval readiness
- missing dependency/decision/input
- whether a future issue should be created

If the blocker is substantial and not resolvable inside the current planning cycle, create a future issue or dependency-tracking issue instead of burying it in notes.

## STEP 2 — Resource intelligence

Read-only only. No code written.

Search in this order, and strengthen the search until uncertainty is acceptably low.
Do not stop at the first plausible match.

## Proof-first rule

Every major claim from resource intelligence should be backed by explicit proof, such as:
- exact file path
- issue or PR number
- commit hash
- doc path
- standards/source reference
- command/query result

Do not rely on vague impressions like "seems to exist" or "probably handled elsewhere."

### a) Repo code
Check whether the feature/fix already exists partially or fully.
Record exact files, modules, functions, tests, configs, scripts, and docs found.
Search both direct names and adjacent synonyms/older terminology.

### b) Existing issue/PR history
Check related GitHub issues, issue comments, linked PRs, and commit references.
Look for prior attempts, rejected approaches, known constraints, and already-landed partial work.

### c) Standards / registries
Check any standards registries or reference ledgers relevant to the issue.
Record gap vs done status when standards are cited.
Identify whether the issue is actually blocked by a missing standard/source artifact.

### d) Primary knowledge base / wiki
Search the repo knowledge base or wiki index before broader guessing.
Record pages/entities consulted and any contradictions vs current repo reality.

### e) Local docs and document index
Read `docs/` and any indexed local references relevant to the issue.
Check for prior plans, architecture notes, design decisions, validation reports, and policy docs.

### f) Session recall
Use session search if similar work may have been done before.
Extract prior decisions, pitfalls, and previous issue numbers when applicable.

### g) External or upstream source check when needed
If the issue depends on an external API, package, standard, vendor tool, or upstream repo behavior, verify that dependency instead of guessing.
Capture version-specific or source-specific constraints.

### h) Artifact location planning
Decide where every artifact will live before drafting:
- plan file
- tests
- implementation files
- review artifacts
- docs/wiki updates
- planning index updates
- future follow-up issue references

Canonical plan artifact location:
- `docs/plans/YYYY-MM-DD-issue-NNN-<slug>.md`

Do not use `.hermes/plans/` for the canonical GitHub issue plan.

## Required Step 2 output schema

Before leaving Step 2, produce a structured intelligence summary with these sections:
- Existing assets
  - code
  - tests
  - docs
  - configs/scripts
- Related prior work
  - issues
  - PRs
  - commits
  - prior sessions
- Constraints
  - standards
  - upstream/API/tooling
  - policy constraints
- Gaps
- Risks / unknowns
- Scope split
  - in scope now
  - future issue candidates
- Artifact map

Also capture negative findings when useful, for example:
- no existing test found for X
- no prior issue found for Y
- no standards/source artifact found for Z

### Resource intelligence strengthening checks
Before leaving Step 2, explicitly ask:
- Did I inspect code, tests, docs, issue history, and prior session context?
- Did I search for alternate names, legacy names, and neighboring modules?
- Did I identify what already exists, what is missing, and what is uncertain?
- Did I identify out-of-scope findings that deserve future issues?
- Have repeated searches converged on the same likely implementation surface?

## Implementation-surface confidence

Assign one confidence rating at the end of Step 2:
- High: clear implementation surface, tests, and artifact locations are known
- Medium: likely implementation surface is known, but some uncertainty remains
- Low: implementation surface is unclear, conflicting, or blocked

## Low-confidence hard stop

If confidence is Low:
- do not draft a detailed plan as if certainty exists
- continue intelligence work, or
- stop and post a blocker update / request decision

## GitHub update template for Step 2

Post a concise GitHub update using this structure:
- Existing: ...
- Missing: ...
- Risks/unknowns: ...
- Likely implementation surface: ...
- Future issues likely: yes/no
- Confidence: High/Medium/Low

## STEP 3 — Draft the plan

Decision checkpoint after Step 2:
- continue drafting
- create future issue(s)
- package work as Claude prompts for agent team(s)
- stop for blocker/user decision

If agent-team delegation is being considered, decide it here before writing execution handoff materials.

## Step 3 recommendations now applied

Draft the plan by consuming the Step 2 output schema directly.
Do not rewrite the plan from memory or from a vague summary.
Each major section of the plan should trace back to Step 2 findings and explicit proof.

Use the repo issue-plan template if present and fill every section.

Minimum sections:
- Resource Intelligence Summary
- Traceability to Step 2 Findings
- Artifact Map
- Deliverable
- Scope Boundaries
- Pseudocode
- Files to Change
- TDD Test List
- Acceptance Criteria
- Risks and Open Questions
- Follow-up Issues
- Review Readiness Notes
- Complexity

Plan requirements:
- pseudocode for each meaningful new function/module
- exact likely file paths
- explicit tests before implementation
- acceptance criteria that are verifiable
- explicit separation between current-scope work and future issues
- each major plan claim should trace back to Step 2 findings or explicit evidence
- explicit scope boundaries: what is included now vs intentionally deferred
- follow-up issues should be listed with status: created now / candidate only / blocked

## Workstream split contract

When Step 3 chooses delegated execution, add one workstream contract per stream.

Each contract must contain:
- Stream name
- Objective
- Owning issue or sub-issue
- Allowed paths
- Forbidden paths
- Dependency on other stream(s) or `none`
- Deliverable

Keep contracts short and operational.
If any field is vague, the split is not ready.

## Delegated prompt pack structure

When producing Claude agent-team materials, create a prompt pack with:
- `master-plan.md` — orchestrator view of the full plan, stream map, dependency order, GitHub authority split, and integration notes
- `stream-<id>.md` per stream — self-contained execution prompt bound to that stream's contract
- `execution-readme.md` — operator instructions for launching teams, branch/worktree mapping, validation order, and return protocol

The prompt pack should live near the canonical plan or in a clearly referenced execution-support directory, and the plan must record the exact paths.
Keep the naming and structure stable so execution sees one prompt pack vocabulary: `master-plan.md`, `stream-<id>.md`, and `execution-readme.md`.

## Execution-ready handoff contract per stream

Every delegated stream prompt must be execution-ready, not advisory.

Include:
- stream objective and success condition
- exact issue context and acceptance criteria slice
- allowed paths and forbidden paths
- dependency status and what inputs are assumed ready
- exact tests/validation commands or required checks
- expected deliverable artifact(s)
- GitHub authority limits
- return format for completion, blockers, and future-issue recommendations

## Acceptance-criteria quality rule

Acceptance criteria should be:
- measurable
- testable
- specific to the issue
- tied to proof expected during execution

Avoid vague criteria like "works correctly" or "looks good."

## Scope discipline rule

Do not silently expand the plan to absorb adjacent work.
Only include adjacent work when it is required for correctness, safety, or to satisfy the stated acceptance criteria.
All other adjacent work must become future issues or explicit follow-ups.

## Review-readiness rule

Before sending the plan for adversarial review, confirm:
- the plan is internally consistent
- the proposed files and tests match the implementation surface discovered in Step 2
- every acceptance criterion has a plausible verification path
- future issues are clearly separated from current deliverables
- blockers and assumptions are visible, not hidden

If future issues were discovered, either create them now or mark them as issue candidates with exact proposed titles and rationale.

## Planning pre-review checklist

Before adversarial review, confirm all are true:
- deliverable is clear in one sentence
- likely files to change are listed explicitly
- tests are named before implementation
- acceptance criteria are measurable
- acceptance criteria have plausible verification paths
- blockers/unknowns are stated plainly
- follow-up work is separated from current scope
- no adjacent work has been silently absorbed without justification
- Step 2 findings are reflected accurately in the plan
- future issue handling is explicit: created, candidate, or none
- delegated streams, if any, have non-overlapping ownership and execution-ready handoff packets

## GitHub update template for Step 3

Post a concise GitHub update using this structure:
- Planned deliverable: ...
- Likely files/tests: ...
- Scope boundaries: ...
- Future issues: created / candidate / none
- Review readiness: yes/no

## STEP 4 — Adversarial plan review

Run three independent plan reviews in parallel before the user sees the plan.
This is a formal quality gate, not a casual opinion check.

## Review package completeness check

Before dispatching reviewers, ensure the review package includes:
- issue body
- Step 2 structured intelligence summary
- draft plan
- acceptance criteria
- follow-up issues or candidates
- blockers, assumptions, and scope boundaries

If the package is incomplete, fix the package before review instead of sending a weak review prompt.

## Blind-first rule

Each reviewer should critique independently before seeing any other reviewer conclusions.
Do not let reviewers anchor on each other.

## Standard reviewer prompt contract

Every reviewer should evaluate the same dimensions:
- correctness
- completeness
- feasibility
- TDD adequacy
- scope discipline
- risk handling
- future-issue separation
- verification readiness

## Required reviewer output schema

Each reviewer should return:
- Verdict: APPROVE | MINOR | MAJOR
- Strengths
- Gaps
- Risks
- Missing tests
- Scope creep concerns
- Weakest assumption and what breaks if it is false
- Most likely implementation failure mode
- Most likely test gap
- Future issues suggested
- Review confidence

## Verdict normalization

Use these meanings consistently:
- APPROVE: no blocking issue remains
- MINOR: safe to proceed after minor or optional corrections
- MAJOR: the plan cannot proceed without revision

## Mandatory synthesis step

After all reviews return, produce one authoritative synthesis containing:
- consensus findings
- disagreements
- accepted changes
- rejected suggestions with rationale
- residual risk level: Low | Medium | High
- user-attention-required decisions, if any
- execution handoff notes
- ready_for_approval: yes/no

## Disagreement handling

If reviewers disagree materially:
- do not average the disagreement away
- resolve it using Step 2 evidence, Step 3 traceability, and explicit reasoning
- revise and re-review if the disagreement affects correctness, scope, tests, or feasibility

## No silent downgrade rule

If any reviewer returns MAJOR, do not silently downgrade that to MINOR without explicit written rationale tied to evidence.

## Material-change re-review rule

If the plan changes materially after review, run Step 4 again.
Material changes include:
- changed deliverable
- changed file map
- changed tests
- changed acceptance criteria
- changed scope boundary
- changed external dependency assumption

## Review artifact schema

When storing review artifacts, capture:
- reviewer
- timestamp
- prompt version
- verdict
- structured findings
- synthesis linkage

## Decision gate

- any MAJOR -> revise plan and re-run review
- all APPROVE/MINOR and ready_for_approval=yes -> proceed to Step 5

## GitHub update template for Step 4

Post a concise synthesis-first GitHub update using this structure:
- Review status: complete / revision required
- Verdict summary: ...
- Accepted changes: ...
- Major unresolved items: ...
- Residual risk: Low/Medium/High
- Future issues: created / candidate / none
- Ready for approval gate: yes/no

Do not dump raw full reviewer text into the issue unless necessary.
Link or reference full review artifacts separately when needed.

## STEP 5 — Hard stop and approval gate

This is the explicit stop line between planning and execution.
No implementation begins from this route until approval handling is complete.

## Exact GitHub action order

Before waiting:
1. Save the plan file to `docs/plans/...`
2. Update the planning index if the repo uses one
3. Ensure any follow-up issues discovered during planning are either created or explicitly marked as candidates
4. Post the final plan comment to the GitHub issue
5. Post or include the Step 4 synthesis summary if not already present in the final plan comment
6. Add `status:plan-review`
7. Remove any stale status labels that conflict with plan-review state
8. Stop and wait for explicit user approval

## Final GitHub plan comment should include

- final deliverable summary
- scope boundaries
- likely files/tests
- review synthesis summary
- residual risk level
- future issue links or candidates
- ready_for_approval status
- explicit request for approval / revision / rejection

## Approval response normalization

Interpret user responses using this mapping:
- APPROVE / GO / YES -> approve
- REVISE / CHANGE / UPDATE -> revise
- REJECT / NO-GO / STOP -> reject
- BLOCKED / HOLD -> pause

If the response is ambiguous, do not start execution. Clarify first.

## Label discipline

Expected planning labels:
- `status:plan-review`
- `status:plan-approved`

Approval handling:
- on approve: remove `status:plan-review`, add `status:plan-approved`
- on revise: keep or re-apply `status:plan-review`
- on reject: remove planning-ready labels that imply approval
- on pause/hold: leave the issue clearly not approved for execution

## Revise flow

If the user requests revision:
1. post a GitHub acknowledgement of requested changes
2. update the plan
3. re-run Step 4 if the revision is material
4. re-post the updated final plan
5. keep the issue in `status:plan-review`
6. wait again for explicit approval

## Reject flow

If the user rejects the plan:
1. post a GitHub acknowledgement of rejection
2. summarize the likely reason and unresolved decision if known
3. remove approval-implying labels
4. do not start execution
5. either stop or open an alternative-plan discussion / future issue

## Pause / hold flow

If the user pauses or holds the plan:
1. post a GitHub note that execution is not authorized yet
2. preserve the current plan artifact
3. keep labels consistent with not-approved state
4. do not start execution until explicit approval arrives later

## Batch-readiness rule

A plan is batch-ready only when:
- the final plan artifact is saved
- Step 4 synthesis is complete
- follow-up issues are captured appropriately
- `status:plan-approved` is present
- no unresolved blocker or approval ambiguity remains

No issue in `status:plan-review` is eligible for execution.

## Execution handoff package

When approval is granted, the handoff into execution should be explicit and include:
- approved plan path
- final deliverable summary
- scope boundaries
- acceptance criteria
- residual risk level and residual risks to watch
- future issue links
- execution handoff notes from Step 4 synthesis
- Claude-packaged prompt files for agent team(s), when execution is delegated or parallelized

When execution is delegated, the handoff must also include:
- prompt pack paths: `master-plan.md`, stream prompt files, and `execution-readme.md`
- one execution-ready handoff contract per stream
- branch/worktree ownership per stream
- dependency order and orchestrator integration checkpoint(s)
- GitHub authority split for orchestrator vs delegated teams
- explicit confirmation that zero git contention is enforced

If execution will be performed by agent teams, package the work into self-contained Claude-readable prompts before handoff.
Each prompt should define:
- owned issue(s)
- owned paths and forbidden paths
- exact validation steps
- GitHub posting expectations
- future-issue capture expectations

The orchestrator remains accountable for the parent issue state even when execution is delegated.

## GitHub update template for Step 5

Use a concise approval-gate update structure:
- Plan status: awaiting approval / approved / revision requested / rejected / on hold
- Plan artifact: ...
- Residual risk: Low/Medium/High
- Future issues: ...
- Execution authorized: yes/no
- Next action: await approval / revise / stop

Valid approval outcomes:
- approve -> set `status:plan-approved`, then execution may begin
- revise -> update plan and re-run review as needed
- reject -> stop and discuss alternative approach
- pause -> hold with no execution authorization

## Required gate

No implementation starts until the issue is explicitly approved and labeled `status:plan-approved`.

## Pre-labeled approved issue recovery rule

Sometimes an issue already carries `status:plan-approved` before the canonical repo planning artifacts exist.
Do not treat the label alone as sufficient proof that the planning route was completed.

When you encounter an already-approved issue with no repo-tracked plan artifact:
1. draft the canonical plan file under `docs/plans/YYYY-MM-DD-issue-NNN-<slug>.md`
2. update `docs/plans/README.md` with the plan index row
3. post a GitHub comment linking the new plan artifact and summarizing scope/resource-intel anchors
4. do **not** start implementation yet just because the old approval label is present
5. next run adversarial plan review and reconcile the issue state with the actual plan artifacts before coding

This recovery pattern is especially important for harness/operations issues that were approved conversationally before the repo plan discipline was enforced.

## GitHub labels

Expected labels:
- `status:plan-review`
- `status:plan-approved`

Create them if missing before relying on this route.

## Preferred companion skills

- `github-issues` for issue view/comment/label/create actions
- `plan` only for non-GitHub or purely local planning

## Pitfalls

- Skipping adversarial review because the issue looks simple
- Posting only once at the end instead of at major planning steps
- Weak resource intelligence based on one search path only
- Folding follow-up work silently into the current issue instead of creating future issues
- Posting a plan before review passes
- Writing the plan in `.hermes/plans/` instead of `docs/plans/`
- Forgetting to update the planning index when the repo uses one
- Starting implementation on `status:plan-review`

## Legacy compatibility

Older guidance may reference `issue-planning-mode`.
Treat that as a deprecated alias/reference for this route, not the primary route name.
