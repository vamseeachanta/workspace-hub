# Plan for #2209: chore(knowledge): define durable-vs-transient knowledge boundary across wikis, issues, registries, and session artifacts

> **Status:** draft
> **Complexity:** T1
> **Date:** 2026-04-16
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2209
> **Review artifacts:** scripts/review/results/2026-04-16-plan-2209-claude-overnight.md

---

## Resource Intelligence Summary

<!-- Verification: count distinct sources above (across all sub-sections).
     Minimum 3 required (issue body + 2 others). Current count: 7 -->

### Existing repo code

- Found: `docs/document-intelligence/durable-vs-transient-knowledge-boundary.md` (33,909 bytes, created 2026-04-11) -- **primary deliverable already exists**. Defines classification of every major artifact class as durable, transient, or recurring-operational. Includes ownership statements, allowed bridge/sync directions, promotion rules with concrete criteria, retention/expiration guidance, anti-patterns, and guardrails.
- Found: `docs/plans/2026-04-11-claude-agent-team-prompt-2209-durable-vs-transient-boundary.md` -- original agent-team prompt used to produce the deliverable.
- Gap: No canonical plan file (in template format) existed prior to this plan.

### Standards

Not applicable -- this is a Knowledge/Intelligence category issue defining boundary policy, not an engineering standards implementation.

### LLM Wiki pages consulted

- No relevant wiki pages -- this issue defines boundary policy for how knowledge flows between layers, not domain knowledge content.

### Documents consulted

- `docs/document-intelligence/llm-wiki-resource-doc-intelligence-operating-model.md` -- parent operating model (#2205). The boundary policy correctly inherits the Layer 3 (durable knowledge), Layer 5 (execution state), and Layer 6 (transient session) definitions, and applies the most-durable-owner rule.
- `docs/document-intelligence/standards-codes-provenance-reuse-contract.md` -- sibling contract (#2207). Correctly cross-referenced; boundary policy complements the provenance contract without redefining reuse/reparse scope.
- `docs/document-intelligence/pyramid-conformance-checks.md` -- sibling design (#2206). Boundary policy identifies future enforcement surfaces without implementing them, correctly deferring to #2206.
- `docs/document-intelligence/intelligence-accessibility-map.md` -- sibling (#2096). Referenced as a related artifact covering accessibility inventory.
- `scripts/review/results/2026-04-11-issue-2209-final-review.md` -- final integrator review. **Verdict: APPROVED.** All 10 checklist items passed. Cross-link decision confirmed: bidirectional reference chain with parent is complete. Residual risk noted: retention periods are advisory until cleanup automation is implemented.
- `scripts/review/results/2026-04-11-issue-2209-claude-review.md` -- adversarial review artifact from implementation session.

### Gaps identified

- The deliverable (`durable-vs-transient-knowledge-boundary.md`) is **already created and reviewed**. No content gaps remain.
- The canonical plan file (this document) was missing -- this plan closes that gap.
- Issue state may need reconciliation: if the issue is still OPEN but work is complete, the planning state should be updated to reflect completion readiness.

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | docs/plans/2026-04-16-issue-2209-durable-vs-transient-knowledge-boundary.md |
| Deliverable | docs/document-intelligence/durable-vs-transient-knowledge-boundary.md |
| Implementation prompt | docs/plans/2026-04-11-claude-agent-team-prompt-2209-durable-vs-transient-boundary.md |
| Adversarial review | scripts/review/results/2026-04-11-issue-2209-claude-review.md |
| Final review | scripts/review/results/2026-04-11-issue-2209-final-review.md |
| Plan review -- Claude overnight | scripts/review/results/2026-04-16-plan-2209-claude-overnight.md |

---

## Deliverable

A durable-vs-transient knowledge boundary policy (`docs/document-intelligence/durable-vs-transient-knowledge-boundary.md`) defining artifact classification, promotion rules, retention guidance, and anti-patterns -- **already created and approved on 2026-04-11**.

---

## Pseudocode

Trivial -- deliverable already exists. Remaining work is reconciliation only (see Files to Change).

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Verify | `docs/document-intelligence/durable-vs-transient-knowledge-boundary.md` | Confirm deliverable meets acceptance criteria |
| Create | `docs/plans/2026-04-16-issue-2209-durable-vs-transient-knowledge-boundary.md` | This canonical plan file |
| Create | `scripts/review/results/2026-04-16-plan-2209-claude-overnight.md` | Overnight review artifact |

---

## TDD Test List

Not applicable -- this issue produces a policy document, not executable code.

---

## Acceptance Criteria

- [x] Deliverable exists at `docs/document-intelligence/durable-vs-transient-knowledge-boundary.md`
- [x] Deliverable classifies every major artifact class as durable, transient, or recurring-operational
- [x] Deliverable defines concrete promotion criteria for L6-to-L3 and L5-to-L3 transitions
- [x] Deliverable includes retention/expiration guidance with numeric periods
- [x] Deliverable inherits from parent operating model (#2205) without redefining it
- [x] Deliverable does not absorb scope from siblings (#2206, #2207, #2208)
- [x] Adversarial review completed with APPROVED verdict
- [x] Final integrator review passed all 10 checklist items
- [ ] Canonical plan file created (this document)
- [ ] Review artifacts posted to scripts/review/results/
- [ ] Issue state reconciled (close or mark done as appropriate)

---

## Adversarial Review Summary

| Provider | Verdict | Key findings |
|---|---|---|
| Claude (2026-04-11 implementation) | APPROVE | All 10 checklist items pass; bidirectional reference chain with parent confirmed complete |
| Claude (2026-04-16 overnight) | pending | See scripts/review/results/2026-04-16-plan-2209-claude-overnight.md |

**Overall result:** Deliverable APPROVED on 2026-04-11. Plan reconciliation pending overnight review.

---

## Risks and Open Questions

- **Risk:** Parent #2205 must remain plan-approved for this issue's deliverable to stay valid. Confirmed: parent operating model exists and is authoritative.
- **Risk:** Retention periods in the deliverable are advisory-only until cleanup automation is implemented (noted in final review as residual risk). This is a downstream implementation concern, not a gap in the boundary policy itself.
- **Open:** Issue may need label update from OPEN to a completion state once this plan is approved and reconciliation is confirmed.

---

## Complexity: T1

**T1** -- deliverable already exists and was approved. Remaining work is plan creation and state reconciliation only.
