---
title: "AMPP/NACE MR 0175 Part 2 — Carbon and Low-Alloy Steels — bounded summary"
tags: ["ampp", "nace", "standards", "materials", "sour-service", "carbon-steel", "metadata-only"]
added: 2026-05-03
last_updated: 2026-05-03
domain: engineering-standards
code_id: ampp-mr-0175-pt2
legacy_code_id: nace-mr-0175-pt2
publisher: AMPP
legacy_publisher: "NACE International"
revision: "2009-2nd-Ed"
revision_source: "/mnt/ace/O&G-Standards/NACE/NACE MR 0175/NACE MR 0175 Pt 2 2nd Ed (2009) Cracking-resistant carbon and low-alloy steels,and the use of cast irons.pdf"
verified_on: 2026-05-03
public_url: https://store.ampp.org/
sources:
  - /mnt/ace/O&G-Standards/NACE/NACE MR 0175/NACE MR 0175 Pt 2 2nd Ed (2009) Cracking-resistant carbon and low-alloy steels,and the use of cast irons.pdf
extraction_policy: metadata-only
raw_copy_allowed: false
nace_doc_number: "MR 0175 Part 2"
iso_equivalent: "ISO 15156-2"
---

# AMPP/NACE MR 0175 Part 2 — Carbon and Low-Alloy Steels

## Scope
Bounded resolver target for Part 2 of the joint NACE/ISO sour-service materials selection standard. Part 2 specifies the cracking-resistance qualification requirements for carbon steels, low-alloy steels, and the limited use of cast irons in wet hydrogen sulfide environments. Part 2 sits under the Part 1 general-principles umbrella and is the workhorse pipeline-and-pressure-vessel material class reference for sour service.

## Why this page exists
This page is the citation resolver target for downstream calc modules selecting carbon and low-alloy steel for sour-service application under the calc-citation contract at `.claude/rules/calc-citation-contract.md`. The `legacy_code_id` field bridges the 2021 NACE-to-AMPP publisher rebrand so calc sites still using legacy `nace-*` spellings resolve to the canonical current identifier. AMPP retained the NACE document numbers; only the publishing organization renamed. This page contains no clause text, formulas, or tables; the qualification rules and environmental limits in Part 2 must be read from the source PDF.

## Where to find the full text
- Raw PDF (2009 2nd Ed, Part 2): `/mnt/ace/O&G-Standards/NACE/NACE MR 0175/NACE MR 0175 Pt 2 2nd Ed (2009) Cracking-resistant carbon and low-alloy steels,and the use of cast irons.pdf` (read-only, vendor-derivative; do not copy into git per #2482)
- Publisher catalog (current edition): https://store.ampp.org/ (registration required for purchase; the publisher-current edition is jointly published with ISO as ISO 15156-2:2020 and supersedes the 2009 second edition on disk)
- Internal callers: no live structured `Citation(...)` calls in `digitalmodel/src/` for Part 2 specifically. Calc-callers must verify against the publisher-current edition before relying on this page.

## Cross-references
- [[ampp-mr-0175-pt1]] — companion Part 1 (general principles)
- [[ampp-mr-0175-pt3]] — companion Part 3 (corrosion-resistant alloys)
- [[ampp-mr-0175-1995]] — superseded historical 1995 single-document edition
- [[ampp-tm-0177]] — sulfide stress cracking laboratory test method (acceptance-criteria companion)
- [Calc citation contract](../../../../../.claude/rules/calc-citation-contract.md)
