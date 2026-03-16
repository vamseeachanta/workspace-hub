---
name: python-pptx-3-chart-generation
description: 'Sub-skill of python-pptx: 3. Chart Generation.'
version: 1.0.0
category: data
type: reference
scripts_exempt: true
---

# 3. Chart Generation

## 3. Chart Generation


```python
"""
Create various chart types in PowerPoint presentations.
"""
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.chart.data import CategoryChartData, ChartData
from pptx.enum.chart import XL_CHART_TYPE, XL_LEGEND_POSITION
from pptx.dml.color import RgbColor

def create_chart_presentation(output_path: str) -> None:
    """Create presentation with various chart types."""
    prs = Presentation()

    # Slide 1: Column Chart
    slide = prs.slides.add_slide(prs.slide_layouts[5])  # Title only
    slide.shapes.title.text = "Quarterly Revenue"

    # Chart data
    chart_data = CategoryChartData()
    chart_data.categories = ['Q1', 'Q2', 'Q3', 'Q4']
    chart_data.add_series('2025', (1200, 1400, 1600, 1800))
    chart_data.add_series('2026', (1500, 1750, 2000, 2200))

    # Add chart
    x, y, cx, cy = Inches(1), Inches(1.5), Inches(11), Inches(5.5)
    chart = slide.shapes.add_chart(
        XL_CHART_TYPE.COLUMN_CLUSTERED,
        x, y, cx, cy,
        chart_data
    ).chart

    # Customize chart
    chart.has_legend = True
    chart.legend.position = XL_LEGEND_POSITION.BOTTOM
    chart.legend.include_in_layout = False

    # Style the chart
    plot = chart.plots[0]
    plot.has_data_labels = True
    data_labels = plot.data_labels
    data_labels.font.size = Pt(10)
    data_labels.number_format = '$#,##0'

    # Slide 2: Line Chart
    slide = prs.slides.add_slide(prs.slide_layouts[5])
    slide.shapes.title.text = "Monthly Trend Analysis"

    chart_data = CategoryChartData()
    chart_data.categories = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun']
    chart_data.add_series('Sales', (100, 120, 140, 135, 160, 180))
    chart_data.add_series('Target', (110, 120, 130, 140, 150, 160))

    chart = slide.shapes.add_chart(
        XL_CHART_TYPE.LINE_MARKERS,
        Inches(1), Inches(1.5), Inches(11), Inches(5.5),
        chart_data
    ).chart

    chart.has_legend = True
    chart.legend.position = XL_LEGEND_POSITION.BOTTOM

    # Slide 3: Pie Chart
    slide = prs.slides.add_slide(prs.slide_layouts[5])
    slide.shapes.title.text = "Market Share Distribution"

    chart_data = CategoryChartData()
    chart_data.categories = ['Product A', 'Product B', 'Product C', 'Other']
    chart_data.add_series('Share', (35, 30, 25, 10))

    chart = slide.shapes.add_chart(
        XL_CHART_TYPE.PIE,
        Inches(3), Inches(1.5), Inches(7), Inches(5.5),
        chart_data
    ).chart

    chart.has_legend = True
    chart.legend.position = XL_LEGEND_POSITION.RIGHT

    plot = chart.plots[0]
    plot.has_data_labels = True
    data_labels = plot.data_labels
    data_labels.show_percentage = True
    data_labels.show_value = False
    data_labels.font.size = Pt(12)

    # Slide 4: Bar Chart (Horizontal)
    slide = prs.slides.add_slide(prs.slide_layouts[5])
    slide.shapes.title.text = "Regional Performance"

    chart_data = CategoryChartData()
    chart_data.categories = ['North', 'South', 'East', 'West', 'Central']
    chart_data.add_series('Revenue', (450, 380, 520, 420, 310))

    chart = slide.shapes.add_chart(
        XL_CHART_TYPE.BAR_CLUSTERED,
        Inches(1), Inches(1.5), Inches(11), Inches(5.5),
        chart_data
    ).chart

    chart.has_legend = False
    plot = chart.plots[0]
    plot.has_data_labels = True
    plot.data_labels.font.size = Pt(11)
    plot.data_labels.number_format = '$#,##0K'

    # Slide 5: Stacked Column Chart
    slide = prs.slides.add_slide(prs.slide_layouts[5])
    slide.shapes.title.text = "Product Mix by Quarter"

    chart_data = CategoryChartData()
    chart_data.categories = ['Q1', 'Q2', 'Q3', 'Q4']
    chart_data.add_series('Hardware', (400, 450, 500, 550))
    chart_data.add_series('Software', (300, 350, 400, 450))
    chart_data.add_series('Services', (200, 250, 300, 350))

    chart = slide.shapes.add_chart(
        XL_CHART_TYPE.COLUMN_STACKED,
        Inches(1), Inches(1.5), Inches(11), Inches(5.5),
        chart_data
    ).chart

    chart.has_legend = True
    chart.legend.position = XL_LEGEND_POSITION.BOTTOM

    # Slide 6: Doughnut Chart
    slide = prs.slides.add_slide(prs.slide_layouts[5])
    slide.shapes.title.text = "Budget Allocation"

    chart_data = CategoryChartData()
    chart_data.categories = ['R&D', 'Marketing', 'Operations', 'Admin']
    chart_data.add_series('Budget', (40, 25, 25, 10))

    chart = slide.shapes.add_chart(
        XL_CHART_TYPE.DOUGHNUT,
        Inches(3), Inches(1.5), Inches(7), Inches(5.5),
        chart_data
    ).chart

    chart.has_legend = True
    chart.legend.position = XL_LEGEND_POSITION.RIGHT

    prs.save(output_path)
    print(f"Chart presentation saved to {output_path}")


create_chart_presentation("chart_presentation.pptx")
```
