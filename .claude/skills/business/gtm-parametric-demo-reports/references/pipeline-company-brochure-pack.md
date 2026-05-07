# Pipeline-Company GTM Brochure Pack Pattern

Use when a prospect/outreach request needs client-ready pipeline/subsea brochures from existing `digitalmodel/examples/demos/gtm` assets.

## Proven asset map

Main repo:

```text
/mnt/local-analysis/workspace-hub/digitalmodel/examples/demos/gtm/
```

Strategy/outreach log repo:

```text
/mnt/local-analysis/workspace-hub/aceengineer-strategy/pipeline/conversations.md
```

### Wall thickness brochure

Ready from existing Demo 2 assets:

```text
examples/demos/gtm/demo_02_wall_thickness_multicode.py
examples/demos/gtm/results/demo_02_wall_thickness_results.json
examples/demos/gtm/output/demo_02_wall_thickness_report.html
examples/demos/gtm/media/demo_02_wall_thickness.gif
examples/demos/gtm/media/demo_02_wall_thickness_workflow.gif
```

Verified positioning facts from `demo_02_wall_thickness_results.json`:

- 72 cases.
- 6 pipe sizes: 6", 8", 10", 12", 16", 20".
- 3 code bases: DNV-ST-F101, API RP 1111, PD 8010-2.
- Internal pressure levels: 10, 15, 20, 25 MPa.
- 500 m water depth, X65, SMYS 448 MPa, SMTS 531 MPa, 1.0 mm corrosion allowance.
- Use as a multi-code screening / governing-check comparison brochure, not a final design certificate.

Suggested title: **Pipeline Wall Thickness Screening — Multi-Code Digital Calculation Pack**.

### Rigid jumper VIV brochure

Ready from existing Demo 1 results; beware the result file name is **not** `demo_01_freespan_viv_results.json`.

Correct file:

```text
examples/demos/gtm/results/demo_01_freespan_results.json
```

Supporting script/report:

```text
examples/demos/gtm/demo_01_dnv_freespan_viv.py
examples/demos/gtm/output/demo_01_freespan_report.html
examples/demos/gtm/data/rigid_jumpers.json
```

Verified positioning facts from `demo_01_freespan_results.json`:

- Demo: GTM Demo 1: DNV Freespan / VIV Screening Analysis.
- Code basis: DNV-RP-F105 (2017).
- 680 total cases, including 200 rigid jumper freespan/VIV cases.
- Jumper spans: 5, 10, 15, 20, 25, 30, 35, 40 m.
- Current velocities: 0.2, 0.4, 0.6, 0.8, 1.0 m/s.
- Jumper gap ratios: 0.5, 1.0, 2.0, 5.0, infinity.
- Status taxonomy includes PASS, INLINE_ONLY, FAIL_CF, FAIL_LOCKIN.

Suggested title: **Rigid Jumper Freespan & VIV Screening — DNV-RP-F105 Digital Assessment Pack**.

### Rigid jumper installation extension

Already has a client-pack PDF from Demo 5:

```text
examples/demos/gtm/output/client_pdf_pack_2026-05-07/05_rigid_jumper_installation_vessel_capability_digitalmodel.pdf
examples/demos/gtm/results/demo_05_jumper_installation_results.json
```

Use as a cross-link from the VIV brochure when the prospect is interested in installation suitability / vessel envelopes.

Verified positioning facts from `demo_05_jumper_installation_results.json`:

- 300 installation cases.
- 2 vessel classes.
- Water depths: 500, 1000, 1500, 2000, 2500, 3000 m.
- Hs values: 1.0, 1.5, 2.0, 2.5, 3.0 m.
- Jumper lengths: 20, 40, 60, 80, 100 m.
- Output supports GO / NO_GO installation suitability envelope messaging.

## Recommended output pack

```text
examples/demos/gtm/output/pipeline_company_pack_<YYYY-MM-DD>/
├── 00_pipeline_company_gtm_pack_index.html
├── 00_pipeline_company_gtm_pack_index.pdf
├── 01_pipeline_wall_thickness_gtm_brochure_digitalmodel.html
├── 01_pipeline_wall_thickness_gtm_brochure_digitalmodel.pdf
├── 02_rigid_jumper_viv_gtm_brochure_digitalmodel.html
├── 02_rigid_jumper_viv_gtm_brochure_digitalmodel.pdf
├── 03_rigid_jumper_installation_vessel_capability_existing_digitalmodel.pdf
├── pipeline_company_outreach_email.md
└── digitalmodel_pipeline_company_gtm_pack_<YYYY-MM-DD>.zip
```

The index should state the routing logic: wall-thickness first for pipeline design/verification teams, freespan/VIV second for rigid-jumper or span-risk teams, and the installation/vessel-suitability PDF as the optional operating-envelope extension.

## Workflow notes

1. Verify source files before claiming readiness; use JSON metadata rather than README memory.
2. If documenting prior outreach, log it in `aceengineer-strategy/pipeline/conversations.md` without personal names or PII.
3. Prefer concise prospect language: low-risk pilot, fixed-fee starter package, 30-minute review, concrete case pack.
4. Avoid desperation/underpricing language such as "survival pricing" in outreach copy.
5. Make the engineering boundary explicit: early screening, option comparison, and traceable reporting; not a replacement for engineering judgment or final certification.

## Example outreach ask

> Would you be open to a 30-minute call to review two sample capability packs: a multi-code wall thickness screen and a rigid jumper freespan/VIV screen, with optional vessel installation suitability envelopes?
