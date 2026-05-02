# Archived Skill: `gh-work-planning`

Original path: `/home/vamsee/.hermes/skills/coordination/gh-work-planning`
Archived into: `/home/vamsee/.hermes/skills/.archive/umbrella-2026-04-29/coordination/gh-work-planning`
Consolidation date: 2026-04-29

---

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

### Post-batch future-issue extraction routine

After a planning-only batch or overnight plan-review wave, do not leave deferred scope buried inside plan files or review artifacts.

Use this routine:
1. Read the batch results report and the newly created/refreshed plan files.
2. Search specifically for explicit deferred-scope markers such as:
   - `Open:`
   - `follow-up issue`
   - `future issue`
   - `out of scope`
   - `can be added incrementally`
3. Filter to items that are genuinely separate from the current bounded issue, not just implementation notes.
4. Search GitHub for duplicates before creating anything.
5. Create concrete follow-up issues immediately for the strongest deferred items, with bodies that explain:
   - why the work was intentionally kept out of the current issue
   - which issue/plan surfaced it
   - what dependency or sequencing relationship exists
6. Record the created issue numbers in the session handoff / results summary so the next execution wave does not silently absorb the deferred work.

This is especially useful after overnight Claude planning runs, where multiple plans may each leave one or two explicit "Open" decisions. Converting the strongest ones into real GitHub issues preserves scope discipline and gives tomorrow's execution wave a cleaner boundary.

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

## Operational-diagnosis vs repo-remediation split

For operations / cron / scheduler / environment issues, explicitly separate:
- live-state diagnosis on the current machine or host
- repo-owned code/config remediation

Do not assume a repo patch is the right answer just because the symptom appears in repo logs.

Required planning behavior for these issues:
1. Capture a reviewable live-state classification artifact first (for example: installed vs not-installed, firing vs not-firing, failing before startup vs failing after startup).
2. State which branch is operational-only and which branch is repo-fixable.
3. If the live cause is operational drift (for example missing crontab installation), do not pretend a repo-code patch solves it. Record the classification explicitly and either stop at operator guidance or create a follow-up ops issue.
4. Only draft implementation files/tests for the repo-owned failure branch that has actually been evidenced.
5. Keep acceptance criteria aligned to the chosen branch; avoid mixing "diagnose the live host" and "ship a code fix" as if both must always happen in one issue.

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

### i) Operational-vs-repo fault isolation for cron/scheduler issues
For issues about cron jobs, scheduled tasks, wrappers, health monitors, or other automation that depends on live machine state, do not assume the fix is in repo code.

Before drafting an implementation-heavy plan:
- capture at least one reviewable live-state probe artifact when possible (for example: `crontab -l`, generated scheduler dry-run output, current log directory contents, current health JSON/log snapshot)
- save the probe in a durable repo-visible artifact such as `docs/reports/YYYY-MM-DD-issue-NNN-<slug>-probe.md` when the result materially changes the decision tree
- explicitly separate these branches:
  - not installed / not scheduled
  - installed but not firing yet / operational drift
  - installed and failing after launch
  - repo-owned command/config defect
- if live evidence eliminates one branch, update the draft plan immediately rather than carrying stale hypothetical branches forward
- if the live cause appears operational rather than repo-owned, the plan must say whether the correct outcome is:
  - diagnosis + operator guidance only
  - diagnosis + follow-up issue
  - bounded repo patch plus separate operational remediation

Important rule:
- do not present a repo-code patch as the solution if the strongest evidence says the issue is host-state or installation drift
- for mixed issues, make the stop condition explicit: exactly when do we stop at diagnosis, and exactly when do repo changes become in-scope?

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

## Strategy / architecture issue packaging rule

For planning-only strategy, architecture, or governance issues, reviewers are highly sensitive to both underscoping and packaging drift.

Operational rules learned from live review waves:
- Do not use a vague single "report" artifact when the issue explicitly calls for multiple durable outputs (for example: standing contract, reusable battery/spec, gap analysis, follow-up issue drafts, consumer inventory). Name each required artifact explicitly in `Artifact Map`, `Files to Change`, and `Acceptance Criteria`.
- Avoid adding auxiliary file edits that are not clearly required by the issue (for example updating unrelated dependency maps or indexes). Reviewers treat these as scope creep.
- If an issue requires conditional follow-up issues, the plan must include a concrete artifact for them (draft pack, issue stubs, or explicit creation step). Saying "recommend follow-ups in the report" is usually judged insufficient.
- If a plan claims something is reusable/standing, place it in a durable standards/config surface rather than only in a date-stamped report.
- For repo-boundary or migration decisions, include a first-class consumer/backlink/path inventory artifact before recommending movement. Reviewers will reject high-level recommendations that are not grounded in concrete dependency evidence.
- For checker/CI/enforcement artifacts, do not bundle rollout prematurely if exception rules or scope boundaries are still unresolved. Separate "define contract" from "enforce contract" unless the issue explicitly requires both.

If repeated review rounds still return MAJOR after tightening, keep the issue in draft/review-only state and post a GitHub status comment summarizing the remaining blockers rather than prematurely moving it to `status:plan-review`.

Review-state hygiene learned from live reruns:
- If a newer rerun wave exists but one or more provider artifacts are empty, `UNAVAILABLE`, or wrapper-failed, do not describe older artifacts as simply the "latest" state. Distinguish clearly between:
  - freshest wave status (including provider failures)
  - last valid artifact per provider, if different
  - whether the review gate is still unsatisfied because the newest wave did not produce the required valid artifacts
- Re-check `.planning/plan-approved/<issue>.md` before claiming approval evidence is absent. If a marker exists with weak/non-auditable provenance (for example `Approval source: current Hermes chat instruction`), treat it as governance drift / likely self-approval evidence, remove it for open draft issues, and note the cleanup explicitly in the plan summary or GitHub status comment.
- For CI-hardening plans that change workflow gates, include both:
  - isolated red/green commands for the narrow source/test fixes, and
  - at least one workflow-shaped local command that matches the CI gate closely enough to expose the likely next blocker (for example coverage thresholds / markers), so the plan does not overclaim "CI parity" from isolated tests alone.

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

### Practical packaging rule for local draft plans

When the plan is still only in local/uncommitted repo state, do **not** rely on the reviewer being able to fetch it from GitHub or rediscover it from the filesystem.

Use this order of preference:
1. Provide the full revised plan text inline / via stdin bundle in the review prompt
2. If needed, include the minimal supporting excerpts inline too
3. Only rely on path-based retrieval when the artifact is definitely readable from the review environment

Why:
- non-interactive provider runs can fail to read local drafts because of sandbox, trust, or repo-state limitations
- a reviewer may return a misleading `MAJOR` caused by retrieval failure rather than by the plan itself
- path-only prompts are best for stable readable files, not for fresh local draft artifacts

Operational rule:
- if a review artifact is being refreshed, write the new review to a temp file first and only replace the canonical artifact after the run succeeds; this avoids accidentally truncating a previously good artifact with a failed rerun
- if a reviewer returns `MAJOR` primarily because retrieval adequacy was insufficient, treat that as a packaging failure first; fix the package, rerun review, and only then treat remaining findings as substantive plan criticism

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

## Diagnosis-vs-remediation branch rule

When an issue can resolve in more than one fundamentally different way — especially:
- operational/environment diagnosis only
- repo-owned code/config remediation

make that branch decision explicit in the plan.

Required pattern:
- identify the live-state classification artifact you will use to choose the branch
- state the stop condition for the diagnosis-only path
- state the stop condition for the repo-remediation path
- avoid mixing both as if implementation is guaranteed
- if a diagnosis-only outcome is plausible, say explicitly that the issue may end with operator guidance and no repo code changes

Good examples:
- installed vs not-installed cron entry
- host drift vs repo defect
- external service outage vs local integration bug

This prevents approval-ready plans from smuggling in speculative code changes before the branch is actually chosen.

## Review-iteration stop rule

When a plan keeps returning fresh `MAJOR` findings across multiple re-review passes, do not iterate indefinitely.

After 2-3 substantive tightening passes, explicitly choose one:
- continue because the remaining blocker is shrinking and clearly actionable
- park the issue in draft with a concise blocker summary
- switch to planning a sibling/follow-up issue that may unblock faster
- split the issue into a narrower parent/child decomposition when the blockers are really decomposition problems rather than wording problems

Operational guidance:
- treat repeated `MAJOR` findings with shrinking but persistent scope as a signal of diminishing returns
- post a GitHub update summarizing the remaining blocker instead of silently grinding through more revisions
- do not move the issue to `status:plan-review` just because the plan is "close"
- if you switch away, record why and what exact blocker remains
- if reviewers keep objecting that one issue mixes too many concerns, stop rewriting the same monolith and decompose it into child issues by artifact/responsibility type

Practical decomposition heuristic for architecture/governance issues:
- split **canonical contract / policy** work from **inventory / evidence gathering** work
- split **fixture corpus / examples / baselines** from **runner / schema / interface design**
- split **normalization of existing entry surfaces** from **new contract language**
- split **follow-up issue creation / dedup automation** from the main policy issue if reviewers treat it as a separate risky subsystem
- keep the original broad issue as a parent/umbrella after the split; do not keep trying to force the parent through approval as one approval unit once review has shown the scopes are separable

Typical signs the split is overdue:
- repeated `MAJOR` findings say the issue is "too broad", "too large for T2", or "mixes contract definition with normalization/automation"
- reviewers accept the high-level direction but block on one or two attached subsystems (for example runner semantics, issue creation policy, or entrypoint normalization)
- each rewrite fixes wording but not the structural objection

### Decomposition trigger after repeated MAJOR reviews

Use this pattern when the review waves keep converging on the same structural complaint, for example:
- "scope too broad for one T2/T3 plan"
- "this includes multiple risky subsystems"
- "runner/schema/policy/inventory should be separate issues"
- "parent umbrella should stay steering-only"

Required response:
1. stop trying to force the whole scope through one approval gate
2. identify the independent workstreams causing the blocking findings
3. create child issues for those workstreams immediately
4. keep the original issue as a parent/umbrella unless the whole issue should be replaced
5. comment on the parent issue with:
   - why the decomposition happened
   - the child issue links
   - recommended execution / approval order
6. narrow the parent issue's role to steering, sequencing, or final synthesis if appropriate

Practical rule:
- if repeated MAJOR findings are mostly about decomposition, boundaries, or "too much in one issue," do not spend another full revision cycle polishing prose inside the monolith. Split it.
- once split, seek approval on the narrowest child issue first, especially the one that establishes the canonical contract or evidence base for the others.


### Monolith-to-child-issue decomposition pattern

Use this when repeated adversarial review converges on the same meta-problem: the issue is too broad, mixes multiple subsystems, or keeps failing because approval is being sought for one large plan instead of several narrower ones.

Trigger signals:
- 2+ review rounds still return `MAJOR`
- multiple providers independently call out scope bloat, packaging sprawl, or unresolved architectural decomposition
- one issue is trying to define policy + fixtures + runner semantics + inventory + automation behavior all at once
- revisions improve wording but do not eliminate the same structural blocker

Required response:
1. Stop trying to force the original issue through approval as one monolith.
2. Identify the natural child workstreams and write them as separate GitHub issues with bounded deliverables.
3. Recast the original issue as a parent/umbrella that links the child issues and owns only steering/synthesis.
4. Comment on the parent issue explaining why decomposition was necessary and in what order the child issues should be reviewed.
5. Prefer approving the narrowest contract/evidence issues first, then the dependent execution/policy issues.

Practical rule:
- If the repeated blocker is decomposition itself, further prose-only tightening of the same parent plan is usually wasteful. Split the work instead of polishing the monolith.

### Monolithic-parent decomposition trigger

If cross-provider review repeatedly says the issue is too broad, mixes multiple subsystems, or bundles governance + inventory + automation + execution-policy concerns into one approval gate, stop rewriting the same parent plan.

Instead:
1. keep the parent issue as umbrella/steering only
2. split the blocked scope into 3-5 narrower child issues, each with one clear approval surface
3. create the child issues immediately so the decomposition is concrete, not just suggested
4. comment on the parent with the decomposition, rationale, and recommended review/approval order
5. move planning/review effort to the narrowest child issue first

Typical split axes:
- contract/policy
- evidence inventory / reconnaissance
- fixture corpus / test assets
- runner/schema/interface design
- follow-up issue creation / governance automation

Use this when the blocker is structural decomposition, not missing wording. Repeatedly polishing a monolithic umbrella usually wastes review cycles and still returns `MAJOR`.

### Monolith-plan split trigger (learned from repeated #2399-style review failures)

If fresh Codex/Gemini/Claude reviews keep converging on findings like:
- "issue is too large for a single T2 governance/planning issue"
- "too many artifacts / documentation sprawl"
- "runner contract / automation / issue-creation logic is scope creep"
- "ecosystem claim is broader than the actual evidence base"
- "this should be split into smaller child issues or rescope to workspace-hub-only"

then stop trying to polish the monolith.

Do this instead:
1. classify the blocker as **decomposition failure**, not wording failure
2. rewrite the parent as a narrower umbrella / steering issue
3. create concrete child issues for the major concern clusters
4. if ecosystem-wide evidence is too thin, rescope the parent to the smaller proven domain (for example workspace-hub-only) and move broader claims into follow-up inventory issues
5. only resume plan-review on the narrower parent/children after the split is reflected in the issue structure

Heuristic:
- if the latest review wave is still `MAJOR` after multiple rewrites and the blocker list keeps naming *scope, packaging, automation, or missing ecosystem evidence* rather than a few specific missing sections, the correct fix is almost always to split/rescope, not to keep editing the same plan.

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

## Audit-report to overnight queue pattern

Use this pattern when a repo capability/readiness audit produces several GitHub follow-up issues that need to become overnight-ready work items.

Operational rules:
1. Treat the audit reports as Step 2 resource-intelligence evidence, but still re-read the issue bodies, canonical repo docs, manifests/configs, and related source files needed to draft each plan.
2. Batch related issues only when they share evidence but have separable implementation surfaces; each issue still needs its own canonical `docs/plans/YYYY-MM-DD-issue-NNN-<slug>.md` artifact and GitHub final plan comment.
3. Freeze source-of-truth decisions in the plan before review when multiple registries disagree (for example manifest vs source tree vs catalog vs CLI registry vs scheduler config). Reviewers should see the chosen authority for each artifact class, not an open-ended reconciliation exercise.
4. For capability/data/scheduler readiness issues, explicitly separate documentation/index reconciliation from runtime refresh execution. Do not authorize unbounded downloads, full refreshes, or long-running scheduler jobs unless the approved plan says so and prerequisite runtime readiness is proven.
5. When one issue owns a shared surface that another issue touches only by reference, state that ownership boundary in both plans so overnight workers do not race on the same file or semantic decision.
6. Use adversarial review to convert vague cleanup themes into frozen decisions, testable acceptance criteria, and bounded no-download smoke checks before moving issues to `status:plan-review`.
7. `status:plan-review` means the issue is ready for human approval, not overnight execution. Only move into long-running/overnight implementation batches after explicit user approval and `status:plan-approved`.

## Approval-candidate audit rule

When asked whether there are issue plans to approve, do not rely on `status:plan-review` labels alone.
Audit all of these before saying a plan is approval-ready:
1. live GitHub issue state and labels (`gh issue list/view`)
2. canonical plan file under `docs/plans/`
3. the plan header/status line and `Adversarial Review Summary`
4. durable review artifacts under `scripts/review/results/`
5. whether any reviewer verdict is `MAJOR`, `FAIL`, `UNAVAILABLE`, or still `pending`
6. whether the plan itself says a fresh re-review is required

Operational pattern:
```bash
gh issue list --repo OWNER/REPO --state open --label 'status:plan-review' --json number,title,url,labels,updatedAt
find docs/plans -maxdepth 1 -type f -name '*issue-NNN-*' -o -name '*NNN*.md'
find scripts/review/results -maxdepth 1 -type f -name '*plan-NNN-*.md'
```

Classification:
- **approval candidate now**: plan exists, review artifacts exist, latest valid verdicts are only APPROVE/MINOR, and the plan does not require another review pass.
- **approval-prep priority**: high-value issue, but missing review artifacts, stale plan status, or a fresh re-review is required.
- **not approval-ready**: any current or latest-valid `MAJOR`, `FAIL`, unresolved blocker, missing required provider evidence, or pending review slot.

If none are approval-ready, answer that directly and list the best approval-prep targets rather than presenting stale `status:plan-review` issues as ready.

## Post-approval implementation-state audit

When the user asks for the current blocker/status of an already-approved issue, do not stop at plan artifacts and labels.

Audit all of these before summarizing status:
1. live GitHub issue labels/state
2. local plan row in `docs/plans/README.md`
3. open PRs referencing the issue (`gh pr list/view`)
4. whether the planned implementation files actually exist on `main`
5. CI / check status on the implementation PR

Operational rules:
- `status:plan-approved` does not mean the work is implemented or merge-ready.
- If the issue comment claims implementation shipped but the planned files are missing on `main`, classify the state as implemented off-main / pending PR resolution, not complete.
- If the local README row still says `plan-review` but the live issue is `status:plan-approved` and work moved into a PR, update the README row to reflect the newer live state.
- If the implementation exists only on a branch/PR and checks are failing, the blocker is PR/CI failure, not plan revision.
- For honest status reporting, explicitly separate:
  - plan state
  - implementation branch/PR state
  - merged-to-main state

This prevents stale local planning metadata from masking the real current blocker on approved issues.

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

Approval-state drift checklist learned from live use:
- verify all three surfaces before treating an issue as execution-ready:
  - live GitHub `status:*` label(s)
  - canonical local plan file under `docs/plans/`
  - local approval marker `.planning/plan-approved/NNN.md`
- if GitHub says `status:plan-approved` but either the canonical plan file or local approval marker is missing, classify the state as **governance drift**, not true approval
- repair the local artifacts first, then reconcile labels/comments; do not let the live label short-circuit the planning gate
- when the user asks for manual review/approval links, provide the exact review surfaces explicitly:
  - GitHub issue URL
  - canonical plan URL/path
  - exact CLI label-flip command
  - required local approval-marker path
- if the issue body points at a stale implementation path, call out the real repo path in the plan before review so approval is anchored to the actual file surface

This recovery pattern is especially important for harness/operations issues that were approved conversationally before the repo plan discipline was enforced, and for cases where GitHub label state drifted ahead of the repo-tracked approval evidence.

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
