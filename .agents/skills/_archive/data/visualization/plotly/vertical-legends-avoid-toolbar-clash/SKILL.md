---
name: plotly-vertical-legends-avoid-toolbar-clash
description: 'Sub-skill of plotly: Vertical Legends (Avoid Toolbar Clash) (+5).'
version: 1.0.0
category: data-visualization
type: reference
scripts_exempt: true
---

# Vertical Legends (Avoid Toolbar Clash) (+5)

## Vertical Legends (Avoid Toolbar Clash)


Horizontal legends at the top clash with Plotly's toolbar (zoom, pan, etc.).
Place legends vertically on the right side:
```python
fig.update_layout(
    legend=dict(
        orientation="v",
        yanchor="top", y=1.0,
        xanchor="left", x=1.02,
        font=dict(size=10),
        tracegroupgap=2,  # compact vertical spacing
    ),
    margin=dict(l=50, r=140, t=30, b=30),  # r=140+ for legend room
)
```

## Heading-First Trace Ordering for Multi-Solver Plots


When comparing solvers across headings, loop headings first then solvers.
This groups legend entries as: `H0-AQWA / H0-OrcaWave / H45-AQWA / H45-OrcaWave`
making it easy to toggle all solvers for a given heading:
```python
for heading_idx in heading_indices:
    heading_label = f"{headings[heading_idx]:.0f}"
    for solver_name in solver_names:
        fig.add_trace(go.Scatter(
            x=frequencies, y=values,
            name=f"H{heading_label} {solver_name}",
            legendgroup=f"H{heading_label}",
        ))
```

## Significance Filtering (Naval Architecture)


Omit headings where response is physically insignificant (< 1% of DOF peak).
This avoids plotting zero-response cases like surge@90deg or sway@0deg:
```python
def get_significant_headings(dof_data, all_headings, threshold=0.01):
    overall_peak = max(np.max(np.abs(solver_data)) for solver_data in all_solvers)
    cutoff = overall_peak * threshold
    return [h for h in all_headings
            if any(np.max(np.abs(solver[h])) > cutoff for solver in all_solvers)]
```

## Inline Plotly in Single-Page HTML


For multi-plot single-page reports, load Plotly CDN once in `<head>` and use
`include_plotlyjs=False` for each inline plot div to avoid duplicate loading:
```python
# In HTML <head>:
# <script src="https://cdn.plot.ly/plotly-2.27.0.min.js"></script>

# For each plot div:
plot_html = fig.to_html(full_html=False, include_plotlyjs=False)
```

## Monospace Fonts for Numeric Data


Use engineering-appropriate monospace fonts for tables and numeric values:
```css
.solver-table td {
    font-family: 'SF Mono', 'Cascadia Code', 'Consolas', 'Monaco', monospace;
    font-size: 0.85em;
}
```

## Engineering Report CSS Patterns


```css
/* Alternating rows */
tbody tr:nth-child(even) { background: #f8f9fa; }
tbody tr:nth-child(odd) { background: #fff; }
tbody tr:hover { background: #ebf5fb; }

/* Dark header */
th { background: #34495e; color: #fff; padding: 0.5em 0.75em; }

/* Section rows in tables */

*See sub-skills for full details.*
