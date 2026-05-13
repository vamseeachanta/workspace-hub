# CTV / Access Operability Reference Flow

Use this when the user provides an infographic, screenshot, or non-native source about CTV/SOV access workability and asks to add it to GTM vessel suitability.

## Pattern

1. **Do not merge it into static vessel spec files by default.** CTV workability references usually describe access/landing/weather-window operability, not crane curves, RAOs, or pipelay system limits.
2. **Classify rights and GTM fitness before creating GTM artifacts.** If the source is competitor material, infographic-derived, non-native, or has unclear reuse rights, treat it as `internal_reference_only` and keep it out of prospect-facing GTM outputs until the user explicitly approves reuse.
3. **For internal/reference-only material, store it under the reference corpus** such as `references/vessel-suitability/data/ctv_operability_<site>.json` plus a synthesis note, not under `examples/demos/gtm/data/`. Include:
   - `_description`, `_version`, `_source`, `_references`
   - `_classification: internal_reference_only` or equivalent
   - `rights_guardrails` / `source_rights_status`
   - `units`
   - `site` and metocean basis
   - `operation_constraints`
   - `headline_metrics`
   - monthly/seasonal operability series if available
   - `engineering_caveats`
4. **For approved GTM-use material only, create a separate GTM input JSON** such as `examples/demos/gtm/data/ctv_operability_<site>.json` with explicit source attribution, caveats, and permitted-use notes.
5. **Add a raw/reference intake note** near the mounted/tracked reference corpus, e.g. `references/vessel-suitability/<topic>.md`, preserving source attribution and caveats.
6. **Update the reference index** (if present) so it links the raw/reference note and any approved tracked GTM data file separately.
7. **Update GTM discoverability only after the rights/GTM classification allows it.** Do not add reference-only data to GTM README/data tables or output indexes.
8. **Add focused validation tests** that check traceability, units, site/metocean basis, headline metrics, month count/order, classification/rights guardrails, and—when reference-only—that old GTM JSON/HTML/PDF/output-index surfaces are absent.

## Caveats

- Treat source-stated headline metrics as more authoritative than chart-read monthly values.
- Label image-derived monthly values as approximate/digitized until a native table/source dataset is obtained.
- Do not use prospect-facing infographic values as design-basis metocean or operability data unless source rights, assumptions, and native data are confirmed.
- Preserve external publisher attribution if the source is reused in reports or screenshots.
- If a reference-only CTV/access-operability file was previously placed under GTM paths, close the loop by removing generated/public-facing derivatives too: HTML report, PDF report, bundled PDF pack, and output-index references. Verify absence with targeted tests and grep before closing.

## Example captured

SeaOps Solutions “CTV Workability · Kincardine” infographic was initially encoded as `ctv_operability_kincardine.json` with annual `[N]` vs `[N]+[S]` operability metrics, approximate monthly values, NORA3 site basis, and a focused pytest validation file. Because it is access-operability uplift reference material rather than vessel specifications—and because GTM reuse required explicit approval—it was reclassified as reference-only and moved to `references/vessel-suitability/data/ctv_operability_kincardine.json` with a synthesis note. The old GTM JSON, HTML/PDF outputs, bundled PDF output, and output-index references were removed and protected with absence tests.
