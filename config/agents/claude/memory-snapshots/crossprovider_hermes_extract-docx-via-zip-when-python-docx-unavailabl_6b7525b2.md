---
name: crossprovider hermes extract-docx-via-zip-when-python-docx-unavailabl
description: Extract DOCX via ZIP when python-docx unavailable
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [document-extraction, workaround]
---

DOCX files are ZIP archives; extract via `unzip -p file.docx word/document.xml` + parsing. Avoids external dependencies (pandoc, wkhtmltopdf) when python-docx module unavailable.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
