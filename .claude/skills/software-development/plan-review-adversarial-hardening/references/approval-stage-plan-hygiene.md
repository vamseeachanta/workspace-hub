# Archived Skill: `approval-stage-plan-hygiene`

Original path: `/home/vamsee/.hermes/skills/software-development/approval-stage-plan-hygiene`
Archived into: `/home/vamsee/.hermes/skills/.archive/umbrella-2026-04-29/software-development/approval-stage-plan-hygiene`
Consolidation date: 2026-04-29

---

---
name: approval-stage-plan-hygiene
description: Prevent approval-stage adversarial review churn by keeping plans implementation-focused, schema-complete, and free of stale review-process narration.
version: 1.0.0
tags: [planning, adversarial-review, github, governance, schema, approval]
---

# Approval-Stage Plan Hygiene

Use when drafting or revising a GitHub issue plan that will go through adversarial plan review.

## When to use
- A plan keeps getting MAJOR findings even after multiple rewrites
- Reviewers complain about stale review-state language, empty review artifacts, or vague test contracts
- The plan introduces a machine-checkable JSON/report contract
- The plan changes launcher/runtime behavior and reviewers want stronger proof than string replacement

## Core rules

1. Keep the plan body about the implementation contract only.
- Do not embed review-process narration like:
  - "this redraft fixes..."
  - "fresh rerun required"
  - "prepared for another approval pass"
  - "latest verdicts are ..."
- Review history belongs in review artifacts or issue comments, not in the plan contract.

2. Do not cite empty review artifacts as evidence.
- If a `scripts/review/results/...` file is empty or unavailable, do not mention it as supporting evidence in the plan.
- Treat review artifacts as external state, not plan content.

3. Remove approval-state/process language from acceptance criteria.
- Avoid acceptance items like:
  - "plan remains draft"
  - "after rerun this can advance to plan-review"
- Acceptance criteria should describe deliverable behavior or artifact state after implementation, not workflow-state transitions.

4. If the plan defines a machine-checkable schema, pin the full contract.
At minimum specify:
- canonical artifact path
- exact field names
- exact top-level JSON shape (for example provider-keyed object vs array of rows)
- allowed enum values
- nullability/omission rules
- first-run / no-history behavior
- malformed-history behavior
- missing-row / key-mismatch behavior
- which artifact is the single source of truth vs derived renderings

Important learned pattern from repeated #2332 reruns:
- reviewers will keep returning MAJOR if the plan says a schema is canonical but does not say whether provider-specific keys must be omitted or present as `null` on other providers
- if a plan introduces multiple non-baseline states (for example `no_prior_audit`, `prior_snapshot_unreadable`, `provider_missing_from_prior_snapshot`), define the full state table in one place, including the resulting compliance/status fields for each branch
- do not spread the same contract across plural wording like "JSON/scorecard outputs"; choose one canonical machine-checked artifact and describe other outputs as derived renderings

5. Tests must prove behavior, not just rendering.
- Add schema-completeness tests, not only "contains these fields" prose checks.
- Add exact branch tests for normal, first-run, malformed-history, missing-row, over-cap, under-cap, etc.
- For launcher/runtime changes, include one behavior-preservation test that exercises the actual call path or an injected runner for that call path, not only a grep/string replacement test.
- For wrapper/launcher rewrites, command-capture checks should preserve the full subprocess contract where relevant: argv tail, cwd, key kwargs, and the fact that the real function reaches the rewritten call site.
- If only one file gets a true end-to-end smoke and the others only get imports or object construction, reviewers may still return MAJOR because the rewritten launcher path itself was never exercised.

## Approval checklist
Before rerunning adversarial review, verify:
- No `Review artifacts:` metadata line if it would point to empty artifacts
- No `Adversarial Review Summary` section containing stale process text
- No acceptance criteria about re-review or status transitions
- If JSON/report contract exists, one canonical machine artifact is explicitly named
- First-run semantics are fully specified
- Behavior-preservation test exists for any runtime/launcher swap
- Resource-intelligence wording is implementation-focused, not reviewer-facing narration (avoid phrases like `approval-stage planning should`, `this redraft fixes`, `prepared for rerun`, `none blocking approval readiness`)
- State tables do not contradict cap tables or branch rules; if non-baseline branches exist, baseline/cap/compliance fields are defined once and reused consistently everywhere

## Additional learned guardrails from repeated #2332 review loops

6. Keep resource-intelligence sections factual and repo-grounded, not meta-commentary.
- Even when the facts are correct, reviewers may keep returning MAJOR if the plan reads like a review diary instead of an implementation contract.
- Prefer neutral statements like:
  - `X is the canonical generated artifact`
  - `Y is the first-wave target`
  - `Z is excluded from actionable debt`
- Avoid process-oriented phrasing like:
  - `approval-stage planning should...`
  - `this redraft fixes...`
  - `none blocking approval readiness`

7. For multi-branch schema contracts, define the state table in one place and make every other section conform to it.
- If you have branches such as:
  - `baseline_available`
  - `no_prior_audit`
  - `prior_snapshot_unreadable`
  - `provider_missing_from_prior_snapshot`
  then specify in one canonical block, for each branch:
  - baseline field value
  - delta field value
  - cap field value
  - compliance status
  - compliance reason
  - markdown/rendering expectation
- Then mirror that exact contract in tests. Reviewers will keep flagging MAJOR if one section says caps are fixed while another says they are reseeded/null.

8. If a repeated one-provider MAJOR persists after many tight reruns, stop the loop and escalate explicitly.
- After several focused reruns where one reviewer continues to object to increasingly narrow contract details, the next best move may be:
  - make the final policy choice explicitly
  - surface the issue link to the user
  - request human judgment instead of burning more cycles
- This is especially true when another strong reviewer consistently returns APPROVE and the remaining blocker has shrunk to a policy interpretation rather than broad plan unsoundness.

## Common MAJOR triggers this prevents
- "Plan still cites empty review artifacts"
- "Plan includes stale review-process narration"
- "Machine-checkable schema is underspecified"
- "First-run/no-history behavior is ambiguous"
- "Tests only prove string replacement, not real behavior"

## Outcome to aim for
A plan that reviewers can assess purely on current implementation intent, with no confusion from stale process metadata and no ambiguity in schema or runtime-contract behavior.
