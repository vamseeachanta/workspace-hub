# 03 — Design Basis

## Purpose

Establish the normative framework: which codes and standards govern the
calculation, design life, safety class, and load combinations. This section
anchors every subsequent calculation step to a specific code clause.

## Schema Fields

```yaml
design_basis:
  codes:                       # list of dicts or list of strings
    - code: string             # standard identifier (e.g., "DNV-ST-F101")
      edition: string          # edition year (e.g., "2021-08")
      clause: string           # optional — applicable clause
  design_life: string          # scalar (e.g., "25 years")
  safety_class: string         # optional — e.g., "medium"
  load_combinations:           # optional — list of strings
    - string
  environment: string          # optional — environmental description
```

> **Renderer Mapping Note:** The methodology recommends richer structures for
> codes (title, role), design life (value + unit), safety class (class +
> justification), and load combinations (id, loads with factors). The renderer
> uses flat structures: `codes[].code` (not `.standard`), no `.title` or
> `.role`, `design_life` as a scalar string, and `load_combinations` as a
> simple list of strings. Encode rich details into the string values.

## Required Content

- At least one code with edition year
- Design life
- Safety class with justification (encode in the string value)

## Quality Checklist

- [ ] Code edition includes the year or date (not just the standard number)
- [ ] Code field uses `code` key (not `standard`)
- [ ] Design life is a scalar string, not a nested object
- [ ] Load combination factors are embedded in the string descriptions
- [ ] Load combinations cover all relevant limit states (ULS, SLS, ALS/FLS)

## Example Snippet

```yaml
design_basis:
  codes:
    - code: "DNV-ST-F101"
      edition: "2021-08"
      clause: "Section 5.4.2"
    - code: "DNV-RP-F105"
      edition: "2017-06"
      clause: "Section 4"
  design_life: "25 years"
  safety_class: "medium — hydrocarbon pipeline in non-populated area"
  load_combinations:
    - "LC-01: System test — mill pressure test (factor 1.0)"
    - "LC-02: Operating — max design pressure + functional loads (factor 1.1)"
  environment: "North Sea, water depth 80-120m, seawater temperature 4-12 degC"
```

## Common Mistakes

- Using `standard` instead of `code` as the key name
- Nesting `design_life` as `{value: 25, unit: "years"}` instead of scalar string
- Standard cited without edition year — different editions have different factors
- Safety class stated without justification for why that class was selected
- Load combinations as dicts with nested load objects instead of simple strings
