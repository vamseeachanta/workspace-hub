---
title: "ASME B16.34 — Valves Flanged, Threaded, and Welding End (bounded summary)"
tags: ["asme", "standards", "valves", "metadata-only"]
added: 2026-05-02
last_updated: 2026-05-02
domain: engineering-standards
code_id: asme-b16-34
publisher: ASME
revision: "1996"
revision_source: "/mnt/ace/O&G-Standards/ASME/BS/ASME B16.34-1996.pdf"
publisher_current_edition: "2020"
methodology_status: "unknown"
verified_on: 2026-05-02
public_url: https://www.asme.org/codes-standards/find-codes-standards/b16-34-valves-flanged-threaded-welding-end
sources:
  - /mnt/ace/O&G-Standards/ASME/BS/ASME B16.34-1996.pdf
extraction_policy: metadata-only
raw_copy_allowed: false
---

# ASME B16.34 — Valves Flanged, Threaded, and Welding End (bounded summary)

## Scope

ASME B16.34 covers pressure-temperature ratings, dimensions, tolerances, materials, nondestructive examination, testing, and marking for cast, forged, and fabricated flanged-end, threaded-end, and welding-end valves. Coverage includes both the standard-class and special-class rating tracks distinguished by the level of supplementary examination.

## Why this page exists

Resolver target for digitalmodel `Citation` instances per `.claude/rules/calc-citation-contract.md`. Contains no clause text, no pressure-temperature rating tables, and no dimensional tables from the source. Downstream callers wire valve-rating lookups through this page rather than parsing the source PDF. B16.34 is the canonical valve-rating consumer for the B31.x process and pipeline calc paths.

## Where to find the full text

- Raw PDF: `/mnt/ace/O&G-Standards/ASME/BS/ASME B16.34-1996.pdf` (read-only, vendor-derivative; do not copy into git per #2482)
- Publisher catalog: https://www.asme.org/codes-standards/find-codes-standards/b16-34-valves-flanged-threaded-welding-end
- Internal callers: `digitalmodel/src/digitalmodel/` modules resolving valve pressure-temperature ratings

## Cross-references

- [[asme-b16-5]] — flange-rating cross-link
- [[asme-pcc-1]] — assembly-side complement on flanged ends
- [[asme-b31-3]] — process-piping consumer
- [Calc citation contract](../../../../../.claude/rules/calc-citation-contract.md)
