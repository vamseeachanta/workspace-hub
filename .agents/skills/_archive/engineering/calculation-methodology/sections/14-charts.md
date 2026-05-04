# 14 — Charts

## Purpose

Guide visualization of calculation results. Charts communicate trends,
comparisons, and sensitivities more effectively than tables of numbers.
This section specifies chart type selection, formatting standards, and
content requirements.

## Schema Fields

```yaml
charts:
  - id: string                 # chart identifier (e.g., "sn_curve")
    title: string              # chart title
    type: enum                 # line | bar | scatter | log_log
    x_label: string            # x-axis label
    y_label: string            # y-axis label
    datasets:                  # one or more data series
      - label: string          # series legend label
        data: list             # [[x,y], [x,y], ...] coordinate pairs
        color: string          # optional — hex color (e.g., "#0f766e")
    x_unit: string             # optional — x-axis unit
    y_unit: string             # optional — y-axis unit
    x_scale: enum              # optional — "linear" (default) | "log"
    y_scale: enum              # optional — "linear" (default) | "log"
```

> **Renderer Mapping Note:** The methodology recommends `axes` (nested x/y
> objects with label/unit/range), `series[]` (with name/description), and
> `annotations[]` (limit lines, data labels). The renderer uses flat
> `x_label`/`y_label` fields, `datasets[]` with `{label, data}` (not
> `series`), and does not support `annotations` or `axes` objects. Chart type
> enum is `line|bar|scatter|log_log` (not `contour|tornado|waterfall`).
> The `log_log` type renders as a scatter chart with logarithmic axes.

## Required Content

- Chart `id` and descriptive `title`
- `x_label` and `y_label` with units
- At least one dataset with `label` and `data` points
- Appropriate `type` for the data relationship

## Quality Checklist

- [ ] Chart `type` is one of: `line`, `bar`, `scatter`, `log_log`
- [ ] Uses `x_label`/`y_label` (not nested `axes` object)
- [ ] Uses `datasets[]` with `{label, data}` (not `series[]`)
- [ ] `data` is a list of `[x, y]` coordinate pairs
- [ ] Legend labels are descriptive when multiple datasets are plotted

## Chart Type Selection Guide

| Data relationship              | Recommended chart type |
|-------------------------------|----------------------|
| Parameter vs continuous variable | `line`              |
| Categorical comparison         | `bar`                |
| Correlation between variables   | `scatter`            |
| S-N curves, log-scale data     | `log_log`            |

## Example Snippet

```yaml
charts:
  - id: "sn_curve"
    title: "S-N Curve (DNV D — Seawater + CP)"
    type: log_log
    x_label: "Stress Range"
    y_label: "Cycles to Failure"
    x_unit: "MPa"
    y_unit: "cycles"
    x_scale: log
    y_scale: log
    datasets:
      - label: "DNV D Curve"
        data: [[10, 1.58e9], [20, 1.97e8], [50, 1.26e7], [100, 1.58e6]]
        color: "#0f766e"
      - label: "Applied Stress Ranges"
        data: [[30, 5.0e7], [50, 1.0e7], [80, 2.5e6], [120, 8.0e5]]
        color: "#b91c1c"
```

## Common Mistakes

- Using nested `axes: {x: {label, unit, range}, y: ...}` instead of flat
  `x_label`/`y_label` fields
- Using `series[]` instead of `datasets[]`
- Including `annotations[]` (not consumed by renderer)
- Using unsupported types (`contour`, `tornado`, `waterfall`)
- Missing axis labels or units
