# Risk Infographic Evidence Taxonomy

Use when creating public-facing infographics from incident / safety / reliability datasets.

## Durable lesson

Do not let broad keyword matches become public risk statistics. A visually polished infographic can still be misleading if the evidence classifier overcounts by substring.

## Pattern

1. Define a named metric with a defensible scope before rendering it.
   - Weak: `weather_or_water_events` from any row containing `weather`, `sank`, or `overboard`.
   - Stronger: `explicit_storm_wave_water_ingress_pathway_events` from explicit pathway groups such as:
     - storm / hurricane / tropical storm / severe weather
     - wave / sea state / capsizing due to seas
     - flooding / water ingress / downflooding / hatch left open causing ingress
2. Keep the numerator auditable.
   - Persist `matched_incident_ids` by metric.
   - Persist `excluded_incident_ids` for tempting-but-invalid matches such as hatch controls, preventative checklist rows, or generic mooring operations.
3. Keep the denominator visible.
   - Report `N matched / total event rows`, not only a percent.
   - If fatalities/injuries are counted from matched rows, label them as `in matched rows`, not total population impact.
4. Include caveats in both the machine-readable stats JSON and the rendered HTML.
   - Example caveat: keyword/pathway classification is directional and should not be treated as regulatory root-cause attribution without source-record review.
5. Test against false positives.
   - Add fixture rows where broad substrings would overcount: `weather deck hatch seal`, `sank after fire`, `crew overboard during routine mooring`.
   - Assert these are excluded from the explicit pathway metric unless the row states the pathway directly.
6. Preserve prior draft artifacts only as references.
   - Rename them with a `reference_..._prior_draft` prefix.
   - Strip absolute local paths from any committed stats or metadata.

## Review trigger

If the infographic is intended for marketing, client, executive, or public use, run adversarial review focused on metric semantics, not just visual quality. Ask reviewers to challenge:

- whether the metric name overclaims causality,
- whether the classifier includes false positives,
- whether counts and percentages expose denominators,
- whether source document names and data provenance are visible without leaking local paths.
