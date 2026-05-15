---
title: "DNV-OS-E301 — Position Mooring"
code_id: DNV-OS-E301
publisher: DNV
revision: 2021-07
tags: [standard, dnv, mooring, position-mooring, infragravity, nearshore, fsru]
sources:
  - mooring-failures-seed
  - skills-metadata
added: 2026-05-15
last_updated: 2026-05-15
---

# DNV-OS-E301 — Position Mooring

DNV-OS-E301 (Edition July 2021) covers position mooring systems for all floating offshore units. Defines wave frequency motion (first-order wave loads) and low-frequency motion (horizontal resonant oscillatory motion induced by oscillatory wind and second-order wave loads).

## Pilot use in this repository

Cited from `digitalmodel.orcaflex.mooring_design.MooringLineDesign.check_mbl_with_safety_factor()` (added 2026-05-15 per [#2685](https://github.com/vamseeachanta/workspace-hub/issues/2685)). Section 2.2.3 design factors:

- Intact, quasi-static: SF = 1.67
- Damaged, quasi-static: SF = 1.25

Resolved via `digitalmodel.citations.registry.get_mooring_safety_factor()`. This page is the citation target — `digitalmodel.citations.schema.validate_citation()` reads the frontmatter above to confirm `code_id`, `publisher`, `revision` match the in-code template before any cited value is returned. Editing those three frontmatter fields without coordinating the in-code template will trip fail-closed validation.

## Key Content

- **Infragravity waves**: Explicitly recognizes periods of 20s to several minutes on low-sloping seabeds as relevant to mooring design
- **Low-frequency motion**: Second-order wave loads drive resonant horizontal oscillation
- **Section 2.2.3 — Design factors**: Quasi-static partial safety factors for intact (1.67) and damaged (1.25) limit states; dynamic-analysis factors are smaller and not covered by this pilot
- **Section 7 — Fatigue assessment**: Mooring line fatigue using T-N curves and design fatigue factors (DFF)
- **Dynamic amplification**: Mooring line damping from drag can dominate total system damping for catenary systems

## OTG-18 — Nearshore Gap

DNV acknowledged existing rules did not fully address nearshore mooring. This led to DNV Offshore Technical Guidance OTG-18 for long-term nearshore positional mooring, specifically addressing FSRUs, FLNGs, and floating storage units in shallow water at jetties/quayside.

## API RP 2SK 4th Edition (2024) Alignment

API RP 2SK critical finding: mean wave drift forces and low-frequency vessel motions increase with decreasing wave period — the N-year return period wave condition may **not** yield the most onerous mooring response.

## Cross-References

- **Pilot caller**: `digitalmodel.orcaflex.mooring_design.MooringLineDesign.check_mbl_with_safety_factor`
- **Citation infrastructure**: `digitalmodel.citations.registry.get_mooring_safety_factor`
- **Test fixture twin**: `digitalmodel/tests/citations/fixtures/knowledge/wikis/engineering/wiki/standards/dnv-os-e301.md`
- **Governance**: [`docs/standards/calc-output-citation.md`](../../../../../docs/standards/calc-output-citation.md), [`.claude/rules/calc-citation-contract.md`](../../../../../.claude/rules/calc-citation-contract.md)
- **Related standard**: OCIMF MEG4 (mooring equipment guidelines)
- **Related standard**: DNV-RP-C205 (environmental conditions)

## Expansion backlog

This is the pilot stub. Full domain content (sections, equations, worked examples) is the deliverable of [#2676](https://github.com/vamseeachanta/workspace-hub/issues/2676) (Domain Knowledge Sweep). Until then, the three frontmatter fields are the load-bearing contract.
