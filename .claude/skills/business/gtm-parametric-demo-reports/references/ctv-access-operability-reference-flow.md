# CTV / Access Operability Reference Flow

Use this when the user provides an infographic, screenshot, or non-native source about CTV/SOV access workability and asks to add it to GTM vessel suitability.

## Pattern

1. **Do not merge it into static vessel spec files by default.** CTV workability references usually describe access/landing/weather-window operability, not crane curves, RAOs, or pipelay system limits.
2. **Create a separate GTM input JSON** such as `examples/demos/gtm/data/ctv_operability_<site>.json` with:
   - `_description`, `_version`, `_source`, `_references`
   - `units`
   - `site` and metocean basis
   - `operation_constraints`
   - `headline_metrics`
   - monthly/seasonal operability series if available
   - `gtm_storyline`
   - `engineering_caveats`
3. **Add a raw/reference intake note** near the mounted reference corpus, e.g. `/mnt/ace/digitalmodel/references/vessel-suitability/<topic>.md`, preserving source attribution and caveats.
4. **Update the reference index** (if present) so it links both the raw/reference note and the tracked GTM data file.
5. **Update GTM discoverability** by adding the dataset to the GTM README/data table and by commenting on the relevant GTM issue rather than opening a duplicate.
6. **Add a focused validation test** that checks traceability, units, site/metocean basis, headline metrics, month count/order, and GTM storyline tags.

## Caveats

- Treat source-stated headline metrics as more authoritative than chart-read monthly values.
- Label image-derived monthly values as approximate/digitized until a native table/source dataset is obtained.
- Do not use prospect-facing infographic values as design-basis metocean or operability data unless source rights, assumptions, and native data are confirmed.
- Preserve external publisher attribution if the source is reused in reports or screenshots.

## Example captured

SeaOps Solutions “CTV Workability · Kincardine” infographic was encoded as `ctv_operability_kincardine.json` with annual `[N]` vs `[N]+[S]` operability metrics, approximate monthly values, NORA3 site basis, and a focused pytest validation file. The data was kept separate from `csv_hlv_vessels.json` and `pipelay_vessels.json` because it describes access-operability uplift, not vessel specifications.
