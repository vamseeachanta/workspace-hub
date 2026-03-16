# Stage 6: Reporting

> Maps to calculation-methodology Phase 6 (sections 14-16)
> Hands off to calculation-report skill for rendering

## Entry

- Extracted results and validation verdict from Stage 5
- Analysis YAML from Stage 1

## Generate Calculation Report YAML

The `generate-calc-yaml.py` script combines:
- Analysis definition (Stage 1 YAML) → metadata, inputs, methodology, assumptions
- Solver results (Stage 4-5) → outputs with computed values
- Validation verdicts → pass/fail status on each output
- Convergence data → charts (residual history)

```bash
uv run --no-project python scripts/openfoam-analysis/generate-calc-yaml.py \
    --analysis my-analysis.yaml \
    --case-dir ~/foam/run/my-case/ \
    --output my-analysis-calc.yaml
```

## Calculation YAML Sections (auto-populated)

| Section | Source | Content |
|---------|--------|---------|
| `metadata` | Analysis YAML | Title, doc_id, revision, date, author, standard |
| `inputs` | Analysis YAML → flow, geometry | All input parameters with sources |
| `methodology` | Analysis YAML → solver config | Standard ref, equations, solver description |
| `outputs` | Solver results | Cd, Fd, pressures — with pass_fail against limits |
| `assumptions` | Analysis YAML | Listed assumptions |
| `references` | Auto-generated | Standards, OpenFOAM version, validation refs |
| `charts` | Solver log | Residual convergence plot, force time history |
| `data_tables` | Post-processing | Force coefficients, probe data |

## Render Report

```bash
# Validate YAML
uv run --no-project python -c "
import yaml
with open('my-analysis-calc.yaml') as f:
    d = yaml.safe_load(f)
for s in ['metadata','inputs','methodology','outputs','assumptions','references']:
    assert s in d, f'Missing: {s}'
print('PASS')
"

# Generate HTML report
uv run --no-project python scripts/reporting/generate-calc-report.py my-analysis-calc.yaml

# Open in browser
xdg-open my-analysis-calc.html 2>/dev/null || echo "Report: my-analysis-calc.html"
```

## Exit Gate

- [ ] Calculation YAML passes schema validation
- [ ] All output values populated (no `null` remaining)
- [ ] Pass/fail status set on acceptance-critical outputs
- [ ] HTML report generated successfully
- [ ] Report opened or path reported to user
