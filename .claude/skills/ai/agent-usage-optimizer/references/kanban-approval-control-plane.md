# Kanban approval control plane for provider-credit utilization

Use this pattern when provider credits are being wasted because there is no ready queue or low-friction approval surface.

## Core principle

Continuous Claude/Codex/Gemini usage should mean a safe pull loop, not agents wandering through repos:

```text
refresh telemetry -> refresh Kanban/provider queue -> dispatch approved work -> monitor lease -> QA packet -> refill queue
```

If no implementation-ready issue exists, spend provider capacity on planning, adversarial review, reconnaissance, or risk enumeration instead of ungated implementation.

## Recommended lanes

1. Planning feedstock — open issues needing resource intelligence or plan drafting.
2. Plan review / approval candidates — canonical plan exists and review is complete or pending.
3. Execution-ready — `status:plan-approved` plus committed approval marker exists.
4. Running / leased — dispatched to a provider with owner, lease, machine, and expected artifact.
5. QA / closeout — output exists and needs tests, review, clean-state proof, and issue closeout.

## Approval dashboard rules

A dashboard/HTML surface may show hover summaries and buttons, but the button must trigger a real auditable transaction:

1. verify live GitHub issue is open;
2. verify canonical plan exists under `docs/plans/`;
3. verify latest review artifacts have no `MAJOR`, `FAIL`, `UNAVAILABLE`, or pending verdicts;
4. write or require `.planning/plan-approved/<issue>.md`;
5. update labels from `status:plan-review` to `status:plan-approved`;
6. add a GitHub comment with plan path, review summary, approval marker, and refreshed queue timestamp;
7. refresh provider work queue before dispatch.

Do not treat GitHub issue-body HTML as the dashboard. GitHub strips active HTML/JS; use a separate rendered dashboard or local web artifact.

## Hover summary fields

Each card should expose:
- issue number/title/url;
- current labels/lane;
- one-paragraph plan summary;
- risk/unknowns;
- expected tests or validation;
- proposed provider route and why;
- approval blocker if the button is disabled.

## Dispatch guardrails

- Codex: bounded implementation, tests, refactors, mechanical cleanup, crisp approved issues.
- Claude: architecture, long-context synthesis, plan/adversarial review, high-complexity implementation.
- Gemini: batched research, recon, risk scans, standards/competitor/source scans.

Implementation dispatch requires the approval lane. Planning/review/recon packets may run when approval-ready implementation work is unavailable, but must be labeled as non-implementation work.

Running jobs need a lease/idempotency key so the same issue is not double-dispatched.
