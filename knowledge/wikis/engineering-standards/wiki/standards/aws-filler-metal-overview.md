---
title: "AWS A5-Series Filler Metal Classification — bounded series overview"
tags: ["aws", "standards", "welding", "filler-metal", "series-overview", "metadata-only"]
added: 2026-05-03
last_updated: 2026-05-03
domain: engineering-standards
code_id: aws-filler-metal-overview
publisher: AWS
publisher_full: "American Welding Society"
revision: "public-metadata-required-before-citation-use"
revision_source: "series overview — no single revision pinned; per-document revisions captured on the individual A5.x pages"
publisher_current_edition: "varies-per-document"
verified_on: 2026-05-03
public_url: https://pubs.aws.org/
sources:
  - "/mnt/ace/O&G-Standards/AWS/AWS-A5-5.pdf"
  - "/mnt/ace/O&G-Standards/AWS/AWS A5.10/AWS A5.10 (1999)Spec for Bare Alum & Alum Alloy Welding Electrodes & Rods.pdf"
extraction_policy: metadata-only
raw_copy_allowed: false
aws_doc_number: "A5-series"
ledger_id: AWS-FILLER-METAL-OVERVIEW
cross_references:
  - { code_id: "aws-a5-5", relation: "references", note: "A5.5 — low-alloy steel SMAW electrodes (member of A5 series)" }
  - { code_id: "aws-a5-10", relation: "references", note: "A5.10 — bare aluminum and aluminum-alloy welding electrodes and rods (member of A5 series)" }
  - { code_id: "asme-bpvc-ix", relation: "references", note: "BPVC Section IX welding procedure qualification cites the A5-series filler-metal classifications" }
---

# AWS A5-Series Filler Metal Classification — Series Overview

## Scope
Series-level overview of the AWS A5 family of filler-metal specifications. The A5 series spans dozens of individual specifications, each covering a base-metal class and process combination — for example A5.1 (carbon steel SMAW), A5.5 (low-alloy steel SMAW), A5.10 (aluminum and aluminum alloys), A5.18 (carbon steel GMAW), A5.20 (carbon steel FCAW), A5.28 (low-alloy steel GMAW), A5.29 (low-alloy steel FCAW), A5.36 (fluxes). Within the on-disk corpus, only A5.5 and A5.10 are present.

## Why this page exists
Conceptual resolver target for the A5-series taxonomy. Calc-callers and welding-procedure resolvers may cite the series at a level above any individual specification when the relevant document is one of several family members. The series-level page is intentionally a stub: per-document revision values are pinned on the individual `aws-a5-5.md` and `aws-a5-10.md` pages, and any future additions follow the same pattern. This page is excluded from the citation-resolvability test because no single revision applies to a series-of-documents pointer.

## Where to find the full text
- Per-document pointers: see individual `aws-a5-*.md` pages under `/mnt/ace/O&G-Standards/AWS/` for raw paths
- Publisher catalog: https://pubs.aws.org/ (registration required for purchase/download)
- Internal callers: no live caller; future-needed as a series-level resolver target

## Edition gap discipline
No single revision applies to the series. Each member document carries its own on-disk-vs-publisher-current gap on its individual page. Calc-callers MUST resolve to the specific A5.x document and verify against the publisher-current edition for that document before any compliance use.

## Cross-references
- [[aws-a5-5]] — low-alloy steel SMAW electrodes
- [[aws-a5-10]] — bare aluminum and aluminum-alloy welding electrodes and rods
- [[asme-bpvc-ix]] — references the A5 series for filler-metal classification in procedure qualification
- [Calc citation contract](../../../../../.claude/rules/calc-citation-contract.md)
