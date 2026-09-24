---
name: crossprovider gemini rao-reference-linking-enables-multi-stage-diffra
description: RAO reference linking enables multi-stage diffraction-to-motion workflow
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [architecture, rao-linking, workflow-separation]
---

RaoReference schema (solver, draft, loading condition, headings) links diffraction analysis results to specific hull panel entries. This separation allows the hull library to remain independent of solver details while enabling downstream motion analysis to reference computed RAO datasets.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
