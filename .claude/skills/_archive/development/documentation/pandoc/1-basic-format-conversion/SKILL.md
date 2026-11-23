---
name: pandoc-1-basic-format-conversion
description: 'Sub-skill of pandoc: 1. Basic Format Conversion (+3).'
version: 1.0.0
category: development
type: reference
scripts_exempt: true
---

# 1. Basic Format Conversion (+3)

## 1. Basic Format Conversion


```bash
# Markdown to PDF
pandoc document.md -o document.pdf

# Markdown to DOCX
pandoc document.md -o document.docx

# Markdown to HTML
pandoc document.md -o document.html --standalone

# Markdown to LaTeX
pandoc document.md -o document.tex

# HTML to Markdown
pandoc page.html -o page.md

# DOCX to Markdown
pandoc document.docx -o document.md

# Multiple input files
pandoc chapter1.md chapter2.md chapter3.md -o book.pdf

# Specify input format explicitly
pandoc -f markdown -t pdf document.md -o document.pdf
```


## 2. PDF Generation with Options


```bash
# Basic PDF with table of contents
pandoc document.md -o document.pdf --toc

# PDF with XeLaTeX engine (better font support)
pandoc document.md -o document.pdf \
    --pdf-engine=xelatex \
    --toc \
    --toc-depth=3

# PDF with custom margins
pandoc document.md -o document.pdf \
    --pdf-engine=xelatex \
    -V geometry:margin=1in

# PDF with custom fonts
pandoc document.md -o document.pdf \
    --pdf-engine=xelatex \
    -V mainfont="Georgia" \
    -V sansfont="Helvetica" \
    -V monofont="Menlo"

# PDF with paper size and font size
pandoc document.md -o document.pdf \
    --pdf-engine=xelatex \
    -V papersize=a4 \
    -V fontsize=11pt

# PDF with numbered sections
pandoc document.md -o document.pdf \
    --number-sections \
    --toc

# PDF with syntax highlighting style
pandoc document.md -o document.pdf \
    --highlight-style=tango

# List available highlighting styles
pandoc --list-highlight-styles
```


## 3. Word Document (DOCX) Generation


```bash
# Basic DOCX
pandoc document.md -o document.docx

# DOCX with table of contents
pandoc document.md -o document.docx --toc

# DOCX with reference document (template)
pandoc document.md -o document.docx \
    --reference-doc=template.docx

# DOCX with syntax highlighting
pandoc document.md -o document.docx \
    --highlight-style=kate

# Creating a reference document template
pandoc --print-default-data-file reference.docx > template.docx
# Edit template.docx in Word to customize styles
```


## 4. HTML Generation


```bash
# Standalone HTML (includes head, body)
pandoc document.md -o document.html --standalone

# HTML with custom CSS
pandoc document.md -o document.html \
    --standalone \
    --css=styles.css

# HTML with embedded CSS
pandoc document.md -o document.html \
    --standalone \
    --css=styles.css \
    --embed-resources \
    --self-contained

# HTML with syntax highlighting
pandoc document.md -o document.html \
    --standalone \
    --highlight-style=pygments

# HTML with table of contents
pandoc document.md -o document.html \
    --standalone \
    --toc \
    --toc-depth=2

# HTML with math rendering (MathJax)
pandoc document.md -o document.html \
    --standalone \
    --mathjax

# HTML5 output
pandoc document.md -o document.html \
    --standalone \
    -t html5
```
