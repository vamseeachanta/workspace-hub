---
name: mkdocs
description: Build professional project documentation with MkDocs and Material theme.
  Covers site configuration, navigation, plugins, search optimization, versioning
  with mike, and deployment to GitHub Pages.
version: 1.0.0
category: _internal
type: skill
capabilities:
- Static site generation from Markdown
- Material for MkDocs theme configuration
- Navigation and site structure
- Search optimization with lunr.js
- Plugin ecosystem (minify, git-revision, macros)
- Multi-version documentation with mike
- GitHub Pages deployment
- Custom CSS/JS extensions
- Admonitions and content tabs
- Mermaid diagrams integration
tools:
- mkdocs
- mkdocs-material
- mike
- mkdocs-minify-plugin
- mkdocs-git-revision-date-localized-plugin
- mkdocs-macros-plugin
tags:
- documentation
- static-site
- markdown
- material-theme
- github-pages
- versioning
platforms:
- linux
- macos
- windows
related_skills:
- sphinx
- docusaurus
- pandoc
- marp
scripts_exempt: true
see_also:
- mkdocs-note
- mkdocs-tip
- mkdocs-warning
- mkdocs-danger
- mkdocs-example
- mkdocs-info
- mkdocs-success
- mkdocs-question
- mkdocs-quote
- mkdocs-collapsible-admonitions
- mkdocs-6-code-blocks-with-features
- mkdocs-basic-code-block
- mkdocs-with-title
- mkdocs-line-numbers
- mkdocs-line-highlighting
- mkdocs-line-number-start
- mkdocs-code-annotations
- mkdocs-tabbed-code-blocks
- mkdocs-7-mermaid-diagrams
- mkdocs-flowchart
- mkdocs-sequence-diagram
- mkdocs-class-diagram
- mkdocs-state-diagram
- mkdocs-entity-relationship
- mkdocs-8-plugin-configuration
- mkdocs-subsection-11
- mkdocs-section-2
- mkdocs-3-abbreviations
- mkdocs-related-resources
---

# Mkdocs

## When to Use This Skill

### USE When

- Building project documentation for open source or internal projects
- Need a fast, searchable static documentation site
- Want beautiful Material Design without custom CSS
- Require multi-version documentation (v1.x, v2.x, etc.)
- Deploying documentation to GitHub Pages, GitLab Pages, or Netlify
- Working with Python projects that need docs alongside code
- Need admonitions, code tabs, and content formatting
- Want simple Markdown-based documentation workflow
- Require offline-capable documentation
- Building API documentation alongside guides
### DON'T USE When

- Need complex React components in docs (use Docusaurus)
- Require auto-generated Python API docs (use Sphinx)
- Building single-page documentation (use simple HTML)
- Need document format conversion (use Pandoc)
- Require collaborative real-time editing (use GitBook)
- Building slide presentations (use Marp)

## Prerequisites

### Installation

```bash
# Using pip
pip install mkdocs mkdocs-material

# Using uv (recommended)
uv pip install mkdocs mkdocs-material

# With common plugins
pip install mkdocs mkdocs-material \
    mkdocs-minify-plugin \

*See sub-skills for full details.*
### System Requirements

- Python 3.8 or higher
- pip or uv package manager
- Git (for git-revision plugin and mike)
- Node.js (optional, for social cards)

## Prerequisites

- Prerequisite 1
- Prerequisite 2

## Version History

### v1.0.0 (2026-01-17)

- Initial skill creation
- Material for MkDocs theme configuration
- Plugin ecosystem documentation
- GitHub Pages deployment workflows
- Versioning with mike
- Mermaid diagrams integration
- Custom CSS/JS extensions
- Best practices and troubleshooting

## Sub-Skills

- [1. Project Initialization (+1)](1-project-initialization/SKILL.md)
- [3. Navigation Structure (+2)](3-navigation-structure/SKILL.md)
- [Integration with Python Package (+2)](integration-with-python-package/SKILL.md)
- [1. Documentation Structure (+1)](1-documentation-structure/SKILL.md)
- [Examples](examples/SKILL.md)
- [Common Issues (+1)](common-issues/SKILL.md)

## Sub-Skills

- [Note](note/SKILL.md)
- [Tip](tip/SKILL.md)
- [Warning](warning/SKILL.md)
- [Danger](danger/SKILL.md)
- [Example](example/SKILL.md)
- [Info](info/SKILL.md)
- [Success](success/SKILL.md)
- [Question](question/SKILL.md)
- [Quote](quote/SKILL.md)
- [Collapsible Admonitions](collapsible-admonitions/SKILL.md)
- [6. Code Blocks with Features](6-code-blocks-with-features/SKILL.md)
- [Basic Code Block](basic-code-block/SKILL.md)
- [With Title](with-title/SKILL.md)
- [Line Numbers](line-numbers/SKILL.md)
- [Line Highlighting](line-highlighting/SKILL.md)
- [Line Number Start](line-number-start/SKILL.md)
- [Code Annotations](code-annotations/SKILL.md)
- [Tabbed Code Blocks](tabbed-code-blocks/SKILL.md)
- [7. Mermaid Diagrams](7-mermaid-diagrams/SKILL.md)
- [Flowchart](flowchart/SKILL.md)
- [Sequence Diagram](sequence-diagram/SKILL.md)
- [Class Diagram](class-diagram/SKILL.md)
- [State Diagram](state-diagram/SKILL.md)
- [Entity Relationship](entity-relationship/SKILL.md)
- [8. Plugin Configuration (+4)](8-plugin-configuration/SKILL.md)
- [Subsection 1.1](subsection-11/SKILL.md)
- [Section 2](section-2/SKILL.md)
- [3. Abbreviations (+2)](3-abbreviations/SKILL.md)
- [Related Resources](related-resources/SKILL.md)
