---
name: build-dashboard
type: command
plugin: data
source: https://github.com/anthropics/knowledge-work-plugins
---

# /build-dashboard - Create Interactive HTML Dashboards

Create self-contained interactive HTML dashboards without server requirements.

## Usage

```
/build-dashboard <description> [data source]
```

## Workflow

### 1. Understand Requirements

Gather from the user:
- What metrics and data to display
- Target audience for the dashboard
- Data source (query results, CSV, or manual input)
- Any specific layout or design preferences

### 2. Gather Data

- Execute queries against connected data warehouse, or
- Load from uploaded file, or
- Accept data pasted by the user

### 3. Design Layout

Standard dashboard layout:
- **KPI cards** at the top for summary metrics
- **Charts** in the middle section for trends and comparisons
- **Detail table** at the bottom for row-level data (optional)
- **Filters** for interactive exploration

### 4. Build the HTML

Generate a single, self-contained HTML file using:
- Chart.js via CDN for visualizations
- Semantic HTML5 layout with responsive design
- Embedded JSON data for offline functionality
- JavaScript-driven filtering and interactivity

### 5. Implement Charts

Select appropriate chart types for each metric:
- Line charts for trends
- Bar charts for comparisons
- Doughnut charts for composition

### 6. Add Interactivity

- Dropdown filters for dimensions
- Date range pickers for temporal filtering
- Sortable table columns
- Hover tooltips on all chart elements
- All filters update all visualizations simultaneously

### 7. Save and Deliver

Save as a single HTML file that can be:
- Opened directly in any browser
- Shared via email or messaging
- Hosted on any static file server

## Tips

- Dashboards are fully self-contained -- share by sending the file
- Keep to 3-5 charts maximum for readability
- Ensure the most important metric is the most visually prominent
- Include the data source and last-updated date in the footer
