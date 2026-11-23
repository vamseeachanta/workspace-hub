# 15 — Data Tables

## Purpose

Format tabular data for clarity and consistency. Tables present input
summaries, parametric results, and comparison data. Good table formatting
makes calculations reviewable and reduces transcription errors.

## Schema Fields

```yaml
data_tables:
  - id: string                 # optional — table identifier (e.g., "TBL-01")
    title: string              # descriptive table title
    columns:
      - name: string           # column header text
        unit: string           # optional — unit in header, not in cells
    rows:
      - list                   # values matching column order
```

> **Renderer Mapping Note:** The methodology recommends `columns[].header`
> (not `.name`), plus `.format`, `.alignment`, `.description`, `.source`,
> and `.notes` per column. The renderer uses `columns[].name` (not `.header`)
> and only consumes `.name` and optional `.unit`. The `rows` field is the
> same: a list of lists matching column order.

## Required Content

- Table title
- Column headers with units (units in headers via `unit` field, not in cells)
- Row data matching column order

## Quality Checklist

- [ ] Column key is `name` (not `header`)
- [ ] Units appear in column `unit` field, not repeated in every cell
- [ ] Numeric columns have consistent precision in the data
- [ ] Table has a descriptive title
- [ ] Table is referenced in the calculation text (not orphaned)

## Example Snippet

```yaml
data_tables:
  - id: "damage_contributors"
    title: "Top Damage Contributors"
    columns:
      - name: "Stress Range"
        unit: "MPa"
      - name: "Cycles Applied"
        unit: "-"
      - name: "Cycles to Failure"
        unit: "-"
      - name: "Damage Fraction"
        unit: "-"
      - name: "Cumulative Damage"
        unit: "-"
    rows:
      - [80, 1.0e5, 2.5e6, 0.040, 0.040]
      - [70, 3.0e5, 4.1e6, 0.073, 0.113]
      - [60, 8.0e5, 7.2e6, 0.111, 0.224]
```

## Common Mistakes

- Using `header` instead of `name` for column key (renderer requires `name`)
- Including `format`, `alignment`, `description`, `source`, or `notes` per
  column (not consumed by renderer — silently dropped)
- Units in every cell instead of in the column `unit` field
- Inconsistent decimal places within a column
- Table not referenced from the calculation text
