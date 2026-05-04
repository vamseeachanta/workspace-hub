---
name: office-docs-python-docx-report-generation
description: 'Sub-skill of office-docs: Python-docx Report Generation (+4).'
version: 1.0.0
category: data
type: reference
scripts_exempt: true
---

# Python-docx Report Generation (+4)

## Python-docx Report Generation


```python
from docx import Document
from docx.shared import Inches, Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH

# Create document
doc = Document()

# Add title
title = doc.add_heading('Monthly Report', level=0)

*See sub-skills for full details.*

## Openpyxl Excel Automation


```python
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.chart import BarChart, Reference

# Create workbook
wb = Workbook()
ws = wb.active
ws.title = "Sales Data"


*See sub-skills for full details.*

## Python-pptx Presentation


```python
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN
from pptx.dml.color import RgbColor

# Create presentation
prs = Presentation()

# Title slide

*See sub-skills for full details.*

## PyPDF Manipulation


```python
from pypdf import PdfReader, PdfWriter, PdfMerger

# Merge PDFs
merger = PdfMerger()
merger.append('report_part1.pdf')
merger.append('report_part2.pdf')
merger.append('appendix.pdf')
merger.write('complete_report.pdf')
merger.close()

*See sub-skills for full details.*

## Docx-Templates Bulk Generation


```python
from docxtpl import DocxTemplate

# Load template
doc = DocxTemplate("contract_template.docx")

# Context for template
context = {
    'client_name': 'Acme Corporation',
    'contract_date': '2026-01-17',

*See sub-skills for full details.*
