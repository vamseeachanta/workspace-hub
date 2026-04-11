# Final Integrator Review: #2207 Standards/Codes Provenance + Reuse Contract

> **Reviewer role:** Integrator (final pass)
> **Date:** 2026-04-11
> **Document:** `docs/document-intelligence/standards-codes-provenance-reuse-contract.md`
> **Adversarial review:** `scripts/review/results/2026-04-11-issue-2207-claude-review.md`

---

## Pre-Finalization Checklist

| Check | Status |
|---|---|
| All 11 required sections present? | PASS (Sections 1-11 + Appendix) |
| Consistent with #2205 parent operating model? | PASS (adversarial review confirmed) |
| Does NOT redefine parent layer boundaries or ownership? | PASS |
| Does NOT absorb #2206, #2208, #2209, or #2216 scope? | PASS |
| Reuse-vs-reparse decision tree is unambiguous? | PASS (artifact-existence guard added per adversarial review) |
| Identity term mapping covers all codebase terms? | PASS (`content_hash`, `sha`/`sha256`, `checksum`, `content_hash()` function) |
| Anti-patterns are concrete, not aspirational? | PASS (5 anti-patterns with specific examples) |
| Implementation surfaces identify specific files? | PASS (17 files identified across 4 categories) |
| Follow-on sequence has explicit dependencies? | PASS (6-step sequence with dependency chain) |
| Open questions are genuine residuals, not deferred work? | PASS (6 items, all require decisions beyond this contract's scope) |

---

## Adversarial Review Action Items — Resolution

| Item | Action taken |
|---|---|
| Add artifact-existence guard to Section 5.1 | **DONE** — added "Artifact-existence guard" paragraph below the decision tree |
| Add pseudocode example for reuse check | **DEFERRED** — nice-to-have; the decision tree is already unambiguous. Implementation issues can include pseudocode in their own plans. |
| Coordinate wiki frontmatter with #2034 | **NOTED** — no action needed in this contract; noted as implementation coordination item |

---

## Internal Consistency Check

1. **Section 3 (Identity) vs Section 4 (Fields):** Section 3 defines `doc_key` as SHA-256 of binary content. Section 4.1 lists `doc_key` as a minimum required field with the same definition. Consistent.

2. **Section 5 (Reuse) vs Section 6 (Promotion):** Section 5 defines when existing outputs are sufficient. Section 6 defines how to promote them to wiki entries. Section 6.4 explicitly cross-references Section 5's sufficiency criteria. Consistent.

3. **Section 8 (Anti-patterns) vs Section 5 (Reuse):** Anti-pattern 8.1 (duplicate parsing) is the inverse of the reuse decision tree. If Section 5 is followed, anti-pattern 8.1 cannot occur. Consistent.

4. **Section 9 (Implementation) vs Section 11 (Sequence):** Section 9 identifies 17 files across 4 categories. Section 11 sequences 6 work items that cover those categories. All Section 9 files appear in at least one Section 11 work item. Consistent.

5. **Glossary vs body:** All glossary terms match their definitions in the document body. No contradictions found.

---

## Cross-Link Assessment

The parent operating model (`docs/document-intelligence/llm-wiki-resource-doc-intelligence-operating-model.md`) Section 11 (Discoverability) lists this contract's parent issue #2207 as a child that should reference the operating model. The contract does this in Section 2.

**Should the parent doc cross-link back to this contract?** Yes — a minimal cross-link helps discoverability. The parent doc's Section 8 already says "These details are delegated to #2207 (provenance contract)." Adding a path reference to the new contract doc would complete the link.

**Decision:** Add a single cross-link line to the parent doc's Section 11 (Discoverability) table. This is within the allowed write paths ("cross-links only, if truly needed").

---

## Final Verdict

**APPROVED for delivery.**

The contract document:
- Defines canonical provenance fields for standards/codes artifacts
- Defines a canonical `doc_key` / content-identity reuse policy consistent with #2205
- Defines reuse-vs-reparse decision rules with an artifact-existence safety guard
- Defines the llm-wiki promotion path using existing document-intelligence outputs
- Defines fallback rules for OCR/reparse when evidence is insufficient
- Identifies likely implementation surfaces and follow-on work
- Includes anti-patterns and conflict-resolution guidance
- Has been adversarially reviewed and revised within this run

---

## Residual Risks

1. **Field name migration timing:** No implementation timeline is set for migrating from `content_hash` to `doc_key`. Without a coordinated migration, the dual-name period could persist indefinitely.

2. **Standards-transfer-ledger gap:** The ledger currently has no `doc_key` fields. Until Phase E back-population runs, the ledger cannot participate in `doc_key`-based lookups.

3. **Wiki ingest coupling:** Adding reuse checks to `llm_wiki.py` couples the wiki subsystem to the registry subsystem. This is architecturally correct but introduces a new dependency that must be tested.

4. **No automated enforcement:** This contract is a markdown document. Until #2206 (conformance checks) implements validation, compliance is advisory only.
