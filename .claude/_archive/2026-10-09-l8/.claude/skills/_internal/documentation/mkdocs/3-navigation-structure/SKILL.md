---
name: mkdocs-3-navigation-structure
description: 'Sub-skill of mkdocs: 3. Navigation Structure (+2).'
version: 1.0.0
category: _internal
type: reference
scripts_exempt: true
---

# 3. Navigation Structure (+2)

## 3. Navigation Structure


```yaml
# mkdocs.yml - Advanced navigation
nav:
  - Home: index.md
  - Getting Started:
      - getting-started/index.md
      - Installation:
          - Linux: getting-started/install-linux.md
          - macOS: getting-started/install-macos.md
          - Windows: getting-started/install-windows.md
          - Docker: getting-started/install-docker.md
      - Quick Start: getting-started/quickstart.md
      - Configuration: getting-started/configuration.md
  - User Guide:
      - guide/index.md
      - Core Concepts:
          - Architecture: guide/architecture.md
          - Components: guide/components.md
          - Data Flow: guide/data-flow.md
      - Tutorials:
          - Basic Tutorial: guide/tutorials/basic.md
          - Advanced Tutorial: guide/tutorials/advanced.md
          - Integration: guide/tutorials/integration.md
      - Best Practices: guide/best-practices.md
  - API Reference:
      - api/index.md
      - REST API: api/rest.md
      - Python SDK: api/python-sdk.md
      - CLI Reference: api/cli.md
  - Examples:
      - examples/index.md
      - Basic Examples: examples/basic.md
      - Advanced Examples: examples/advanced.md
  - Contributing: contributing.md
  - Changelog: changelog.md
  - License: license.md
```


## 4. Material Theme Features


```yaml
# mkdocs.yml - Theme customization
theme:
  name: material
  custom_dir: docs/overrides  # Custom templates
  logo: assets/logo.png
  favicon: assets/favicon.ico
  icon:
    repo: fontawesome/brands/github
    admonition:
      note: octicons/tag-16
      warning: octicons/alert-16
      danger: octicons/zap-16
      tip: octicons/light-bulb-16
      example: octicons/beaker-16

  palette:
    # Light mode
    - media: "(prefers-color-scheme: light)"
      scheme: default
      primary: deep purple
      accent: deep purple
      toggle:
        icon: material/weather-sunny
        name: Switch to dark mode
    # Dark mode
    - media: "(prefers-color-scheme: dark)"
      scheme: slate
      primary: deep purple
      accent: deep purple
      toggle:
        icon: material/weather-night
        name: Switch to light mode

  features:
    # Navigation
    - navigation.instant
    - navigation.instant.progress
    - navigation.tracking
    - navigation.tabs
    - navigation.tabs.sticky
    - navigation.sections
    - navigation.expand
    - navigation.path
    - navigation.prune
    - navigation.indexes
    - navigation.top
    - navigation.footer
    # Table of contents
    - toc.follow
    - toc.integrate
    # Search
    - search.suggest
    - search.highlight
    - search.share
    # Header
    - header.autohide
    # Content
    - content.tabs.link
    - content.code.copy
    - content.code.select
    - content.code.annotate
    - content.tooltips
    # Announce
    - announce.dismiss
```


## 5. Admonitions and Call-outs


```markdown
<!-- docs/guide/admonitions.md -->

# Using Admonitions

MkDocs Material supports various admonition types for highlighting content.
