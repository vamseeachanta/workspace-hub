# 15 — Data Tables

## Purpose

Format tabular data for clarity and consistency. Tables present input
summaries, parametric results, and comparison data. Good table formatting
makes calculations reviewable and reduces transcription errors.

## Schema Fields

```yaml
data_tables:
  - id: string                 # table identifier (e.g., "TBL-01")
    title: string
    description: string
    columns:
      - header: string
        unit: string           # unit in header, not in cells
        format: string         # e.g., "0.000", "integer", "2 d.p."
        alignment: enum        # left | center | right
    rows:
      - list                   # values matching column order
    source: string             # data source reference
    notes:
      - string                 # footnotes or clarifications
```

## Required Content

- Table identifier and descriptive title
- Column headers with units (units in headers, never in cell values)
- Consistent number formatting within each column
- Source reference for the data

## Quality Checklist

- [ ] Units appear in column headers, not repeated in every cell
- [ ] Number formatting is consistent (same decimal places per column)
- [ ] Numeric columns are right-aligned for easy comparison
- [ ] Table has a source reference (section, document, or standard)
- [ ] Table is referenced in the calculation text (not orphaned)

## Example Snippet

```yaml
data_tables:
  - id: "TBL-01"
    title: "Wall Thickness Check Summary"
    description: "Summary of all pressure checks with utilization ratios"
    columns:
      - header: "Check"
        unit: ""
        format: "text"
        alignment: left
      - header: "Capacity"
        unit: "MPa"
        format: "0.0"
        alignment: right
      - header: "Demand"
        unit: "MPa"
        format: "0.0"
        alignment: right
      - header: "Utilization"
        unit: ""
        format: "0.000"
        alignment: right
      - header: "Status"
        unit: ""
        format: "text"
        alignment: center
    rows:
      - ["Burst", 55.8, 34.5, 0.618, "PASS"]
      - ["Collapse", 42.3, 12.1, 0.286, "PASS"]
      - ["Combined", 48.1, 36.2, 0.752, "PASS"]
    source: "Section 09 output summary"
    notes:
      - "Utilization = Demand / Capacity"
      - "All checks per DNV-ST-F101 (2021)"
```

## Common Mistakes

- Units in every cell instead of in the column header
- Inconsistent decimal places within a column (e.g., 55.8, 42.31, 48)
- Numeric data left-aligned, making decimal alignment difficult
- Table not referenced from the calculation text
- Missing title — table cannot be cross-referenced
