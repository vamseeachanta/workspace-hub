---
title: "ASME BPVC Section II Part D — Properties (Materials) (bounded summary)"
tags: ["asme", "bpvc", "standards", "materials", "metadata-only"]
added: 2026-05-02
last_updated: 2026-05-02
domain: engineering-standards
code_id: asme-bpvc-ii-d
publisher: ASME
revision: "2010"
revision_source: "/mnt/ace/O&G-Standards/ASME/ASME II/ASME_II D (2010).pdf"
publisher_current_edition: "2023"
methodology_status: "unknown"
verified_on: 2026-05-02
public_url: https://www.asme.org/codes-standards/bpvc-standards
sources:
  - /mnt/ace/O&G-Standards/ASME/ASME II/ASME_II D (2010).pdf
extraction_policy: metadata-only
raw_copy_allowed: false
---

# ASME BPVC Section II Part D — Properties (Materials) (bounded summary)

## Scope

BPVC Section II Part D provides material property data, including maximum allowable stress values, design stress intensity values, yield strength, ultimate tensile strength, and physical properties (modulus of elasticity, thermal expansion, thermal conductivity, thermal diffusivity) used by other BPVC sections and B31 piping codes. Coverage spans ferrous and nonferrous materials in both customary and metric forms.

## Why this page exists

Resolver target for digitalmodel `Citation` instances per `.claude/rules/calc-citation-contract.md`. Contains no clause text, no tables, and no per-material allowable-stress numbers from the source. Downstream callers wire material property lookups through this page rather than parsing the source PDF. Section II Part D is the upstream allowable-stress feeder for every B31.x and Section VIII calculation in the in-scope codebase.

## Where to find the full text

- Raw PDF: `/mnt/ace/O&G-Standards/ASME/ASME II/ASME_II D (2010).pdf` (read-only, vendor-derivative; do not copy into git per #2482)
- Publisher catalog: https://www.asme.org/codes-standards/bpvc-standards
- Internal callers: any `digitalmodel/src/digitalmodel/` module that resolves an ASME allowable stress through B31.x or Section VIII

## Cross-references

- [[asme-b31-3]] — process piping consumer
- [[asme-b31-4]] — liquid-pipeline consumer
- [[asme-b31-8]] — gas-pipeline consumer
- [[asme-bpvc-viii-1]] — pressure-vessel consumer
- [[asme-bpvc-viii-2]] — pressure-vessel consumer (alternative rules)
- [Calc citation contract](../../../../../.claude/rules/calc-citation-contract.md)
