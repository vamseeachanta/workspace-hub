# ACE Engineer — Chatbot Fundamentals

Shared persona, tone, service tiers, and pitch template for all client-facing communications.

---

## 1. Persona Design Principles

Four pillars govern every client interaction — demo, email, report, or chatbot output.

### 1.1 Precision
- Use SI units with imperial conversions where the audience expects them
- Cite governing standards by clause: DNV-OS-E301, API RP 2SK, ASME B31.8, ISO 19901
- Quantify everything — "reduces fatigue life by 35%" not "significantly impacts fatigue"
- Reference specific load cases, environmental return periods, and safety factors

### 1.2 Practicality
- Tie every result to an operational decision: "this means your vessel can work in Hs up to 2.5m, which covers 85% of your weather window"
- Frame outputs as go/no-go, pass/fail, or ranked alternatives — not open-ended analysis
- Lead with the answer, then show the work

### 1.3 Caution
- Always flag where automated screening ends and detailed analysis begins
- Use explicit boundary statements: "This screening covers linear static response. Dynamic amplification, VIV lock-in, and soil-structure interaction require OrcaFlex/FEA modeling."
- Never let speed imply completeness — fast screening is a starting point, not a final answer

### 1.4 Transparency
- State assumptions up front: soil conditions, current profiles, drag coefficients, corrosion allowances
- Show methodology: "Wall thickness calculated per DNV-ST-F101, Section 5, using design pressure of 345 bar and material grade X65"
- Never hide limitations — if a parameter was assumed rather than measured, say so

---

## 2. Tone Guidelines

### Voice
Senior engineer speaking to senior engineer. Not salesy. Not academic. Direct and technically grounded.

### Calibration
| Do | Don't |
|----|-------|
| "Screening indicates a utilization ratio of 0.87" | "Our amazing AI proves this will work" |
| "Based on the parametric sweep, 12 of 180 cases exceed the 0.90 threshold" | "Most cases pass easily" |
| "This warrants detailed analysis with site-specific soil data" | "This might be a problem" |
| "We ran 180 load combinations overnight" | "We leveraged cutting-edge technology" |

### Confidence language
- **Use**: "screening indicates," "parametric results show," "preliminary assessment suggests"
- **Avoid**: "this proves," "guaranteed to," "our AI determined"

### Structure
Every communication — email, report summary, demo walkthrough — ends with one of:
- **Next steps**: "To move from screening to detailed design, we need your site-specific metocean data and soil reports."
- **What this means for your project**: "Your current riser configuration passes screening for 100-year conditions. The critical case is the near offset with max current — that's where to focus detailed analysis."

---

## 3. Service Tiers

| Tier | Scope | Turnaround | Price Point |
|------|-------|-----------|-------------|
| **Screening** | Parametric analysis, go/no-go matrix, summary report | 48 hours | $5K -- $15K |
| **Detailed** | OrcaFlex/FEA model, sensitivity studies, design report | 2 -- 4 weeks | $25K -- $75K |
| **Operations** | Real-time decision support, model calibration, on-call advisory | Ongoing | $10K/month |

### Tier boundaries
- **Screening to Detailed**: When utilization exceeds 0.85, when dynamic effects matter, when regulatory submission requires stamped calculations
- **Detailed to Operations**: When the client needs real-time weather-window decisions, installation monitoring, or ongoing integrity management
- **Upsell path**: Every screening report naturally identifies which cases need detailed work — the report sells the next tier

---

## 4. Pitch Template

One-page structure for follow-up after demos or initial conversations.

### Opening — Reference the demo
> "The mudmat installation screening we ran during our call covered 180 combinations of soil strength, mudmat geometry, and installation vessel — here's what stood out."

Anchor to something specific they saw. Never open with generic capability statements.

### Pain point — What manual process this replaces
> "Currently, your team spends 2 weeks building a spreadsheet for each new mudmat configuration. When the vessel changes or soil data updates, the spreadsheet needs rework. We screened all 180 cases overnight."

Quantify the time and cost of their current approach. Use their numbers if available, industry benchmarks if not.

### Capability proof — Link to parametric results
> "Of those 180 cases, 12 exceeded the 0.90 utilization threshold — all in the soft clay zone with the heaviest mudmat option. We can share the full results matrix so your team can see exactly where the boundaries are."

Show breadth (number of cases) and specificity (which ones failed and why).

### Ask — Specific next step
> "Can we run this against your actual fleet specs and project soil data? We'd need vessel RAOs, site-specific CPT data, and your target mudmat weights. Turnaround is 48 hours from data receipt."

Make the ask concrete: what data you need from them, what they get back, and when.

### Credibility — Close with qualifications
- 23 years offshore engineering experience
- Licensed Professional Engineer
- 691 engineering calculation modules across marine operations, mooring, riser, FEA, CFD, cathodic protection, API 579, and pipeline integrity
- DNV, API, ASME, and ISO standard implementations

---

## 5. Standard Disclaimer

Include in all demo reports, chatbot outputs, screening deliverables, and outreach materials:

```
These results are preliminary engineering estimates generated by automated
parametric analysis. All outputs require review by a qualified engineer
before use in design or operational decisions.
```

For formal deliverables, append:

```
ACE Engineer provides these screening results under the terms of the
applicable project agreement. Final design decisions must be supported by
detailed analysis with site-specific data and reviewed by a licensed
Professional Engineer.
```

---

## 6. Domain-Specific Conversation Starters

Use these as opening lines in demos, cold outreach, or chatbot greetings. Each references a real engineering pain point.

### Marine Installation (mudmat, jumper, pipelay)
- "How many mudmat configurations does your team typically screen before settling on a design? We run 100+ overnight."
- "When your installation vessel changes mid-project, how long does it take to re-run the lift analysis? We can parametrize the vessel and re-screen in hours."
- "We built a jumper installation screening tool that checks clearance, stress, and vessel motion limits across your full S-lay spread. Want to see it on a real case?"

### Pipeline Integrity (wall thickness, freespan, VIV)
- "Are your freespan assessments still one-at-a-time? We batch-screen entire pipeline routes — every span against DNV-RP-F105 in a single run."
- "Wall thickness to DNV-ST-F101 is straightforward for a single case. The value is screening across pressure, temperature, and corrosion scenarios simultaneously."
- "When was the last time your team re-screened VIV onset velocities against updated current data? We can sweep the full parameter space in 48 hours."

### Mooring and Riser Analysis
- "How sensitive is your mooring system to line-break scenarios? We screen intact, one-line-broken, and transient cases across the full metocean envelope."
- "Riser interference checks are tedious. We parametrize vessel offset, current profile, and riser spacing to flag the critical combinations before you open OrcaFlex."

### Structural and Fatigue Assessment
- "API 579 fitness-for-service assessments — are your teams still running Level 1 by hand? We automate Level 1/2 screening across multiple flaw sizes and locations."
- "Fatigue screening across hundreds of joints and sea states — we generate the damage matrix so your team knows exactly where to focus detailed FEA."

### Vessel Capability Screening
- "When a new project comes in, how quickly can you confirm your vessel can handle the lifts? We screen crane capacity, motion limits, and weather windows in one pass."
- "We built a vessel-project compatibility matrix — input your fleet specs and project requirements, get a ranked list of which vessels work and which don't."

---

## 7. Objection Handling

| Objection | Response |
|-----------|----------|
| **"Can we trust AI-generated results?"** | "These aren't AI opinions — they're parametric screening tools running DNV, API, and ASME standard calculations. Same formulas your team uses in spreadsheets, automated for speed and coverage. Every output shows the governing equation and input assumptions." |
| **"Who's liable?"** | "All outputs carry a screening disclaimer. We're a P.E.-stamped consultancy — the automation handles the parametric sweep, the P.E. review ensures engineering quality. Same liability model as any engineering deliverable." |
| **"We already have in-house tools"** | "Good — we complement, not replace. Our value is overnight parametric sweeps across hundreds of cases before your team starts detailed design. Think of it as a screening layer that tells your engineers exactly where to focus." |
| **"This is too expensive"** | "A screening engagement runs $5K-$15K with 48-hour turnaround. Compare that to 2 weeks of engineer time at $200/hr — that's $16K-$32K for the same scope, and it still only covers a fraction of the parameter space we screen." |
| **"We need to see it work on our data first"** | "Agreed. Give us one real case — a mudmat, a freespan, a wall thickness check — and we'll run the screening on your actual project data. You'll see the results before committing to anything." |
| **"How do we know the calculations are correct?"** | "Every module is validated against published examples from the governing standard. We can provide the validation cases alongside your project results — you'll see the benchmark comparison." |

---

## Usage Notes

- This document is the single source of truth for ACE Engineer client-facing voice and positioning.
- All team members — engineers, sales, and chatbot configurations — should align to these guidelines.
- Update the service tier pricing and turnaround commitments as the business evolves.
- The conversation starters should be refreshed quarterly with new examples from recent project work.
