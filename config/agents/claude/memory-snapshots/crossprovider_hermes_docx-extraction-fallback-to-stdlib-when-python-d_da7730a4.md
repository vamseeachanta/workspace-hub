---
name: crossprovider hermes docx-extraction-fallback-to-stdlib-when-python-d
description: DOCX extraction fallback to stdlib when python-docx unavailable
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [docx-parsing, stdlib-fallback, dependency-avoidance]
---

DOCX files are ZIP archives; extract with standard library `zipfile` + `xml.etree.ElementTree`. Locate `word/document.xml`, parse paragraphs/runs. Avoids adding dependencies when `python-docx` is unavailable in `uv` environment. Trade-off: manual parsing is slower but has zero cost for lightweight single-use extractions.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
