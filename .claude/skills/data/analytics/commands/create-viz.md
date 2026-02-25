---
name: create-viz
type: command
plugin: data
source: https://github.com/anthropics/knowledge-work-plugins
---

# /create-viz - Create Data Visualizations

Create publication-quality data visualizations using Python (matplotlib/seaborn or plotly).

## Usage

```
/create-viz <data source> [chart type] [additional instructions]
```

## Workflow

### 1. Understand the Request

Determine:
- What data to visualize (query results, uploaded file, existing analysis)
- What type of chart (or auto-select based on data relationship)
- Any specific requirements (colors, formatting, interactivity)

### 2. Get the Data

- From a query: run the SQL and load results
- From a file: load CSV/Excel/Parquet
- From existing analysis: use data already in the session

### 3. Select Chart Type

Match the data relationship to the best chart type:

| Relationship | Chart Type |
|---|---|
| Trend over time | Line chart |
| Comparison across categories | Bar chart |
| Ranking | Horizontal bar chart |
| Part-to-whole composition | Stacked bar or treemap |
| Distribution | Histogram or box plot |
| Correlation | Scatter plot |
| Multiple KPIs | Small multiples |

### 4. Generate the Visualization

Follow data-visualization skill design principles:
- Descriptive title that states the insight
- Colorblind-friendly palette
- Clean layout with minimal chart junk
- Proper number formatting
- Axes labeled with units

### 5. Output

Save the chart as a PNG file (150 DPI) and provide:
- The chart image
- The Python code used (for user modification)
- Suggestions for variations or improvements

## Tips

- Mention "interactive" to get a plotly chart instead of matplotlib
- Specify the insight you want to highlight for a better title
- Request multiple charts in one go for comparison views
