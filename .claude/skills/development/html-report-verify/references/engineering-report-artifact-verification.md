# Engineering Report Artifact Verification

Use this reference when verifying generated engineering reports that emit a manifest plus HTML/PDF/CSV/JSON artifacts.

## Trigger

A report generator writes multiple artifacts such as:
- `*_results.csv`
- `*_results.json`
- `*_provenance.json`
- `*_report.md`
- `*_report.html`
- `*_report.pdf`
- `*_manifest.json`

## Verification sequence

1. **Regeneration evidence**
   - Capture the exact command, working directory, and output paths.
   - Record row counts and governing extrema printed by the generator when available.
   - Preserve non-blocking warnings separately from failures. Example: solver-license warnings may be irrelevant when the report uses packaged/static data only, but they still belong in the caveat list.

2. **Manifest integrity**
   - Parse the manifest JSON.
   - Confirm every referenced artifact exists.
   - Confirm no manifest path points outside the expected report output directory unless explicitly intended.

3. **File existence and readability**
   - Check each expected artifact exists and has non-zero size.
   - For CSV/JSON, parse enough to verify row count and required keys.
   - For HTML, parse with Python stdlib `html.parser` if browser verification is unavailable.
   - For PDF, verify non-zero size and extract text or metadata when a PDF tool is available; otherwise label PDF verification as existence-only, not content-verified.

4. **HTML structural checks without browser tools**
   - Confirm non-empty `<title>`.
   - Confirm at least one `h1`/`h2`.
   - Confirm expected report-specific section headings are present.
   - Confirm expected generated figures/schematics appear as inline SVG, image tags, or labeled sections.
   - Confirm provenance/caveat text is visible if the calculation is bounded or uses static/package data.

5. **PDF checks**
   - Prefer text extraction for report-specific headings and schematic captions.
   - If extraction is unavailable, report only: path, size, and conversion artifact timestamp; do not claim content fidelity.

6. **Resultant-force report checks**
   - For current/rudder force comparison reports, verify individual force components and resultant forces are both present.
   - Verify schematics show both ship/current heading convention and rudder angle convention.
   - Verify the basecase/current magnitude selected by the user is clearly identified in the report.

## Reporting pattern

Return a compact status with:
- `Current state`
- `Evidence`
- `Caveats / blockers`
- `Recommended next action`

Do not claim HTML/PDF content verification until the content was actually parsed, browser-rendered, or text-extracted.