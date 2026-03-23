# Stage 17: User Review - Implementation — Gotchas

## No-Bypass Rules
- No user-review acceptance unless the completed HTML was opened in the default browser.
- No user-review completion unless the Gate-Pass Stage Status section was reviewed with the user and gaps called out.
- No user-review acceptance unless relevant review artifacts are pushed to `origin`.
- HTML verification parameter is required (WRK>=624).

## Operational Lessons
- All future work from Stage 15 must be captured before Stage 17 approval.
- Push to origin before asking for review — remote visibility is required.

## Edge Cases
- If HTML generation fails, debug before proceeding — no close without HTML.
