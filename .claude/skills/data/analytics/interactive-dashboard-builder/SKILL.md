---
name: interactive-dashboard-builder
description: "Create self-contained HTML/JavaScript dashboards with Chart.js, filters, and professional styling"
version: 1.0.0
category: data-analytics
last_updated: 2026-02-03
source: https://github.com/anthropics/knowledge-work-plugins
related_skills:
  - data-visualization
  - data-exploration
  - sql-queries
---

# Interactive Dashboard Builder Skill

Patterns for creating self-contained HTML/JavaScript dashboards using Chart.js, with built-in filtering and professional styling.

## Core Architecture

Every dashboard follows this structure with sections for headers, KPI cards, charts, tables, and footers. The foundation uses a Dashboard class that manages data, filtering, and rendering.

## Key Components

### KPI Cards

Display metrics with formatted values and period-over-period changes. Format currency, percentages, and numbers with automatic scale adjustment (e.g., "$1.5M" for millions).

### Chart Types Supported

- **Line charts** for trends with multiple datasets
- **Bar charts** with automatic horizontal orientation for 8+ categories
- **Doughnut charts** for composition analysis

Charts use responsive containers and maintain interactivity through hover tooltips and legend controls. Customize tooltips and formatting per chart type.

### Filtering System

Implement dropdown selects, date range inputs, and combined filter logic that triggers real-time updates across all visualizations and tables simultaneously using an `applyFilters()` function.

### Data Tables

Sortable columns with clickable headers toggle ascending/descending order.

## Design System

Use CSS custom properties for consistent theming: dark headers, light cards, and a six-color palette for data visualization. Layout relies on CSS Grid for responsive multi-column arrangements that stack to single column on mobile.

## Performance Guidelines

| Dataset Size | Approach |
|---|---|
| <1,000 rows | Embed data directly in HTML |
| 1,000-10,000 rows | Pre-aggregate before embedding |
| >10,000 rows | Pre-aggregate server-side |

Chart.js performance limits:
- Line charts: <500 points per series
- Bar charts: <50 categories
- Scatter plots: <1,000 points
- Disable animations when multiple charts exist for better responsiveness

## Data Formatting Utilities

Provide utility functions for displaying values as currency, percentages, or abbreviated numbers:

```javascript
function formatValue(value, type) {
    if (type === 'currency') {
        if (Math.abs(value) >= 1e6) return `$${(value / 1e6).toFixed(1)}M`;
        if (Math.abs(value) >= 1e3) return `$${(value / 1e3).toFixed(1)}K`;
        return `$${value.toFixed(0)}`;
    }
    if (type === 'percent') return `${value.toFixed(1)}%`;
    if (type === 'number') {
        if (Math.abs(value) >= 1e6) return `${(value / 1e6).toFixed(1)}M`;
        if (Math.abs(value) >= 1e3) return `${(value / 1e3).toFixed(1)}K`;
        return value.toFixed(0);
    }
    return value;
}
```

## Dashboard Template Structure

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dashboard Title</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        :root {
            --primary: #1a1a2e;
            --accent: #e94560;
            --bg: #f5f5f5;
            --card-bg: #ffffff;
            --text: #333333;
            --text-light: #666666;
        }
        /* Grid layout, card styles, responsive breakpoints */
    </style>
</head>
<body>
    <header><!-- Title, date range, filters --></header>
    <section class="kpi-cards"><!-- KPI summary cards --></section>
    <section class="charts"><!-- Chart containers --></section>
    <section class="data-table"><!-- Sortable detail table --></section>
    <footer><!-- Data source, last updated --></footer>
    <script>
        // Embedded data, Dashboard class, chart initialization, filter logic
    </script>
</body>
</html>
```

Dashboards are fully self-contained HTML files that can be shared by sending the file, with no server required.
