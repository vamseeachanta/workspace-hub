---
name: pdf-dependencies
description: 'Sub-skill of pdf: Dependencies.'
version: 1.2.2
category: data
type: reference
scripts_exempt: true
---

# Dependencies

## Dependencies


```bash
# Core PDF libraries
pip install pypdf pdfplumber reportlab pytesseract pdf2image

# OpenAI Codex for PDF to Markdown conversion
pip install openai
```

System tools:
- Poppler (pdftotext, pdftoppm)
- qpdf
- pdftk
- Tesseract OCR

Environment variables:
```bash
export OPENAI_API_KEY="your-api-key-here"
```

---
