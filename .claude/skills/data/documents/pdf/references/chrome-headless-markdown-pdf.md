# Chrome headless Markdown/HTML → PDF fallback

Use this when asked to prepare a polished PDF from Markdown/HTML and richer PDF generation stacks are missing (`pandoc`, `wkhtmltopdf`, `weasyprint`, `reportlab`, or `markdown` unavailable).

## Pattern

1. Treat Markdown as the durable source and generate a self-contained HTML intermediary with embedded CSS.
2. Use Chrome headless for PDF output:

```bash
google-chrome --headless --disable-gpu --no-sandbox --no-pdf-header-footer \
  --print-to-pdf=path/to/output.pdf \
  file://$(pwd)/path/to/source.html
```

`--no-pdf-header-footer` is essential for job-search/client-ready PDFs; without it Chrome may add date, title, URL, and page numbers.

3. Verify the PDF mechanically:

```bash
file path/to/output.pdf
pdfinfo path/to/output.pdf | grep Pages
pdftotext path/to/output.pdf - | head -60
```

4. Verify visually when layout quality matters:

```bash
mkdir -p /tmp/pdf_verify
pdftoppm -f 1 -l 2 -png path/to/output.pdf /tmp/pdf_verify/output
file /tmp/pdf_verify/output-1.png /tmp/pdf_verify/output-2.png
```

Inspect rendered PNGs for browser artifacts, orphan headings, flattened nested bullets, and readability. If a section heading lands alone at the bottom of a page, add CSS such as:

```css
.section-break { break-before: page; page-break-before: always; margin-top: 0; }
```

## Resume/CV-specific checks

- Clarify overlapping `Present` roles with labels such as `Co-Founder`, `Independent Consulting Practice`, or `concurrent` where truthful.
- Prefer a single-column professional layout for technical/executive job-search PDFs.
- If a lightweight Markdown converter flattens nested bullets, consolidate nested items into clear single-level bullets before final PDF generation.
- Keep the PDF free of browser print headers/footers and verify via both `pdftotext` and page image renderings.
