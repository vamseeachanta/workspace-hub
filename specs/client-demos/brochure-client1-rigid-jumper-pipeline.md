# Engineering AI Assistant
## Rigid Jumper & Pipeline Teams

*Powered by large language model technology with deep offshore engineering context*

---

## Page 1 — What It Does

### Engineering Areas Covered

#### Rigid Jumper & Spool Design
- Wall thickness sizing — ASME B31.8 / API 2RD pressure containment
- Combined stress checks — Von Mises (pressure + bending + thermal)
- Fatigue screening — DNV-RP-C203 S-N curves, SCF lookup, Miner's rule
- VIV susceptibility — reduced velocity check, lock-in range, DNV-RP-F105
- OrcaFlex model setup — element types, boundary conditions, time step guidance
- OrcaFlex output processing — ASCII result extraction, envelope tables, load case summaries

#### Subsea Pipeline Engineering
- Wall thickness design — DNV-OS-F101 (pressure + collapse + propagation buckling)
- On-bottom stability screening — DNV-RP-F109 absolute lateral stability
- Free span assessment — DNV-RP-F105 allowable span length vs pipe size
- Installation method selection — S-lay / J-lay / reel comparison by water depth + OD
- Corrosion management — NACE MR0175 sour service, internal/external CA logic

#### Fitness for Service (API 579-1 / ASME FFS-1)
- **Wall loss** — Part 4/5 Level 1/2: RSF screening, remaining strength factor
- **Corroded pipeline** — ASME B31G / modified B31G (RSTRENG), MAOP de-rating
- **Dents** — Part 12: d/D ≤ 6% plain, d/D ≤ 2% on weld; gouge interaction
- **Remaining life** — corrosion growth projection, re-inspection interval

#### Gulf of Alaska (GoA) Specifics
- GoA vs GoM design criteria — wave heights, seismic loading, ice constraints
- BSEE GoA data — lease activity, environmental permits, regulatory requirements
- Seismic design — API RP 2EQ spectral approach for GoA platforms
- Extreme metocean — 100-yr parameters for GoA (typically harsher than GoM)

### Sample Conversations

| Question | Time: Manual | Time: AI |
|----------|-------------|---------|
| "What's the wall thickness for 12" X65 at 5,000 ft WD, 3,000 psi?" | 30–60 min | < 2 min |
| "Assess FFS for 15% wall loss in a GoM rigid jumper" | 2–4 hr | 15 min |
| "Draft calculation memo for rigid jumper strength check" | 4–8 hr | 1–2 hr |
| "What's the GoA 100-yr Hs and how does it compare to GoM?" | 1–2 hr | 2 min |
| "Extract max tension and curvature from OrcaFlex ASCII results" | 1–2 hr/case | 5 min |

---

## Page 2 — Roadmap & Next Steps

### Phased Deployment

```
┌─────────────────────────────────────────────────────────────────┐
│  PHASE 1 — Desktop Q&A Demo          Week 1                     │
│  Live demo: code lookups · calculations · OrcaFlex processing   │
│  Cost: $0 additional · uses existing AI subscriptions           │
├─────────────────────────────────────────────────────────────────┤
│  PHASE 2 — Microsoft Teams Chatbot   Weeks 2–4                  │
│  Bot in your existing Teams channels · always-on assistant      │
│  Discipline-specific context loaded · conversation threading    │
│  Cost: ~$20–200/month · Azure Bot Service + Claude API          │
├─────────────────────────────────────────────────────────────────┤
│  PHASE 3 — Document Intelligence     Months 2–3                 │
│  Connect to project docs: design basis · metocean reports       │
│  "What riser OD did we evaluate for this site?" → instant       │
│  Cost: ~$500–2,000/month · RAG backend + document index         │
├─────────────────────────────────────────────────────────────────┤
│  PHASE 4 — Engineering Review QC     Months 4–6                 │
│  Automated checks: analysis vs. design basis alignment          │
│  Flag inconsistencies · compliance check vs. applicable codes   │
│  Grows smarter with every project                               │
└─────────────────────────────────────────────────────────────────┘
```

### What the AI Does Not Do

- Does not replace the reviewing engineer — augments and accelerates
- Does not execute OrcaFlex or other engineering software directly
- All outputs carry a disclaimer: *preliminary/informational, requires engineer verification*
- No proprietary project data stored or used without explicit setup

### Expected Returns

| Metric | Current | With AI | Saving |
|--------|---------|---------|--------|
| Code reference lookup | 15–30 min | 1–2 min | **90%** |
| Preliminary sizing | 2–4 hr | 15–30 min | **85%** |
| Calculation memo draft | 4–8 hr | 1–2 hr | **75%** |
| Simulation data extraction | 1–2 hr/case | 5–10 min | **90%** |
| Scope of work drafting | 1–2 days | 2–4 hr | **70%** |

### Pilot Proposal

1. **Week 1** — Live demo (30 min per team) with 3–5 real project questions
2. **Week 2–3** — Pilot with 2–3 engineers using actual project work
3. **Week 4** — ROI review · decision on Teams chatbot deployment
4. **Month 2+** — Full team rollout · document intelligence integration

---

*Engineering judgment encoded into a system that scales.*
*Domain expertise — not generic AI — is the differentiator.*
