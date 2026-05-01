# Disagreement report — plan #2554 (2026-05-01)

## Verdicts

| Provider | Verdict |
|---|---|
| claude | UNKNOWN |
| codex | UNKNOWN |
| gemini | MAJOR |

## Findings unique to each provider

A finding is 'unique to X' if its text appears in X's artifact but not
verbatim in any other provider's artifact.

### claude

(no findings unique to this provider)

### codex

(no findings unique to this provider)

### gemini

- Plan §Resource Intelligence Summary claims "Found: `docs/gtm/outreach-candidate-briefs-2026-04-28.md` (1014 lines, lane C2 output)". Glob search confirms this file does not exist anywhere at HEAD in the workspace.
- Plan §Resource Intelligence Summary claims "The current scaffold now provides that matrix at `docs/reports/gtm/2026-04-29-vessel-contractor-outreach-matrix-scaffold.md`". Glob search confirms this file does not exist at HEAD.
- Plan §Resource Intelligence Summary claims the plan requires a "targeted committed-artifact scan recorded at `docs/reports/gtm/legal-scans/2026-04-30-issue-2554-public-matrix-scan.md`" and the Evidence section claims this file "EXISTS after #2554/#2560 work". Glob search confirms this scan file does not exist at HEAD.
- Plan §Documents consulted claims `docs/BUSINESS_BRAIN.md` contains sections "§Interactive Weekly GTM Targets (line 106-112)", "§GTM-to-Code Readiness Loop (lines 114-120)", and "§Legal Sanity Gates for Public Artifacts (lines 122-132)". Reading `docs/BUSINESS_BRAIN.md` confirms it is only 102 lines long and contains none of these sections. These policies are hallucinated or reference an unmerged branch.
- Plan §Test List claims the validation script can be executed via `uv run python scripts/validation/validate_gtm_2554_matrix.py --write-artifact`. Glob search confirms `validate_gtm_2554_matrix.py` does not exist in `scripts/validation/` or anywhere else at HEAD.

