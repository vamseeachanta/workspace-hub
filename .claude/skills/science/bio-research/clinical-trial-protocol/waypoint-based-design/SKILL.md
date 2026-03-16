---
name: clinical-trial-protocol-waypoint-based-design
description: 'Sub-skill of clinical-trial-protocol: Waypoint-Based Design (+2).'
version: 1.0.0
category: science
type: reference
scripts_exempt: true
---

# Waypoint-Based Design (+2)

## Waypoint-Based Design


All analysis data is stored in `waypoints/` directory as JSON/markdown files:

```
waypoints/
├── intervention_metadata.json           # Intervention info, status, initial context
├── 01_clinical_research_summary.json   # Similar trials, FDA guidance, recommendations
├── 02_protocol_foundation.md            # Protocol sections 1-6 (Step 2)
├── 03_protocol_intervention.md          # Protocol sections 7-8 (Step 3)
├── 04_protocol_operations.md            # Protocol sections 9-12 (Step 4)
├── 02_protocol_draft.md                 # Complete protocol (concatenated in Step 4)
├── 02_protocol_metadata.json            # Protocol metadata
└── 02_sample_size_calculation.json      # Statistical sample size calculation
```

**Rich Initial Context Support:**
Users can provide substantial documentation, technical specifications, or research data when initializing the intervention (Step 0). This is preserved in `intervention_metadata.json` under the `initial_context` field. Later steps reference this context for more informed protocol development.


## Modular Subskill Steps


Each step is an independent skill in `references/` directory:

```
references/
├── 00-initialize-intervention.md    # Collect device or drug information
├── 01-research-protocols.md         # Clinical trials research and FDA guidance
├── 02-protocol-foundation.md        # Protocol sections 1-6 (foundation, design, population)
├── 03-protocol-intervention.md      # Protocol sections 7-8 (intervention details)
├── 04-protocol-operations.md        # Protocol sections 9-12 (assessments, statistics, operations)
└── 05-generate-document.md          # NIH Protocol generation
```


## Utility Scripts


```
scripts/
└── sample_size_calculator.py   # Statistical power analysis (validated)
```
