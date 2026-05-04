---
name: pandoc-11-makefile-for-document-projects
description: 'Sub-skill of pandoc: 11. Makefile for Document Projects (+1).'
version: 1.0.0
category: development
type: reference
scripts_exempt: true
---

# 11. Makefile for Document Projects (+1)

## 11. Makefile for Document Projects


```makefile
# Makefile for document conversion project

# Configuration
PANDOC = pandoc
PDF_ENGINE = xelatex
TEMPLATE = templates/report.tex
BIBLIOGRAPHY = references/main.bib
CSL = styles/ieee.csl

# Directories
SRC_DIR = src
OUT_DIR = output
BUILD_DIR = build

# Source files
MD_FILES := $(wildcard $(SRC_DIR)/*.md)
PDF_FILES := $(patsubst $(SRC_DIR)/%.md,$(OUT_DIR)/%.pdf,$(MD_FILES))
DOCX_FILES := $(patsubst $(SRC_DIR)/%.md,$(OUT_DIR)/%.docx,$(MD_FILES))
HTML_FILES := $(patsubst $(SRC_DIR)/%.md,$(OUT_DIR)/%.html,$(MD_FILES))

# Common options
PANDOC_OPTS = --toc --number-sections --highlight-style=tango
PDF_OPTS = --pdf-engine=$(PDF_ENGINE) --template=$(TEMPLATE)
CITE_OPTS = --citeproc --bibliography=$(BIBLIOGRAPHY) --csl=$(CSL)

# Phony targets
.PHONY: all pdf docx html clean help

# Default target
all: pdf

# Build all PDFs
pdf: $(PDF_FILES)

# Build all DOCX
docx: $(DOCX_FILES)

# Build all HTML
html: $(HTML_FILES)

# Pattern rules
$(OUT_DIR)/%.pdf: $(SRC_DIR)/%.md $(TEMPLATE) $(BIBLIOGRAPHY) | $(OUT_DIR)
	@echo "Building PDF: $@"
	$(PANDOC) $< -o $@ $(PANDOC_OPTS) $(PDF_OPTS) $(CITE_OPTS)

$(OUT_DIR)/%.docx: $(SRC_DIR)/%.md $(BIBLIOGRAPHY) | $(OUT_DIR)
	@echo "Building DOCX: $@"
	$(PANDOC) $< -o $@ $(PANDOC_OPTS) $(CITE_OPTS)

$(OUT_DIR)/%.html: $(SRC_DIR)/%.md $(BIBLIOGRAPHY) | $(OUT_DIR)
	@echo "Building HTML: $@"
	$(PANDOC) $< -o $@ --standalone $(PANDOC_OPTS) $(CITE_OPTS) --embed-resources

# Create output directory
$(OUT_DIR):
	mkdir -p $(OUT_DIR)

# Clean build artifacts
clean:
	rm -rf $(OUT_DIR)/*
	rm -rf $(BUILD_DIR)/*

# Watch for changes (requires entr)
watch:
	find $(SRC_DIR) -name "*.md" | entr -c make pdf

# Help
help:
	@echo "Available targets:"
	@echo "  all    - Build all PDFs (default)"
	@echo "  pdf    - Build PDF files"
	@echo "  docx   - Build DOCX files"
	@echo "  html   - Build HTML files"
	@echo "  clean  - Remove built files"
	@echo "  watch  - Watch for changes and rebuild"
	@echo ""
	@echo "Source files: $(MD_FILES)"
```


## 12. GitHub Actions Workflow


```yaml
# .github/workflows/build-docs.yml
name: Build Documents

on:
  push:
    branches: [main]
    paths:
      - 'docs/**'
      - 'templates/**'
      - '.github/workflows/build-docs.yml'
  pull_request:
    paths:
      - 'docs/**'
      - 'templates/**'
  workflow_dispatch:

jobs:
  build:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Install Pandoc
        run: |
          wget https://github.com/jgm/pandoc/releases/download/3.1.11/pandoc-3.1.11-linux-amd64.tar.gz
          tar xzf pandoc-3.1.11-linux-amd64.tar.gz
          sudo mv pandoc-3.1.11/bin/* /usr/local/bin/

      - name: Install pandoc-crossref
        run: |
          wget https://github.com/lierdakil/pandoc-crossref/releases/download/v0.3.17.0/pandoc-crossref-Linux.tar.xz
          tar xf pandoc-crossref-Linux.tar.xz
          sudo mv pandoc-crossref /usr/local/bin/

      - name: Install LaTeX
        run: |
          sudo apt-get update
          sudo apt-get install -y texlive-xetex texlive-fonts-recommended \
            texlive-latex-extra texlive-fonts-extra

      - name: Build PDF documents
        run: |
          mkdir -p output
          for file in docs/*.md; do
            output="output/$(basename "${file%.md}.pdf")"
            echo "Building: $file -> $output"
            pandoc "$file" -o "$output" \
              --pdf-engine=xelatex \
              --toc \
              --number-sections \
              --filter pandoc-crossref \
              --template=templates/report.tex
          done

      - name: Upload artifacts
        uses: actions/upload-artifact@v4
        with:
          name: documents
          path: output/*.pdf

  release:
    needs: build
    runs-on: ubuntu-latest
    if: github.event_name == 'push' && github.ref == 'refs/heads/main'

    steps:
      - name: Download artifacts
        uses: actions/download-artifact@v4
        with:
          name: documents
          path: output

      - name: Create release
        uses: softprops/action-gh-release@v1
        if: startsWith(github.ref, 'refs/tags/')
        with:
          files: output/*.pdf
```
