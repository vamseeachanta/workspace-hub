---
name: docx-templates-6-mail-merge-and-batch-generation
description: 'Sub-skill of docx-templates: 6. Mail Merge and Batch Generation.'
version: 1.0.0
category: data
type: reference
scripts_exempt: true
---

# 6. Mail Merge and Batch Generation

## 6. Mail Merge and Batch Generation


**Generating Multiple Documents:**
```python
"""
Generate multiple documents from a template with different data.
"""
from docxtpl import DocxTemplate
from typing import List, Dict, Any, Iterator
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
import csv
import json
import pandas as pd

def mail_merge_from_list(
    template_path: str,
    output_dir: str,
    records: List[Dict[str, Any]],
    filename_field: str = "id"
) -> List[str]:
    """
    Generate documents for multiple records.

    Args:
        template_path: Path to template
        output_dir: Directory for output files
        records: List of data records
        filename_field: Field to use for output filename

    Returns:
        List of generated file paths
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    generated_files = []

    for record in records:
        # Load fresh template for each document
        template = DocxTemplate(template_path)

        # Generate filename
        filename = f"{record.get(filename_field, 'document')}.docx"
        file_path = output_path / filename

        # Render and save
        template.render(record)
        template.save(str(file_path))

        generated_files.append(str(file_path))

    print(f"Generated {len(generated_files)} documents in {output_dir}")
    return generated_files


def mail_merge_from_csv(
    template_path: str,
    csv_path: str,
    output_dir: str,
    filename_field: str = "id"
) -> List[str]:
    """
    Generate documents from CSV data source.

    Args:
        template_path: Path to template
        csv_path: Path to CSV file
        output_dir: Directory for output files
        filename_field: Field to use for output filename

    Returns:
        List of generated file paths
    """
    with open(csv_path, 'r', newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        records = list(reader)

    return mail_merge_from_list(template_path, output_dir, records, filename_field)


def mail_merge_from_excel(
    template_path: str,
    excel_path: str,
    output_dir: str,
    sheet_name: str = None,
    filename_field: str = "id"
) -> List[str]:
    """
    Generate documents from Excel data source.

    Args:
        template_path: Path to template
        excel_path: Path to Excel file
        output_dir: Directory for output files
        sheet_name: Sheet to read (default: first sheet)
        filename_field: Field to use for output filename

    Returns:
        List of generated file paths
    """
    df = pd.read_excel(excel_path, sheet_name=sheet_name)
    records = df.to_dict('records')

    return mail_merge_from_list(template_path, output_dir, records, filename_field)


def mail_merge_parallel(
    template_path: str,
    output_dir: str,
    records: List[Dict[str, Any]],
    filename_field: str = "id",
    max_workers: int = 4
) -> List[str]:
    """
    Generate documents in parallel for better performance.

    Args:
        template_path: Path to template
        output_dir: Directory for output files
        records: List of data records
        filename_field: Field to use for output filename
        max_workers: Maximum parallel workers

    Returns:
        List of generated file paths
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    def generate_single(record: Dict) -> str:
        """Generate a single document."""
        template = DocxTemplate(template_path)
        filename = f"{record.get(filename_field, 'document')}.docx"
        file_path = output_path / filename

        template.render(record)
        template.save(str(file_path))

        return str(file_path)

    generated_files = []

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(generate_single, r): r for r in records}

        for future in as_completed(futures):
            try:
                result = future.result()
                generated_files.append(result)
            except Exception as e:
                record = futures[future]
                print(f"Error generating document for {record.get(filename_field)}: {e}")

    print(f"Generated {len(generated_files)} documents")
    return generated_files


class MailMergeGenerator:
    """
    Full-featured mail merge generator.
    """

    def __init__(self, template_path: str):
        self.template_path = template_path
        self._validate_template()

    def _validate_template(self) -> None:
        """Validate template file exists."""
        if not Path(self.template_path).exists():
            raise FileNotFoundError(f"Template not found: {self.template_path}")

    def _get_template_variables(self) -> List[str]:
        """Extract variable names from template."""
        template = DocxTemplate(self.template_path)
        return list(template.get_undeclared_template_variables())

    def validate_data(self, records: List[Dict]) -> Dict[str, List]:
        """
        Validate data against template variables.

        Returns:
            Dict with 'missing' and 'extra' variable lists
        """
        template_vars = set(self._get_template_variables())


*Content truncated — see parent skill for full reference.*
