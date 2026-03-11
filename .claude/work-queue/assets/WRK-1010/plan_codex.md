# WRK-1010 Plan Review — Codex

**Reviewer:** Codex
**Date:** 2026-03-10
**Plan ref:** specs/wrk/WRK-1010/plan.md
**Verdict:** APPROVE
**Note:** Review ran against updated plan (after Gemini MINOR fixes to Phase 1/4 static scope)

## Summary

The plan is mostly well-ordered and concrete. Phase 0 as a grounding pass is correct,
the per-skill static assessment before overlap analysis makes sense, and the deliverables
are specific enough to execute. Main issues are methodological gaps (addressed below).

## Issues Found (from Codex review)

- Phase 3 only checks 4 hand-picked pairs; may miss overlap across the rest of the
  8-skill graph — pair selection needs an explicit basis or a lightweight full-matrix
  coarse scan first.
- Phase 2 with-vs-without scoring is vulnerable to subjectivity — no rubric for 0-5.
- Phase 1 scores pass/partial/fail but doesn't require citing the SKILL.md section
  supporting the score — weakens reproducibility.
- Phase 4 only targets step-sequence skills; weakly-specified skills may escape scrutiny.
- "At least 1 retirement/merge recommendation" could force artificial recommendations;
  should allow "no merge/retire justified" outcome with "retain-with-clarification".
- Assessment artifact benefits from a fixed per-skill schema.
- Knowledge map baseline vs post-assessment corrections should be distinguishable.

## Suggestions Applied in Plan

1. Phase 3: add coarse full 8-skill matrix scan before deep-dive on 4 pairs
2. Phase 2: add scoring rubric (0=no unique protocol, 1=minor terminology,
   3=material workflow scaffolding, 5=strong deterministic protocol with artifacts)
3. Phase 1/4: require evidence citations from SKILL.md per scored claim
4. Recommendation gate: "at least 1 concrete recommendation (retain/refine/merge/retire)"
5. Assessment doc: define per-skill schema (claimed behaviors, citation, score, delta,
   overlap notes, recommendation)

## Questions for Author (answered in plan)

- Do you want this WRK to claim actual capability performance, or only assess whether
  the skill documents appear to add structured guidance?
  → Document-based assessment only. Runtime capability deferred to WRK-1009.
- Why only 4 overlap pairs?
  → Phase 3 updated to include coarse scan of all 8 skills first.
- If no credible merge/retire candidate emerges, should the plan still pass?
  → Yes — gate updated to allow "retain-with-clarification" as a valid outcome.
