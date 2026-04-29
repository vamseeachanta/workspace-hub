# Lane B — #2555 review-readiness patch summary

## What changed
- Patched `docs/plans/2026-04-29-issue-2555-vessel-capability-charts.md` to:
  - fix the TDD grep check to `^### Chart C`
  - clarify provider-review acceptance criteria with an explicit unavailable-provider fallback
  - name the future non-`digitalmodel/` render entry point as `scripts/gtm/render_brochure_charts.py`
  - lock brochure asset home to `docs/reports/gtm/assets/` unless review rejects it
  - require the storyboard to distinguish headline numbers verified now vs re-verified later
- Patched `docs/reports/gtm/2026-04-29-vessel-capability-chart-storyboard.md` to:
  - mirror the locked asset home and render entry point
  - add verification-scope notes for each chart headline
  - update C1 caption to include API RP 1111 where shallow-pipelay screening is involved
  - restate provider-review fallback and render-time headline recomputation discipline

## Diff summary
- Plan: tightened review-readiness gates and removed the previously ambiguous implementation home.
- Storyboard: made the evidence boundary explicit by separating currently verified headline facts from render-time revalidation requirements.

## Remaining blockers
- Live provider-review evidence is still incomplete: Codex/Gemini artifacts remain unavailable, so `status:plan-review` is still blocked until the clarified fallback requirement is satisfied.
- `scripts/gtm/render_brochure_charts.py` and `docs/reports/gtm/assets/` are specified but intentionally not created in this planning-only lane.

## Review readiness
- **Ready for Gemini/Codex review:** Yes.
- **Ready for `status:plan-review`:** No, not until live provider-review evidence exists under the clarified acceptance criterion.

## Files modified
- `docs/plans/2026-04-29-issue-2555-vessel-capability-charts.md`
- `docs/reports/gtm/2026-04-29-vessel-capability-chart-storyboard.md`
- `docs/plans/overnight-prompts/2026-04-29-reverse-prompt-48h/results/lane-b-2555-summary.md`
