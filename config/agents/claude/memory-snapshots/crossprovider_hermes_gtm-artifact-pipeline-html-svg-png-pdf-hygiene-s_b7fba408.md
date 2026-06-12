---
name: crossprovider hermes gtm-artifact-pipeline-html-svg-png-pdf-hygiene-s
description: GTM artifact pipeline: HTML → SVG → PNG/PDF + hygiene scan + commit
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [artifact-pipeline, gtm, infographic-workflow]
---

Repeatable pattern for client-facing infographics: HTML source → SVG intermediate for editability → PNG (web) + PDF (print) exports → scoped secret/path scan → commit/push. White-background variants created for print markup, dark for web. Hygienic and composable; worth encoding as reusable skill/template to avoid one-off manual cleanup.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
