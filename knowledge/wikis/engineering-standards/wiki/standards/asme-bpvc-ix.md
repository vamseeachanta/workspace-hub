---
title: "ASME BPVC Section IX — Welding, Brazing, and Fusing Qualifications (bounded summary)"
tags: ["asme", "bpvc", "standards", "welding", "metadata-only"]
added: 2026-05-02
last_updated: 2026-05-02
domain: engineering-standards
code_id: asme-bpvc-ix
publisher: ASME
revision: "2010"
revision_source: "/mnt/ace/O&G-Standards/ASME/asme.bpvc.ix.2010.pdf"
publisher_current_edition: "2023"
methodology_status: "unknown"
verified_on: 2026-05-02
public_url: https://www.asme.org/codes-standards/bpvc-standards
sources:
  - /mnt/ace/O&G-Standards/ASME/asme.bpvc.ix.2010.pdf
extraction_policy: metadata-only
raw_copy_allowed: false
---

# ASME BPVC Section IX — Welding, Brazing, and Fusing Qualifications (bounded summary)

## Scope

BPVC Section IX establishes qualification requirements for welding, brazing, and fusing procedures and for the personnel performing those operations. Coverage includes procedure qualification records, welding procedure specifications, performance qualification, essential and nonessential variables, and the parameters that govern requalification when variables change beyond defined limits.

## Why this page exists

Resolver target for digitalmodel `Citation` instances per `.claude/rules/calc-citation-contract.md`. Contains no clause text, no formulas, and no qualification-variable tables from the source. Downstream callers wire welding-qualification compliance markers through this page rather than parsing the source PDF. Section IX is the qualification basis for every weld covered by the B31.x and Section VIII calc paths in the in-scope codebase.

## Where to find the full text

- Raw PDF: `/mnt/ace/O&G-Standards/ASME/asme.bpvc.ix.2010.pdf` (read-only, vendor-derivative; do not copy into git per #2482)
- Publisher catalog: https://www.asme.org/codes-standards/bpvc-standards
- Internal callers: `digitalmodel/src/digitalmodel/` modules resolving welding-qualification compliance markers

## Cross-references

- [[asme-b31-3]] — process piping welds qualified per Section IX
- [[asme-bpvc-viii-1]] — pressure-vessel welds qualified per Section IX
- [[asme-bpvc-viii-2]] — pressure-vessel welds qualified per Section IX
- [Calc citation contract](../../../../../.claude/rules/calc-citation-contract.md)
