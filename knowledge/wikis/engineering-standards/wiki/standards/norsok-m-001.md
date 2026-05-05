---
title: "NORSOK M-001 Materials Selection — bounded summary"
tags: ["norsok", "standards", "materials", "metadata-only"]
added: 2026-05-03
last_updated: 2026-05-03
domain: engineering-standards
code_id: norsok-m-001
publisher: "Standards Norway"
publisher_full: "Standards Norway (NORSOK)"
revision: "4th-Ed-2004"
publisher_current_revision: "4th-Ed-2004"
lifecycle_status: "in-force-shelf-specific"
revision_source: "https://standard.no/en/sectors/petroleum/norsok-standards/"
verified_on: 2026-05-03
public_url: https://standard.no/en/sectors/petroleum/norsok-standards/
sources:
  - "/mnt/ace/O&G-Standards/Norsok/Norsok_Standard_M-001_4th_Ed_(2004)_Materials_selection.pdf"
extraction_policy: metadata-only
raw_copy_allowed: false
norsok_series: M
norsok_doc_number: "M-001"
ledger_id: NORSOK-M-001-2004
iso_relationship:
  - { code: "ISO 21457", relationship: "parallel-mirror", note: "ISO 21457 (materials selection and corrosion control for oil and gas production systems) is the international mirror; both remain in force with M-001 retaining Norwegian-shelf-specific service-class mappings." }
iso_equivalent: "ISO 21457"
publisher_catalog_url: "https://standard.no/en/sectors/petroleum/norsok-standards/"
cross_links:
  - []
---

# NORSOK M-001 Materials Selection

## Scope
Bounded resolver target for the NORSOK materials-selection code, covering qualification and selection of materials for petroleum-production process, utility, and structural systems on the Norwegian continental shelf — including service-class definitions, corrosion-allowance philosophy, and acceptance criteria for carbon, low-alloy, stainless, nickel-alloy, and non-metallic materials.

## Why this page exists
This page is the citation resolver target for materials-selection-aware calc modules under the calc-citation contract. M-001 is the umbrella materials code that the more-cited but on-disk-absent M-506 (CO2-corrosion modelling) references for service-class definitions; downstream callers needing M-506 must wait for the W5-B publisher-portal pointer page. The page contains no clause text or material-class table values from the source.

## Where to find the full text
- Raw PDF: `/mnt/ace/O&G-Standards/Norsok/Norsok_Standard_M-001_4th_Ed_(2004)_Materials_selection.pdf` (read-only, vendor-derivative; do not copy into git per #2482)
- Publisher catalog: https://standard.no/en/sectors/petroleum/norsok-standards/
- Internal callers: no live caller in `digitalmodel/src/` cites M-001 directly today; M-506 (5 grep hits) references M-001 service classes and is deferred to W5-B publisher-portal pointer
- Lifecycle: see frontmatter `revision`, `publisher_current_revision`, `lifecycle_status`, and `iso_relationship` for ISO-21457 parallel-mirror context

## Cross-references
- [[norsok-m-501]] — surface preparation and protective coating companion in the materials series
- [[norsok-m-710]] — non-metallic sealing materials qualification companion
- [Calc citation contract](../../../../../.claude/rules/calc-citation-contract.md)

## Cross-References

- **Cross-wiki (asset-management)**: [NORSOK Z-008 — Risk-based maintenance and consequence classification](../../../asset-management/wiki/standards/norsok-z-008.md) -- similar slugs (83%); shared tags: norsok; shared keywords: cross-references, norsok, scope, where; shared entities: NORSOK
