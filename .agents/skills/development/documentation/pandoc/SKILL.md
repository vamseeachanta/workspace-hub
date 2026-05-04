---
name: pandoc
description: Universal document converter for transforming Markdown to PDF, DOCX,
  HTML, LaTeX, and 40+ other formats. Covers templates, filters, citations with BibTeX/CSL,
  and batch conversion automation scripts.
version: 1.0.0
category: development
type: skill
capabilities:
- Markdown to PDF conversion
- Markdown to DOCX (Word) conversion
- Markdown to HTML conversion
- Markdown to LaTeX conversion
- Custom LaTeX templates
- Custom DOCX reference documents
- Lua filters for content transformation
- Citation processing with BibTeX/CSL
- Batch conversion scripts
- Cross-reference support
- Table of contents generation
- Syntax highlighting
tools:
- pandoc
- pandoc-crossref
- pandoc-citeproc
- latexmk
- xelatex
- wkhtmltopdf
tags:
- documentation
- conversion
- pdf
- docx
- latex
- markdown
- citations
- templates
platforms:
- linux
- macos
- windows
related_skills:
- mkdocs
- sphinx
- marp
---

# Pandoc

## When to Use This Skill

### USE When

- Converting Markdown to PDF with professional formatting
- Creating Word documents from Markdown sources
- Need reproducible document builds from plain text
- Managing academic papers with citations (BibTeX/CSL)
- Batch converting multiple documents
- Need custom templates for consistent branding
- Converting between multiple documentation formats
- Creating LaTeX documents from Markdown
- Need cross-references (figures, tables, equations)
- Building automated document pipelines
### DON'T USE When

- Building documentation websites (use MkDocs or Sphinx)
- Need interactive documentation (use web frameworks)
- Require real-time collaborative editing (use Google Docs)
- Building slide presentations (use Marp)
- Need WYSIWYG editing (use Word directly)
- Converting complex nested HTML (may lose formatting)

## Prerequisites

### Installation

```bash
# macOS (Homebrew)
brew install pandoc
brew install pandoc-crossref  # For cross-references
brew install basictex         # Minimal LaTeX for PDF
# Or full LaTeX: brew install --cask mactex

# Ubuntu/Debian
sudo apt-get update
sudo apt-get install pandoc pandoc-citeproc

*See sub-skills for full details.*
### System Requirements

- Pandoc 2.19 or higher (3.x recommended)
- LaTeX distribution (for PDF output)
- Python 3.8+ (for pandoc-filters)

## Version History

### v1.0.0 (2026-01-17)

- Initial skill creation
- PDF, DOCX, HTML conversion workflows
- Custom LaTeX templates
- Citation management with BibTeX/CSL
- Cross-references with pandoc-crossref
- Lua filters documentation
- Batch conversion scripts
- Makefile integration
- GitHub Actions workflows

## Sub-Skills

- [1. Basic Format Conversion (+3)](1-basic-format-conversion/SKILL.md)
- [5. Custom LaTeX Templates (+1)](5-custom-latex-templates/SKILL.md)
- [7. Citations and Bibliography (+1)](7-citations-and-bibliography/SKILL.md)
- [9. Lua Filters](9-lua-filters/SKILL.md)
- [10. Batch Conversion Scripts](10-batch-conversion-scripts/SKILL.md)
- [11. Makefile for Document Projects (+1)](11-makefile-for-document-projects/SKILL.md)
- [Integration with Git Hooks (+1)](integration-with-git-hooks/SKILL.md)
- [1. Document Structure](1-document-structure/SKILL.md)
- [Common Issues (+1)](common-issues/SKILL.md)

## Sub-Skills

- [Background](background/SKILL.md)
- [Subsection](subsection/SKILL.md)
- [2. Image Management (+2)](2-image-management/SKILL.md)
- [Related Resources](related-resources/SKILL.md)
