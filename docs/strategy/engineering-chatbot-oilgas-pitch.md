# Engineering Chatbot for Oil & Gas: Capability Roadmap & Client Pitch

## Overview

A domain-specific AI chatbot built on large language model technology, tailored for offshore oil and gas engineering. The system leverages deep expertise in subsea engineering, floating systems, riser analysis, mooring design, and fatigue assessment to deliver scalable, intelligent engineering support to clients.

---

## Current State of Technology

### What Works Well Today

- General engineering concept explanation and methodology walkthroughs
- Standards and code interpretation (API, DNV, ABS)
- Technical report drafting and documentation assistance
- Code and scripting automation (Python, OrcaFlex batch scripting, Excel macros)
- Conversational Q&A with engineering-grade vocabulary

### Known Limitations

- Risk of hallucination on highly specific technical values (pipe properties, S-N curves, code clauses)
- No direct access to proprietary project data without integration
- Cannot execute engineering software (OrcaFlex, SACS, etc.) — assists with setup and post-processing only
- Liability considerations when outputs feed into engineering decisions

### Deployment Readiness

| Tier | Description | Readiness |
|------|-------------|-----------|
| Tier 1 | Knowledge assistant — Q&A, documentation, scripting help | **Ready today** |
| Tier 2 | RAG-based system connected to project document libraries | **Feasible with effort** |
| Tier 3 | Autonomous engineering agent with analysis capabilities | **Emerging (2–3 years)** |

---

## Phased Capability Roadmap

### Phase 1 — Smart Knowledge Base

**Objective:** Replace email chains and document hunting with instant, conversational access to engineering knowledge.

**Capabilities:**

- Query project standards (API, DNV, ABS) in natural language
- On-demand methodology explainers (fatigue analysis, CALM buoy mooring, FDAS systems)
- Automated glossary and acronym resolution
- Onboarding tool for engineers joining projects mid-stream

**Client Value:** Reduced time searching for information; consistency in engineering communication across teams.

---

### Phase 2 — Project Document Intelligence (RAG System)

**Objective:** Connect the chatbot to client project documents for intelligent retrieval and cross-referencing.

**Capabilities:**

- Upload design basis, metocean reports, or vessel data sheets and query in natural language
  - *"What's the 100-year Hs for this site?"*
  - *"What riser OD and wall thickness options did we evaluate?"*
- Cross-reference across documents (e.g., mooring analysis vs. metocean basis alignment)
- Automated extraction of key parameters from PDFs and spreadsheets
- Change tracking between document revisions (*"What changed between Rev A and Rev B?"*)

**Client Value:** Engineers spend 30–40% of their time finding and cross-referencing information. This capability cuts that dramatically.

---

### Phase 3 — Analysis Pre-Processor & QC Tool

**Objective:** Accelerate routine engineering analysis setup and quality control.

**Capabilities:**

- Automated OrcaFlex input file generation based on project parameters
- Pre-run sanity checks (*"Your riser weight in water doesn't match the wall thickness specified"*)
- Post-processing of OrcaFlex results into client-ready summary tables
- Fatigue life calculation workflows with S-N curve selection guidance
- Vessel motion data parsing and statistical summaries from RAO files or time series

**Client Value:** Faster turnaround on routine analysis, fewer late-stage errors, and faster ramp-up for junior engineers.

---

### Phase 4 — Engineering Review Assistant

**Objective:** Serve as a QA/QC multiplier — augmenting, not replacing, the reviewing engineer.

**Capabilities:**

- Automated checks of analysis reports against design basis requirements
- Flag inconsistencies between documents (e.g., load cases in analysis vs. design basis)
- Compliance checking against relevant codes and standards
- Lessons-learned database that grows with every project

**Client Value:** Reduces senior engineer review time; catches errors missed due to fatigue or familiarity.

---

### Phase 5 — Digital Engineering Advisor (Long-Term Vision)

**Objective:** Provide strategic engineering intelligence and concept-level decision support.

**Capabilities:**

- Concept screening — input field parameters, water depth, and metocean data to receive preliminary riser and mooring configuration recommendations
- Historical benchmarking from past projects (anonymized)
- Risk identification based on similar project experience
- Integration with real-time monitoring data from installed systems

**Client Value:** Data-driven decision-making from the earliest stages of field development.

---

## Recommended Pricing Structure

| Package | Scope | Pricing Model |
|---------|-------|---------------|
| **Starter** | Phase 1 — General knowledge assistant | Per seat / month |
| **Project** | Phase 2–3 — Document intelligence + analysis tools | Per project |
| **Enterprise** | Phase 4–5 — Embedded engineering QA/QC + advisory | Annual contract |

---

## Key Differentiator

> **You're not selling AI — you're selling engineering judgment encoded into a system that scales.**

Any software company can build a chatbot. Very few can build one that understands the difference between a lazy-wave SCR and a free-hanging catenary, or why fatigue in the touch-down zone matters. Domain expertise is the competitive moat.

---

## Persona Design Principles

The chatbot should project:

- **Technical precision** — correct terminology, no hand-waving on engineering details
- **Practical orientation** — solution-focused, not academic
- **Appropriate caution** — engineering decisions carry safety and environmental consequences
- **Transparent reasoning** — engineers want to verify the logic, not just accept answers

All outputs carry clear disclaimers that results are for preliminary/informational purposes and require independent verification by a qualified engineer.

---

*Prepared by: [Your Name / Company]*
*Date: February 2026*
