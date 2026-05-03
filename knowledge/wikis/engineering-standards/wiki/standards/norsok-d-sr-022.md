---
title: "NORSOK D-SR-022 BOP, Diverter and Drilling Riser System — bounded summary (designation withdrawn)"
tags: ["norsok", "standards", "drilling", "bop", "withdrawn", "metadata-only"]
added: 2026-05-03
last_updated: 2026-05-03
domain: engineering-standards
code_id: norsok-d-sr-022
publisher: "Standards Norway"
publisher_full: "Standards Norway (NORSOK)"
legacy_publisher: "NORSOK Steering Committee"
revision: "designation-withdrawn-1994"
publisher_current_revision: "designation-withdrawn"
lifecycle_status: "designation-withdrawn"
revision_source: "https://standard.no/en/sectors/petroleum/norsok-standards/"
verified_on: 2026-05-03
public_url: https://standard.no/en/sectors/petroleum/norsok-standards/
sources:
  - "/mnt/ace/O&G-Standards/Norsok/NORSOK_D-SR-022_(1994)_BOP,_Diverter_and_Drilling_Riser_System.pdf"
extraction_policy: metadata-only
raw_copy_allowed: false
norsok_series: D
norsok_doc_number: "D-SR-022"
ledger_id: NORSOK-D-SR-022-1994
iso_relationship:
  - { code: "norsok-d-001", relationship: "withdrawn-no-replacement", note: "NORSOK D-001 (drilling facilities) absorbed portions of D-SR-022 well-control-equipment scope after the SR-prefixed draft series was withdrawn." }
  - { code: "norsok-d-002", relationship: "withdrawn-no-replacement", note: "NORSOK D-002 (system requirements for drilling and well facilities) absorbed portions of the operational-system scope." }
  - { code: "norsok-d-010", relationship: "withdrawn-no-replacement", note: "NORSOK D-010 (well integrity in drilling and well operations) absorbed BOP-stack and well-control-barrier scope." }
  - { code: "API Spec 16A", relationship: "partial-overlap", note: "API Spec 16A (well-control equipment) is the international counterpart for BOP-stack design and pressure-control components; on-disk presence verification deferred to W5-B." }
  - { code: "API Spec 16D", relationship: "partial-overlap", note: "API Spec 16D (BOP control systems) covers the control-system scope of the legacy D-SR-022 envelope; on-disk presence verification deferred to W5-B." }
  - { code: "API RP 16Q", relationship: "partial-overlap", note: "API RP 16Q (drilling riser design and operation) covers the drilling-riser scope; an on-disk page already exists at api-rp-16q.md for cross-link." }
publisher_catalog_url: "https://standard.no/en/sectors/petroleum/norsok-standards/"
cross_links:
  - []
---

# NORSOK D-SR-022 BOP, Diverter and Drilling Riser System

## Scope
Bounded resolver target for the historical NORSOK draft-for-revision document covering the well-control-equipment envelope on the Norwegian continental shelf — blowout preventer stack, diverter, and drilling-riser system requirements. The SR-prefixed designation was a pre-2002 draft series; the designation has been withdrawn and the technical content migrated across multiple successor documents.

## Why this page exists
This page is the historical-traceability resolver target for legacy citations to D-SR-022. The designation is withdrawn; calc callers MUST NOT cite D-SR-022 for new work — instead consult the listed migration targets (NORSOK D-001 / D-002 / D-010 NORSOK-internal successors plus API Spec 16A / 16D and API RP 16Q international successors). Each cited successor's on-disk presence MUST be verified individually before citation. The page contains no clause text from the source.

## Where to find the full text
- Raw PDF: `/mnt/ace/O&G-Standards/Norsok/NORSOK_D-SR-022_(1994)_BOP,_Diverter_and_Drilling_Riser_System.pdf` (read-only, vendor-derivative; do not copy into git per #2482)
- Publisher catalog: https://standard.no/en/sectors/petroleum/norsok-standards/ (D-SR-022 designation withdrawn; migration targets D-001 / D-002 / D-010 are publisher-current)
- Internal callers: no live caller in `digitalmodel/src/` today
- Lifecycle: see frontmatter `revision`, `publisher_current_revision`, `lifecycle_status: designation-withdrawn`, and `iso_relationship` for the multi-target migration map

## Cross-references
- [[api-rp-16q]] — drilling riser systems international counterpart (already on-disk in this wiki)
- [[norsok-n-001]] — structural-design code for the Norwegian shelf envelope
- [Calc citation contract](../../../../../.claude/rules/calc-citation-contract.md)
