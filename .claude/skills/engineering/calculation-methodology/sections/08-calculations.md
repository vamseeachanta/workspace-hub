# 08 — Calculations

## Purpose

Execute the methodology step-by-step with clause references, numeric
substitutions, intermediate results, and hand-checks. This is the core
computational section — every step must be traceable and reproducible.

## Schema Fields

```yaml
calculations:
  - id: string                # step identifier (e.g., "CALC-01")
    description: string
    reference: string         # code clause or equation from section 07
    formula: string           # symbolic equation
    substitution: string      # equation with numbers substituted
    result:
      value: number
      unit: string
    intermediate_results:
      - name: string
        value: number
        unit: string
    hand_check:
      method: string          # e.g., "order of magnitude", "simplified formula"
      expected_range: string
      status: enum            # consistent | inconsistent
    notes: string             # clarifications or code interpretation
```

## Required Content

- Sequential calculation steps with clause references
- Symbolic formula followed by numeric substitution
- Intermediate results shown (not just final answer)
- At least one hand-check or sanity check per major calculation

## Quality Checklist

- [ ] Each step cites the specific code clause or equation number
- [ ] Symbolic form precedes numeric substitution (reviewer sees the formula)
- [ ] Intermediate results are shown and have units
- [ ] Order-of-magnitude or hand-check confirms the computed result
- [ ] Unit consistency is maintained throughout (no silent conversions)

## Example Snippet

```yaml
calculations:
  - id: "CALC-01"
    description: "Corroded wall thickness"
    reference: "DNV-ST-F101 Sec. 5.4.2"
    formula: "t_1 = t_nom - t_fab - t_corr"
    substitution: "t_1 = 20.6 - 1.0 - 3.0"
    result:
      value: 16.6
      unit: "mm"
    hand_check:
      method: "Direct subtraction — trivially verifiable"
      expected_range: "15–20 mm"
      status: consistent

  - id: "CALC-02"
    description: "Pressure containment resistance"
    reference: "DNV-ST-F101 Eq. 5.8"
    formula: "p_b = (2 * t_1) / (D_o - t_1) * f_cb * (2 / sqrt(3))"
    substitution: "p_b = (2 × 16.6) / (323.9 - 16.6) × 450 × 1.1547"
    result:
      value: 55.8
      unit: "MPa"
    intermediate_results:
      - name: "Geometry ratio 2t/(D-t)"
        value: 0.1081
        unit: "dimensionless"
    hand_check:
      method: "Barlow approximation: p = 2*SMYS*t/D"
      expected_range: "40–60 MPa"
      status: consistent
```

## Common Mistakes

- Showing only final result without intermediate steps
- Missing code clause reference — reviewer cannot trace the formula
- No hand-check — a wrong decimal place goes unnoticed
- Unit conversion done silently mid-calculation (e.g., mm to m without note)
- Copy-paste errors in substitution not caught because intermediates are hidden
