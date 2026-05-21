# Generic OCIMF workbook adapter TDD for engineering reports

Use this reference when an approved engineering-report issue depends on a licensed OCIMF workbook or similar off-repo standards workbook, especially when generated HTML/DOCX/PDF artifacts are part of acceptance.

## Durable lesson

A green report-generation test is not enough when the numerical model still uses inline placeholder formulas. The RED test must prove that coefficients are resolved from the approved workbook route at calculation time, not merely that stale placeholder names were removed or that generated report text looks current.

## Source-boundary pattern

1. Keep raw licensed artifacts off-repo.
   - Use an explicit absolute/source route in provenance and fail-closed preflight.
   - Do not commit the workbook, PDFs, or a reusable extracted coefficient corpus.
2. Add a small workbook adapter rather than embedding formulas in the report generator.
   - The adapter should expose selected table IDs/families, selected heading/depth/draft basis, units/sign convention, and interpolation method.
   - The report layer should consume resolved coefficients plus provenance, not reconstruct source math.
3. Use independent expected values in tests.
   - Read a small number of workbook cells/rows in test setup or a locked issue-specific fixture that is not produced by the production function under test.
   - Include at least one assertion that would fail if a trig placeholder such as `sin/cos(heading)` were still driving coefficients.
4. Preserve generic/reference limitations in generated artifacts.
   - If the workbook data is generic OCIMF/reference tanker-current data, report it as such.
   - Do not call it asset-specific, client-specific, or SIROCCO-specific unless an approved source proves that linkage.
5. Check every emitted surface before closeout.
   - CSV/JSON numerical output, provenance JSON, manifest, Markdown, HTML, DOCX, and PDF must all reflect the same source-gated model and limitation language.

## Example acceptance checks

- Default current speed and heading/rudder sweeps match the issue comments or approved plan.
- Coefficients for at least one representative heading are interpolated from the workbook-selected basis.
- Sign convention is asserted for positive and negative headings.
- Missing workbook/source route raises a clear calculation/provenance error before report artifacts are claimed complete.
- No tracked output serializes a reusable coefficient corpus; only issue-specific outputs and provenance pointers are produced.

## Closeout warning

After context compaction or tool-call exhaustion, preserve the exact gap: distinguish `reports generated and focused tests passed` from `coefficient adapter source-gated and all artifacts verified`. If inline formulas remain, the issue is not ready for adversarial review, commit, push, or close.