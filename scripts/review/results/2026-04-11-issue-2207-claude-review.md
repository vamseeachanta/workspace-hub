# Adversarial Review: #2207 Standards/Codes Provenance + Reuse Contract

> **Reviewer role:** Adversarial Reviewer (internal agent team)
> **Date:** 2026-04-11
> **Document under review:** `docs/document-intelligence/standards-codes-provenance-reuse-contract.md`
> **Parent contract:** `docs/document-intelligence/llm-wiki-resource-doc-intelligence-operating-model.md` (#2205)

---

## Review Criteria

1. Consistency with #2205 parent operating model
2. Avoidance of schema creep beyond #2207 issue scope
3. Clarity of reuse-vs-reparse decision rules
4. Whether future implementation teams could use this without guessing

---

## Finding 1: Consistency with #2205 — PASS

**Assessment:** The contract correctly inherits all parent rules and does not redefine any of them. Specifically:

- The pyramid layer model is referenced, not redefined.
- The `doc_key` rule from #2205 Section 3 is concretized (mapped to existing `content_hash` fields) without changing its semantics.
- Information flow rules are respected: reuse follows L2→L3, reparsing falls back to L1→L2.
- The forbidden flows (L3 reparsing raw docs when L2 evidence exists) are explicitly enforced in the decision tree.
- Child guardrails from #2205 Section 10 are honored: the contract does NOT redefine parent ownership model, layer boundaries, or workflow policy.

**Risk:** None identified.

---

## Finding 2: Schema Creep Assessment — PASS with one NOTE

**Assessment:** The contract stays within #2207 scope. It defines provenance fields and reuse rules. It does not:
- Define conformance validation (#2206 scope)
- Define issue-workflow retrieval hooks (#2208 scope)
- Define durable-vs-transient boundary rules (#2209 scope)
- Define the registry file format or query interface (#2136 scope)

**NOTE:** Section 6.3 defines a wiki-page YAML frontmatter schema (`doc_key`, `source_ref`, `promoted_from`, etc.). This is borderline — it could be argued as #2034 scope (LLM wiki ingest pipeline). However, the frontmatter is minimal and serves the provenance back-link purpose, which is clearly #2207 scope. The contract does not prescribe the full wiki page format, only the provenance fields within it.

**Recommendation:** No change needed, but future implementation of the frontmatter should coordinate with #2034.

---

## Finding 3: Reuse-vs-Reparse Decision Rules — PASS

**Assessment:** The decision tree in Section 5.1 is unambiguous:
- It branches on `doc_key` existence first (correct — identity before processing).
- It branches on processing status second (correct — progressive refinement).
- It provides sufficiency criteria for each target use case (Section 5.2).
- It correctly identifies when OCR is needed (Section 5.3) and when re-extraction is permitted (Section 5.4).

**Stress test — edge case:** What if a document is `status: summarized` but the summary file is missing or corrupt?
- The contract's decision tree says "REUSE the summary" — but the file is gone.
- **Gap:** The decision tree assumes the referenced output actually exists. It should fall through to reparse if the referenced artifact is missing.

**Recommendation:** Add a note to Section 5.1 that reuse requires the referenced artifact to be *present and non-empty*. If the artifact is missing, treat as the next-lower status level.

---

## Finding 4: Implementation Usability — PASS with MINOR improvement

**Assessment:** The contract is implementation-guiding:
- Section 9 identifies specific files, current state, and likely changes — an implementation agent can follow this directly.
- The field-name mapping table (Section 3.1) is critical for bridging existing code to the new contract.
- The anti-patterns (Section 8) are concrete, not abstract.
- The follow-on sequence (Section 11) has explicit dependencies.

**Minor gap:** The contract does not provide a concrete example of what a "reuse check" looks like in pseudocode. An implementation agent working on `llm_wiki.py` would benefit from a 5-line pseudocode example showing: query registry by `doc_key` → check status → load summary if sufficient → skip raw file read.

**Recommendation:** Consider adding a brief pseudocode snippet to Section 5.1 or 6.2. However, this is a nice-to-have, not a blocker — the decision tree is already unambiguous.

---

## Finding 5: Identity Term Coverage — PASS

**Assessment:** The mapping table in Section 3.1 covers all identity terms found in the codebase:
- `content_hash` in `index.jsonl` and pipeline scripts
- `sha` / `sha256` in shard files and summary lookups
- `checksum` in `doc_intelligence/schema.py`
- `content_hash()` function in promoters (correctly identified as NOT a `doc_key`)

No unmapped identity terms were found in the source surfaces inspected.

---

## Finding 6: Cross-Machine Consistency — PASS

**Assessment:** The contract inherits #2205's cross-machine access model and correctly notes that:
- `doc_key` is the join key across machines (Section 3.3)
- Path changes do not change identity (Section 3.4)
- The `provenance.py` merge logic handles multi-machine dedup (Section 3.3)

The open question about subtly different file copies (Section 10, item 6) is an honest residual risk, not a gap.

---

## Summary Verdict

| Criterion | Verdict |
|---|---|
| Consistency with #2205 | PASS |
| Schema creep avoidance | PASS (one borderline note on wiki frontmatter) |
| Reuse-vs-reparse clarity | PASS (one edge case gap on missing artifacts) |
| Implementation usability | PASS (minor: pseudocode example would help) |
| Identity term coverage | PASS |
| Cross-machine consistency | PASS |

**Overall:** PASS — proceed to finalization with one recommended revision:
- Add an artifact-existence check note to the reuse decision tree (Section 5.1).

---

## Action Items for Integrator

1. **SHOULD DO:** Add a note to Section 5.1 that reuse requires the referenced artifact to be present and non-empty; fall through to reparse if missing.
2. **OPTIONAL:** Add a brief pseudocode example to Section 5 or 6 showing a reuse check flow.
3. **NO ACTION:** Wiki frontmatter in Section 6.3 is within scope; coordinate with #2034 during implementation.
