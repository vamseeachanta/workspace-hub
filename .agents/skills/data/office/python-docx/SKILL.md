---
name: python-docx
description: Create and manipulate Microsoft Word documents programmatically. Build
  reports, contracts, and documentation with full control over paragraphs, tables,
  headers, styles, and images.
version: 1.0.0
category: data
type: skill
capabilities:
- document_creation
- paragraph_formatting
- table_generation
- header_footer_management
- style_customization
- image_insertion
- template_manipulation
- mail_merge_patterns
tools:
- python
- python-docx
- lxml
tags:
- word
- docx
- document-generation
- reports
- templates
- office-automation
platforms:
- windows
- macos
- linux
related_skills:
- docx-templates
- pypdf
- openpyxl
requires: []
scripts_exempt: true
---

# Python Docx

## Overview

Python-docx is a Python library for creating and manipulating Microsoft Word (.docx) documents. This skill covers comprehensive patterns for document automation including:

- **Document creation** from scratch or templates
- **Paragraph formatting** with styles, fonts, and alignment
- **Table generation** with merged cells, styles, and formatting
- **Headers and footers** with page numbers and dynamic content
- **Image insertion** with sizing and positioning
- **Style management** for consistent document appearance
- **Template manipulation** for document workflows
- **Mail merge patterns** for bulk document generation

## When to Use This Skill

### USE when:

- Creating Word documents programmatically from data
- Generating reports with consistent formatting
- Building contracts, invoices, or legal documents
- Automating template-based document creation
- Modifying existing Word documents
- Creating documents with complex table structures
- Generating technical documentation with code blocks
- Building multi-section documents with headers/footers
- Creating documents with embedded images and charts
- Batch processing document generation
### DON'T USE when:

- Simple template filling (use docx-templates instead)
- PDF generation is the final output (use pypdf or reportlab)
- Need real-time collaborative editing
- Document requires complex macros or VBA
- Need to preserve complex Word features (use COM automation on Windows)
- Only need to extract text from documents (use python-docx2txt)

## Prerequisites

### Installation

```bash
# Using pip
pip install python-docx

# Using uv (recommended)
uv pip install python-docx

# With image support
pip install python-docx Pillow

# Full installation with all optional dependencies
pip install python-docx Pillow lxml
```
### Verify Installation

```python
from docx import Document
from docx.shared import Inches, Pt, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT

print("python-docx installed successfully!")
```

## Version History

### 1.0.0 (2026-01-17)

- Initial skill creation
- Core capabilities documentation
- 6 complete code examples
- Integration patterns
- Best practices guide
- Troubleshooting section

## Resources

- **Official Documentation**: https://python-docx.readthedocs.io/
- **GitHub Repository**: https://github.com/python-openxml/python-docx
- **PyPI Package**: https://pypi.org/project/python-docx/
- **Open XML SDK Reference**: https://docs.microsoft.com/en-us/office/open-xml/

## Related Skills

- **docx-templates** - Jinja2-style template rendering for Word documents
- **pypdf** - PDF manipulation and generation
- **openpyxl** - Excel file automation
- **python-pptx** - PowerPoint presentation generation

---

*This skill provides comprehensive patterns for Word document automation refined from production document generation systems.*

## Sub-Skills

- [1. Basic Document Creation](1-basic-document-creation/SKILL.md)
- [2. Advanced Paragraph Formatting](2-advanced-paragraph-formatting/SKILL.md)
- [3. Table Creation and Formatting](3-table-creation-and-formatting/SKILL.md)
- [4. Headers, Footers, and Page Setup](4-headers-footers-and-page-setup/SKILL.md)
- [5. Image Insertion and Positioning](5-image-insertion-and-positioning/SKILL.md)
- [6. Style Management and Custom Styles](6-style-management-and-custom-styles/SKILL.md)
- [Report Generation from Database (+1)](report-generation-from-database/SKILL.md)
- [Batch Document Generation](batch-document-generation/SKILL.md)
- [1. Document Structure (+3)](1-document-structure/SKILL.md)
- [Common Issues](common-issues/SKILL.md)
