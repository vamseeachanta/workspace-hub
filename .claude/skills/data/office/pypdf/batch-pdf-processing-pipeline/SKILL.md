---
name: pypdf-batch-pdf-processing-pipeline
description: 'Sub-skill of pypdf: Batch PDF Processing Pipeline.'
version: 1.0.0
category: data
type: reference
scripts_exempt: true
---

# Batch PDF Processing Pipeline

## Batch PDF Processing Pipeline


```python
"""
Batch process PDFs with configurable operations.
"""
from pypdf import PdfReader, PdfWriter, PdfMerger
from pathlib import Path
from typing import List, Dict, Any, Callable
from concurrent.futures import ThreadPoolExecutor, as_completed
import logging

logger = logging.getLogger(__name__)

class PDFProcessor:
    """Batch PDF processing with configurable operations."""

    def __init__(self, output_dir: str):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def process_batch(
        self,
        pdf_files: List[str],
        operations: List[Dict[str, Any]],
        parallel: bool = False
    ) -> List[Dict]:
        """Process multiple PDFs with specified operations.

        Args:
            pdf_files: List of PDF file paths
            operations: List of operation configs
            parallel: Run in parallel if True
        """
        results = []

        if parallel:
            with ThreadPoolExecutor(max_workers=4) as executor:
                futures = {
                    executor.submit(self._process_single, f, operations): f
                    for f in pdf_files
                }
                for future in as_completed(futures):
                    results.append(future.result())
        else:
            for pdf_file in pdf_files:
                results.append(self._process_single(pdf_file, operations))

        return results

    def _process_single(
        self,
        pdf_path: str,
        operations: List[Dict[str, Any]]
    ) -> Dict:
        """Process single PDF with operations."""
        result = {'file': pdf_path, 'success': True, 'operations': []}

        try:
            current_path = pdf_path

            for op in operations:
                op_name = op['name']
                op_params = op.get('params', {})

                output_path = str(
                    self.output_dir / f"{Path(current_path).stem}_{op_name}.pdf"
                )

                if op_name == 'rotate':
                    self._rotate(current_path, output_path, **op_params)
                elif op_name == 'watermark':
                    self._watermark(current_path, output_path, **op_params)
                elif op_name == 'extract_pages':
                    self._extract_pages(current_path, output_path, **op_params)
                elif op_name == 'encrypt':
                    self._encrypt(current_path, output_path, **op_params)

                result['operations'].append({
                    'name': op_name,
                    'output': output_path
                })
                current_path = output_path

            result['final_output'] = current_path

        except Exception as e:
            result['success'] = False
            result['error'] = str(e)
            logger.exception(f"Failed to process {pdf_path}")

        return result

    def _rotate(self, input_path, output_path, rotation=90, pages=None):
        reader = PdfReader(input_path)
        writer = PdfWriter()
        for i, page in enumerate(reader.pages):
            if pages is None or i in pages:
                page.rotate(rotation)
            writer.add_page(page)
        writer.write(output_path)

    def _watermark(self, input_path, output_path, watermark_path):
        reader = PdfReader(input_path)
        watermark = PdfReader(watermark_path).pages[0]
        writer = PdfWriter()
        for page in reader.pages:
            page.merge_page(watermark)
            writer.add_page(page)
        writer.write(output_path)

    def _extract_pages(self, input_path, output_path, pages):
        reader = PdfReader(input_path)
        writer = PdfWriter()
        for p in pages:
            if 0 <= p < len(reader.pages):
                writer.add_page(reader.pages[p])
        writer.write(output_path)

    def _encrypt(self, input_path, output_path, password):
        reader = PdfReader(input_path)
        writer = PdfWriter()
        for page in reader.pages:
            writer.add_page(page)
        writer.encrypt(password)
        writer.write(output_path)


# Example usage
# processor = PDFProcessor('processed_output/')
# results = processor.process_batch(
#     ['doc1.pdf', 'doc2.pdf', 'doc3.pdf'],
#     [
#         {'name': 'rotate', 'params': {'rotation': 90}},
#         {'name': 'watermark', 'params': {'watermark_path': 'watermark.pdf'}},
#         {'name': 'encrypt', 'params': {'password': 'secure123'}}
#     ],
#     parallel=True
# )
```
