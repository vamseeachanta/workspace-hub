# #2112 online field-development data-gate progress report

Issue: #2112  
Parent: #2055  
Date: 2026-04-29

## Result

Built a provisional online-research seed dataset, then ran adversarial review. The structural validator passes, but the substantive data-quality gate does **not** pass yet.

Artifacts:

- Candidate dataset: `data/field-development/gom-field-development-unblock-2112.json`
- Truthfulness/data-gate validator: `scripts/knowledge/tests/test_field_development_unblock_2112.py`
- This report: `docs/reports/field-development-unblock-2112.md`

Current gate state:

- records_with_all_required_structural: 10
- records_with_all_required_public_sourced_and_semantically_consistent: 0
- status:needs-data should remain on #2055 and #2112 until the remaining primary-source backfill is complete.

## Why this is not closed yet

The initial dataset has useful public-source leads, but adversarial review classified it as **MAJOR** because several fields are not yet suitable for engineering or benchmark use:

1. `num_manifolds` is often proxy-coded from drill centres, risers, field centres, or phases rather than a directly sourced subsea-manifold count.
2. `tieback_distance_km` mixes inconsistent meanings: well-to-host distance, export pipeline length, field/platform proximity, host-to-host separation, and placeholder host-local zeroes.
3. `cost_usd_bn` mixes directly sourced project costs with cost-class seeds and phase-only costs.
4. Some basis notes rely on repository scan snippets or search-result snippets instead of durable primary source text.

## Data policy

No invented values are accepted as final. Proxy/cost-class/placeholder values are now explicitly treated as candidate leads only, not as unblock evidence.

The candidate dataset is useful because it identifies likely source URLs and the fields that need primary-source replacement, but it is not yet correlation-ready for #2055.

## Validation summary

Target validator:

```bash
uv run pytest scripts/knowledge/tests/test_field_development_unblock_2112.py -q
```

The validator now checks that the artifact remains honest about the blocked gate:

- 10 structurally complete GoM candidate records exist.
- The top-level gate status remains `blocked_adversarial_review_failed`.
- The report explicitly keeps `status:needs-data` in place.
- The dataset does not claim that proxy-coded data has unblocked #2055.

## Next #2112 execution path

Continue #2112 by replacing candidate/proxy values with primary-source values. Priority order:

1. Mad Dog Phase 2 / Argos — strongest current public source set for wells, drill centres, cost, and host separation.
2. Appomattox — strong source for trees/manifolds; still needs semantically correct tieback metric and cost.
3. Thunder Horse — strong trees/tieback expansion data; still needs base/project cost and normalized manifold meaning.
4. Stones / Lucius / Perdido — need OTC/SPE/operator fact-sheet extraction for manifold and tieback definitions.
5. Atlantis / Na Kika / Mars — replace placeholder zeroes and proxy field-centre values or drop from the initial 10-record accepted set.

Acceptance target before removing `status:needs-data` from #2055:

- At least 10 records where `num_trees`, `num_manifolds`, `tieback_distance_km`, and `cost_usd_bn` are direct-source or defensibly normalized with a consistent field definition.
- A normalized definition for `tieback_distance_km`, e.g. "maximum subsea production system offset from receiving host"; export-pipeline lengths and host-to-host distances must move to separate fields.
- A normalized definition for `num_manifolds`, e.g. "subsea production/injection manifold structures"; drill centres/risers/field centres must move to separate fields.
- Confidence/source notes retained per field.

## Residual risk

Residual risk level: Medium.

The source landscape is feasible, but completing the gate requires deeper source extraction than search snippets: OTC/SPE papers, operator fact sheets, offshore project pages, and/or public GIS/infrastructure records.
