---
name: docx-templates-database-integration
description: 'Sub-skill of docx-templates: Database Integration.'
version: 1.0.0
category: data
type: reference
scripts_exempt: true
---

# Database Integration

## Database Integration


```python
"""
Generate documents from database queries.
"""
from docxtpl import DocxTemplate
from typing import List, Dict
import sqlite3
from sqlalchemy import create_engine, text
import pandas as pd

def generate_from_database(
    template_path: str,
    output_dir: str,
    db_connection: str,
    query: str,
    filename_field: str = "id"
) -> List[str]:
    """
    Generate documents from database query results.

    Args:
        template_path: Path to template
        output_dir: Output directory
        db_connection: Database connection string
        query: SQL query to fetch data
        filename_field: Field for output filename

    Returns:
        List of generated file paths
    """
    # Connect and fetch data
    engine = create_engine(db_connection)

    with engine.connect() as conn:
        result = conn.execute(text(query))
        records = [dict(row._mapping) for row in result]

    # Generate documents
    return mail_merge_from_list(template_path, output_dir, records, filename_field)


def generate_customer_reports(
    template_path: str,
    output_dir: str,
    db_path: str
) -> Dict:
    """Generate customer reports from SQLite database."""

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row

    # Fetch customers with their orders
    query = """
    SELECT
        c.id,
        c.name,
        c.email,
        c.address,
        COUNT(o.id) as order_count,
        SUM(o.total) as total_spent
    FROM customers c
    LEFT JOIN orders o ON c.id = o.customer_id
    GROUP BY c.id
    """

    cursor = conn.cursor()
    cursor.execute(query)

    records = []
    for row in cursor.fetchall():
        record = dict(row)

        # Fetch order details for each customer
        cursor.execute(
            "SELECT * FROM orders WHERE customer_id = ?",
            (record["id"],)
        )
        record["orders"] = [dict(r) for r in cursor.fetchall()]
        records.append(record)

    conn.close()

    # Generate reports
    generated = mail_merge_from_list(
        template_path,
        output_dir,
        records,
        filename_field="id"
    )

    return {
        "total_customers": len(records),
        "generated_reports": len(generated),
        "files": generated
    }
```
