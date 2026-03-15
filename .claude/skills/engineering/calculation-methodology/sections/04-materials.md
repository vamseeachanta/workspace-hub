# 04 — Materials

## Purpose

Document material grades, characteristic and design property values, partial
safety factors, and traceability to certificates or code tables. Material
properties directly affect capacity calculations, so source traceability
is critical.

## Schema Fields

```yaml
materials:
  - id: string                # short identifier (e.g., "pipe_steel")
    description: string
    grade: string             # e.g., "API 5L X65 PSL2"
    specification: string     # governing material standard
    properties:
      - name: string          # e.g., "SMYS"
        symbol: string        # e.g., "fy"
        characteristic: number
        design: number        # after applying material factor
        unit: string
        source: string        # MTC ref, code table, or test report
    partial_factors:
      - name: string
        symbol: string
        value: number
        reference: string     # code clause for the factor
    certificates:
      - type: string          # MTC, test_report, qualification_record
        reference: string
```

## Required Content

- Material grade and governing specification
- SMYS and SMTS (or equivalent characteristic strengths)
- Material partial safety factors with code clause reference
- Source for each property (certificate or code table)

## Quality Checklist

- [ ] Characteristic values come from certificates or code minima (not assumed)
- [ ] Design values = characteristic / material factor (show the division)
- [ ] Partial factors match the safety class from section 03
- [ ] Temperature derating applied if operating above ambient
- [ ] Weld strength reduction factors included where applicable

## Example Snippet

```yaml
materials:
  - id: "line_pipe"
    description: "12-inch export pipeline"
    grade: "API 5L X65 PSL2"
    specification: "API 5L 46th Edition"
    properties:
      - name: "Specified Minimum Yield Strength"
        symbol: "SMYS"
        characteristic: 450
        design: 415
        unit: "MPa"
        source: "MTC-2026-0042 / API 5L Table 4"
      - name: "Specified Minimum Tensile Strength"
        symbol: "SMTS"
        characteristic: 535
        design: 493
        unit: "MPa"
        source: "MTC-2026-0042 / API 5L Table 4"
    partial_factors:
      - name: "Material resistance factor"
        symbol: "gamma_m"
        value: 1.15
        reference: "DNV-ST-F101 Table 5-5, safety class medium"
```

## Common Mistakes

- Using nominal yield strength instead of SMYS from certificate
- Forgetting temperature derating for elevated service temperatures
- Partial factor taken from wrong safety class row in the code table
- No traceability — property listed with no source reference
- Weld strength mismatch factor omitted for girth welds
