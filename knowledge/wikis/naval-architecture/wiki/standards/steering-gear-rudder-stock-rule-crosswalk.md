---
title: "Steering Gear / Rudder Stock Rule Crosswalk"
tags: [standards, steering-gear, rudder-stock, crosswalk]
sources:
  - /mnt/ace/O&G-Standards/SNAME/textbooks/SOLAS-2020-Consolidated-Edition.pdf
  - /mnt/ace/acma-codes/DNV Rules/2010 DNV/2010 Ship Rules/ts414, steering gear.pdf
  - /mnt/local-analysis/workspace-hub/data/document-index/online-resource-registry.yaml
  - /mnt/local-analysis/workspace-hub/docs/reports/2264-wave4-inventory.yaml
code_id: steering-gear-rudder-stock-crosswalk
publisher: mixed
revision: 2026-05-01 working draft
jurisdiction: international / class-rule candidate set
added: 2026-05-01
last_updated: 2026-05-01
---

# Steering Gear / Rudder Stock Rule Crosswalk

This is a decomposition crosswalk, not a compliance matrix. Rows are intentionally conservative about readiness.

## Readiness legend

- **implementation-ready** — exact clause text and edition are locally available and judged sufficient for a tightly bounded follow-up
- **source-gap** — portal-only, metadata-only, or otherwise missing implementation-grade clause text
- **out-of-scope** — useful context but not the right authority for standards-backed checks
- **partial** — clause text exists locally, but authority/edition/integration work is still needed before implementation should begin

## Crosswalk

| Topic bucket | Publisher | Standard / source | Edition / year | Exact locator | Path / URL | Extraction status | Readiness | Rationale |
|---|---|---|---|---|---|---|---|---|
| Functional / regulatory requirements | IMO | SOLAS Consolidated Edition | 2020 | Chapter II-1, Part C, Regulation 29; definitions in Reg. 3 items 1-4 and 13 | `/mnt/ace/O&G-Standards/SNAME/textbooks/SOLAS-2020-Consolidated-Edition.pdf` | Local PDF text extracted and locator verified | **partial** | Strong for steering system definitions, timing, redundancy, control, alarms, and alternate power thresholds, but not the class-rule machinery/scantling formulas |
| Structural / mechanical baseline delegation | IMO | SOLAS Consolidated Edition | 2020 | Chapter II-1, Part A-1, Regulation 3-1 | `/mnt/ace/O&G-Standards/SNAME/textbooks/SOLAS-2020-Consolidated-Edition.pdf` | Local text available | **partial** | Important because SOLAS explicitly delegates structural/mechanical detail to recognized class rules or equivalent national standards |
| Steering gear load / actuator design | DNV | Ship Rules TS414 — Steering Gear | local file under 2010 DNV archive; body header shows January 2005 rules with July 2010 amendments | Pt.4 Ch.14 Sec.1, item 1119 "Design torque" | `/mnt/ace/acma-codes/DNV Rules/2010 DNV/2010 Ship Rules/ts414, steering gear.pdf` | Local PDF text extracted; formula heading and definitions verified | **partial** | Best local class-rule candidate; suitable for follow-up clause extraction, but edition governance must be explicit before implementation |
| Steering gear to rudder-stock connection | DNV | Ship Rules TS414 — Steering Gear | same as above | Pt.4 Ch.14 Sec.1, items 1201-1215 "Connection between steering gear and rudder stock" | `/mnt/ace/acma-codes/DNV Rules/2010 DNV/2010 Ship Rules/ts414, steering gear.pdf` | Local PDF text extracted; torque-capacity rules and keyed/frictional connection clauses visible | **partial** | Strong local candidate for a dedicated connection-check issue |
| Rudder-stock diameter / safety-factor candidate | DNV | Ship Rules TS414 — Steering Gear | same as above | TOC and extracted headings show "Rudder stock diameter" and "Safety factor for rudder stock" in Pt.4 Ch.14 Sec.1 | `/mnt/ace/acma-codes/DNV Rules/2010 DNV/2010 Ship Rules/ts414, steering gear.pdf` | Headings verified in local extraction; full row-level formula extraction still pending | **partial** | Enough to justify a child issue for exact clause extraction, not enough to claim implementation-ready scantling checks today |
| Stopper and bearing reaction checks | DNV | Ship Rules TS414 — Steering Gear | same as above | Pt.4 Ch.14 Sec.1, B1300 "Stopper arrangement" and B1400 "Bearings" | `/mnt/ace/acma-codes/DNV Rules/2010 DNV/2010 Ship Rules/ts414, steering gear.pdf` | Local text extracted; clause headings and load narrative visible | **partial** | Explicitly separate from torque-only work; likely needs its own follow-up slice |
| Non-duplicated rudder actuator requirements | DNV | Ship Rules TS414 — Steering Gear | same as above | Appendix A "Additional Requirements for Non-Duplicated Rudder Actuators" | `/mnt/ace/acma-codes/DNV Rules/2010 DNV/2010 Ship Rules/ts414, steering gear.pdf` | Appendix heading verified in local extract | **partial** | Important for failure-criterion decomposition; exact clause extraction still pending |
| Modern ABS machinery rules | ABS | Marine Vessel Rules — Part 4 | 2024 portal entry | Exact chapter/section not yet captured | `https://ww2.eagle.org/en/rules-and-resources/rules-and-guides-v2.html` | Portal only | **source-gap** | Registry confirms likely source family, but no local clause text or locator was verified in this issue |
| ABS rule-system orientation | ABS | Introduction to Rules and Guides | Jul 2025 backup in registry entry | overview only | `/mnt/ace/docs/_standards/SNAME/textbooks/ABS-Intro-to-Rules-and-Guides.pdf` | Local backup exists but this is an overview document | **out-of-scope** | Useful to understand ABS taxonomy, not a formula authority |
| ABS maneuvering context | ABS | Guide for Vessel Maneuverability | Feb 2017 | Appendix 3 etc. | `/mnt/ace/acma-codes/ABS Rules/Vessel Maneuverability/Vessel_Maneuverability_Guide_e-Feb17.pdf` | Already summarized in naval-architecture wiki | **out-of-scope** | Good maneuvering-model context, not steering-gear machinery/rudder-stock scantling authority |
| Unified interpretations / minimum class standards | IACS | Unified Requirements and Blue Book | portal current | Exact UR/UI locator not yet captured | `https://iacs.org.uk/resolutions/unified-requirements` | Portal only | **source-gap** | Crosswalk acknowledges likely relevance but no steering-specific local clause file was verified |
| Inventory metadata anchor | Internal inventory | Wave-4 inventory entry for DNV TS414 | n/a | DNV rules inventory row for `ts414, steering gear.pdf` | `docs/reports/2264-wave4-inventory.yaml` | Metadata only | **out-of-scope** | Confirms file existence only; not clause authority |
| Existing preliminary code / docs | Workspace repo | #2565 torque workflow and wiki pages | 2026-04-30 | plan + source pages | repo-local | Fully available | **out-of-scope** | Important boundary evidence showing current work is preliminary and non-compliance-grade |

## Key crosswalk conclusions

1. **SOLAS gives the regulatory envelope; it does not replace class-rule mechanical/scantling clauses.**
2. **DNV TS414 is the strongest local class-rule candidate discovered in this issue.**
3. **ABS and IACS still need exact clause capture before they can anchor implementation.**
4. **The current repo should not implement standards-backed formulas until a later issue promotes exact clause text and edition decisions.**

## Safe follow-up types from this crosswalk

- clause extraction / promotion
- child issue drafting
- standards-page normalization
- explicit comparison between SOLAS thresholds and class-rule mechanical checks

## Unsafe next steps from this crosswalk

- implementing formulas directly from portal memory
- relabeling #2565 outputs as compliance checks
- claiming ABS/IACS parity without local clause capture
