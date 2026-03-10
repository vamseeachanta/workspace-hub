# Plan Draft — WRK-667

**WRK:** WRK-667 — Strengthen Resource Intelligence skill with measurable quality impact
**Route:** B | **Stage:** 4 Plan Draft | **Generated:** 2026-03-09

## Summary

Extend the existing resource-intelligence skill (built by WRK-655) with:
1. Canonical usage path documentation (where in the workflow, how to invoke)
2. Quality metrics schema (`quality_signals` block in evidence yaml template)
3. Validator checks for required RI refs (extend validate-resource-pack.sh + verify-gate-evidence.py)
4. HTML summary block in lifecycle HTML (via generate-html-review.py)
5. 3+ before/after comparison examples from archived WRKs

## Phases

| # | Phase | Deliverables | ACs |
|---|-------|-------------|-----|
| 1 | Canonical usage path | SKILL.md update / doc | AC 1 |
| 2 | Quality metrics schema | Template + SKILL.md | AC 2, 3 |
| 3 | Validator checks | validate-resource-pack.sh, verify-gate-evidence.py | AC 4 |
| 4 | HTML summary block | generate-html-review.py | AC 5 |
| 5 | Comparison examples | evidence/ri-comparison-examples.md | AC 6 |
| 6 | Cross-review | review-input.md + verdicts | AC 7 |

## Test Strategy

5 tests: validate-resource-pack.sh pass/fail, verify-gate-evidence.py RI gate, HTML output,
comparison examples artifact check.

## Risk

Low. All work is additive to existing skill; no breaking changes to schema (quality_signals is optional).
