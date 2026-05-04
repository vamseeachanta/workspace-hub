---
name: documentation-1-docs-as-code
description: 'Sub-skill of documentation: 1. Docs as Code (+1).'
version: 1.0.0
category: development
type: reference
scripts_exempt: true
---

# 1. Docs as Code (+1)

## 1. Docs as Code

```yaml
# .github/workflows/docs.yml
name: Documentation
on:
  push:
    branches: [main]
    paths: ['docs/**']

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: pip install mkdocs-material
      - run: mkdocs build
      - uses: peaceiris/actions-gh-pages@v3
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          publish_dir: ./site
```


## 2. Consistent Structure

```bash
# Documentation template
create_doc_template() {
    local name="$1"
    cat > "docs/$name.md" << 'EOF'
# Title
