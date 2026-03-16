---
name: python-pptx-data-driven-presentation-from-database
description: 'Sub-skill of python-pptx: Data-Driven Presentation from Database (+1).'
version: 1.0.0
category: data
type: reference
scripts_exempt: true
---

# Data-Driven Presentation from Database (+1)

## Data-Driven Presentation from Database


```python
"""
Generate presentations from database queries.
"""
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.chart.data import CategoryChartData
from pptx.enum.chart import XL_CHART_TYPE
import sqlite3
from datetime import datetime

def generate_database_presentation(
    db_path: str,
    output_path: str
) -> None:
    """Generate presentation from database data."""
    conn = sqlite3.connect(db_path)
    prs = Presentation()

    # Title slide
    slide = prs.slides.add_slide(prs.slide_layouts[0])
    slide.shapes.title.text = "Sales Analysis Report"
    slide.placeholders[1].text = f"Generated: {datetime.now().strftime('%Y-%m-%d')}"

    # Query 1: Sales by region
    cursor = conn.execute("""
        SELECT region, SUM(amount) as total
        FROM sales
        GROUP BY region
        ORDER BY total DESC
    """)
    regions = cursor.fetchall()

    # Create chart slide
    slide = prs.slides.add_slide(prs.slide_layouts[5])
    slide.shapes.title.text = "Sales by Region"

    chart_data = CategoryChartData()
    chart_data.categories = [r[0] for r in regions]
    chart_data.add_series('Sales', [r[1] for r in regions])

    slide.shapes.add_chart(
        XL_CHART_TYPE.BAR_CLUSTERED,
        Inches(1), Inches(1.5), Inches(11), Inches(5.5),
        chart_data
    )

    # Query 2: Monthly trend
    cursor = conn.execute("""
        SELECT strftime('%Y-%m', date) as month, SUM(amount)
        FROM sales
        GROUP BY month
        ORDER BY month
    """)
    monthly = cursor.fetchall()

    slide = prs.slides.add_slide(prs.slide_layouts[5])
    slide.shapes.title.text = "Monthly Sales Trend"

    chart_data = CategoryChartData()
    chart_data.categories = [m[0] for m in monthly]
    chart_data.add_series('Sales', [m[1] for m in monthly])

    slide.shapes.add_chart(
        XL_CHART_TYPE.LINE_MARKERS,
        Inches(1), Inches(1.5), Inches(11), Inches(5.5),
        chart_data
    )

    conn.close()
    prs.save(output_path)
    print(f"Database presentation saved: {output_path}")
```


## Pandas DataFrame to Presentation


```python
"""
Generate presentations from pandas DataFrames.
"""
import pandas as pd
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RgbColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR

def dataframe_to_slide(
    prs: Presentation,
    df: pd.DataFrame,
    title: str,
    max_rows: int = 15
) -> None:
    """Add DataFrame as table to presentation."""
    slide = prs.slides.add_slide(prs.slide_layouts[5])
    slide.shapes.title.text = title

    # Limit rows if necessary
    display_df = df.head(max_rows)
    rows, cols = display_df.shape
    rows += 1  # For header

    # Calculate dimensions
    table_width = min(cols * 1.5, 12)
    left = Inches((13.333 - table_width) / 2)

    table = slide.shapes.add_table(
        rows, cols,
        left, Inches(1.5),
        Inches(table_width), Inches(0.4 * rows)
    ).table

    # Headers
    for i, col_name in enumerate(display_df.columns):
        cell = table.cell(0, i)
        cell.text = str(col_name)
        cell.fill.solid()
        cell.fill.fore_color.rgb = RgbColor(0x2F, 0x54, 0x96)
        para = cell.text_frame.paragraphs[0]
        para.font.bold = True
        para.font.color.rgb = RgbColor(255, 255, 255)
        para.font.size = Pt(10)
        para.alignment = PP_ALIGN.CENTER

    # Data
    for row_idx, (_, row) in enumerate(display_df.iterrows(), start=1):
        for col_idx, value in enumerate(row):
            cell = table.cell(row_idx, col_idx)
            cell.text = str(value)
            para = cell.text_frame.paragraphs[0]
            para.font.size = Pt(9)
            para.alignment = PP_ALIGN.CENTER


def create_dataframe_presentation(
    dataframes: dict,
    output_path: str
) -> None:
    """Create presentation from multiple DataFrames."""
    prs = Presentation()

    # Title slide
    slide = prs.slides.add_slide(prs.slide_layouts[0])
    slide.shapes.title.text = "Data Analysis Report"

    for title, df in dataframes.items():
        dataframe_to_slide(prs, df, title)

    prs.save(output_path)
    print(f"DataFrame presentation saved: {output_path}")
```
