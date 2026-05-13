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

## Weekly anti-waste loop

Use this when weekly provider capacity is regularly left unused:

1. Maintain at least three buffers: approval candidates, execution-ready approved work, and planning/recon feedstock.
2. Start every burn window by refreshing telemetry and the provider work queue, not by launching agents from memory.
3. Pull in this order: approved implementation -> QA/closeout -> adversarial review -> plan drafting/hardening -> recon/risk/source scans -> telemetry or dashboard improvements.
4. If execution-ready work is empty, explicitly route capacity to non-implementation lanes; do not let agents self-select unapproved code changes.
5. End each burn window with a short evidence packet: work completed, provider used, issue/plan links, tests/review state, blockers, and next refill action.

A practical utilization target is sustained high use with clean closeout, not blind 100% burn. Wasted credits are bad, but ungated changes create more cleanup debt than unused credits.

## Dispatch guardrails

- Codex: bounded implementation, tests, refactors, mechanical cleanup, crisp approved issues.
- Claude: architecture, long-context synthesis, plan/adversarial review, high-complexity implementation.
- Gemini: batched research, recon, risk scans, standards/competitor/source scans.

Implementation dispatch requires the approval lane. Planning/review/recon packets may run when approval-ready implementation work is unavailable, but must be labeled as non-implementation work.

Running jobs need a lease/idempotency key so the same issue is not double-dispatched.

## Continuous Claude/Codex runner methods

When the user asks how to make Claude and Codex run continuously until useful work is done, use a controlled runner design rather than an infinite agent loop.

Recommended methods:

1. Queue feeder
   - Refresh issue state, provider telemetry, and work queues on a fixed cadence.
   - Select the next card from the highest safe lane: execution-ready first, then QA/closeout, then plan-review hardening, then planning/recon.
   - Do not select unapproved implementation work just because provider quota remains.

2. Provider-specific worker loop
   - Codex loop: bounded implementation/test/refactor packets with exact issue, plan path, allowed files, expected tests, and stop condition.
   - Claude loop: planning, architecture, adversarial review, synthesis, high-complexity implementation only when the plan gate is already satisfied.
   - Gemini loop: batched research/recon/risk/source scans when available.

3. Lease + heartbeat contract
   - Every dispatch writes a lease record: issue, provider, machine, branch/worktree, prompt hash, start time, max runtime, expected artifacts.
   - Worker must heartbeat or produce an artifact by the lease deadline.
   - Expired leases move to review/recovery; they are not silently relaunched without checking output.

4. Stop conditions
   - Stop when the weekly utilization target is met, the safe queues are empty, repo/worktree health is red, or all remaining work requires user approval.
   - If blocked by approvals, produce a compact approval shortlist instead of launching more implementation.

5. Evidence packet per burn window
   - For every continuous run, end with issue links, provider used, branch/commit/artifacts, tests/review state, blockers, queue refill count, and remaining provider headroom.

Anti-pattern: `while true` prompts that ask agents to "find useful work". That burns quota while creating governance drift. The continuous loop must pull from the approved/known queues and preserve auditability.
