---
name: python-docx-report-generation-from-database
description: 'Sub-skill of python-docx: Report Generation from Database (+1).'
version: 1.0.0
category: data
type: reference
scripts_exempt: true
---

# Report Generation from Database (+1)

## Report Generation from Database


```python
"""
Generate reports from database query results.
"""
from docx import Document
from docx.shared import Inches, Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
from datetime import datetime
from typing import List, Dict, Any
import sqlite3

def generate_database_report(
    db_path: str,
    query: str,
    output_path: str,
    title: str = "Database Report"
) -> None:
    """Generate Word report from database query."""
    # Connect and fetch data
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute(query)
    rows = cursor.fetchall()
    columns = [description[0] for description in cursor.description]
    conn.close()

    # Create document
    doc = Document()

    # Title
    title_para = doc.add_heading(title, level=0)
    title_para.alignment = WD_ALIGN_PARAGRAPH.CENTER

    # Metadata
    meta_para = doc.add_paragraph()
    meta_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
    meta_para.add_run(f'Generated: {datetime.now().strftime("%Y-%m-%d %H:%M")}')
    meta_para.add_run(f' | Records: {len(rows)}')

    doc.add_paragraph()  # Spacing

    # Create table
    if rows:
        table = doc.add_table(rows=len(rows) + 1, cols=len(columns))
        table.style = 'Table Grid'

        # Headers
        for i, col in enumerate(columns):
            cell = table.rows[0].cells[i]
            cell.text = col.replace('_', ' ').title()
            cell.paragraphs[0].runs[0].bold = True

        # Data
        for row_idx, row in enumerate(rows, start=1):
            for col_idx, col in enumerate(columns):
                table.rows[row_idx].cells[col_idx].text = str(row[col])
    else:
        doc.add_paragraph('No records found.')

    doc.save(output_path)
    print(f"Report saved to {output_path}")
```


## Template-Based Document Generation


```python
"""
Generate documents by modifying a template.
"""
from docx import Document
from docx.shared import Pt
from typing import Dict, Any
from pathlib import Path
import re

def replace_placeholders(doc: Document, replacements: Dict[str, str]) -> None:
    """Replace {{placeholder}} patterns in document."""
    # Process paragraphs
    for para in doc.paragraphs:
        for key, value in replacements.items():
            placeholder = f'{{{{{key}}}}}'
            if placeholder in para.text:
                for run in para.runs:
                    if placeholder in run.text:
                        run.text = run.text.replace(placeholder, str(value))

    # Process tables
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                for para in cell.paragraphs:
                    for key, value in replacements.items():
                        placeholder = f'{{{{{key}}}}}'
                        if placeholder in para.text:
                            for run in para.runs:
                                if placeholder in run.text:
                                    run.text = run.text.replace(placeholder, str(value))


def generate_from_template(
    template_path: str,
    output_path: str,
    data: Dict[str, Any]
) -> None:
    """Generate document from template with data substitution."""
    # Load template
    doc = Document(template_path)

    # Replace placeholders
    replace_placeholders(doc, data)

    # Save generated document
    doc.save(output_path)
    print(f"Generated document saved to {output_path}")


# Usage example
data = {
    'client_name': 'Acme Corporation',
    'date': '2026-01-17',
    'contract_value': '$50,000',
    'project_duration': '6 months',
    'contact_person': 'John Smith'
}

# generate_from_template('contract_template.docx', 'acme_contract.docx', data)
```
