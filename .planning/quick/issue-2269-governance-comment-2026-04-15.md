Governance update:

- A canonical local draft plan now exists for #2269:
  - `docs/plans/2026-04-15-issue-2269-openfoam-v2312-baseline-workflow-and-validation.md`
- The local planning index now records #2269 as `draft`, which is the honest local state until provider review artifacts exist.
- This issue was previously in earlier-stage drift: live `status:plan-review` without a canonical local plan artifact or any provider review artifacts.

Next step
- run adversarial plan review (Claude + Codex + Gemini) on the new draft, revise if needed, then restore/keep `status:plan-review` based on actual review state rather than drift.
