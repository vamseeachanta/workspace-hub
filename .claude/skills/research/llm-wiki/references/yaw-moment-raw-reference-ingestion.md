# Yaw Moment Raw-Reference Ingestion Pattern

Session learning from workspace-hub issue #2564: before implementing an engineering calculation, the user asked to mine `/mnt/ace` raw references and preserve all relevant context into the LLM wiki so implementation would not lose source rationale.

## When to use

Use this as a concrete example when:
- the task is an engineering-critical calculation or methodology issue;
- relevant standards/textbooks/PDFs live outside git under `/mnt/ace`;
- implementation is still blocked by plan-review/user-approval; and
- the user asks to preserve raw data/context in LLM wikis before coding.

## Successful sequence

1. Keep implementation blocked; do not touch calculation code while issue remains `status:plan-review`.
2. Orient in the target domain wiki:
   - `knowledge/wikis/<domain>/CLAUDE.md`
   - `knowledge/wikis/<domain>/wiki/index.md`
   - recent `knowledge/wikis/<domain>/wiki/log.md`
3. Search existing wiki pages and repo docs for the topic to avoid duplicate source/concept pages.
4. Use parallel extraction/subagents for the raw sources:
   - filename/directory scan for obvious candidates;
   - text-searchable content inspection;
   - domain/reference collection inspection.
5. Verify high-value candidates directly with metadata/text extraction before writing durable wiki pages.
6. Create a compact knowledge pack:
   - source pages for each verified reference;
   - concept pages for formulas, coordinate/sign conventions, validation metrics, and limitations;
   - a comparison/extraction page mapping source references to implementation decisions.
7. Update the issue plan/addendum with exact wiki anchors and validation result.
8. Run:
   - `uv run scripts/knowledge/llm_wiki.py status --wiki <domain>`
   - `uv run scripts/knowledge/llm_wiki.py lint --wiki <domain>`
9. Force-add ignored wiki pages only after confirming no raw PDFs/bulk data are staged.
10. Commit, push, and comment on the GitHub issue with commit SHA, wiki anchors, and validation commands.

## #2564 source classes captured

For rudder-induced ship yaw moment, useful source classes were:
- PNA Vol. III / Motions and Controllability for maneuvering fundamentals;
- USNA ship-performance course notes for coordinate/sign conventions;
- Bertram / Practical Ship Hydrodynamics for hydrodynamic limitations;
- ShipMo3D / McTaggart maneuvering report for full maneuvering-model extension path;
- ABS/IMO/USCG maneuverability references for design/regulatory context;
- OrcaFlex/OCIMF manoeuvring/current/wind-load wiki pages for separation between rudder-induced yaw and environmental yaw moments.

## Guardrails preserved for future implementation

- Scope the first implementation to preliminary rudder-induced yaw moment, e.g. `M_z = F_N * x_rudder_from_CG`.
- Do not claim ABS/IMO compliance from a simple calculator; cite those references as context only.
- Do not conflate rudder-induced yaw moment with OCIMF/OrcaFlex environmental current/wind yaw moment coefficients.
- Pin port/starboard sign convention with a non-tautological test grounded in documented axes/rudder-angle convention; `Mz(+delta) == -Mz(-delta)` alone only proves odd symmetry.
- Calculation modules using standards-derived formulas/constants need citation output or an explicit exemption/inheritance note.
