---
name: docx-templates
description: Template-based Word document generation using Jinja2 syntax. Create reports,
  contracts, and documents with loops, conditionals, tables, and mail merge capabilities.
version: 1.0.0
author: workspace-hub
category: data
type: skill
trigger: manual
auto_execute: false
capabilities:
- jinja2_templates
- loop_rendering
- conditional_content
- table_generation
- image_insertion
- mail_merge
- batch_generation
- nested_data_support
tools:
- Read
- Write
- Bash
- Grep
tags:
- docx
- templates
- jinja2
- word
- document-generation
- mail-merge
- reports
- automation
platforms:
- python
related_skills:
- python-docx
- openpyxl
- pypdf
requires: []
scripts_exempt: true
---

# Docx Templates

## Quick Start

```bash
# Install docxtpl
pip install docxtpl

# Install with image support
pip install docxtpl Pillow

# For Excel data sources
pip install docxtpl openpyxl pandas

# Verify installation
python -c "from docxtpl import DocxTemplate; print('docxtpl ready!')"
```

## When to Use This Skill

**USE when:**
- Generating documents from templates with dynamic data
- Creating mail merge documents from data sources
- Building reports with loops and conditional sections
- Need to maintain consistent formatting across generated documents
- Generating contracts, invoices, letters from templates
- Processing batch document generation from databases or spreadsheets
- Templates need professional formatting preserved
- Non-technical users maintain template design

**DON'T USE when:**
- Building documents programmatically from scratch (use python-docx)
- Need complex document manipulation beyond template filling
- PDF output is the final format (generate docx then convert)
- Templates require complex macros or VBA
- Real-time collaborative editing needed

## Prerequisites

```bash
# Core installation
pip install docxtpl>=0.16.0

# For image handling
pip install docxtpl Pillow>=9.0.0

# For data processing
pip install docxtpl pandas>=2.0.0 openpyxl>=3.1.0

# For database connections
pip install docxtpl sqlalchemy psycopg2-binary

# All dependencies
pip install docxtpl Pillow pandas openpyxl sqlalchemy
```
### Verify Installation

```python
from docxtpl import DocxTemplate, InlineImage
from docx.shared import Mm, Inches

print("docxtpl installed successfully!")

# Quick test
# template = DocxTemplate("template.docx")
# context = {"name": "World"}
# template.render(context)
# template.save("output.docx")
```

## Resources

- **docxtpl Documentation**: https://docxtpl.readthedocs.io/
- **GitHub Repository**: https://github.com/elapouya/python-docx-template
- **Jinja2 Template Syntax**: https://jinja.palletsprojects.com/
- **python-docx (underlying library)**: https://python-docx.readthedocs.io/

## Version History

- **1.0.0** (2026-01-17): Initial release with template rendering, loops, conditionals, tables, images, mail merge

---

*This skill provides comprehensive patterns for template-based document generation with docxtpl, refined from production document automation workflows.*

## Sub-Skills

- [1. Basic Template Rendering](1-basic-template-rendering/SKILL.md)
- [2. Loops and Iterations](2-loops-and-iterations/SKILL.md)
- [3. Conditional Content](3-conditional-content/SKILL.md)
- [4. Table Generation](4-table-generation/SKILL.md)
- [5. Image Insertion](5-image-insertion/SKILL.md)
- [6. Mail Merge and Batch Generation](6-mail-merge-and-batch-generation/SKILL.md)
- [Database Integration](database-integration/SKILL.md)
- [FastAPI Service](fastapi-service/SKILL.md)
- [1. Template Design (+2)](1-template-design/SKILL.md)
- [Template Variables Not Rendering (+2)](template-variables-not-rendering/SKILL.md)
