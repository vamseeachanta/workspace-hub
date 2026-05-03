---
title: "ASME B16.5 — Pipe Flanges and Flanged Fittings NPS 1/2 through NPS 24 (bounded summary)"
tags: ["asme", "standards", "flanges", "metadata-only"]
added: 2026-05-02
last_updated: 2026-05-02
domain: engineering-standards
code_id: asme-b16-5
publisher: ASME
revision: "2013"
revision_source: "/mnt/ace/O&G-Standards/ASME/BS/ASME B16.5-2013.pdf"
publisher_current_edition: "2020"
methodology_status: "unknown"
verified_on: 2026-05-02
public_url: https://www.asme.org/codes-standards/find-codes-standards/b16-5-pipe-flanges-flanged-fittings-nps-12-nps-24-metric-inch-standard
sources:
  - /mnt/ace/O&G-Standards/ASME/BS/ASME B16.5-2013.pdf
extraction_policy: metadata-only
raw_copy_allowed: false
---

# ASME B16.5 — Pipe Flanges and Flanged Fittings NPS 1/2 through NPS 24 (bounded summary)

## Scope

ASME B16.5 covers pipe flanges and flanged fittings in nominal pipe sizes one-half through twenty-four inches and in pressure classes from the lowest standard rating up through the highest commonly tabulated rating. Coverage includes pressure-temperature ratings, materials, dimensions, tolerances, marking, and testing for the in-scope flange and flanged-fitting products.

## Why this page exists

Resolver target for digitalmodel `Citation` instances per `.claude/rules/calc-citation-contract.md`. Contains no clause text, no pressure-temperature rating tables, and no dimensional tables from the source. Downstream callers wire flange-class rating lookups through this page rather than parsing the source PDF. B16.5 is the canonical flange-rating consumer for the B31.x process and pipeline calc paths and pairs with PCC-1 on the assembly side.

## Where to find the full text

- Raw PDF: `/mnt/ace/O&G-Standards/ASME/BS/ASME B16.5-2013.pdf` (read-only, vendor-derivative; do not copy into git per #2482)
- Publisher catalog: https://www.asme.org/codes-standards/find-codes-standards/b16-5-pipe-flanges-flanged-fittings-nps-12-nps-24-metric-inch-standard
- Internal callers: `digitalmodel/src/digitalmodel/` modules resolving flange-class pressure-temperature ratings

## Cross-references

- [[asme-pcc-1]] — assembly-side complement
- [[asme-b16-34]] — valve flange-rating cross-link
- [[asme-b31-3]] — process-piping consumer
- [Calc citation contract](../../../../../.claude/rules/calc-citation-contract.md)
