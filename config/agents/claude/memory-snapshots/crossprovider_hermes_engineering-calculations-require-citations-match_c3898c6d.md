---
name: crossprovider hermes engineering-calculations-require-citations-match
description: Engineering calculations require Citations matching calc-output-citation schema
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [engineering-calculations, citation, provenance, workflow]
---

Calc modules using standards-derived constants/formulas must emit a `Citation` object matching `docs/standards/calc-output-citation.md` or explicitly justify exemption/inheritance per `.claude/rules/calc-citation-contract.md`. Do not silently ship engineering calcs without provenance.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
