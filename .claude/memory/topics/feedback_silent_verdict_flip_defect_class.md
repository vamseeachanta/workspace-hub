> Git-tracked snapshot from Claude auto-memory. Captured: 2026-05-22
> Source: /home/vamsee/.claude/projects/-mnt-local-analysis-workspace-hub/memory/feedback_silent_verdict_flip_defect_class.md

---
name: silent-verdict-flip-defect-class
description: Two implementations citing the same standard but using different sections/editions can return OPPOSITE stable/unstable verdicts at design margin. Found in cathodic protection (CP design materially undersized) and on-bottom stability (UNSTABLE vs STABLE for same scenario). Most insidious because both implementations claim standards compliance.
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 37c4fd1d-3784-4903-a5ea-5fe997dd7044
---

**"Both cite the same standard" is not the same as "both compute the same answer." Two implementations of a DNV/API calc can return opposite verdicts because they implemented different *sections* of the same document, both legitimately.**

**Why:** 2026-05-13 — Found during the cross-domain duplicate-implementation cleanup (workspace-hub#2694) audits:

1. **On-bottom stability** (`subsea/on_bottom_stability/dnv_rp_f109.py` vs `geotechnical/on_bottom_stability.py`): Same input (W_s=500, F_H=183, F_L=150, μ=0.6) → util=1.000 UNSTABLE per §4.3.1 vs util=0.957 STABLE per §4.3.2. Both labeled "DNV-RP-F109", both legitimate methods.

2. **Cathodic protection** (functional package vs router): Same DNV-RP-B401 standard, different editions (2017 vs 2021). 4 of 15 dimensions diverge materially. Splash-zone treatment (0.0 vs 0.10-0.20 A/m²) can produce **materially undersized CP designs for jacket structures**. Flush-anode resistance formulas differ by 2×.

**How to apply:**

1. When auditing duplicate implementations, do NOT stop at "both cite the same standard." Check:
   - Which *section/clause* of the standard does each implement?
   - Which *edition* of the standard does each apply?
   - For shared inputs, compute outputs from both and compare numerically (not just "same file output structure")

2. The diff to look for in code review:
   - Different default coefficient values for what should be the same standard constant
   - Different function names that compute "the same" quantity
   - Different units (kN vs N, m vs mm)
   - Different physical assumptions (smooth vs rough, intact vs damaged, splash zone treatment)

3. The fix is rarely "delete one":
   - If implementations cover different *legitimate* methods of the same standard, parameterize the method choice (e.g., `method: Literal["§4.3.1", "§4.3.2"]`)
   - If implementations cover different *editions* of the same standard, parameterize the edition (e.g., `edition: Literal["2017", "2021"]`)
   - Emit the chosen method/edition in result objects so downstream review (and regulators) can trace which path was taken

4. Calc-citation-contract is necessary but not sufficient:
   - A `Citation` instance that says "DNV-RP-F109" is *not* enough provenance
   - Citations must include `section` (e.g., "§4.3.1") and `revision`/`edition` (e.g., "2021")
   - Per `.claude/rules/calc-citation-contract.md` (which already has these fields in schema)

**Regulatory framing:** A DNV class survey would flag both surfaces as non-defensible. "We implemented the standard" is not a defense if the implementation silently picks one section/edition and the result depends on that choice.

**Related memory:**
- [[feedback_llm_wiki_concept_pages_need_public_references]] — single-source can mislead
- [[project_domain_knowledge_sweep]] — comprehensive auditing surfaces this defect class
- Issue surfaces: workspace-hub#2694 (epic), #2692 (Pipelines R5)
