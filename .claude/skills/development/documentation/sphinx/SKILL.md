---
name: sphinx
description: Generate comprehensive Python documentation with Sphinx. Covers autodoc
  for API extraction, Napoleon for Google/NumPy docstrings, intersphinx for cross-references,
  and multiple output formats including HTML, PDF, and ePub.
version: 1.0.0
category: development
type: skill
capabilities:
- Automatic API documentation from docstrings
- reStructuredText and MyST Markdown support
- Napoleon extension for Google/NumPy docstrings
- Cross-project references with intersphinx
- Multiple output formats (HTML, PDF, ePub, man pages)
- Read the Docs theme integration
- Code documentation with viewcode
- Type hint documentation with autodoc_typehints
- Custom domain extensions
- Internationalization (i18n) support
tools:
- sphinx
- sphinx-rtd-theme
- sphinx-autodoc-typehints
- myst-parser
- sphinx-copybutton
- sphinxcontrib-napoleon
- sphinx-autoapi
tags:
- documentation
- python
- api-reference
- autodoc
- rst
- pdf
- readthedocs
platforms:
- linux
- macos
- windows
related_skills:
- mkdocs
- pandoc
- docusaurus
see_also:
- sphinx-features
- sphinx-quick-example
- sphinx-admonitions
- sphinx-cross-references
- sphinx-math-support
- sphinx-task-lists
- sphinx-7-intersphinx-cross-references
- sphinx-related-resources
---

# Sphinx

## When to Use This Skill

### USE When

- Building Python library or package documentation
- Need automatic API reference from docstrings
- Require PDF or ePub documentation output
- Using Google or NumPy docstring styles
- Need cross-references between documentation projects
- Deploying to Read the Docs
- Building scientific or academic documentation
- Need versioned API documentation
- Working with large Python codebases
- Require internationalized documentation
### DON'T USE When

- Simple project documentation without API docs (use MkDocs)
- Non-Python projects (use MkDocs or Docusaurus)
- Need React components in docs (use Docusaurus)
- Quick format conversion only (use Pandoc)
- Building presentation slides (use Marp)
- Collaborative wiki-style docs (use GitBook)

## Prerequisites

### Installation

```bash
# Core Sphinx installation
pip install sphinx

# With common extensions
pip install sphinx \
    sphinx-rtd-theme \
    sphinx-autodoc-typehints \
    sphinx-copybutton \
    myst-parser \

*See sub-skills for full details.*
### System Requirements

- Python 3.8 or higher
- pip or uv package manager
- LaTeX distribution (for PDF output)
- Graphviz (optional, for diagrams)

## Version History

### v1.0.0 (2026-01-17)

- Initial skill creation
- Autodoc configuration for Python API
- Napoleon support for Google/NumPy docstrings
- Intersphinx cross-references
- Multiple output formats (HTML, PDF, ePub)
- Read the Docs configuration
- MyST Markdown support
- Custom extensions guide
- GitHub Actions deployment

## Sub-Skills

- [1. Project Initialization (+1)](1-project-initialization/SKILL.md)
- [3. Index and Table of Contents](3-index-and-table-of-contents/SKILL.md)
- [4. Autodoc - Automatic API Documentation](4-autodoc-automatic-api-documentation/SKILL.md)
- [5. Generate API Documentation (+1)](5-generate-api-documentation/SKILL.md)
- [Integration with pyproject.toml (+2)](integration-with-pyprojecttoml/SKILL.md)
- [1. Docstring Style Guide (+3)](1-docstring-style-guide/SKILL.md)
- [Common Issues (+1)](common-issues/SKILL.md)

## Sub-Skills

- [Features](features/SKILL.md)
- [Quick Example](quick-example/SKILL.md)
- [Admonitions](admonitions/SKILL.md)
- [Cross-References](cross-references/SKILL.md)
- [Math Support](math-support/SKILL.md)
- [Task Lists](task-lists/SKILL.md)
- [7. Intersphinx Cross-References (+5)](7-intersphinx-cross-references/SKILL.md)
- [Related Resources](related-resources/SKILL.md)
