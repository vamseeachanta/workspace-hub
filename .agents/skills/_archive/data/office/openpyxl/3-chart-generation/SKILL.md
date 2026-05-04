---
name: openpyxl-3-chart-generation
description: 'Sub-skill of openpyxl: 3. Chart Generation.'
version: 1.0.0
category: data
type: reference
scripts_exempt: true
---

# 3. Chart Generation

## 3. Chart Generation


```python
"""
Create various chart types in Excel.
"""
from openpyxl import Workbook
from openpyxl.chart import (
    BarChart, LineChart, PieChart, AreaChart, ScatterChart,
    Reference, Series
)
from openpyxl.chart.label import DataLabelList
from openpyxl.chart.layout import Layout, ManualLayout

def create_charts_workbook(output_path: str) -> None:
    """Create workbook with various chart examples."""
    wb = Workbook()
    ws = wb.active
    ws.title = "Chart Data"

    # Sample data for charts
    data = [
        ["Month", "Sales", "Expenses", "Profit"],
        ["Jan", 15000, 12000, 3000],
        ["Feb", 18000, 13000, 5000],
        ["Mar", 22000, 14500, 7500],
        ["Apr", 20000, 14000, 6000],
        ["May", 25000, 15000, 10000],
        ["Jun", 28000, 16000, 12000],
    ]

    for row in data:
        ws.append(row)

    # Bar Chart
    bar_chart = BarChart()
    bar_chart.type = "col"
    bar_chart.grouping = "clustered"
    bar_chart.title = "Monthly Financial Overview"
    bar_chart.y_axis.title = "Amount ($)"
    bar_chart.x_axis.title = "Month"

    # Data references
    data_ref = Reference(ws, min_col=2, max_col=4, min_row=1, max_row=7)
    cats_ref = Reference(ws, min_col=1, min_row=2, max_row=7)

    bar_chart.add_data(data_ref, titles_from_data=True)
    bar_chart.set_categories(cats_ref)
    bar_chart.shape = 4  # Rounded corners

    # Style the chart
    bar_chart.style = 10
    bar_chart.width = 15
    bar_chart.height = 10

    ws.add_chart(bar_chart, "F2")

    # Line Chart
    line_chart = LineChart()
    line_chart.title = "Profit Trend"
    line_chart.y_axis.title = "Profit ($)"
    line_chart.x_axis.title = "Month"
    line_chart.style = 12

    profit_data = Reference(ws, min_col=4, min_row=1, max_row=7)
    line_chart.add_data(profit_data, titles_from_data=True)
    line_chart.set_categories(cats_ref)

    # Add markers
    line_chart.series[0].marker.symbol = "circle"
    line_chart.series[0].marker.size = 7
    line_chart.series[0].graphicalProperties.line.width = 25000  # in EMUs

    ws.add_chart(line_chart, "F18")

    # Pie Chart on new sheet
    pie_ws = wb.create_sheet("Pie Chart")

    pie_data = [
        ["Category", "Value"],
        ["Product A", 35],
        ["Product B", 25],
        ["Product C", 20],
        ["Product D", 15],
        ["Other", 5],
    ]

    for row in pie_data:
        pie_ws.append(row)

    pie_chart = PieChart()
    pie_chart.title = "Sales by Product Category"

    pie_data_ref = Reference(pie_ws, min_col=2, min_row=2, max_row=6)
    pie_labels_ref = Reference(pie_ws, min_col=1, min_row=2, max_row=6)

    pie_chart.add_data(pie_data_ref)
    pie_chart.set_categories(pie_labels_ref)

    # Add data labels with percentages
    pie_chart.dataLabels = DataLabelList()
    pie_chart.dataLabels.showPercent = True
    pie_chart.dataLabels.showVal = False
    pie_chart.dataLabels.showCatName = True

    pie_ws.add_chart(pie_chart, "D2")

    # Stacked Area Chart
    area_ws = wb.create_sheet("Area Chart")

    area_data = [
        ["Quarter", "Region A", "Region B", "Region C"],
        ["Q1", 5000, 4000, 3000],
        ["Q2", 6000, 4500, 3500],
        ["Q3", 7000, 5000, 4000],
        ["Q4", 8000, 5500, 4500],
    ]

    for row in area_data:
        area_ws.append(row)

    area_chart = AreaChart()
    area_chart.title = "Regional Sales Growth"
    area_chart.style = 13
    area_chart.grouping = "stacked"

    area_data_ref = Reference(area_ws, min_col=2, max_col=4, min_row=1, max_row=5)
    area_cats_ref = Reference(area_ws, min_col=1, min_row=2, max_row=5)

    area_chart.add_data(area_data_ref, titles_from_data=True)
    area_chart.set_categories(area_cats_ref)

    area_ws.add_chart(area_chart, "F2")

    # Scatter Chart
    scatter_ws = wb.create_sheet("Scatter Chart")

    scatter_data = [
        ["X", "Y"],
        [1, 2.5],
        [2, 4.1],
        [3, 5.8],
        [4, 8.2],
        [5, 10.1],
        [6, 12.5],
        [7, 14.8],
    ]

    for row in scatter_data:
        scatter_ws.append(row)

    scatter_chart = ScatterChart()
    scatter_chart.title = "Correlation Analysis"
    scatter_chart.x_axis.title = "X Values"
    scatter_chart.y_axis.title = "Y Values"
    scatter_chart.style = 13

    x_values = Reference(scatter_ws, min_col=1, min_row=2, max_row=8)
    y_values = Reference(scatter_ws, min_col=2, min_row=2, max_row=8)

    series = Series(y_values, x_values, title="Data Points")
    scatter_chart.series.append(series)

    # Add trendline
    from openpyxl.chart.trendline import Trendline
    series.trendline = Trendline(trendlineType='linear')

    scatter_ws.add_chart(scatter_chart, "D2")

    wb.save(output_path)
    print(f"Charts workbook saved to {output_path}")


create_charts_workbook("charts_example.xlsx")
```
