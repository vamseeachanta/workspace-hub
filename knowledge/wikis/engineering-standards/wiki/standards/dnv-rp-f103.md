---
title: "DNV-RP-F103 Cathodic Protection of Submarine Pipelines by Galvanic Anodes — bounded summary"
tags: ["dnv", "standards", "cathodic-protection", "submarine-pipeline", "corrosion", "metadata-only"]
added: 2026-05-03
last_updated: 2026-05-03
domain: engineering-standards
code_id: dnv-rp-f103
publisher: DNV
revision: "2010"
revision_source: "/mnt/ace/O&G-Standards/DNV/DNV_RP_F103_(2010)_Cathodic_Protection_of_Submarine_Pipelines_by_Galvanic_Anodes.pdf"
verified_on: 2026-05-03
public_url: https://standards.dnv.com/explorer/
sources:
  - /mnt/ace/O&G-Standards/DNV/DNV_RP_F103_(2010)_Cathodic_Protection_of_Submarine_Pipelines_by_Galvanic_Anodes.pdf
extraction_policy: metadata-only
raw_copy_allowed: false
status: published
type: standard
---

# DNV-RP-F103 Cathodic Protection of Submarine Pipelines by Galvanic Anodes

## Scope
Bounded resolver target for the DNV recommended practice on cathodic protection of submarine pipelines using galvanic (sacrificial) anodes. Covers anode mass and current-output sizing, current density requirements as a function of burial state and internal fluid temperature, coating breakdown factors over design life, longitudinal pipe-metal resistance, anode spacing along the line, and pipeline attenuation analysis for current distribution.

This page is the publisher-and-application companion to [[dnv-rp-b401]]: F103 covers submarine pipelines specifically; B401 covers offshore structures, subsea components, and broader CP design. Calc modules selecting between the two routes do so by `calculation_type` (see source reference below).

## Why this page exists
Citation resolver target for the calc-citation contract at `.claude/rules/calc-citation-contract.md`. The digitalmodel cathodic-protection module routes to `DNV_RP_F103_2010` for submarine-pipeline CP, and per the contract every standards-derived constant or formula it emits must resolve to a wiki page with [vamseeachanta/workspace-hub#2471](https://github.com/vamseeachanta/workspace-hub/issues/2471) frontmatter (`code_id`, `publisher`, `revision`). This page satisfies that requirement so the resolver can read the page directly (v1 file-read mode per [vamseeachanta/workspace-hub#2481](https://github.com/vamseeachanta/workspace-hub/issues/2481) D3) without raising `CitationResolutionError`. No clause text, current-density tables, or formula reproductions from the source are included — see `.claude/rules/calc-citation-contract.md` clause 7 (vendor-derivative deny-list).

## In scope of the standard
- Galvanic-anode CP design for submarine carbon-steel pipelines
- Anode mass / current capacity sizing (Annex 1)
- Current density requirements for buried vs. seawater-exposed pipeline (Table 5-1)
- Coating breakdown factors over design life with linepipe and field-joint coating (FJC) constants (Annex 1)
- Wet-storage period and its effect on initial breakdown
- Longitudinal pipe-metal resistance and pipeline attenuation along the line
- Anode spacing optimization for distributed bracelet anodes
- Polarization resistance methodology

## Out of scope (use other standards)
- Offshore structure CP (jackets, hulls, subsea components) — see [[dnv-rp-b401]]
- Pipeline external corrosion control system specification — see DNV-ST-F101
- Corroded-pipeline integrity assessment — see DNV-RP-F101
- Impressed-current CP systems

## Where to find the full text
- Raw PDF (2010 edition, October 2010): `/mnt/ace/O&G-Standards/DNV/DNV_RP_F103_(2010)_Cathodic_Protection_of_Submarine_Pipelines_by_Galvanic_Anodes.pdf` (read-only, vendor-derivative; do not copy into git)
- Earlier revision on disk: `/mnt/ace/O&G-Standards/DNV/DNV_RP_F103_(2003)_Cathodic_protection_of_submarine_pipelines_by_galvanic_anodes.pdf`
- Publisher catalog and free full-text portal: https://standards.dnv.com/explorer/

## Key clauses referenced by digitalmodel

The `DNV_RP_F103_2010` method in `digitalmodel/src/digitalmodel/infrastructure/base_solvers/hydrodynamics/cathodic_protection.py` (router branch at line 21, method body at line 67) cites the following clauses. Source for each is the local reference PDF; no transcription appears below.

| Clause | What digitalmodel uses it for |
|---|---|
| Annex 1 Eq.2 (`f_cm = a + 0.5 * b * t_f`) | Mean coating breakdown factor over design life — applied per coating type |
| Annex 1 Eq.4 (`f_cf = a + b * t_f`) | Final coating breakdown factor at end-of-design-life |
| Annex 1 Tables A.1 / A.2 | Linepipe coating constants `a, b` (Table A.1) and field-joint coating constants (Table A.2) keyed by coating type |
| Eq.11 (`R_Me = L * rho_Me / (pi * d * (D - d))`) | Longitudinal pipe-metal resistance; per-unit-length form drives attenuation calc |
| Sec. 5.6.10 | Default CMn-steel resistivity `rho_Me = 0.2e-6 ohm-m` for longitudinal-resistance default |
| Table 5-1 | Current density requirements (A/m^2) for buried pipelines as a function of internal fluid temperature |
| Wet-storage period factor | Initial coating breakdown adjustment for pre-installation wet storage |
| Polarization resistance methodology | Used in the enhanced attenuation factor calculation |

Source-of-truth for these citations is the calc method itself; the wiki page is the resolver target, not the algorithm.

## Revision notes

- **Primary revision (this page):** `2010` (October 2010 edition). This matches the canonical method name `DNV_RP_F103_2010` in source code and the test module ABOUTME line `Comprehensive test suite for DNV RP-F103:2010 cathodic protection calculations`.
- **Secondary revision under test (2016):** The `TestDNVPhase1Enhancements` test class in `digitalmodel/tests/marine_ops/marine_engineering/test_cathodic_protection_dnv.py` describes its scope as "DNV RP-F103:2016 features" (wet-storage period support, longitudinal resistance, polarization-resistance-driven attenuation). The 2010 reference PDF is the on-disk source; no 2016 PDF is currently filed under `/mnt/ace/O&G-Standards/DNV/`.
- **Future reconciliation:** If a 2016 edition introduces material differences vs. 2010 for the constants the digitalmodel calc emits, the resolver target will either (a) bump this page's `revision` to `2016` after the 2016 PDF is filed and verified, or (b) split into a sibling `dnv-rp-f103-2016.md` with this page retained as the 2010 anchor. No bump now — the on-disk source is 2010, and the citation contract requires the `revision` field to match the verified source.

## Citation usage

A digitalmodel emit of a standards-derived constant (e.g., a Table 5-1 current density) instantiates a `Citation` per the schema at `digitalmodel/src/digitalmodel/citations/schema.py` with `code_id="dnv-rp-f103"`, `publisher="DNV"`, `revision="2010"`, and a clause anchor (e.g., `clause="Table 5-1"`). The v1 resolver reads this wiki page directly and validates the frontmatter trio matches the citation; mismatch raises `CitationResolutionError` with the `code_id` in the message ([vamseeachanta/workspace-hub#2481](https://github.com/vamseeachanta/workspace-hub/issues/2481) D2 fail-closed). The pilot pattern is in `digitalmodel/src/digitalmodel/orcaflex/mooring_design.py` (DNV-OS-E301 mooring safety factors).

## Cross-references
- [[dnv-rp-b401]] — sister CP standard for offshore structures (publisher-aligned, application-disjoint)
- [[dnv-os-e301]] — citation pilot for mooring safety factors per [vamseeachanta/workspace-hub#2481](https://github.com/vamseeachanta/workspace-hub/issues/2481)
- Source caller: `digitalmodel/src/digitalmodel/infrastructure/base_solvers/hydrodynamics/cathodic_protection.py` (router L21, `DNV_RP_F103_2010` L67, helpers below)
- Tests: `digitalmodel/tests/marine_ops/marine_engineering/test_cathodic_protection_dnv.py`
- [Calc citation contract](../../../../../.claude/rules/calc-citation-contract.md)
- Issue: [vamseeachanta/workspace-hub#2627](https://github.com/vamseeachanta/workspace-hub/issues/2627) (creation), [vamseeachanta/workspace-hub#2609](https://github.com/vamseeachanta/workspace-hub/issues/2609) R3 cluster (downstream consumer)

## Cross-References

- **Cross-wiki (engineering)**: [DNV-RP-F101: Corroded Pipelines](../../../engineering/wiki/standards/dnv-rp-f101.md) -- similar slugs (91%); shared tags: corrosion, dnv; shared keywords: by, cross-references, full, key, other; shared entities: DNV, DNV-RP-F101, DNV-ST-F101
- **Cross-wiki (engineering)**: [DNV-RP-F105 — Free Spanning Pipelines](../../../engineering/wiki/standards/dnv-rp-f105.md) -- similar slugs (91%); shared tags: dnv; shared entities: DNV, DNV-RP-F101, DNV-ST-F101
