---
name: crossprovider hermes html-report-artifact-verification-workflow-for-g
description: HTML report artifact verification workflow for generated documents
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [artifact-verification, html-to-document, quality-gate]
---

When converting HTML reports to client-facing formats (PDF/DOCX), use a multi-step verification gate: browser render (title, inputs, charts, controls, provenance), interactive test (change inputs, verify updates), format extraction (page count, text identity), and scoped hygiene scan (no environment/path leakage). This prevents artifact identity loss during format conversion.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
