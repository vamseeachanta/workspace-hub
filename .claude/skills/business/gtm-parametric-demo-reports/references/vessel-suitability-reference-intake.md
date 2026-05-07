# Vessel Suitability Reference Intake Pattern

Use this when a GTM demo needs vessel suitability analysis but the exact external reference is unavailable or spread across raw/reference folders.

## Session pattern captured

A vessel suitability GTM request can have two different deliverables:

1. **Raw/reference intake** — identify where vessel-supporting reference material lives and add a small traceability index near the raw/reference corpus.
2. **GTM issue/plan seed** — create a prospect-facing issue that turns representative vessel data into a suitability scoring/reporting capability.

Keep those separate from the deeper engineering implementation anchor (e.g., vessel performance, RAO generation, OrcaFlex/AQWA/OrcaWave integration).

## Useful digitalmodel paths

Tracked GTM input data commonly lives under:

- `examples/demos/gtm/data/csv_hlv_vessels.json`
- `examples/demos/gtm/data/pipelay_vessels.json`
- `examples/demos/gtm/data/pipelines.json`
- `examples/demos/gtm/data/rigid_jumpers.json`
- `examples/demos/gtm/data/mudmat_structures.json`

Raw/reference material may also be mounted outside the tracked checkout, e.g. `/mnt/ace/digitalmodel`, with useful sources such as:

- `llm-wiki/orcaflex/topics/Vessels.md`
- `llm-wiki/orcaflex/topics/Vesseltypes.md`
- `llm-wiki/orcaflex/topics/Vesselmodellingoverview.md`
- `llm-wiki/papers/Buoy-Vessel-Modelling.md`
- `docs/references/literature/field_development/`
- `references/`

## Issue shape for GTM vessel suitability

A good issue requests:

- source/reference metadata normalization for vessel JSON raw data
- scoring for installation/heavy-lift and pipeline/pipelay suitability
- output report/comparison matrix with go/no-go, limiting criteria, and assumptions
- tests for deterministic scoring, metadata validation, and cached report regeneration
- explicit relationship to any deeper engineering anchor issue without duplicating its implementation plan

## Pitfall

If context compaction or missing user attachment makes the exact “this reference” unavailable, do not pretend it was reviewed. State the limitation, index only the reference material actually found, and ask for the missing PDF/URL/document if they intended a specific source.
