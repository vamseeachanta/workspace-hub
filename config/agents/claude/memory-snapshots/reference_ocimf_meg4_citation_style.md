---
name: reference-ocimf-meg4-citation-style
description: "Canonical professional citation format for OCIMF MEG4 standard, related naval-arch standards (DNV-OS-E301, API RP 2SK, ISO 19901-7), and internal project documents in consulting reports"
metadata: 
  node_type: memory
  type: reference
  originSessionId: ea3c0fbd-33d7-41f3-a92e-42b0026c13c7
---

# Citation conventions for marine engineering consulting reports

Researched 2026-05-22 (workspace-hub #2760 Pass G; full source URLs in agent transcript at `/tmp/claude-1000/.../tasks/a5b68f4dfe7704b96.output`).

## Inline form
- Standards: `OCIMF MEG4 (2018), Annex A, Fig. A9` (designator + year + locator)
- Numeric: `[1]` mapping to References list
- Bibliographic citation goes in References, not inline.

## Standards full-citation format
**Pattern:** Issuer + Designation + *Italic Title* + Edition + Year + Publisher + City + ISBN.

- OCIMF (2018). *Mooring Equipment Guidelines*, 4th ed. (MEG4). Witherby Publishing Group, Livingston, UK. ISBN 978-1-85609-771-0.
- DNV (2021). *DNV-OS-E301 Position Mooring*, Offshore Standard, Edition July 2021. DNV AS, Høvik, Norway.
- API (2024). *API RP 2SK Design and Analysis of Stationkeeping Systems for Floating Structures*, 4th ed., February 2024. American Petroleum Institute, Washington, DC.
- ISO (2013). *ISO 19901-7:2013 Petroleum and natural gas industries — Specific requirements for offshore structures — Part 7: Stationkeeping systems...*. ISO, Geneva.
- ABS (2024). *Rules for Building and Classing Single Point Moorings*. American Bureau of Shipping, Spring, TX.
- IMO (1974, as amended). *International Convention for the Safety of Life at Sea (SOLAS)*. London. (For circulars: `IMO MSC.1/Circ.1175 (2005)`.)

## Project document citation
Cite as controlled document with: **Project No. / Document No. / Title / Revision / Date / Originator / availability marker**.

Example: ACMA Engineering (2026). *B1528 SIROCCO — Vessel Geometry and Rudder Particulars Workbook*. Document No. B1528-NA-CAL-001, Rev. B, dated 2026-04-15. (Proprietary; available on request.)

## Coefficient source provenance
Name figure + interpolation axis + regime: *"Longitudinal current force coefficient Cxc digitized from OCIMF MEG4 (2018), Annex A, Fig. A9 (loaded VLCC, conventional bow), interpolated at water-depth-to-draft ratio > 4.4, per MEG4 §A.1 conventions."*

## References section structure
- **Numbered**, ordered by **first citation in text** (engineering convention, NOT alphabetic)
- Hanging indent, single-spaced
- Separate `Project Documents` subsection with `[P1]`, `[P2]` markers
- Code/software cited inline as `Tool (Vendor, version)`; full URL in References

## Vague phrase replacements
| Vague | Professional |
|---|---|
| "licensed off-repo workbook" | "OCIMF MEG4 (2018), Annex A, Figs. A9–A11" (cite the standard, not the workbook) |
| "B1528 SIROCCO source pack" | "Project Document B1528-NA-CAL-001 Rev. B (proprietary)" |
| "generic-reference OCIMF tanker-current basis" | "current load coefficients derived per OCIMF MEG4 (2018), Annex A (loaded VLCC, conventional bow, h/T > 4.4)" |

## Style rules
- Always cite **edition + year** for standards (regulators care which edition was in force at calc time — see [[calc-citation-contract]])
- Italicize titles of standards and books; quote titles of papers; plain text for designators (DNV-OS-E301, API RP 2SK)
- Use designator + year inline; reserve numeric `[n]` for References list
- Internal documents in separate "Project Documents" block makes the public-vs-proprietary boundary explicit

Apply this when writing client-facing naval-arch / mooring / offshore engineering reports. Related: [[calc-citation-contract]] in `.claude/rules/`.
