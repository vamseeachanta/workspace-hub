---
name: dark-intelligence-workflow-step-6-implement
description: "Sub-skill of dark-intelligence-workflow: Step 6 \u2014 Implement (+1)."
version: 1.0.0
category: data
type: reference
scripts_exempt: true
---

# Step 6 — Implement (+1)

## Step 6 — Implement


Build the clean implementation using extracted methodology and test data.

**Process:**
1. Choose target repo based on category (see repo-map.yaml)
2. Write failing tests first (from Step 5 output)
3. Implement equations from the archive YAML
4. Run tests until green
5. Refactor while keeping tests green

**Target repo selection:**

| Category | Primary repo |
|----------|-------------|
| Structural, geotechnical, subsea, pipeline | digitalmodel |
| Shared utilities, unit conversion, common calcs | assetutilities |
| Energy market, drilling, production data | worldenergydata |
| Financial analysis, portfolio | assethold |


## Step 7 — Produce Calc Report


Generate a calculation-report YAML from the extracted data.

1. Use the `data/calculation-report` skill for the report template
2. Populate with equations, inputs, outputs from the archive YAML
3. Include worked examples as verification cases
4. Validate the YAML against the calc-report schema
5. Generate HTML report for review
