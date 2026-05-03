---
title: "ASME B31.3 — Process Piping (bounded summary)"
tags: ["asme", "standards", "piping", "metadata-only"]
added: 2026-05-02
last_updated: 2026-05-02
domain: engineering-standards
code_id: asme-b31-3
publisher: ASME
revision: "2012"
revision_source: "/mnt/ace/O&G-Standards/ASME/ASME B31.3 - Process Piping/ASME B31.3 2012 - Processing Piping.pdf"
publisher_current_edition: "2024/2026 cycle"
methodology_status: "stale-as-of-publisher-cycle"
verified_on: 2026-05-02
public_url: https://www.asme.org/codes-standards/find-codes-standards/b31-3-process-piping
sources:
  - /mnt/ace/O&G-Standards/ASME/ASME B31.3 - Process Piping/ASME B31.3 2012 - Processing Piping.pdf
extraction_policy: metadata-only
raw_copy_allowed: false
---

# ASME B31.3 — Process Piping (bounded summary)

## Scope

ASME B31.3 governs design, materials, fabrication, examination, and testing for piping systems carrying process fluids in petroleum refineries, chemical plants, pharmaceutical, and related installations. It establishes minimum engineering requirements for pressure piping outside the boiler and pipeline-transportation scopes covered by other B31 sections.

## Why this page exists

Resolver target for digitalmodel `Citation` instances per `.claude/rules/calc-citation-contract.md`. Contains no clause text, no formulas, and no tables from the source. Downstream callers wire B31.3 stress-check constants through this page rather than parsing the source PDF. The on-disk revision lags the publisher's currently active 2024/2026 cycle by approximately 14 years; the methodology for Stress Intensification Factor (SIF) calculation changed across that gap (the simplified Appendix-D chart approach is no longer the mandatory route in the current cycle, having been superseded by an ASME B31J based method). Calc callers MUST treat the on-disk 2012 SIF approach as stale-as-of-publisher-cycle and confirm the citing calc is not silently relying on the retired methodology.

## Where to find the full text

- Raw PDF: `/mnt/ace/O&G-Standards/ASME/ASME B31.3 - Process Piping/ASME B31.3 2012 - Processing Piping.pdf` (read-only, vendor-derivative; do not copy into git per #2482)
- Publisher catalog: https://www.asme.org/codes-standards/find-codes-standards/b31-3-process-piping
- Internal callers: `digitalmodel/src/digitalmodel/` modules referencing `ASME B31.3` / `ASMEB313` symbols (process-piping stress checks)

## Cross-references

- [[asme-bpvc-ii-d]] — allowable stresses sourced upstream
- [[asme-bpvc-ix]] — welding qualification basis
- [[asme-b16-5]] — flange-rating cross-link
- [Calc citation contract](../../../../../.claude/rules/calc-citation-contract.md)
