---
name: python-pptx
description: Create and manipulate PowerPoint presentations programmatically. Build
  slide decks with layouts, shapes, charts, tables, and images. Generate data-driven
  presentations from templates.
version: 1.0.0
category: data
type: skill
capabilities:
- presentation_creation
- slide_layouts
- shape_manipulation
- chart_generation
- table_creation
- image_insertion
- template_based_generation
- master_slide_customization
tools:
- python
- python-pptx
- Pillow
tags:
- powerpoint
- pptx
- presentation
- slides
- charts
- office-automation
platforms:
- windows
- macos
- linux
related_skills:
- python-docx
- openpyxl
- plotly
requires: []
scripts_exempt: true
---

# Python Pptx

## Overview

Python-pptx is a Python library for creating and updating PowerPoint (.pptx) presentations. This skill covers comprehensive patterns for presentation automation including:

- **Presentation creation** with multiple slide layouts
- **Shape manipulation** including text boxes, images, and geometric shapes
- **Chart generation** for data visualization within slides
- **Table creation** for structured data display
- **Master slide customization** for branding consistency
- **Template-based generation** for consistent presentations
- **Placeholder management** for dynamic content insertion

## When to Use This Skill

### USE when:

- Generating presentations from data automatically
- Creating standardized report presentations
- Building slide decks with consistent branding
- Automating dashboard presentations
- Creating training materials from templates
- Generating client presentations from databases
- Building presentation pipelines for regular reports
- Creating slides with charts and tables from data
- Mass-producing presentations with variable content
### DON'T USE when:

- Need real-time presentation editing (use PowerPoint)
- Creating presentations with complex animations
- Need advanced transitions (limited support)
- Require embedded videos with playback controls
- Need to preserve complex PowerPoint features
- Creating presentations from scratch without Python (use PowerPoint)

## Prerequisites

### Installation

```bash
# Basic installation
pip install python-pptx

# Using uv (recommended)
uv pip install python-pptx

# With image support
pip install python-pptx Pillow

# Full installation for charts
pip install python-pptx Pillow lxml
```
### Verify Installation

```python
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN

print("python-pptx installed successfully!")
```

## Version History

### 1.0.0 (2026-01-17)

- Initial skill creation
- Core capabilities documentation
- 6 complete code examples
- Template-based generation patterns
- Chart and table creation

## Resources

- **Official Documentation**: https://python-pptx.readthedocs.io/
- **GitHub Repository**: https://github.com/scanny/python-pptx
- **PyPI Package**: https://pypi.org/project/python-pptx/

## Related Skills

- **python-docx** - Word document generation
- **openpyxl** - Excel workbook automation
- **plotly** - Interactive chart generation
- **pypdf** - PDF manipulation

---

*This skill provides comprehensive patterns for PowerPoint automation refined from production presentation generation systems.*

## Sub-Skills

- [1. Basic Presentation Creation](1-basic-presentation-creation/SKILL.md)
- [2. Advanced Text Formatting](2-advanced-text-formatting/SKILL.md)
- [3. Chart Generation](3-chart-generation/SKILL.md)
- [4. Table Creation](4-table-creation/SKILL.md)
- [5. Image and Shape Manipulation](5-image-and-shape-manipulation/SKILL.md)
- [6. Template-Based Generation](6-template-based-generation/SKILL.md)
- [Data-Driven Presentation from Database (+1)](data-driven-presentation-from-database/SKILL.md)
- [1. Template Design (+2)](1-template-design/SKILL.md)
- [Common Issues](common-issues/SKILL.md)
