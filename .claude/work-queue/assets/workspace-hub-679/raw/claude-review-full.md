### Verdict: REQUEST_CHANGES

### Summary
WRK-624 presents a thorough and well-structured canonical workflow hardening plan. The 8-stage lifecycle, review matrix, dependency contract, phased rollout, and testing strategy are all commendable in scope. However, several internal contradictions, underspecified terms, and structural gaps need to be resolved before the plan can be approved.

### Issues Found
- Frontmatter contradiction: `status: implemented` and `progress: 100` conflict with the review section showing `status: pending`, all approval-gate flags false, and `ready_for_next_step: false`. The item appears to be a draft, not an implemented artifact.
- Gemini reviewer contradiction: `review.reviewers.google_gemini.status` is `approved` but `review.approval_gate.gemini_approved` is `false`. These must be consistent.
- Mermaid execute loop is problematic: when 'Route Review Passed?' (M) is No, the diagram loops directly back to Execute (K) with no revision or planning step. This can produce an infinite execute cycle and does not reflect a realistic failure-recovery path.
- `INVALID_OUTPUT` is introduced in the Dependency Contract section but is absent from the Standard Verdict Set. An artifact classified as `INVALID_OUTPUT` has no defined handling path in the review rules, creating a gap between detection and remediation.
- Phases 2 and 3 have no rollback paths. Phase 1 explicitly documents a rollback strategy; the omission for later phases is an inconsistency given the plan's own requirement-class model states all routes share universal obligations.
- The Triage minimum contract requires a `computer` field whose meaning is undefined. It is unclear whether this refers to a compute resource, a machine name, an executor type, or something else.
- Route A escalation trigger 'risk signals' is undefined. Without a concrete definition or checklist, automated or agent-based escalation cannot be implemented deterministically.
- 'Week-scale waits are not acceptable' in the Claim stage is vague. The threshold between an acceptable short defer and an unacceptable week-scale delay is not specified (e.g., is 5 days acceptable? 8 days?).

### Suggestions
- Align frontmatter `status`, `progress`, and `phase` with actual review state. If this is a plan under review, set `status: draft` or `status: pending` and `progress` to a value consistent with the incomplete approval gate.
- Synchronize the Gemini approval entry: either set `approval_gate.gemini_approved: true` to match `google_gemini.status: approved`, or revert the reviewer status to `pending` pending formal gate confirmation.
- Revise the Mermaid execute loop so that a failed route review routes to a 'Revise / Address Findings' node before re-entering Execute, mirroring the existing Plan revision loop pattern.
- Add `INVALID_OUTPUT` to the Standard Verdict Set and define its handling: e.g., treated as a blocking non-approval that requires the reviewer to re-run, with escalation policy if re-run also produces `INVALID_OUTPUT`.
- Add explicit rollback paths for Phase 2 and Phase 3, including the triggering conditions and recovery steps.
- Define `computer` in the Triage minimum contract with a concrete description and allowed values or a reference to a schema.
- Define 'risk signals' for Route A escalation with a concrete list (e.g., external dependencies, security changes, cross-repo impact, legal flags) so agents and validators can apply the rule consistently.
- Specify a numeric threshold for the claim short-defer tolerance (e.g., 'defer of up to 24 hours is acceptable; beyond that, recommend an alternate agent') to replace the vague 'week-scale' language.
- Map each implementation backlog item to its target phase so it is clear which deliverables gate each phase transition.
- Add a stage-level SLA or aging policy (e.g., maximum time an item may sit in `working` without a recorded progress update before escalation or failure is triggered).

### Questions for Author
- Should the frontmatter `status: implemented` reflect the WRK item itself or the plan artifact? If the intent is that WRK-624 is self-describing its own lifecycle contract as 'implemented', clarify with a note; otherwise correct the value.
- For the failed-review loop in the Mermaid diagram, was the intent to allow re-execution after in-place fixes without a formal re-plan step? If so, document the conditions under which in-place fixes are sufficient versus requiring a new plan revision.
- Is `INVALID_OUTPUT` intended to be a distinct verdict that reviewers can emit, or is it purely a validator classification applied after the fact? The answer determines whether it belongs in the Standard Verdict Set or in a separate validator output schema.
- Are Phases 2 and 3 intentionally exempt from rollback planning (e.g., because hard gates are considered irreversible by design), or was the rollback section simply omitted and needs to be added?
- The `test_coverage: 80` metadata field — is this a target for the scripts and automation produced by this plan, or a coverage figure for the plan document itself? If the former, which scripts are in scope and how will coverage be measured?
