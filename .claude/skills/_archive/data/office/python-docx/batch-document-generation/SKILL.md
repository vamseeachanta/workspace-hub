---
name: python-docx-batch-document-generation
description: 'Sub-skill of python-docx: Batch Document Generation.'
version: 1.0.0
category: data
type: reference
scripts_exempt: true
---

# Batch Document Generation

## Batch Document Generation


```python
"""
Generate multiple documents from a data source.
"""
from docx import Document
from docx.shared import Pt, Inches
from typing import List, Dict, Any
from pathlib import Path
import csv
from concurrent.futures import ThreadPoolExecutor, as_completed

def generate_single_document(
    template_path: str,
    output_dir: Path,
    data: Dict[str, Any],
    filename_field: str = 'id'
) -> str:
    """Generate a single document from template."""
    doc = Document(template_path)

    # Replace placeholders
    for para in doc.paragraphs:
        for key, value in data.items():
            placeholder = f'{{{{{key}}}}}'
            if placeholder in para.text:
                for run in para.runs:
                    if placeholder in run.text:
                        run.text = run.text.replace(placeholder, str(value))

    # Generate filename
    filename = f"{data.get(filename_field, 'document')}.docx"
    output_path = output_dir / filename

    doc.save(str(output_path))
    return str(output_path)


def batch_generate_documents(
    template_path: str,
    csv_data_path: str,
    output_dir: str,
    max_workers: int = 4
) -> List[str]:
    """Generate multiple documents from CSV data."""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # Read CSV data
    with open(csv_data_path, 'r') as f:
        reader = csv.DictReader(f)
        records = list(reader)

    generated_files = []

    # Generate documents in parallel
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {
            executor.submit(
                generate_single_document,
                template_path,
                output_path,
                record
            ): record
            for record in records
        }

        for future in as_completed(futures):
            try:
                result = future.result()
                generated_files.append(result)
                print(f"Generated: {result}")
            except Exception as e:
                print(f"Error generating document: {e}")

    return generated_files


# Usage
# batch_generate_documents(
#     'invoice_template.docx',
#     'clients.csv',
#     'generated_invoices/'
# )
```
