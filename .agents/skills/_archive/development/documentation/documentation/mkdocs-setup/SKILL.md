---
name: documentation-mkdocs-setup
description: 'Sub-skill of documentation: MkDocs Setup (+3).'
version: 1.0.0
category: development
type: reference
scripts_exempt: true
---

# MkDocs Setup (+3)

## MkDocs Setup

```bash
# See mkdocs for complete patterns
pip install mkdocs mkdocs-material

# Initialize project
mkdocs new my-docs
cd my-docs

# mkdocs.yml configuration
cat > mkdocs.yml << 'EOF'
site_name: My Documentation
theme:
  name: material
  palette:
    primary: indigo
  features:
    - navigation.tabs
    - search.highlight

plugins:
  - search
  - minify

nav:
  - Home: index.md
  - Getting Started: getting-started.md
  - API Reference: api.md
EOF

# Serve locally
mkdocs serve

# Build for production
mkdocs build
```


## Sphinx Autodoc

```bash
# See sphinx for complete patterns
pip install sphinx sphinx-rtd-theme

# Initialize
sphinx-quickstart docs

# conf.py configuration
cat >> docs/conf.py << 'EOF'
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinx.ext.viewcode',
    'sphinx.ext.intersphinx',
]

autodoc_default_options = {
    'members': True,
    'undoc-members': True,
    'show-inheritance': True,
}

intersphinx_mapping = {
    'python': ('https://docs.python.org/3', None),
}
EOF

# Generate API docs
sphinx-apidoc -o docs/api src/

# Build HTML
sphinx-build -b html docs docs/_build
```


## Pandoc Conversion

```bash
# See pandoc for complete patterns

# Markdown to PDF
pandoc README.md -o output.pdf \
    --pdf-engine=xelatex \
    --template=template.tex \
    --toc

# Markdown to Word
pandoc doc.md -o output.docx \
    --reference-doc=template.docx

# Multiple files to single document
pandoc chapter1.md chapter2.md chapter3.md \
    -o book.pdf \
    --toc \
    --number-sections

# HTML to Markdown
pandoc https://example.com/page.html -o page.md
```


## Marp Presentation

```bash
# See marp for complete patterns
npm install -g @marp-team/marp-cli

# Create presentation
cat > slides.md << 'EOF'
---
marp: true
theme: default
paginate: true
---

# Presentation Title

Speaker Name
2026-01-17

---
