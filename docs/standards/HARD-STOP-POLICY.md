# Hard-Stop Policy — Mandatory User Review Gates

## Implementation authority

The task request or standing authority authorizes implementation, including substantial work; no separate user plan approval, approval label or local marker is required. Complete planning, TDD and adversarial review, and resolve required domain decisions and blocking findings. Honor explicit planning-only requests. Consequential actions outside existing authority require matching explicit authorization. Implementation authority alone does not authorize publication, deployment, access changes or destructive actions; verify action/destination authority and reuse it when already provided.

> Issue: #1839 | Date: 2026-04-05
> Status: ACTIVE — all agents must follow this policy

---

## Scope

This policy applies to **engineering-critical issues** — issues labeled `cat:engineering`, `cat:engineering-calculations`, `cat:engineering-methodology`, or `cat:data-pipeline`.

These are the issues where incorrect implementation directly impacts:
- GTM demo reports shipped to prospects
- Client-facing calculations (OrcaFlex, DNV, API 579, cathodic protection)
- Data pipelines that feed client deliverables

All other issues (documentation, harness, infrastructure, career, ci, maintenance) proceed without these gates unless the user explicitly requests them.

## Detection

An issue is engineering-critical if ANY of these are true:
1. Label includes `cat:engineering`, `cat:engineering-calculations`, `cat:engineering-methodology`, or `cat:data-pipeline`
2. The issue touches engineering calculation code (`digitalmodel/`, `worldenergydata/`, `assetutilities/`)
3. The issue involves offshore engineering standards (DNV, API, ABS, ISO)

## The Rule

Engineering-critical issues MUST pass through these gates in order:

```
1. ISSUE SELECTED
   Agent picks an issue to work on

2. PLAN WRITTEN
   Agent writes a plan: what will be built, what files change, what tests

3. ADVERSARIAL PLAN REVIEW AND SCOPE CHECK
   Resolve blocking review findings and required domain decisions.
   The task request authorizes implementation; no separate plan approval is required.
   Honor planning-only scope and separately authorize consequential actions outside task authority.

4. IMPLEMENTATION
   Agent implements the approved plan. TDD where applicable.

5. ADVERSARIAL CROSS-REVIEW
   Route to Codex + Gemini for independent review.
   They review implementation against the approved plan.

6. CLOSE
   Issue closed with commit reference.
```

## Why This Order

- If the plan is wrong, implementing it wastes tokens and time
- Cross-review against a bad plan catches bugs in the wrong thing
- User approval at the plan stage is the highest-leverage gate
- Implementation confidence comes from a validated plan, not from post-hoc review

## What Counts as a Plan

A plan MUST include:

1. **What**: one-sentence summary of the deliverable
2. **Files**: which files will be created, modified, or deleted
3. **Tests**: what tests will be written (if applicable)
4. **Acceptance criteria**: how to verify it worked
5. **Risk**: anything that could go wrong

A plan can be:
- A GitHub issue comment (preferred — visible to all agents)
- A message in the chat session (minimum — for quick wins)
- A PLAN.md file in .planning/phases/ (for GSD workflow)

## What Does NOT Count

- Jumping straight to implementation
- A vague "I'll create a script that does X"
- Implementation code with a plan comment after the fact

## Enforcement

### For Interactive Sessions (user present)
- Agent records the reviewed plan and continues within task authority; ask only for a necessary domain decision or action outside scope
- If the user requests implementation, the agent writes and reviews the plan, then continues within that task authority without a separate approval request

### For Overnight/Batch Sessions (user absent)
- Plan must be written as a GitHub issue comment BEFORE implementation
- Implementation starts only after the plan comment is posted
- Cross-review runs against the plan + implementation together
- User reviews results the next morning

### For Quick Wins (< 15 minutes)
- Plan can be a brief chat message: "I'll do X by changing Y, test with Z"
- Task/standing authority covers bounded implementation after planning/review; no separate approval is required
- Cross-review can be waived for trivial changes (docs, config, formatting)

## Non-Critical Issues

For issues WITHOUT engineering-critical labels:

- No mandatory plan review required
- No mandatory cross-review required
- Agent may proceed directly to implementation
- TDD mandatory — tests before implementation
- User can request review gates by comment

## Bypasses (Engineering-Critical)

The only legitimate bypasses:
1. **Emergency fix**: client impact is active, fix now, review later (must log bypass)
2. **User explicitly waives**: "skip the plan, just implement" (logged)
3. **Pure configuration change**: no engineering logic changes (auto-detected)

All bypasses are logged to `logs/hooks/plan-gate-bypass.jsonl`.

## Relationship to Cross-Review

Cross-review (Codex + Gemini adversarial review) happens AFTER implementation.
The cross-reviewers receive BOTH the approved plan AND the implementation diff.
Their job is to verify the implementation matches the plan and is correct.

Cross-review does NOT replace plan review. They are different gates:
- Plan review: "Is this the right thing to build?"
- Cross-review: "Was the right thing built correctly?"
