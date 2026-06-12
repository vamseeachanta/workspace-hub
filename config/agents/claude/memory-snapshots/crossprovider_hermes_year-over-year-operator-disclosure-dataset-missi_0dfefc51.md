---
name: crossprovider hermes year-over-year-operator-disclosure-dataset-missi
description: Year-over-year operator disclosure dataset missing from worldenergydata cost architecture
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [worldenergydata, cost-data, missing-architectural-layer, data-modeling]
---

The cost module already ingests one-off sanction cost-points from annual reports (BP 2017, Shell 2018/2021, etc.), but lacks a structured time-series layer for operator-level and project-level disclosure tracking (fiscal_year, filing_type, metric_name, confidence, source_url). This blocks cost-history analysis, rebaselining event detection, and capex forecasting—a gap recurring across multiple sessions. The solution is a new disclosure layer with both operator-level series (upstream capex, offshore capex, decommissioning provision) and project-level series (sanctioned capex, revised capex, startup year) keyed to fiscal_year and source priority (operator filings > FID press > regulator approvals > investor presentations).

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
