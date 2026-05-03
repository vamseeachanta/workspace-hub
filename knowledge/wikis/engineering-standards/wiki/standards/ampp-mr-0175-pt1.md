---
title: "AMPP/NACE MR 0175 Part 1 — Sour Service Materials, General Principles — bounded summary"
tags: ["ampp", "nace", "standards", "materials", "sour-service", "metadata-only"]
added: 2026-05-03
last_updated: 2026-05-03
domain: engineering-standards
code_id: ampp-mr-0175-pt1
legacy_code_id: nace-mr-0175-pt1
publisher: AMPP
legacy_publisher: "NACE International"
revision: "2009-2nd-Ed"
revision_source: "/mnt/ace/O&G-Standards/NACE/NACE MR 0175/NACE MR 0175 Pt 1 2nd Ed (2009) General principles for selection of cracking-resistant materials.pdf"
verified_on: 2026-05-03
public_url: https://store.ampp.org/
sources:
  - /mnt/ace/O&G-Standards/NACE/NACE MR 0175/NACE MR 0175 Pt 1 2nd Ed (2009) General principles for selection of cracking-resistant materials.pdf
extraction_policy: metadata-only
raw_copy_allowed: false
nace_doc_number: "MR 0175 Part 1"
iso_equivalent: "ISO 15156-1"
---

# AMPP/NACE MR 0175 Part 1 — Sour Service Materials, General Principles

## Scope
Bounded resolver target for Part 1 of the joint NACE/ISO sour-service materials selection standard. Part 1 sets the general principles, definitions, and qualification framework that govern selection of cracking-resistant metallic materials for use in oilfield equipment exposed to wet hydrogen sulfide. Part 1 is the umbrella under which Parts 2 and 3 specify carbon and corrosion-resistant alloy material classes.

## Why this page exists
This page is the citation resolver target for downstream `digitalmodel/cathodic_protection/` and materials-selection calc modules under the calc-citation contract at `.claude/rules/calc-citation-contract.md`. Calc callers needing the sour-service qualification framework must cite this code_id. The `legacy_code_id` field bridges the 2021 NACE-to-AMPP publisher rebrand so calc sites still using legacy `nace-*` spellings can be normalized without losing provenance. AMPP retained the NACE document numbers; only the publishing organization renamed. This page contains no clause text, formulas, or tables.

## Where to find the full text
- Raw PDF (2009 2nd Ed, Part 1): `/mnt/ace/O&G-Standards/NACE/NACE MR 0175/NACE MR 0175 Pt 1 2nd Ed (2009) General principles for selection of cracking-resistant materials.pdf` (read-only, vendor-derivative; do not copy into git per #2482)
- Publisher catalog (current edition): https://store.ampp.org/ (registration required for purchase; the publisher-current edition is jointly published with ISO as ISO 15156-1:2020 and supersedes the 2009 second edition on disk)
- Internal callers: no live structured `Citation(...)` calls in `digitalmodel/src/` for Part 1 specifically; the broader `MR0175` token appears once in `digitalmodel/cathodic_protection/`. Calc-callers must verify against the publisher-current edition before relying on this page.

## Cross-references
- [[ampp-mr-0175-pt2]] — companion Part 2 (carbon and low-alloy steels)
- [[ampp-mr-0175-pt3]] — companion Part 3 (corrosion-resistant alloys)
- [[ampp-mr-0175-1995]] — superseded historical 1995 single-document edition
- [[ampp-tm-0177]] — sulfide stress cracking laboratory test method (acceptance-criteria companion)
- [Calc citation contract](../../../../../.claude/rules/calc-citation-contract.md)
