---
name: mkdocs-1-project-initialization
description: 'Sub-skill of mkdocs: 1. Project Initialization (+1).'
version: 1.0.0
category: _internal
type: reference
scripts_exempt: true
---

# 1. Project Initialization (+1)

## 1. Project Initialization


```bash
# Create new documentation project
mkdocs new my-project-docs
cd my-project-docs

# Project structure
# my-project-docs/
# ├── docs/
# │   └── index.md
# └── mkdocs.yml

# Or initialize in existing project
mkdir -p docs
touch docs/index.md
touch mkdocs.yml
```


## 2. Basic Configuration (mkdocs.yml)


```yaml
# mkdocs.yml - Minimal configuration
site_name: My Project Documentation
site_url: https://example.com/docs/
site_description: Comprehensive documentation for My Project
site_author: Your Name

# Repository
repo_name: username/my-project
repo_url: https://github.com/username/my-project
edit_uri: edit/main/docs/

# Theme
theme:
  name: material
  palette:
    - scheme: default
      primary: indigo
      accent: indigo
      toggle:
        icon: material/brightness-7
        name: Switch to dark mode
    - scheme: slate
      primary: indigo
      accent: indigo
      toggle:
        icon: material/brightness-4
        name: Switch to light mode
  font:
    text: Roboto
    code: Roboto Mono
  features:
    - navigation.instant
    - navigation.tracking
    - navigation.tabs
    - navigation.sections
    - navigation.expand
    - navigation.top
    - search.suggest
    - search.highlight
    - content.tabs.link
    - content.code.copy
    - content.code.annotate

# Navigation
nav:
  - Home: index.md
  - Getting Started:
      - Installation: getting-started/installation.md
      - Quick Start: getting-started/quickstart.md
      - Configuration: getting-started/configuration.md
  - User Guide:
      - Overview: guide/overview.md
      - Basic Usage: guide/basic-usage.md
      - Advanced: guide/advanced.md
  - API Reference: api/reference.md
  - FAQ: faq.md
  - Changelog: changelog.md

# Plugins
plugins:
  - search:
      lang: en
      separator: '[\s\-,:!=\[\]()"/]+|(?!\b)(?=[A-Z][a-z])|\.(?!\d)|&[lg]t;'
  - minify:
      minify_html: true

# Markdown extensions
markdown_extensions:
  - abbr
  - admonition
  - attr_list
  - def_list
  - footnotes
  - md_in_html
  - toc:
      permalink: true
      toc_depth: 3
  - pymdownx.arithmatex:
      generic: true
  - pymdownx.betterem:
      smart_enable: all
  - pymdownx.caret
  - pymdownx.details
  - pymdownx.emoji:
      emoji_index: !!python/name:material.extensions.emoji.twemoji
      emoji_generator: !!python/name:material.extensions.emoji.to_svg
  - pymdownx.highlight:
      anchor_linenums: true
      line_spans: __span
      pygments_lang_class: true
  - pymdownx.inlinehilite
  - pymdownx.keys
  - pymdownx.magiclink:
      repo_url_shorthand: true
      user: username
      repo: my-project
  - pymdownx.mark
  - pymdownx.smartsymbols
  - pymdownx.superfences:
      custom_fences:
        - name: mermaid
          class: mermaid
          format: !!python/name:pymdownx.superfences.fence_code_format
  - pymdownx.tabbed:
      alternate_style: true
  - pymdownx.tasklist:
      custom_checkbox: true
  - pymdownx.tilde

# Extra
extra:
  social:
    - icon: fontawesome/brands/github
      link: https://github.com/username
    - icon: fontawesome/brands/twitter
      link: https://twitter.com/username
  generator: false
  version:
    provider: mike

# Copyright
copyright: Copyright &copy; 2024-2026 Your Name
```
