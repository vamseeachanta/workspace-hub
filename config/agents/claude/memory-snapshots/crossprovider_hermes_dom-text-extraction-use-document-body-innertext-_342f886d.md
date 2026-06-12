---
name: crossprovider hermes dom-text-extraction-use-document-body-innertext-
description: DOM text extraction: use document.body.innerText when paragraph iteration fails
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [javascript, dom, extraction]
---

When JavaScript DOM traversal (e.g., iterating `querySelectorAll('p')`) yields empty results due to nesting structure, fall back to `document.body.innerText` to capture all visible text content at once.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
