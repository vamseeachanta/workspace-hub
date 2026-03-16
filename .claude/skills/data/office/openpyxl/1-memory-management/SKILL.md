---
name: openpyxl-1-memory-management
description: 'Sub-skill of openpyxl: 1. Memory Management (+2).'
version: 1.0.0
category: data
type: reference
scripts_exempt: true
---

# 1. Memory Management (+2)

## 1. Memory Management


```python
"""Best practices for memory-efficient Excel operations."""

# DO: Use write_only mode for large writes
wb = Workbook(write_only=True)
ws = wb.create_sheet()
for row in large_data:
    ws.append(row)  # Streams directly to file
wb.save('output.xlsx')

# DO: Use read_only mode for large reads
wb = load_workbook('large_file.xlsx', read_only=True)
for row in wb.active.iter_rows(values_only=True):
    process_row(row)
wb.close()  # Important: close when done

# DON'T: Load entire file into memory unnecessarily
# wb = load_workbook('large_file.xlsx')  # Loads all into memory
```


## 2. Style Reuse


```python
"""Reuse styles for better performance."""
from openpyxl.styles import NamedStyle

# DO: Create named styles once, apply many times
header_style = NamedStyle(name="header")
header_style.font = Font(bold=True, color="FFFFFF")
header_style.fill = PatternFill(start_color="4472C4", fill_type="solid")
wb.add_named_style(header_style)

# Apply to multiple cells efficiently
for cell in ws[1]:
    cell.style = "header"

# DON'T: Create style objects for each cell
# for cell in ws[1]:
#     cell.font = Font(bold=True)  # Creates new Font each time
```


## 3. Error Handling


```python
"""Robust error handling for Excel operations."""
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

def safe_save_workbook(wb: Workbook, output_path: str) -> bool:
    """Safely save workbook with error handling."""
    try:
        # Ensure directory exists
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)

        # Check if file is locked
        if Path(output_path).exists():
            try:
                Path(output_path).rename(output_path)
            except PermissionError:
                logger.error(f"File is locked: {output_path}")
                return False

        wb.save(output_path)
        logger.info(f"Workbook saved: {output_path}")
        return True

    except Exception as e:
        logger.exception(f"Failed to save workbook: {e}")
        return False
```
