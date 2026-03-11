---
name: maritime-legal
version: "1.0.0"
category: engineering/maritime-legal
description: "AI-assisted maritime legal and casualty consulting — engineering-technical interface with admiralty proceedings"
capabilities:
  - casualty_investigation_support
  - expert_witness_report
  - admiralty_law_reference
  - incident_database_query
  - liability_framing
  - regulatory_framework
requires: []
see_also:
  - engineering/marine-offshore/marine-safety
  - data/energy/marine-safety-incidents
  - engineering/marine-offshore/risk-assessment
  - business/legal/compliance
trigger: manual
---

# Maritime Legal Engineering Skill

> Engineering-technical interface with maritime legal proceedings. Covers casualty investigation, expert witness support, admiralty law reference, and regulatory compliance.
>
> **Scope boundary:** This skill covers engineering-technical analysis only. It does NOT provide legal advice. All outputs require review by qualified maritime attorneys.

## Casualty Investigation Support

Analyze marine casualty reports (MAIB, NTSB, USCG) to:
- Identify ISM Code non-conformities (SMS failures, inadequate procedures)
- Map findings to root-cause taxonomy:
  - **Equipment failure** — material defect, maintenance lapse, design inadequacy
  - **Human factors** — situational awareness, fatigue, communication breakdown
  - **Weather/environment** — sea state beyond design basis, visibility, ice
  - **SMS failure** — procedure not followed, not written, or inadequate
- Cross-reference `worldenergydata.MAIBLoader` + `NTSBMarineLoader` for comparable incidents

## Expert Witness Report Structure

For admiralty proceedings produce reports in this order:

1. **Qualifications** — credentials, relevant experience, publications
2. **Scope and instructions** — what was asked; documents reviewed
3. **Technical background** — relevant standards and vessel type overview
4. **Factual findings** — timeline reconstruction; condition of equipment
5. **Standard of care analysis** — what a competent operator would have done
6. **Causation** — proximate cause chain; contributing factors
7. **Opinion** — engineering conclusion framed for legal use
8. **Limitations** — what could not be determined; data gaps

Framing standard: Daubert (US federal/USDC) or Civil Evidence Act 1995 (UK) as applicable.

## Admiralty Law Reference

| Instrument | Scope |
|-----------|-------|
| COLREGs 1972 | Collision regulations — Rules of the Road |
| Jones Act (46 USC 30104) | US seaman negligence claims |
| Limitation of Liability Act (46 USC 30505) | Shipowner liability cap |
| Hague-Visby Rules | Bill of lading cargo claims |
| MLC 2006 | Seafarer working and living conditions |
| P&I Club process | Third-party liability; club letters of undertaking |

## Incident Database Query

```python
# Example: find comparable propulsion casualties
from worldenergydata import MAIBLoader, NTSBMarineLoader
maib = MAIBLoader()
results = maib.query(vessel_type="bulk carrier", cause_category="propulsion", year_range=(2015, 2024))
# Returns: incident_id, vessel, date, cause_summary, outcome
```

## Liability Framing

Translate engineering findings into legal causation language:
- **Proximate cause** — "The immediate cause of the allision was the failure of the bow thruster, which directly caused loss of maneuverability in confined waters."
- **Standard of care** — "A prudent operator would have tested thruster response before entering the channel per port authority standing instructions."
- **Damages estimation** — hull repair quote + cargo loss + wreck removal + third-party property; reference comparable settlements where available

## Regulatory Framework

| Regulation | Applicability |
|-----------|--------------|
| 46 CFR Parts 90–196 | US vessel inspection requirements |
| 33 CFR Parts 160–173 | US navigation and waterways safety |
| SOLAS Chapter II-1/II-2 | Construction, subdivision, machinery, fire |
| MARPOL Annex I–VI | Pollution prevention |
| ISM Code (SOLAS IX) | Safety management systems |
| USCG MISLE | US marine casualty reporting (CG-2692) |
| BSEE 30 CFR 250 | OCS incident notifications (offshore) |
