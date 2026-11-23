# Plan for #2207: feat(doc-intel): define standards/codes provenance + reuse contract for llm-wiki promotion

> **Status:** draft
> **Complexity:** T1
> **Date:** 2026-04-16
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2207
> **Review artifacts:** scripts/review/results/2026-04-16-plan-2207-claude-overnight.md

---

## Resource Intelligence Summary

<!-- Verification: count distinct sources above (across all sub-sections).
     Minimum 3 required (issue body + 2 others). Current count: 7 -->

### Existing repo code

- Found: `docs/document-intelligence/standards-codes-provenance-reuse-contract.md` (27,391 bytes, created 2026-04-11) -- **primary deliverable already exists**. Defines the canonical identity model (`doc_key`), required provenance fields at each pyramid layer, reuse-vs-reparse decision rules, promotion path from document-intelligence to LLM-wiki, and 5 anti-patterns.
- Found: `docs/plans/2026-04-11-claude-agent-team-prompt-2207-provenance-reuse-contract.md` -- original agent-team prompt used to produce the deliverable.
- Gap: No canonical plan file (in template format) existed prior to this plan.

### Standards

- `data/document-index/standards-transfer-ledger.yaml` -- referenced in the agent-team prompt as a source surface for provenance inspection. The deliverable's identity model maps `doc_key` to existing `content_hash` fields in the ledger.

### LLM Wiki pages consulted

- No relevant wiki pages -- this issue defines a provenance contract, not domain knowledge content.

### Documents consulted

- `docs/document-intelligence/llm-wiki-resource-doc-intelligence-operating-model.md` -- parent operating model (#2205). The provenance contract correctly inherits layer boundaries and applies the `doc_key` rule from Section 3.
- `docs/document-intelligence/pyramid-conformance-checks.md` -- sibling design (#2206). The provenance contract is referenced as an input for conformance checks without scope overlap.
- `docs/document-intelligence/durable-vs-transient-knowledge-boundary.md` -- sibling policy (#2209). Correctly cross-referenced without redefining boundary scope.
- `scripts/review/results/2026-04-11-issue-2207-final-review.md` -- final integrator review. All 10 checklist items passed. Adversarial review item "artifact-existence guard" was resolved (added to Section 5.1). Pseudocode example deferred as nice-to-have.
- `scripts/review/results/2026-04-11-issue-2207-claude-review.md` -- adversarial review artifact from implementation session.

### Gaps identified

- The deliverable (`standards-codes-provenance-reuse-contract.md`) is **already created and reviewed**. No content gaps remain.
- The canonical plan file (this document) was missing -- this plan closes that gap.
- Issue state may need reconciliation: if the issue is still OPEN but work is complete, the planning state should be updated to reflect completion readiness.

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | docs/plans/2026-04-16-issue-2207-standards-codes-provenance-reuse-contract.md |
| Deliverable | docs/document-intelligence/standards-codes-provenance-reuse-contract.md |
| Implementation prompt | docs/plans/2026-04-11-claude-agent-team-prompt-2207-provenance-reuse-contract.md |
| Adversarial review | scripts/review/results/2026-04-11-issue-2207-claude-review.md |
| Final review | scripts/review/results/2026-04-11-issue-2207-final-review.md |
| Plan review -- Claude overnight | scripts/review/results/2026-04-16-plan-2207-claude-overnight.md |

---

## Deliverable

A provenance and reuse contract (`docs/document-intelligence/standards-codes-provenance-reuse-contract.md`) defining `doc_key` identity model, provenance fields, reuse-vs-reparse decision rules, and LLM-wiki promotion path -- **already created and approved on 2026-04-11**.

---

## Pseudocode

Trivial -- deliverable already exists. Remaining work is reconciliation only (see Files to Change).

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Verify | `docs/document-intelligence/standards-codes-provenance-reuse-contract.md` | Confirm deliverable meets acceptance criteria |
| Create | `docs/plans/2026-04-16-issue-2207-standards-codes-provenance-reuse-contract.md` | This canonical plan file |
| Create | `scripts/review/results/2026-04-16-plan-2207-claude-overnight.md` | Overnight review artifact |

---

## TDD Test List

Not applicable -- this issue produces a contract document, not executable code.

---

## Acceptance Criteria

- [x] Deliverable exists at `docs/document-intelligence/standards-codes-provenance-reuse-contract.md`
- [x] Deliverable defines canonical identity model (`doc_key`) with concrete mapping to existing codebase terms
- [x] Deliverable defines reuse-vs-reparse decision rules with artifact-existence guard
- [x] Deliverable inherits from parent operating model (#2205) without redefining it
- [x] Deliverable does not absorb scope from siblings (#2206, #2208, #2209)
- [x] Adversarial review completed; action items resolved or deferred with rationale
- [x] Final integrator review passed all 10 checklist items
- [ ] Canonical plan file created (this document)
- [ ] Review artifacts posted to scripts/review/results/
- [ ] Issue state reconciled (close or mark done as appropriate)

---

## Adversarial Review Summary

| Provider | Verdict | Key findings |
|---|---|---|
| Claude (2026-04-11 implementation) | APPROVE | All 10 checklist items pass; artifact-existence guard added per adversarial feedback |
| Claude (2026-04-16 overnight) | pending | See scripts/review/results/2026-04-16-plan-2207-claude-overnight.md |

**Overall result:** Deliverable APPROVED on 2026-04-11. Plan reconciliation pending overnight review.

---

## Risks and Open Questions

- **Risk:** Parent #2205 must remain plan-approved for this issue's deliverable to stay valid. Confirmed: parent operating model exists and is authoritative.
- **Open:** Pseudocode example for reuse check was deferred from the adversarial review as nice-to-have. Implementation issues can include pseudocode in their own plans.
- **Open:** Issue may need label update from OPEN to a completion state once this plan is approved and reconciliation is confirmed.

---

## Complexity: T1

**T1** -- deliverable already exists and was approved. Remaining work is plan creation and state reconciliation only.
