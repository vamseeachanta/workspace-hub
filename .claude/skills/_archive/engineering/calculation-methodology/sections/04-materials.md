# 04 — Materials

## Purpose

Document material grades, characteristic and design property values, partial
safety factors, and traceability to certificates or code tables. Material
properties directly affect capacity calculations, so source traceability
is critical.

## Schema Fields

```yaml
materials:
  - name: string             # material description (e.g., "Line pipe steel")
    grade: string            # grade designation (e.g., "API 5L X65 PSL2")
    value: number            # characteristic property value
    unit: string             # unit of the property value
    source: string           # optional — MTC ref, code table, or test report
    partial_factor: number   # optional — material partial safety factor
    certificate: string      # optional — certificate reference
```

> **Renderer Mapping Note:** The methodology recommends rich nested structures
> with multiple properties per material, separate partial factor lists, and
> certificate arrays. The renderer uses a flat list where each entry is one
> material property row: `{name, grade, value, unit}` required, plus optional
> `source` and `partial_factor` scalars. To document multiple properties for
> one material, use multiple list entries with the same grade.

## Required Content

- Material grade
- At least SMYS and SMTS (as separate list entries)
- Source for each property (certificate or code table)
- Material partial safety factors where applicable

## Quality Checklist

- [ ] Each entry has `name`, `grade`, `value`, and `unit`
- [ ] Characteristic values come from certificates or code minima (not assumed)
- [ ] Partial factors match the safety class from section 03
- [ ] Temperature derating applied if operating above ambient
- [ ] Weld strength reduction factors included where applicable

## Example Snippet

```yaml
materials:
  - name: "Specified Minimum Yield Strength"
    grade: "API 5L X65 PSL2"
    value: 450
    unit: "MPa"
    source: "MTC-2026-0042 / API 5L Table 4"
    partial_factor: 1.15
  - name: "Specified Minimum Tensile Strength"
    grade: "API 5L X65 PSL2"
    value: 535
    unit: "MPa"
    source: "MTC-2026-0042 / API 5L Table 4"
    partial_factor: 1.15
```

## Common Mistakes

- Using nested `properties[]` and `partial_factors[]` sub-objects (renderer expects flat entries)
- Forgetting temperature derating for elevated service temperatures
- Partial factor taken from wrong safety class row in the code table
- No traceability — property listed with no source reference
- Weld strength mismatch factor omitted for girth welds
