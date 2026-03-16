---
name: openpyxl-5-large-dataset-handling-with-streaming
description: 'Sub-skill of openpyxl: 5. Large Dataset Handling with Streaming.'
version: 1.0.0
category: data
type: reference
scripts_exempt: true
---

# 5. Large Dataset Handling with Streaming

## 5. Large Dataset Handling with Streaming


```python
"""
Handle large datasets efficiently with read-only and write-only modes.
"""
from openpyxl import Workbook, load_workbook
from openpyxl.utils import get_column_letter
from typing import Generator, List, Dict, Any, Iterator
import time

def write_large_dataset_streaming(
    output_path: str,
    data_generator: Generator,
    headers: List[str],
    chunk_size: int = 10000
) -> int:
    """Write large dataset using write-only mode for memory efficiency."""
    # Use write_only mode for streaming
    wb = Workbook(write_only=True)
    ws = wb.create_sheet("Large Data")

    # Write headers
    ws.append(headers)

    rows_written = 0
    start_time = time.time()

    for row in data_generator:
        ws.append(row)
        rows_written += 1

        if rows_written % chunk_size == 0:
            elapsed = time.time() - start_time
            print(f"Written {rows_written:,} rows ({elapsed:.1f}s)")

    wb.save(output_path)

    total_time = time.time() - start_time
    print(f"Total: {rows_written:,} rows written in {total_time:.1f}s")

    return rows_written


def read_large_dataset_streaming(
    file_path: str,
    chunk_size: int = 1000
) -> Generator:
    """Read large dataset using read-only mode for memory efficiency."""
    # Use read_only mode for streaming
    wb = load_workbook(file_path, read_only=True)
    ws = wb.active

    chunk = []
    headers = None

    for row_idx, row in enumerate(ws.iter_rows(values_only=True)):
        if row_idx == 0:
            headers = row
            continue

        # Convert row to dictionary
        row_dict = dict(zip(headers, row))
        chunk.append(row_dict)

        if len(chunk) >= chunk_size:
            yield chunk
            chunk = []

    if chunk:
        yield chunk

    wb.close()


def generate_sample_data(num_rows: int) -> Generator:
    """Generate sample data for testing."""
    import random
    from datetime import datetime, timedelta

    base_date = datetime(2026, 1, 1)
    categories = ["Electronics", "Clothing", "Food", "Books", "Home"]
    regions = ["North", "South", "East", "West"]

    for i in range(num_rows):
        yield [
            i + 1,  # ID
            f"Product_{i+1}",  # Product Name
            random.choice(categories),  # Category
            random.choice(regions),  # Region
            round(random.uniform(10, 1000), 2),  # Price
            random.randint(1, 100),  # Quantity
            (base_date + timedelta(days=random.randint(0, 365))).strftime("%Y-%m-%d"),  # Date
        ]


def process_large_file_example() -> None:
    """Example of processing large Excel files."""
    # Generate large dataset
    headers = ["ID", "Product", "Category", "Region", "Price", "Quantity", "Date"]
    num_rows = 100000  # 100k rows

    print(f"Generating {num_rows:,} rows...")
    output_path = "large_dataset.xlsx"

    # Write large file
    rows_written = write_large_dataset_streaming(
        output_path,
        generate_sample_data(num_rows),
        headers
    )

    # Read and process in chunks
    print(f"\nReading file in chunks...")
    total_revenue = 0
    category_totals = {}

    for chunk in read_large_dataset_streaming(output_path, chunk_size=5000):
        for row in chunk:
            revenue = row['Price'] * row['Quantity']
            total_revenue += revenue

            category = row['Category']
            category_totals[category] = category_totals.get(category, 0) + revenue

    print(f"\nTotal Revenue: ${total_revenue:,.2f}")
    print("\nRevenue by Category:")
    for category, total in sorted(category_totals.items()):
        print(f"  {category}: ${total:,.2f}")


# process_large_file_example()
```
