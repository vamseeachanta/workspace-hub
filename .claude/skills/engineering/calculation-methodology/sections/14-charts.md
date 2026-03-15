# 14 — Charts

## Purpose

Guide visualization of calculation results. Charts communicate trends,
comparisons, and sensitivities more effectively than tables of numbers.
This section specifies chart type selection, formatting standards, and
content requirements.

## Schema Fields

```yaml
charts:
  - id: string                 # chart identifier (e.g., "FIG-01")
    title: string
    type: enum                 # line | bar | scatter | contour | tornado | waterfall
    data_source: string        # section or calculation step reference
    axes:
      x:
        label: string
        unit: string
        range: [number, number]
      y:
        label: string
        unit: string
        range: [number, number]
    series:
      - name: string
        description: string
    annotations:
      - type: enum             # limit_line | data_label | region
        value: number
        label: string
    notes: string              # interpretation or context for the chart
```

## Required Content

- Chart title describing what is shown
- Axis labels with units
- Data source traceability to a calculation section
- At least limit lines or design criteria shown on the chart

## Quality Checklist

- [ ] Chart type matches the data relationship (see selection guide below)
- [ ] Both axes have labels and units
- [ ] Design limits or code criteria are shown as reference lines
- [ ] Legend is present when multiple series are plotted
- [ ] Chart can be understood without reading the full calculation text

## Chart Type Selection Guide

| Data relationship              | Recommended chart type |
|-------------------------------|----------------------|
| Parameter vs continuous variable | Line chart          |
| Categorical comparison         | Bar chart            |
| Correlation between variables   | Scatter plot         |
| Parameter influence ranking     | Tornado chart        |
| Spatial distribution            | Contour plot         |
| Incremental contributions       | Waterfall chart      |

## Example Snippet

```yaml
charts:
  - id: "FIG-01"
    title: "Burst Utilization vs Corrosion Allowance"
    type: line
    data_source: "section 10, corrosion allowance sweep"
    axes:
      x:
        label: "Corrosion Allowance"
        unit: "mm"
        range: [0, 8]
      y:
        label: "Utilization Ratio"
        unit: "dimensionless"
        range: [0, 1.0]
    series:
      - name: "Burst utilization"
        description: "DNV-ST-F101 burst check utilization"
    annotations:
      - type: limit_line
        value: 1.0
        label: "Unity limit"
    notes: "Design passes for corrosion allowance up to 7.2 mm"
```

## Common Mistakes

- Missing axis labels or units
- Chart type does not match the data (e.g., bar chart for continuous data)
- No design limit reference lines — chart shows data without context
- Axis range auto-scaled so that important features are not visible
- Chart referenced in text but not included in the document
