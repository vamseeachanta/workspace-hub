# Adversarial Review: #2209 Durable-vs-Transient Knowledge Boundary

**Reviewer role:** Adversarial Reviewer (Role 3 of 4-role agent team)
**Date:** 2026-04-11
**Artifact:** `docs/document-intelligence/durable-vs-transient-knowledge-boundary.md`

---

## Review Criteria

1. Consistency with #2205 parent operating model
2. Non-overlap with #2207 provenance/reuse contract
3. Clarity of promotion/retention rules
4. Whether future implementation teams could use this without guessing
5. Whether anti-patterns are concrete and enforceable

---

## Finding 1: Consistency with #2205

**Verdict: PASS**

The document correctly inherits from the parent model and does not redefine layers, ownership, or flow rules. Specific checks:

- Layer definitions (L2, L3, L5, L6) match #2205 Section 2 exactly
- Allowed flows (L6→L3, L5→L3) match #2205 Section 4 exactly
- Forbidden flows align with #2205 Section 5 anti-patterns
- The "most-durable-owner rule" from #2205 is cited and applied in borderline cases (Section 5.3)
- Conflict resolution clause correctly defers to parent

**One observation:** The document introduces a "recurring-operational" classification for weekly review outputs that does not map to a formal layer in #2205. This is explicitly acknowledged as "a pragmatic classification, not a formal new layer" (Section 11, point 6). This is acceptable as long as the parent model is not amended to add a Layer 5.5. Recommendation: no change needed, but if recurring-operational artifacts proliferate, revisit.

## Finding 2: Non-overlap with #2207

**Verdict: PASS**

The document explicitly avoids defining `doc_key` semantics, provenance fields, reparse decision trees, or registry schemas. Section 3 maps the boundary between this policy and #2207:

- #2209 covers artifact *roles* (durable vs transient)
- #2207 covers artifact *identity* (provenance, `doc_key`, reuse rules)

The L2→L3 promotion bridge (Section 6.1) references the #2207 pipeline as the mechanism for structured promotion. This is correct delegation, not overlap.

## Finding 3: Clarity of Promotion/Retention Rules

**Verdict: PASS with minor observation**

The five promotion criteria (Section 7.1) are concrete and testable:
- Reusability, verification, non-redundancy, source traceability, stability
- Each has a clear test description

The promotion process (Section 7.2) is step-by-step and auditable.

The retention schedule (Section 8.1) gives specific numeric retention periods for each artifact class.

**Minor observation:** The "stability" criterion ("not expected to change within the next 30 days") is the hardest to assess objectively. A session-ending agent cannot reliably predict whether a finding will remain stable. However, this is inherent to any promotion policy and the 30-day threshold provides a reasonable heuristic. Recommendation: no change needed.

## Finding 4: Usability for Future Implementation Teams

**Verdict: PASS**

The document provides:
- A decision tree (Section 5.1) that an agent can follow mechanically
- Hard classification rules (Section 5.2) with no ambiguity for the common cases
- Borderline case resolution (Section 5.3) with worked examples from the actual repo
- Anti-patterns (Section 9.1) with concrete examples, not abstract warnings
- An implementation sequence (Section 12) that can be directly converted to issues

An implementation agent reading this document would know:
- Whether a specific artifact is durable or transient (decision tree)
- What to do with a transient artifact that contains valuable findings (promotion process)
- What NOT to do (anti-patterns with specific repo examples)
- What to build next (implementation sequence)

## Finding 5: Anti-Pattern Enforceability

**Verdict: PASS**

The 8 anti-patterns (Section 9.1) are concrete:
- Each has a description, harm statement, and repo-specific example
- AP-1 through AP-8 cover the most common boundary violations observed in this repo

The 6 guardrails (Section 9.2) include enforcement levels:
- GR-1, GR-2, GR-4 are enforceable via conformance checks (#2206)
- GR-3 is enforceable via skill updates
- GR-5 is enforceable via cleanup scripts
- GR-6 is a convention that requires manual or orchestrator judgment

No guardrail is left without a proposed enforcement mechanism.

---

## Issues Found Requiring Revision

**None.** No major issues found that require revision before finalization.

## Minor Recommendations (non-blocking)

1. **Recurring-operational formalization:** If the workspace-hub acquires more recurring operational outputs beyond weekly reviews (e.g., nightly batch reports, daily solver queue dashboards), the "recurring-operational" classification should be promoted to a formal sub-layer definition in the parent model. Track as a watch item.

2. **Cross-repo extension:** The policy explicitly scopes to `workspace-hub` only (Section 11, point 5). When `digitalmodel` or other satellite repos need boundary guidance, this document should be extended or a sibling policy created.

3. **Retention enforcement priority:** The retention schedule (Section 8) is entirely advisory until cleanup automation exists. Recommend prioritizing work item #5 (transient-artifact cleanup script) from the implementation sequence.

---

## Summary Verdict

**PASS — Ready for finalization.**

The document is internally consistent, properly scoped, non-overlapping with #2207, and provides actionable guidance for future implementation teams. No revisions required.
