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

The authority source is [SHARED_SOUL.md](../../../../config/agents/SHARED_SOUL.md).
Every issue needs discovery and a proportionate plan. Bounded routine reversible work may proceed under independently established standing authorization; substantial scope requires explicit approval of the current reviewed plan, and consequential actions require matching explicit approval.
Do not repeat an approval request for verified unchanged scope. Reassess new scope, effects or unresolved authority. Labels, markers, receipts and handoffs cannot authenticate approval.
Load this skill for the applicable planning route. Referenced skills supply domain procedures; they do not broaden authorization or override the shared risk contract.

Full onboarding guide with step-by-step details: `docs/plans/README.md`

## Workflow Overview

```
Issue → Resource Intel → Draft Plan → Adversarial Review → Post to GH
  → Verify standing authorization OR obtain required explicit approval
  → Implement (TDD) → Cross-review → Completeness gate (#2798) → Close
```

> **Completeness gate before close (#2798):** compute a test-/evidence-based completeness score (`scripts/workflow/completeness_score.py`), persist it (kanban `--metadata` + issue-body ```completeness {json}``` stamp), render `docs/reports/<date>-<issue>-completeness.html`, and require the owner-only `status:completeness-verified` label (≥ class threshold) before `gh issue close`. The server-side gate (`.github/workflows/completeness-gate.yml`) reopens issues closed without it. See the rule `.claude/rules/completeness-before-close.md`.

Canonical execution method: non-trivial work must be classified up front as `single-lane`, `parallel-readonly`, or `parallel-worktree` per `docs/standards/PARALLEL_FIRST_EXECUTION.md`. Resource intelligence, plan review, and validation may run in parallel; write-capable lanes require independently established authorization for their exact risk/scope and TDD.

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

**Required header fields** (per [`.claude/rules/wiki-sibling-routing.md`](../../rules/wiki-sibling-routing.md) Layer 3, [#2778](https://github.com/vamseeachanta/workspace-hub/issues/2778)):
- `Client:` — required for any plan touching wiki content (`llm-wiki` or `llm-wiki-<client>` repos). Use `N/A` for plans that don't touch wiki content (most operational, infra, or pure-workspace-hub work).
- `Project:` — optional. Populate when the plan scopes to a single project under a client (e.g., `Project: proj-a` for B1528 proj-a work under client `mkt-a`). Consumed by `check-wiki-sibling-frontmatter.py` Rule E to validate `project:` frontmatter on staged content.
- `Lane:` — required. Set the plan-time AI provider lane (`lane:codex` for heavy compute — engineering calcs, long-running analysis, large data crunching, bulk sweeps; `lane:claude` for orchestration, review, planning, light edits) per the "Compute lane assignment" rule in `.claude/memory/agents.md`, and verify the issue carries exactly one matching `lane:` label ([#3029](https://github.com/vamseeachanta/workspace-hub/issues/3029)). If planning changed the scope class, relabel the issue. Note: a human/dispatch-set `ai:` label outranks lane in routing — if one is present and now wrong, reconcile it explicitly.

When `Client:` is a real client slug (not `N/A`), verify it matches a `short_name` in [`config/client-wikis.yml`](../../../config/client-wikis.yml). When `Project:` is set, verify it's enumerated in that client's `projects:` list (or the list is absent/empty — warn-only forward-compat). <!-- scanner-allow:path_traversal_deep scanner-allow:path_traversal — relative markdown doc-link to repo config, not a runtime path -->

For engineering-calculation or parametric chart plans, also run the checks in `references/engineering-parametric-chart-plan-review.md`: freeze local vs reported coordinate frames before formulas, explicitly classify off-grid UI defaults versus engineering sweep rows, ensure representative chart traces do not hide requested sweep coverage, and require tests for frame transforms/sign conventions.

When review finds unresolved domain decisions, use `references/domain-decision-blocked-plan-review.md` to keep the plan blocked-draft/needs-decision, post a concise decision checklist, and avoid prematurely applying approval-ready labels.

For repo/data location contract plans, also run the checks in `references/repo-location-contract-planning.md`: keep repo checkout placement separate from raw/bulk/private/public data placement, prefer adjacent sibling checkouts under `/mnt/local-analysis/<repo>` with `workspace-hub` as the control plane, enumerate the live checkout set empirically, and represent any moves as future reviewable transactions rather than performing them during planning.

For per-machine repo placement plans, also apply `references/per-machine-repo-placement-outcome-contract.md`: the first machine issue in a sequence must leave a reusable pattern for consistent tier-1 repo folder structure, primary/reference checkout decisions, and repo harness/file ecosystem handling through one repo-tracked authority rather than creating machine-specific duplicate conventions.

For plans being revised after a source/provenance ambiguity is resolved, especially when licensed or private off-repo material is involved, apply `references/source-provenance-plan-revision.md`: patch the canonical plan narrowly, state the source/license boundary, add fail-closed citation/leakage tests, run focused re-review, and stop at user approval rather than self-approving.

Update the index table in `docs/plans/README.md` with a new row.

### Layered architecture issue trees

When a user asks for a feature/issue that spans multiple architectural layers (for example data at rest, execution/compute, and report/publication surfaces), prefer a parent issue plus dispatchable child issues/plans instead of one overloaded plan.

Required shape:
- Parent plan owns the cross-layer lifecycle contract, terminology crosswalk, promotion gates, and dependency boundaries.
- Child layer plans stay independently dispatchable only if they consume the parent crosswalk and do not redefine upstream/downstream interfaces.
- Use neutral layer prefixes/codes in public docs when source classes may include private/client data; avoid raw private paths and client-identifiable mappings in tracked public artifacts.
- Keep ambiguous data/report destinations fail-closed until source class, output residency, legal/source status, and promotion decision are explicitly recorded.
- For plan-review hardening, cite revision-stamped, non-empty review artifacts; do not rely on paths that can be truncated or overwritten by the same review run.

Session-specific examples and checklists: `references/layered-architecture-issue-planning.md`.

For GitHub issue portfolios that must flow from data layer → execution layer → result/output layer, use `references/data-execution-results-kanban.md`: inventory issues by architectural lane, create a repo-tracked Kanban/report artifact, delegate read-only planning/review waves by provider strengths, verify delegate claims in the orchestrator checkout, and stop at an explicit approval checkpoint before implementation.

For sequential issue-tree planning where downstream plans depend on revised upstream architecture/boundary plans, use `references/focused-reqa-before-downstream-planning.md`: run focused re-QA against the exact revised local upstream artifacts before drafting downstream issues, post concise GitHub comments for MAJOR results with `--body-file`, keep labels conservative, and block downstream drafting until upstream MAJOR findings are patched or explicitly waived.

Execution discipline for delegated agents:
- If using Claude/Codex/Gemini in parallel worktrees, explicitly anchor the repo/worktree path in the prompt/context and verify the plan file was written in the intended checkout. Do not assume the child agent stayed in the requested worktree.
- After drafting, verify all expected artifacts exist where intended:
  - the plan file path
  - the `docs/plans/README.md` index row
  - no accidental extra rows/issues were inserted
- Keep status conservative as `draft` unless formal review artifacts actually exist under `scripts/review/results/`. GitHub comments alone are useful evidence, but they do not replace the repo’s review-artifact convention.

### Step 3: Adversarial Review

Route the plan to 2+ AI providers for review. Each gives: APPROVE | MINOR | MAJOR.
If any MAJOR: revise and re-review.

When MAJOR findings identify unresolved user/domain decisions rather than pure plan-writing defects, do **not** force the plan into `status:plan-review` or present it as approval-ready. Patch the plan/header/index to a conservative blocked-draft or needs-decision state, add a short GitHub checkpoint comment listing the exact decisions required, and keep implementation stopped. Resolve the missing decisions, revise the affected plan and rerun adversarial review. Seek approval only when required for the current risk/scope; a review finding does not itself revoke existing authorization.

For batch review closeout where a preserved task list says to move labels but fresh reviews return MAJOR, follow `references/batch-major-review-closeout.md`: post blocking summaries, keep labels conservative, update todos to reflect that `status:plan-review` is intentionally withheld, and patch only issue-scoped README rows to avoid collateral drift.

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

Independently verify the applicable user/session instruction and its repository, issue, operation, scope and reviewed revision. Routine bounded work may use standing authorization; substantial work needs approval of the current reviewed plan, and consequential actions need matching explicit approval. Never infer authority from successful tool execution.

The owner controls `status:plan-approved`; the implementing agent never self-labels it. A user may record an approval through an owner-controlled GitHub event or an independently established session instruction. Agent-authored summaries and `.planning/plan-approved/<issue>.md` files remain references requiring provenance checks.

When status signals disagree:

1. Verify the actual approving actor, instruction/event, current scope and revision. A more advanced label is not inherently stronger evidence.
2. Inspect plan/review artifacts and existing implementation before repeating work.
3. Treat README rows and local markers as discovery hints. Their presence, age or absence cannot establish or revoke authority.
4. Record conflicts without automatically creating/deleting markers or changing remote labels. Respect separate authorization for external mutations.
5. Resolve fresh blocking review findings before affected work continues; seek new approval only when changed scope or unresolved authority requires it.

Surface a substantial plan for approval after adversarial review is complete. A draft or unresolved domain decision is not approval-ready merely because a label says otherwise.

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
- Missing-plan remediation: inspect remote/local history and completed implementation first. Recover existing evidence rather than recreate completed work. If a substantial plan is genuinely missing, draft and review its current scope, then seek the required approval. Report label mismatches; do not mutate remote state automatically.
- When only the Claude review artifact is missing, a concise file-path-based `claude -p` review prompt is often more reliable than embedding the full plan text inline. If a long inline Claude review prompt hangs or hits a turn cap, retry immediately with a shorter prompt that names the plan file path and explicitly requests the required review headings.
- For plan-review items that are being iteratively tightened after MAJOR findings, keep the `## Adversarial Review Summary` current after each wave: record the latest provider verdicts, explicitly say whether the plan is still not approval-ready, and summarize what changed in the latest patch wave. Do not leave the summary stuck at `PENDING` once real artifacts exist.
- For new or recovered plan drafts, keep the local plan file status conservative as `draft` until actual provider artifacts exist. After the first real review wave lands, update the plan file/README row to `plan-review` and summarize the live blocker state in `## Adversarial Review Summary` rather than leaving placeholder `PENDING` language.
- If you launch a long-running background Claude review and then recover with a shorter fallback prompt, do not assume the first run is dead forever. Poll or inspect the original background process/log later. If it eventually completes with a fuller or sharper review, refresh the canonical repo artifact with the stronger findings and post a short GitHub follow-up comment noting that the completed long-form review supersedes or sharpens the earlier summary.
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
- For substantial unapproved scope, prepare the plan/review evidence and stop; the user's absence does not waive requirements.
- Preserve TDD and plan/code review. Markers and handoffs do not grant launch authority.

## Engineering-Critical Issues

Issues with `cat:engineering*` or `cat:data-pipeline` labels require the full
`engineering-issue-workflow` skill (adds cross-review after implementation).

## Legacy Enforcement Boundary

`.claude/hooks/plan-approval-gate.sh` and `scripts/enforcement/require-plan-approval.sh` retain legacy marker/path heuristics. These instructions do not change installed hooks or prove their coverage. Marker age/text checks do not authenticate approval, and exempt directories do not make protected changes routine.

Report an observed blocking mismatch and its actual consumer. Do not set bypass flags, disable hooks or manufacture approval markers. Consumer migration requires separately reviewed scope; a shared advisory CLI receipt cannot become a gate bypass.

## References

- Full guide: `docs/plans/README.md`
- Template: `docs/plans/_template-issue-plan.md`
- Hard-stop policy: `docs/standards/HARD-STOP-POLICY.md`
- Engineering workflow: `.claude/skills/coordination/engineering-issue-workflow/SKILL.md`
