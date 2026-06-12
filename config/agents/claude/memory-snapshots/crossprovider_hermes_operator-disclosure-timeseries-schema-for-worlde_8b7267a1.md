---
name: crossprovider hermes operator-disclosure-timeseries-schema-for-worlde
description: Operator disclosure timeseries schema for worldenergydata
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [worldenergydata, data-architecture, timeseries, operator-disclosures]
---

worldenergydata already sources from annual reports/SEC filings but only tracks one-off sanctioned cost points. Add structured disclosure layer (operator, fiscal_year, filing_type, metric_name/value/currency, source_url, confidence) to enable year-over-year timeseries. Source hierarchy: annual report > 10-K > regulator PDO > investor presentation > validated press release.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
