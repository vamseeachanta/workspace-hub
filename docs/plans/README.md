# Issue Planning Workflow — Onboarding Guide and Plan Index

This document is the single onboarding reference for the mandatory issue planning workflow.
All agents (Claude, Codex, Gemini, Hermes) must follow this workflow for every GitHub issue.

## Why Planning Is Mandatory

Historical data shows that agents skipping the planning step produced incorrect implementations, wasted tokens, and created rework. The planning workflow catches problems before implementation begins, when they are cheapest to fix.

- **Plan review** answers: "Is this the right thing to build?"
- **Cross-review** answers: "Was the right thing built correctly?"

Both are required. Neither replaces the other.

## The Workflow (Step by Step)

```
1. INTAKE           — Read issue, classify complexity (T1/T2/T3)
2. RESOURCE INTEL   — Search existing code, standards, documents, prior plans
3. DRAFT PLAN       — Copy template, fill all sections, save to docs/plans/
4. ADVERSARIAL REVIEW — Route to 2+ AI providers; revise if MAJOR verdict
5. POST TO GITHUB   — Comment plan on issue, label status:plan-review
6. HARD STOP        — Wait for user approval (never self-approve)
7. USER APPROVES    — Swap label to status:plan-approved
8. IMPLEMENT        — TDD: tests first, then code, then full suite
9. CLOSE            — Commit, push, post summary, close issue
```

### Step 1: Intake

- Read the full issue body — scope, acceptance criteria, references
- Classify complexity:
  - **T1** (trivial): config, typo, single-file fix — brief plan, still requires approval
  - **T2** (standard): new module, multiple files, tests — full workflow
  - **T3** (complex): multi-module, architecture, standards — full workflow + subagents

### Step 2: Resource Intelligence

Before writing anything, search all available sources:
- **Existing code**: search relevant repos for prior implementations
- **Standards**: `data/document-index/standards-transfer-ledger.yaml` (425 standards)
- **Documents**: `data/document-index/online-resource-registry.yaml` (247 entries)
- **Prior plans**: `docs/plans/` directory and this index

### Step 3: Draft Plan

1. Copy the template: `docs/plans/_template-issue-plan.md`
2. Save as: `docs/plans/YYYY-MM-DD-issue-NNN-slug.md`
3. Fill all required sections (see "Required Sections" below)
4. Add a row to the Index table in this file

### Step 4: Adversarial Review

Route the plan to at least 2 other AI providers. Each gives a verdict:
- **APPROVE** — plan is sound
- **MINOR** — small issues, can proceed after fixing
- **MAJOR** — significant issues, must revise and re-review

Save review artifacts to `scripts/review/results/YYYY-MM-DD-plan-NNN-<agent>.md`.

### Step 5: Post and Label

1. Post the completed plan as a GitHub issue comment
2. Apply label: `gh issue edit NNN --add-label "status:plan-review"`
3. **STOP** — do NOT write any implementation code

### Step 6: User Approval

The user (never the implementing agent) approves the plan:
- `gh issue edit NNN --remove-label "status:plan-review" --add-label "status:plan-approved"`
- Creates marker: `.planning/plan-approved/NNN.md`

### Step 7: Implement (TDD)

Only after `status:plan-approved` label exists:
1. Write tests first — confirm they fail
2. Implement minimum code to pass tests
3. Run full test suite — confirm no regressions
4. Self-review against approved plan

### Step 8: Close

- Conventional commit referencing the issue number
- Push to remote
- Post summary comment on issue: what was done, test results, review verdicts
- Close the issue

## Batch / Overnight Sessions

When the user is not present:
- Draft plans and label `status:plan-review` — do NOT implement
- Only implement issues already labeled `status:plan-approved`
- User reviews results the next morning

## Status Meanings

| Status | Meaning |
|---|---|
| draft | Plan file exists locally but has not yet completed adversarial review |
| adversarial-reviewed | Frontier-model review passed; ready to post for user review |
| plan-review | Posted to GitHub; waiting for user approval |
| plan-approved | User approved; ready for implementation or batch execution |
| superseded | Replaced by a newer version of the plan |
| completed | Issue implemented and closed |

## Required Sections in Each Plan

Every plan file must include (see `_template-issue-plan.md` for full format):

1. **Resource Intelligence Summary** — what exists, what is missing
2. **Artifact Map** — paths to plan, tests, implementation, review files
3. **Deliverable** — one sentence: what will exist after this issue is done
4. **Pseudocode** — 5-15 lines per function (T2/T3); "trivial" note for T1
5. **Files to Change** — action, path, reason for each file
6. **TDD Test List** — one row per test with name, verification, input, output
7. **Acceptance Criteria** — checkboxes for all verification steps
8. **Adversarial Review Summary** — provider, verdict, key findings
9. **Risks and Open Questions** — what could go wrong, what needs user input
10. **Complexity** — T1, T2, or T3 with justification

## Enforcement

- **PreToolUse hook**: `.claude/hooks/plan-approval-gate.sh` blocks writes without approval marker
- **Pre-commit hook**: `scripts/enforcement/require-plan-approval.sh --strict` blocks commits without approval
- **Labels**: `status:plan-review` (orange) and `status:plan-approved` (green) exist on the repo

## Key References

| Resource | Path |
|---|---|
| Plan template | `docs/plans/_template-issue-plan.md` |
| Planning skill | `.claude/skills/coordination/issue-planning-mode/SKILL.md` |
| Engineering workflow | `.claude/skills/coordination/engineering-issue-workflow/SKILL.md` |
| Hard-stop policy | `docs/standards/HARD-STOP-POLICY.md` |
| Review artifacts | `scripts/review/results/` |

---

## Plan Index

| Issue # | Title / Slug | Plan File | Date | Status | Complexity | Notes |
|---|---|---|---|---|---|---|
| 1963 | email-infrastructure-cluster-a | `docs/plans/2026-04-09-issue-1963-email-infrastructure-cluster-a.md` | 2026-04-09 | draft | T3 | Cluster A architecture plan anchored by #1963 |
| 2045 | agent-planning-onboarding | `docs/plans/2026-04-09-issue-2045-agent-planning-onboarding.md` | 2026-04-09 | plan-approved | T2 | Onboard all agents to strict planning workflow |
| 2046 | planning-compliance-audit | `docs/plans/2026-04-09-issue-2046-planning-compliance-audit.md` | 2026-04-09 | draft | T2 | Audit agent compliance with planning workflow |
| 2047 | planning-enforcement-escalation | `docs/plans/2026-04-09-issue-2047-planning-enforcement-escalation.md` | 2026-04-09 | draft | T2 | Stronger enforcement if audit fails; depends on #2046 |
| 2127 | make-plan-approval-gate-honor-force-plan-gate-strict-and-disable-enforcement | `docs/plans/2026-04-11-issue-2127-make-plan-approval-gate-honor-force-plan-gate-strict-and-disable-enforcement.md` | 2026-04-11 | draft | T2 | Runtime plan gate ignores documented enforcement env contract; plan covers hook, tests, and governance docs |
| 2128 | install-hooks-pre-push-chain-drift | `docs/plans/2026-04-11-issue-2128-install-hooks-pre-push-chain-drift.md` | 2026-04-11 | draft | T2 | Wire enforcement-env and require-review-on-push into install-hooks pre-push chain; fix dead-code drift guard |
| 2205 | multi-machine-llm-wiki-resource-doc-intelligence-operating-model | `docs/plans/2026-04-11-issue-2205-multi-machine-llm-wiki-resource-doc-intelligence-operating-model.md` | 2026-04-11 | draft | T3 | Parent operating-model plan defining pyramid, information flow, and child issue tree for llm-wikis + resource/document intelligence |

## Entry Format

Add one row per plan:

```
| 1234 | short-slug | `docs/plans/2026-04-08-issue-1234-short-slug.md` | 2026-04-08 | plan-review | T2 | notes |
```

## Notes for Agents

- All plans go in `docs/plans/` — never in `.hermes/plans/` or `.planning/phases/`
- Keep this README updated whenever a new plan is created or its status changes
- Batch execution agents must only act on issues marked `status:plan-approved`
- If a plan is revised materially, update the row and mark the older version `superseded`
- Never self-approve a plan — the user or a designated operator must approve
