---
name: office-docs-testing-document-generation
description: 'Sub-skill of office-docs: Testing Document Generation.'
version: 1.0.0
category: data
type: reference
scripts_exempt: true
---

# Testing Document Generation

## Testing Document Generation


```python
import pytest
from docx import Document

def test_report_generation():
    """Test report document structure."""
    generate_report(sample_data, 'test_output.docx')

    doc = Document('test_output.docx')

    # Verify structure
    assert len(doc.paragraphs) > 0
    assert doc.paragraphs[0].text == 'Monthly Report'

    # Verify tables
    assert len(doc.tables) == 1
    assert len(doc.tables[0].rows) == 4

def test_template_rendering():
    """Test template variable substitution."""
    context = {'name': 'Test Corp', 'amount': '$1000'}

    doc = DocxTemplate('template.docx')
    doc.render(context)
    doc.save('output.docx')

*See sub-skills for full details.*
