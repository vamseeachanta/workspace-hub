---
title: "NORSOK N-004 Design of Steel Structures — bounded summary"
tags: ["norsok", "standards", "structural", "fatigue", "metadata-only"]
added: 2026-05-03
last_updated: 2026-05-03
domain: engineering-standards
code_id: norsok-n-004
publisher: "Standards Norway"
publisher_full: "Standards Norway (NORSOK)"
revision: "2nd-Ed-2004"
publisher_current_revision: "2nd-Ed-2004"
lifecycle_status: "in-force-shelf-specific"
revision_source: "https://standard.no/en/sectors/petroleum/norsok-standards/"
verified_on: 2026-05-03
public_url: https://standard.no/en/sectors/petroleum/norsok-standards/
sources:
  - "/mnt/ace/O&G-Standards/Norsok/Norsok_Standard_N-004_2nd_Ed_(2004)_Design_of_Steel_Structures.pdf"
  - "/mnt/ace/O&G-Standards/Norsok/Norsok_Standard_N-004_1st_Ed_(1998)_Design_of_Steel_Structures.pdf"
extraction_policy: metadata-only
raw_copy_allowed: false
norsok_series: N
norsok_doc_number: "N-004"
ledger_id: NORSOK-N-004-2004
supersedes: ["norsok-n-004-1998-internal"]
iso_relationship:
  - { code: "ISO 19902", relationship: "parallel-mirror", note: "ISO 19902 (fixed steel offshore structures) is the international parallel-mirror counterpart; both remain in force on the Norwegian continental shelf with shelf-specific N-004 provisions retained." }
  - { code: "ISO 19904-1", relationship: "partial-overlap", note: "ISO 19904-1 (floating offshore structures) overlaps for floater-applied detail design; relationship is partial because N-004 retains fixed-platform-specific clauses." }
iso_equivalent: "ISO 19902"
publisher_catalog_url: "https://standard.no/en/sectors/petroleum/norsok-standards/"
cross_links:
  - []
---

# NORSOK N-004 Design of Steel Structures

## Scope
Bounded resolver target for the NORSOK detailed-design code for offshore steel structures, covering tubular member and joint capacity, fatigue assessment via S-N curves and stress-concentration factors, plate girder and stiffened-panel design, and accidental-action checks for jacket and topside components on the Norwegian continental shelf.

## Why this page exists
This page is the citation resolver target for downstream `digitalmodel/fatigue/` calc modules. The code is cited 7 times in `digitalmodel/src/digitalmodel/fatigue/sn_library.py`, `fatigue_reporting.py`, and `environmental_correction.py` — making this resolver target the highest-priority NORSOK page for live-caller resolution. The page contains no S-N curve numerics, stress-concentration formulas, or clause text from the source.

## Where to find the full text
- Raw PDFs: `/mnt/ace/O&G-Standards/Norsok/Norsok_Standard_N-004_2nd_Ed_(2004)_Design_of_Steel_Structures.pdf` (current on-disk umbrella) and `Norsok_Standard_N-004_1st_Ed_(1998)_Design_of_Steel_Structures.pdf` (superseded; included for traceability) — read-only, vendor-derivative; do not copy into git per #2482
- Publisher catalog: https://standard.no/en/sectors/petroleum/norsok-standards/
- Internal callers: `digitalmodel/src/digitalmodel/fatigue/sn_library.py`, `fatigue_reporting.py`, `environmental_correction.py` (7 grep hits; Annex C S-N methodology)
- Lifecycle: see frontmatter `revision`, `publisher_current_revision`, `lifecycle_status`, and `iso_relationship` for the ISO-19902 parallel-mirror and ISO-19904-1 partial-overlap context

## Cross-references
- [[norsok-n-001]] — overarching structural-design framework code
- [[norsok-m-001]] — materials selection feeds steel-class inputs
- [[dnv-rp-c203]] — companion fatigue methodology (parallel S-N curve framework)
- [Calc citation contract](../../../../../.claude/rules/calc-citation-contract.md)
