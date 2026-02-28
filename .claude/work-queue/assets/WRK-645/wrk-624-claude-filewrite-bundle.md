# Claude Compact Plan Review Bundle

Source: `specs/wrk/WRK-624/plan.md`
Plan Title: WRK-624 Canonical Workflow Hardening

## Plan Metadata
- Title: WRK-624 Canonical Workflow Hardening
- Description: Route C plan/spec for the canonical 8-stage work-item lifecycle, review matrix, closure enforcement, and ecosystem learning loop.
- Priority: high
- Complexity: critical
- Status: implemented
- Phase: 3
- Timeline: phased rollout

## Reviewer Instructions
Focus on completeness, feasibility, dependency clarity, migration risk, testing depth, and machine-enforceable gates.
Treat this as a compact proxy for the full plan. If a risk appears underspecified due to truncation, call that out explicitly.

## Executive Summary
This plan converts the work-queue process from a loose set of scripts and conventions into a canonical lifecycle contract. The contract starts with WRK-624 and then rolls forward to all new or touched WRKs, while older backlog items are normalized in phases instead of through a disruptive one-shot migration.

The new model adds a mandatory `Resource Intelligence` stage, standardized review evidence, an explicit orchestrator field, example- and variation-based quality validation, active session binding, and a strict close/archive gate. It also treats work items as learning units: each WRK must produce real examples, variation tests, review evidence, future-work capture, direct ecosystem learnings where appropriate, and compatibility with both fast session-memory capture and deeper scheduled learning synthesis.

## Review Matrix
| Route | Review Level | Required Reviewers | Required Artifacts | Escalation |
|---|---|---|---|---|
| A | lightweight | 1 | `review-primary.md` | auto-escalate to 3-model review on risk signals |
| B | standard | 3 | `review-claude.md`, `review-codex.md`, `review-gemini.md`, `review-synthesis.md` | n/a |
| C | full | 3 per plan, phase, and final close | same as Route B per phase | n/a |

### Route A lightweight review acceptance criteria
1. Reviewer artifact exists.
2. Verdict is `APPROVE` or `MINOR`.
3. Acceptance criteria were explicitly checked.
4. Relevant tests/checks were run and recorded.
5. No unresolved `MAJOR` finding remains.
6. Close evidence exists before move to `done`.

### Route B/C review rules
- Claude, Codex, and Gemini are all required.
- Gemini runs in deepest-thinking mode.
- `review-synthesis.md` is mandatory.
- All three agent review artifacts must use the same interpretable review format so other agents and validators can consume them without provider-specific parsing.

[truncated for Claude compact bundle]

## Phased Rollout
### Phase 1: Normalize and report
- start: February 27, 2026
- target completion: March 7, 2026
- owner: workspace-hub orchestrator / WRK-624 execution owner
- migrate legacy statuses
- add reporting validator
- reconcile folder/status drift
- rename malformed WRK filenames
- repair queue/index/session-state inconsistencies
- auto-fix mismatches that are mechanically unambiguous
- emit manual-remediation list for stale, blocked, or ambiguous legacy WRKs
- rollback path: restore queue metadata from git before enabling hard-fail enforcement
- success metrics:
  - zero invalid legacy status values remain
  - zero folder/status mismatches remain in `done/` and `archive/`
  - all ambiguous cases are listed in a manual-remediation report

### Phase 2: Require new artifacts
- start: March 8, 2026
- target completion: March 21, 2026
- require resource packs for all new WRKs and any legacy WRK when touched
- require close evidence and reviewer artifact normalization
- require legal scan on generated artifacts
- require HTML review artifacts for every WRK
- require draft-plan HTML review evidence before multi-agent review
- require final-plan HTML review evidence before execution

[truncated for Claude compact bundle]

## Testing Strategy
- transition tests:
  - capture -> plan draft -> multi-agent review -> claim -> execute -> close -> archive
- validator tests:
  - folder/status mismatch detection
  - missing artifact detection
  - legacy status migration detection
- idempotency tests:
  - rerun close/archive/validator operations safely
- concurrency tests:
  - conflicting claim attempts
  - stale session ownership recovery
- outage tests:
  - reviewer `NO_OUTPUT`
  - reviewer `INVALID_OUTPUT`
  - quota snapshot unavailable
  - legal/doc-index/html verification tool failure
- migration tests:
  - malformed historical filenames
  - `complete/completed/closed` status migration
  - dormant vs touched legacy WRKs
- HTML gate tests:
  - draft-plan review required before multi-agent review
  - final-plan review required before execution
  - close blocked on missing final HTML verification

## Acceptance Criteria
- 3 review artifacts exist for the current plan revision, or fallback policy is explicitly invoked for `NO_OUTPUT`.
- Each review artifact conforms to the shared interpretable schema with the required sections.
- One synthesis artifact records final verdict and unresolved findings count.
- Mermaid renders the planning HTML review gates, claim routing gate, and archive gate.
- WRK metadata schema includes:
  - `plan_html_review_draft_ref`
  - `plan_html_review_final_ref`
  - `claim_routing_ref`
  - `claim_quota_snapshot_ref`
  - `claim_recommendation`
- Migration matrix is documented with:
  - start date
  - target completion
  - hard-fail cutoff
  - rollback path
  - success metrics
- Dependency contract table exists and names the source of truth and blocking behavior for each gate input.
- Testing strategy covers transitions, idempotency, concurrency, outages, migration, and HTML gates.
- HTML review artifact exists for this WRK and includes an executive summary near the top.
