---
name: mkdocs-common-issues
description: 'Sub-skill of mkdocs: Common Issues (+1).'
version: 1.0.0
category: _internal
type: reference
scripts_exempt: true
---

# Common Issues (+1)

## Common Issues


#### Build Fails with "Page not in nav"

```yaml
# mkdocs.yml - Allow pages not in nav
validation:
  nav:
    omitted_files: info
    not_found: warn
    absolute_links: info
```

#### Mermaid Diagrams Not Rendering

```yaml
# Ensure superfences is configured correctly
markdown_extensions:
  - pymdownx.superfences:
      custom_fences:
        - name: mermaid
          class: mermaid
          format: !!python/name:pymdownx.superfences.fence_code_format
```

#### Search Not Working

```yaml
# Check search configuration
plugins:
  - search:
      lang: en
      prebuild_index: true  # Build search index at build time
```

#### Git Revision Plugin Fails

```bash
# Ensure git history is available
git fetch --unshallow  # In CI environments

# Or disable in mkdocs.yml for local testing
plugins:
  - git-revision-date-localized:
      fallback_to_build_date: true
```

#### Social Cards Generation Fails

```bash
# Install required dependencies
pip install pillow cairosvg

# On Ubuntu
apt-get install libcairo2-dev libffi-dev

# On macOS
brew install cairo
```


## Debug Mode


```bash
# Verbose build output
mkdocs build --verbose

# Serve with debug info
mkdocs serve --verbose --dev-addr 0.0.0.0:8000

# Strict mode catches warnings as errors
mkdocs build --strict
```
