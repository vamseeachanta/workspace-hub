---
title: "Issue #2567 Steering Gear / Rudder Stock Source Map"
tags: [steering-gear, rudder-stock, standards, source-intelligence]
sources:
  - /mnt/local-analysis/workspace-hub/data/document-index/online-resource-registry.yaml
  - /mnt/local-analysis/workspace-hub/data/document-index/standards-transfer-ledger.yaml
  - /mnt/local-analysis/workspace-hub/docs/reports/2264-wave4-inventory.yaml
  - /mnt/ace/O&G-Standards/SNAME/textbooks/SOLAS-2020-Consolidated-Edition.pdf
  - /mnt/ace/acma-codes/DNV Rules/2010 DNV/2010 Ship Rules/ts414, steering gear.pdf
added: 2026-05-01
last_updated: 2026-05-01
---

# Issue #2567 Steering Gear / Rudder Stock Source Map

This page is the source-intelligence landing page for issue #2567. It inventories what is actually available for steering-gear and rudder-stock design checks, what is only a portal or metadata anchor, and what is sufficiently extracted to support later decomposition work.

Hard boundary: this page does **not** approve any standards-derived implementation. It only records source status and traceability.

Issue: <https://github.com/vamseeachanta/workspace-hub/issues/2567>

## Candidate source inventory

| Source | Publisher / type | Path or URL | Steering / rudder relevance | Extraction status | Readiness |
|---|---|---|---|---|---|
| SOLAS 2020 Consolidated Edition | IMO regulatory convention | `/mnt/ace/O&G-Standards/SNAME/textbooks/SOLAS-2020-Consolidated-Edition.pdf` and `data/document-index/online-resource-registry.yaml` lines 1828-1838 | Functional and safety requirements for main/auxiliary steering gear, control systems, alarms, alternate power, and rudder-stock thresholds in way of tiller | Clause text locally extractable; Regulation II-1/29 text verified in local PDF extract | **Partial / implementation support only for regulatory framing** — useful for requirement framing, not class scantling formulas |
| DNV Rules and Standards Explorer | DNV portal | `https://standards.dnv.com/explorer/` and `online-resource-registry.yaml` lines 352-362 | Live rules portal for steering gear / rudder stock clauses by edition | Portal only in repo registry | **Source-gap** until exact edition + clause text are extracted |
| DNV Ship Rules TS414 — Steering Gear | DNV class rule chapter | `/mnt/ace/acma-codes/DNV Rules/2010 DNV/2010 Ship Rules/ts414, steering gear.pdf` plus metadata anchor in `docs/reports/2264-wave4-inventory.yaml` | Strongest local class-rule candidate for steering gear actuator loads, connection-to-stock checks, stopper loads, bearing loads, and non-duplicated actuator requirements | Local PDF present and text extracted with clause headings/definitions visible | **Partial / best local class anchor** — suitable for decomposition and candidate follow-ups, but still needs edition/authority decisions before any implementation claim |
| DNV TS414 metadata inventory anchor | Repo inventory metadata | `docs/reports/2264-wave4-inventory.yaml` | Confirms local file presence and archive location lineage | Metadata only | **Non-authoritative support** |
| ABS Marine Vessel Rules — Part 4 (2024) | ABS class rules portal entry | `https://ww2.eagle.org/en/rules-and-resources/rules-and-guides-v2.html` and `online-resource-registry.yaml` lines 1544-1554 | Likely machinery / steering-gear rule home for modern ABS edition | Portal entry only; direct PDF not locally registered | **Source-gap** until exact Part/Chapter clauses are extracted |
| ABS — Introduction to Rules and Guides | ABS overview | `online-resource-registry.yaml` lines 1555-1565; local backup `/mnt/ace/docs/_standards/SNAME/textbooks/ABS-Intro-to-Rules-and-Guides.pdf` | Explains ABS rule-system structure, not design formulas | Overview only | **Out-of-scope for formulas** |
| ABS Guide for Vessel Maneuverability (2017) | ABS guidance document | `/mnt/ace/acma-codes/ABS Rules/Vessel Maneuverability/Vessel_Maneuverability_Guide_e-Feb17.pdf` and existing source page `wiki/sources/abs-vessel-maneuverability-guide-2017.md` | Valuable for maneuvering simulation context, not steering gear machinery or rudder-stock scantling | Already summarized in wiki | **Non-authoritative for #2567 formula scope** |
| IACS Unified Requirements and Blue Book | IACS portal | `https://iacs.org.uk/resolutions/unified-requirements` and `online-resource-registry.yaml` lines 2547-2559 | Potential bridge for rudder-stock interpretation and member-society minimums referenced by SOLAS/DNV | Portal only; no verified steering-gear UR/UI file captured locally in this audit | **Source-gap** |
| standards-transfer-ledger.yaml | Internal promotion ledger | `data/document-index/standards-transfer-ledger.yaml` | Checks whether steering gear / rudder stock clauses were already promoted | No dedicated steering gear or rudder stock entry found in audit | **Gap signal only** |

## Verified local extraction anchors

### SOLAS
- Local PDF: `/mnt/ace/O&G-Standards/SNAME/textbooks/SOLAS-2020-Consolidated-Edition.pdf`
- Verified extract anchor: Part C / Regulation 29, lines ~3282 onward in local text extraction.
- Immediate value:
  - defines main steering gear, auxiliary steering gear, power actuating system
  - sets functional timing / availability / redundancy expectations
  - sets rudder-stock diameter thresholds that trigger power-operation / alternate power requirements
- Limitation: not a class-rule scantling formula source.

### DNV TS414
- Local PDF: `/mnt/ace/acma-codes/DNV Rules/2010 DNV/2010 Ship Rules/ts414, steering gear.pdf`
- Table-of-contents anchors visible in extracted text:
  - `Sec. 1 Steering Gear`
  - `Additional Requirements for Non-Duplicated Rudder Actuators`
  - `Connection between steering gear and rudder stock`
  - `Rudder stock diameter`
  - `Design torque`
  - `Safety factor for rudder stock`
- Immediate value:
  - strongest local evidence that the repo has a usable class-rule chapter for later decomposition
  - sufficient to draft follow-up slices around actuator load envelope, stock connection, bearings, and stopper checks
- Limitation: this audit does not establish that TS414 alone is the final authoritative edition for implementation.

## Classification by source authority

| Bucket | What belongs here now | Notes |
|---|---|---|
| Functional / regulatory requirement | SOLAS II-1 Reg. 29 | Good for "what must exist / be demonstrated" framing |
| Class-rule load / scantling formulas | DNV TS414 local PDF candidate | Needs edition governance and clause-ready promotion before implementation |
| Machinery / actuator sizing | DNV TS414 candidate; ABS Part 4 portal candidate | Local ABS clause text still missing |
| Bearing reaction / connection details | DNV TS414 candidate | Extracted headings confirm likely coverage |
| Non-authoritative references | ABS maneuverability guide, metadata inventory anchors, portal-only registry rows | Useful context but not formula authority |

## Explicit gaps

1. **No promoted steering-gear/rudder-stock ledger entry** exists in `standards-transfer-ledger.yaml`.
2. **Modern ABS design clauses are not locally extracted**; only a portal anchor is registered.
3. **IACS steering-related UR/UI documents were not captured locally** in this audit.
4. **No source in this package should be treated as approval to implement formulas now**.

## Resulting decomposition stance

- Steering-gear/rudder-stock work should be split by source family, not by desired code feature alone.
- SOLAS-derived requirements should stay separate from class-rule formula checks.
- DNV TS414 is the best local candidate for later detailed decomposition, but the crosswalk must keep its status as **candidate class authority pending explicit clause promotion / edition decision**.

## Related pages

- [[steering-gear-design-checks]]
- [[rudder-stock-design-checks]]
- [Standards crosswalk](../standards/steering-gear-rudder-stock-rule-crosswalk.md)
