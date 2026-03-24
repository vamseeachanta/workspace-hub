### Verdict: REQUEST_CHANGES

### Summary
WRK-624 establishes a well-intentioned 8-stage lifecycle framework with meaningful gate enforcement and a multi-route review matrix. However, the specification as presented is too abstract to be actionable: critical definitions (stage boundaries, risk criteria, authority resolution, failure/rollback handling, SLAs) are absent or deferred. The review matrix is inconsistent in reviewer counts, and migration/legacy coverage is flagged as a risk without any mitigation path. These gaps represent P1 blockers before the design can be approved or implemented safely.

### Issues Found
- [P1] The '8 stages' are referenced but only a partial subset is enumerated in the summary (plan HTML review, multi-agent review, claim, close, archive). The remaining stages are undefined, making lifecycle completeness unverifiable.
- [P1] Route A specifies '1 reviewer by default, escalate on risk' but no risk-scoring criteria, thresholds, or escalation authority are defined. This makes the escalation rule unenforceable and subjective.
- [P1] Authority conflict between validators and readiness signals is identified as a known risk but no resolution mechanism, tie-breaking rule, or override policy is provided.
- [P1] No rollback, failure, or timeout semantics are defined for any stage gate. If a gate check fails mid-lifecycle (e.g., claim-stage quota exhausted), there is no specified recovery path.
- [P2] Migration contract for legacy work items is described only as a 'complexity risk' with no concrete migration strategy, compatibility shim, or phased rollout plan.
- [P2] Close-gate 'queue validation and HTML verification' criteria are unspecified — pass/fail conditions, responsible party, and artifact retention requirements are all absent.
- [P2] The review matrix mandates a uniform artifact schema across Routes A/B/C, but no schema version, enforcement mechanism, or schema evolution policy is defined.
- [P3] Testing contracts are mentioned but no coverage targets, test types (unit, integration, end-to-end), or CI gate requirements are specified for lifecycle transitions.
- [P3] Workflow overhead risk for all WRKs is acknowledged but no cost-benefit analysis, opt-out path, or lightweight-route criteria are provided for low-risk items.

### Suggestions
- Define all 8 stages explicitly with entry criteria, exit criteria, responsible roles, and expected artifacts for each — a table format would reduce ambiguity.
- Introduce a formal risk rubric (e.g., impact × probability scoring) to make Route A escalation deterministic and auditable.
- Add a conflict resolution protocol for validator vs. readiness-signal disagreements: specify who holds final authority, under what conditions an override is valid, and what audit trail is required.
- Specify SLAs or timeout policies per stage gate to prevent lifecycle stalls; include automatic escalation triggers for breached SLAs.
- Provide a migration runbook or at minimum a decision tree: which legacy items need backfill, which can be grandfathered, and what the cutover timeline looks like.
- Version the artifact schema and publish it as a shared contract (e.g., JSON Schema or OpenAPI component) so all routes can validate against the same source of truth.
- Define minimum test coverage requirements per lifecycle transition and require CI gate enforcement before close/archive stages are permitted.

### Questions for Author
- What are the exact definitions and names of all 8 stages? The summary only surfaces approximately 5 distinct checkpoints.
- Who owns the risk-scoring decision for Route A escalation, and what is the appeals or override process if stakeholders disagree on a risk classification?
- How are 'readiness signals' generated and by whom — are they automated (e.g., CI status), manual attestations, or both? How are conflicts with validator outputs resolved today?
- Is there a plan to grandfather existing in-flight work items, or will all open WRKs be required to retroactively conform to the new lifecycle immediately upon rollout?
- What is the intended rollout strategy — big-bang, pilot cohort, or feature-flagged? How will teams opt in or out during a transition period?
- Does 'HTML review' at the planning and close stages imply a specific rendered-artifact format, or is this referring to a UI surface within workspace-hub? Clarifying this affects tooling and accessibility requirements.
