---
title: "Engineering AI Assistant"
subtitle: "General Oil & Gas Engineering Teams"
date: "February 2026"
author: "ACE Engineer"
accent_color: "#1a6e3c"
footer: "ACE Engineer | Confidential"
confidentiality: "Confidential"
---

# Engineering AI Assistant
## General Oil & Gas Engineering Teams

*Powered by large language model technology with deep O&G engineering, production analytics, and regulatory data context*

---

## Page 1 — What It Does

### Engineering Areas Covered

#### Drilling & Well Engineering
- **ROP modelling** — Bourgoyne-Young (8-parameter) and Warren power-law models; parameter fitting from offset well data
- **Drilling hydraulics** — ECD calculation, annular pressure loss, bit hydraulics; kick tolerance and kill mud weight
- **Casing & tubular design** — API 5CT burst/collapse/tension envelopes; casing pipe sizing to API RP 7G
- **Wellhead fatigue** — S-N based wellhead fatigue life; drilling riser integrity checks
- **Dysfunction detection** — stick-slip, whirl, and bit-bounce pattern recognition from surface data

#### Reservoir & Production Analytics
- **Decline curve forecasting** — Arps exponential/hyperbolic/harmonic with `fit_from_data()` from production history; multi-well batch CLI
- **BSEE GoM production data** — monthly well/lease/block production (API-12), well spud/completion records, infrastructure inventory
- **US shale analytics** — EIA Drilling Productivity Report by basin; `ShaleDeclineAnalyzer` for rate/EUR benchmarking
- **Global production databases** — SODIR (Norway NCS), UKCS, ANP (Brazil), Texas RRC — decline analysis and field benchmarking
- **Field economics** — NPV/IRR, lease cash flow, workover decision support; BSEE cost calibration against GoM actuals
- **Decommissioning economics** — cost model, late-life P&A, regulatory obligation quantification

#### Pipeline & Subsea Integrity
- **Wall thickness design** — DNV-OS-F101 pressure containment, collapse, propagation buckling; ASME B31.8 operating limits
- **Free span VIV** — DNV-RP-F105 full implementation: natural frequency (Se/Pcr, Ca), onset screening (Ks, ψ proximity), IL/CF amplitude, fatigue damage (D_IL + D_CF), allowable span length
- **Fitness for Service** — API 579-1 Level 1/2: UT thickness grid → CTP map → RSF → MAWP re-rating; B31G/RSTRENG MAOP de-rating; remaining life and re-inspection scheduling
- **Cathodic protection** — DNV-RP-B401/F103 anode design (4 standard routes); sacrificial anode sizing; inspection scheduling

#### Regulatory Data & Compliance
- **BSEE GoM data** — operator lease activity, rig fleet, well verification, environmental incident records; GoA Cook Inlet data
- **Safety incident analysis** — BSEE/USCG MISLE casualty records; ISM Code non-conformity extraction; root-cause taxonomy; statistical benchmarking against comparable incidents
- **Metocean data** — NOAA NDBC buoy data; return period estimation; 100-yr Hs/Tp/current for GoM, GoA, North Sea, Brazil
- **Standards quick-lookup** — API RP 7G, API 5CT, DNV-OS-F101, DNV-RP-F105, API 579-1, NACE MR0175, API RP 580 — version-aware code interpretation on demand

### Sample Conversations

| Question | Time: Manual | Time: AI |
|----------|-------------|---------|
| "Fit Arps decline to this well's production history and forecast 5-yr EUR" | 2–4 hr | 10 min |
| "Design casing string for 12,000 ft well, 8.5 ppg mud, 5,500 psi shut-in" | 2–4 hr | 20 min |
| "Assess FFS for 20% wall loss at a girth weld — RSTRENG vs B31G" | 2–4 hr | 15 min |
| "Calculate DNV-RP-F105 allowable span for 10\" OD, 0.562\" WT, 300m WD" | 1–2 hr | 5 min |
| "What is the GoM 100-yr Hs for Green Canyon and how does GoA compare?" | 1–2 hr | 2 min |
| "Analyse this BSEE incident report — identify root causes and CFR citations" | 3–6 hr | 20 min |

<div class="page-break"></div>

## Page 2 — Roadmap & Next Steps

### Phased Deployment

```
┌─────────────────────────────────────────────────────────────────┐
│  PHASE 1 — Desktop Q&A Demo          Week 1                     │
│  Live demo: drilling · production · pipeline · regulatory data  │
│  Cost: $0 additional · uses existing AI subscriptions           │
├─────────────────────────────────────────────────────────────────┤
│  PHASE 2 — Microsoft Teams Chatbot   Weeks 2–4                  │
│  Discipline-specific bots in your existing Teams channels       │
│  Separate context per team: wells · reservoir · integrity       │
│  Cost: ~$20–200/month · Azure Bot Service + Claude API          │
├─────────────────────────────────────────────────────────────────┤
│  PHASE 3 — Document Intelligence     Months 2–3                 │
│  Index your well files, inspection records, production reports  │
│  "What was the EUR on our Permian infill programme?" → instant  │
│  Cost: ~$500–2,000/month · RAG backend + document index         │
├─────────────────────────────────────────────────────────────────┤
│  PHASE 4 — Automated QC & Analytics  Months 4–6                 │
│  Cross-check AFEs vs actuals · flag code non-compliance         │
│  Decline curve monitoring · pipeline integrity trend alerts     │
│  Grows smarter with every well and inspection added             │
└─────────────────────────────────────────────────────────────────┘
```

### Gets Smarter Over Time

Unlike a generic AI tool, this assistant is discipline-specific from day one — and compounds in value with every engagement:

- **Phase 1 → 2**: Each demo question that stretches the system becomes the next knowledge update; the assistant improves after every session
- **Phase 2 → 3**: Once your well files, production reports, and inspection records are indexed, answers are grounded in *your* asset history — not just public benchmarks
- **Phase 3 → 4**: Repeated use encodes your team's preferred methods, field-specific decline behaviour, and integrity lessons learned across your portfolio
- The longer it runs, the more precise it becomes: *"What EUR did we forecast on our last Permian infill programme and how did actuals compare?"* becomes instantly answerable

### What the AI Does Not Do

- Does not replace the drilling engineer, reservoir engineer, or integrity assessor
- Does not execute simulation software (PIPESIM, Eclipse, Landmark, Petrel) directly
- All outputs carry a disclaimer: *preliminary/informational, requires qualified engineer verification*
- No proprietary well or production data stored without explicit setup
- Regulatory data (BSEE/EIA) is public-domain; company well data requires explicit connection

### Expected Returns

| Metric | Current | With AI | Saving |
|--------|---------|---------|--------|
| Code & standard lookups | 15–30 min | 1–2 min | **90%** |
| Decline curve fit + 5-yr EUR | 2–4 hr | 10–15 min | **88%** |
| Casing / wall thickness sizing | 2–4 hr | 20–30 min | **85%** |
| FFS Level 1/2 screening | 2–4 hr | 15–30 min | **85%** |
| BSEE/regulatory data lookup | 1–2 hr | 5 min | **92%** |
| Incident report root-cause analysis | 3–6 hr | 20–40 min | **88%** |

### Pilot Proposal

1. **Week 1** — Live demo (30 min) with 3–5 real engineering questions from your teams
2. **Week 2–3** — Pilot: wells + reservoir + integrity teams on active project work
3. **Week 4** — ROI review · decision on Teams chatbot (one bot per discipline team)
4. **Month 2+** — Full team rollout · well file and inspection record indexing

---

*Full O&G engineering stack — wells, production, pipeline, and compliance — in one assistant.*
*Real regulatory data, real standards, real calculations. Not a generic chatbot.*
