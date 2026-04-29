# Focused Re-review Synthesis — Elements Wave #2541-#2544

Review artifacts:
- `.planning/quick/rereview-elements-wave-2541-2544-hardening-prompt.md`
- `scripts/review/results/2026-04-29-plan-2541-2544-codex-rereview.md`
- `scripts/review/results/2026-04-29-plan-2541-2544-gemini-rereview.md`

## Post-hardening verdicts

| Issue | Codex re-review | Gemini re-review | Approval shortlist decision |
|---:|---|---|---|
| #2541 SESA | MINOR | APPROVE | Candidate only with explicit SESA clearance before extraction/publication; vendor/TBE remains metadata-only unless cleared |
| #2542 Doris University | APPROVE | APPROVE | Candidate for bounded metadata-first/test-first execution; no OCR/full-text/figures/standards excerpts |
| #2543 DORIS Codes/Specs | APPROVE | APPROVE | Strongest approval candidate; metadata-only standards pointers/stubs from public metadata only |
| #2544 Woodfibre | APPROVE | APPROVE | Candidate for pointer/scout metadata-only subset; all extraction/abstract/quote work remains blocked pending separate plan + row-level clearance |

## Recommended execution order

1. #2543 first — establishes standards metadata discipline and is independent.
2. #2542 second — uses `engineering-standards` namespace rules from #2543.
3. #2541 third — only after/with SESA clearance; updates LNG wiki before Woodfibre.
4. #2544 fourth — pointer/scout metadata-only; runs after #2541 because both touch LNG index/log files.

## Approval wording constraint

User approval should be requested for bounded subsets only. Approval must not authorize:
- retention cleanup/source deletion (#2534 remains blocked until 2026-05-28);
- raw bulk copying into git/wiki;
- persisted full-text extraction dumps;
- OCR;
- standards clause text;
- Woodfibre abstracts/quotes/technical extraction before a separate post-scout plan and row-level clearance;
- SESA extraction/publication before the required clearance record.
