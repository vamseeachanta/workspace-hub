---
name: crossprovider hermes data-source-priority-hierarchy-for-financial-dat
description: Data source priority hierarchy for financial datasets
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [data-architecture, financial-data, sourcing-strategy]
---

Establish explicit source priority when building year-on-year financial/operational datasets: operator filings (annual reports, 10-K, 20-F) > official press releases > regulator project documents > investor presentations > media/wire services (only operator-confirmed). Include confidence field and page reference in schema to track provenance.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
