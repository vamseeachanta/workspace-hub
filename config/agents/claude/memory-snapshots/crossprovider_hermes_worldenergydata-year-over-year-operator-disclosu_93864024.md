---
name: crossprovider hermes worldenergydata-year-over-year-operator-disclosu
description: worldenergydata: year-over-year operator disclosure dataset
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [worldenergydata, dataset-design, operator-disclosures]
---

Repo ingests operator annual reports + SEC filings for one-off cost points but lacks structured timeseries. Build disclosure layer with [operator, fiscal_year, filing_type, project_name, metric_name, metric_value, currency, source_url, confidence]. Track operator-level capex + project-level rebaselining. Source priority: annual_report > 10-K > press_release.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
