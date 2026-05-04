---
name: docx-templates-4-table-generation
description: 'Sub-skill of docx-templates: 4. Table Generation.'
version: 1.0.0
category: data
type: reference
scripts_exempt: true
---

# 4. Table Generation

## 4. Table Generation


**Dynamic Tables with Data:**
```python
"""
Generate tables dynamically from data.
"""
from docxtpl import DocxTemplate
from typing import List, Dict, Any
import pandas as pd

def render_data_table(
    template_path: str,
    output_path: str,
    headers: List[str],
    rows: List[List[Any]],
    table_title: str = ""
) -> None:
    """
    Render a simple data table.

    Template structure:
        {{ table_title }}

        | Header 1 | Header 2 | Header 3 |
        |----------|----------|----------|
        {%tr for row in rows %}
        | {{ row[0] }} | {{ row[1] }} | {{ row[2] }} |
        {%tr endfor %}
    """
    template = DocxTemplate(template_path)

    # Convert rows to list of dicts for easier template access
    row_dicts = []
    for row in rows:
        row_dict = {f"col{i}": val for i, val in enumerate(row)}
        row_dicts.append(row_dict)

    context = {
        "table_title": table_title,
        "headers": headers,
        "rows": row_dicts,
        "column_count": len(headers)
    }

    template.render(context)
    template.save(output_path)


def render_pandas_table(
    template_path: str,
    output_path: str,
    df: pd.DataFrame,
    title: str = ""
) -> None:
    """
    Render a pandas DataFrame as a table.

    Template:
        {%tr for row in data %}
        {%tc for cell in row %}{{ cell }}{%tc endfor %}
        {%tr endfor %}
    """
    template = DocxTemplate(template_path)

    # Convert DataFrame to list of dicts
    headers = df.columns.tolist()
    data = df.values.tolist()

    context = {
        "title": title,
        "headers": headers,
        "data": data,
        "row_count": len(data),
        "col_count": len(headers)
    }

    template.render(context)
    template.save(output_path)


def render_grouped_table(
    template_path: str,
    output_path: str,
    grouped_data: Dict[str, List[Dict]]
) -> None:
    """
    Render table with grouped rows and subtotals.

    Template:
        {%tr for group_name, items in groups.items() %}
        {{ group_name }} ({{ items|length }} items)
        {%tr for item in items %}
        | {{ item.name }} | {{ item.value }} |
        {%tr endfor %}
        Subtotal: {{ group_subtotals[group_name] }}
        {%tr endfor %}
    """
    template = DocxTemplate(template_path)

    # Calculate subtotals
    subtotals = {}
    for group, items in grouped_data.items():
        subtotals[group] = sum(item.get("value", 0) for item in items)

    context = {
        "groups": grouped_data,
        "group_subtotals": subtotals,
        "total": sum(subtotals.values())
    }

    template.render(context)
    template.save(output_path)


class TableBuilder:
    """
    Builder for complex table structures.
    """

    def __init__(self):
        self.headers: List[str] = []
        self.rows: List[Dict] = []
        self.footer_row: Dict = {}
        self.title: str = ""

    def set_title(self, title: str) -> 'TableBuilder':
        """Set table title."""
        self.title = title
        return self

    def set_headers(self, headers: List[str]) -> 'TableBuilder':
        """Set column headers."""
        self.headers = headers
        return self

    def add_row(self, **kwargs) -> 'TableBuilder':
        """Add a data row."""
        self.rows.append(kwargs)
        return self

    def add_rows_from_dicts(self, rows: List[Dict]) -> 'TableBuilder':
        """Add multiple rows from list of dicts."""
        self.rows.extend(rows)
        return self

    def add_rows_from_dataframe(self, df: pd.DataFrame) -> 'TableBuilder':
        """Add rows from DataFrame."""
        self.headers = df.columns.tolist()
        self.rows = df.to_dict('records')
        return self

    def set_footer(self, **kwargs) -> 'TableBuilder':
        """Set footer row (e.g., totals)."""
        self.footer_row = kwargs
        return self

    def auto_calculate_footer(self, columns: List[str], operation: str = "sum") -> 'TableBuilder':
        """Auto-calculate footer values."""
        for col in columns:
            values = [row.get(col, 0) for row in self.rows if isinstance(row.get(col), (int, float))]
            if operation == "sum":
                self.footer_row[col] = sum(values)
            elif operation == "avg":
                self.footer_row[col] = sum(values) / len(values) if values else 0
            elif operation == "count":
                self.footer_row[col] = len(values)

        return self

    def to_context(self) -> Dict[str, Any]:
        """Convert to template context."""
        return {
            "table_title": self.title,
            "headers": self.headers,
            "rows": self.rows,
            "footer": self.footer_row,
            "has_footer": bool(self.footer_row),
            "row_count": len(self.rows)
        }

    def render(self, template_path: str, output_path: str) -> None:
        """Render to document."""
        template = DocxTemplate(template_path)
        template.render(self.to_context())
        template.save(output_path)

*Content truncated — see parent skill for full reference.*
