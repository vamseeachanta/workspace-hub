---
name: marp
description: Create professional Markdown-based slide presentations with Marp. Covers
  themes, directives, speaker notes, presenter view, and export to PDF, HTML, and
  PPTX formats. Includes VS Code integration, CLI usage, and CI/CD automation.
version: 1.0.0
category: development
type: skill
capabilities:
- Markdown-based slide creation
- Built-in and custom themes
- Directives for slide control
- Speaker notes and presenter view
- Export to PDF, HTML, PPTX
- VS Code extension integration
- CLI for automation and CI/CD
- Math equations with KaTeX
- Mermaid diagrams
tools:
- marp-cli
- marp-vscode
- marp-core
- puppeteer
tags:
- documentation
- presentations
- slides
- markdown
- pdf
- pptx
platforms:
- linux
- macos
- windows
related_skills:
- pandoc
- mkdocs
see_also:
- marp-slide-2-key-points
- marp-2-frontmatter-configuration
- marp-7-images-and-backgrounds
- marp-8-math-equations
- marp-inline-math
- marp-9-mermaid-diagrams
- marp-flowchart
- marp-10-cli-usage
- marp-left-column
- marp-right-column
- marp-3-image-guidelines
- marp-related-resources
---

# Marp

## When to Use This Skill

### USE When

- Creating presentations from Markdown content
- Need quick slide creation without design overhead
- Want version-controlled presentations (Git-friendly)
- Require multiple output formats (PDF, HTML, PPTX)
- Building automated presentation pipelines
- Need consistent branding across presentations
- Creating technical presentations with code
- Need math equations in slides
### DON'T USE When

- Need complex animations and transitions (use PowerPoint/Keynote)
- Require real-time collaboration (use Google Slides)
- Building interactive web applications (use reveal.js directly)
- Need embedded videos with playback controls
- Building documentation websites (use MkDocs or Docusaurus)

## Prerequisites

### Installation

```bash
# Using npm (recommended)
npm install -g @marp-team/marp-cli

# Using npx (no installation needed)
npx @marp-team/marp-cli --version

# Using Homebrew (macOS)
brew install marp-cli


*See sub-skills for full details.*
### VS Code Extension

```bash
# Install from VS Code marketplace
# Search: "Marp for VS Code"
# Extension ID: marp-team.marp-vscode

code --install-extension marp-team.marp-vscode
```

## Version History

### v1.0.0 (2026-01-17)

- Initial skill creation
- Basic slide creation with Markdown
- Theme customization
- Speaker notes and presenter view
- Image and background handling
- Math equations with KaTeX
- Mermaid diagram integration
- CLI usage and configuration
- VS Code extension setup
- GitHub Actions workflow
- Best practices and troubleshooting

## Sub-Skills

- [1. Basic Slide Creation](1-basic-slide-creation/SKILL.md)
- [Integration with npm Project (+1)](integration-with-npm-project/SKILL.md)
- [1. Project Structure (+1)](1-project-structure/SKILL.md)
- [PDF Export Fails (+3)](pdf-export-fails/SKILL.md)

## Sub-Skills

- [Slide 2: Key Points](slide-2-key-points/SKILL.md)
- [2. Frontmatter Configuration (+4)](2-frontmatter-configuration/SKILL.md)
- [7. Images and Backgrounds](7-images-and-backgrounds/SKILL.md)
- [8. Math Equations](8-math-equations/SKILL.md)
- [Inline Math](inline-math/SKILL.md)
- [9. Mermaid Diagrams](9-mermaid-diagrams/SKILL.md)
- [Flowchart](flowchart/SKILL.md)
- [10. CLI Usage (+5)](10-cli-usage/SKILL.md)
- [Left Column](left-column/SKILL.md)
- [Right Column](right-column/SKILL.md)
- [3. Image Guidelines](3-image-guidelines/SKILL.md)
- [Related Resources](related-resources/SKILL.md)
