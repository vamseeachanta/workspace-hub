---
title: "AI in Drill Well on Paper (DWOP)"
tags: [drilling, dwop, genai, well-planning, iadc]
sources:
  - career-learnings-seed
added: 2026-04-08
last_updated: 2026-04-08
---

# AI in Drill Well on Paper (DWOP)

DWOP is a pre-spud planning exercise where the drilling team walks through every well section on paper before a single foot of hole is drilled. The goal: identify risks, optimise procedures, and build shared understanding among all disciplines (drilling, completions, geology, logistics, HSE). Emerging GenAI applications aim to accelerate the preparation phase — but the core value of DWOP remains the human team alignment, not the documentation.

## What Is DWOP?

DWOP originated as a best practice in the 1990s and is now standard across most operators. The process:

1. **Assemble the team**: drilling engineer, mud engineer, casing designer, geologist, completions engineer, rig crew, HSE representative
2. **Walk each section**: from spud to TD, section by section — surface hole, intermediate, production
3. **For each section, discuss**: bit selection, mud weight window, casing design, cementing plan, trip schedule, contingency procedures
4. **Identify risks**: lost circulation zones, kicks, stuck pipe, wellbore instability, formation damage
5. **Agree on decision points**: at what depth/condition does the team deviate from plan?
6. **Document**: the output is a well program (or well execution document) that the rig follows

The discipline of walking every section on paper — before the rig is on location — catches problems that spreadsheets and design software miss. It is fundamentally a **communication exercise**.

## GenAI Application — IADC Presentation

Akshay Manjramkar (Jindal Drilling) presented a GenAI application for DWOP at an IADC conference. The system:

- **Automated well program parsing** — ingests historical well programs (PDFs, Word docs), extracts structured data (depths, mud weights, casing sizes, bit records)
- **Execution-ready plan generation** — produces a draft well program from offset well data and the planned well trajectory
- **Claimed efficiency**: ~98% faster preparation time compared to manual DWOP preparation

### The 98% Claim — Handle with Skepticism

The "98% faster" figure applies to the **document preparation** phase, not the entire DWOP process. The value of DWOP is in the team discussion, not the document. Generating a draft faster is useful, but the critical thinking happens in the room, not in the AI output.

| Phase | Manual Time | AI-Assisted Time | Where Value Actually Is |
|-------|------------|------------------|------------------------|
| Data gathering from offset wells | Days | Hours | Genuine time savings — data retrieval is tedious |
| Draft well program creation | Days | Hours | Moderate value — but draft quality must be verified |
| Team review and discussion | Hours-Days | Hours-Days | **Unchanged** — this is the irreducible core |
| Risk identification | Team-dependent | Team-dependent | AI can surface historical incidents, but judgment is human |

## Domain Expert Caution

Senior drilling professionals have been clear about the limits:

**Peter Aird** (well engineering author, industry veteran): AI tools are useful for data retrieval and pattern recognition in historical records, but **drilling judgment comes from experience with failure modes** that are poorly represented in training data. The rare events — kicks, blowouts, stuck pipe in unusual formations — are exactly what DWOP exists to anticipate, and these are sparse in any dataset.

**John de Wardt** (DE&S, well delivery optimisation): The bottleneck is not the algorithm — it is **data quality and data sourcing**. Offset well data is often inconsistent (different operators, different reporting standards, different eras of technology). An AI system trained on poor-quality data produces confident-sounding but unreliable plans.

### Key Takeaway

**Speed without competence is dangerous in drilling**. A well program generated in 2 hours instead of 2 days is only valuable if the team still reviews it with the same rigor. The risk is that fast generation leads to superficial review.

## Where AI Genuinely Adds Value

1. **Offset well data retrieval**: searching through hundreds of historical well reports to find relevant analogues — this is where LLMs and RAG systems genuinely save time
2. **Structured extraction from unstructured documents**: converting PDF daily drilling reports (DDRs) into structured databases of events, depths, and parameters
3. **Pattern recognition**: identifying correlations between formation properties and drilling problems across a portfolio of wells
4. **Planning-to-execution feedback loop**: comparing planned vs. actual performance to improve future well designs — this is where **value compounds over time**

The compounding value comes from closing the loop: each drilled well's actual performance feeds back to improve the next well's plan. AI can automate this feedback, but the insights must be validated by engineers who understand the geology and mechanics.

## Data Quality — The Real Bottleneck

The limiting factor for AI in drilling is data, not algorithms:

| Data Challenge | Impact |
|---------------|--------|
| **Inconsistent formats** | DDRs from different rigs use different templates, units, and conventions |
| **Missing records** | Older wells may have no digital records; paper logs may be illegible |
| **Operator-specific terminology** | "tight hole" means different things in different organisations |
| **Survivorship bias** | Success data is plentiful; failure data is under-reported or sanitised |
| **Contextual information loss** | A DDR says "stuck pipe at 3500m" but not the full geological and operational context |

Until the industry solves the data quality problem — standardised digital reporting, comprehensive incident databases, interoperable formats — AI tools will be limited to well-documented, data-rich environments.

## Key Patterns

1. **DWOP is pre-spud — walk every section on paper** — the value is in team alignment, not the document
2. **98% faster claim: skeptical** — speed without competence is dangerous; the claim applies to document prep, not the planning process
3. **Data quality and sourcing is the actual bottleneck** — algorithms are not the limiting factor
4. **Planning-to-execution feedback is the compounding value** — each well improves the next, and AI can automate this loop

## Practical Guidance

- If adopting AI-assisted DWOP, **keep the team review session unchanged**. The AI draft is a starting point, not a replacement for the discussion.
- Focus AI investment on the **data pipeline** first: digitise DDRs, standardise offset well databases, build structured incident records. The AI tools will only be as good as the data they ingest.
- Use AI-generated risk flags as **prompts for discussion**, not as definitive risk assessments. The team should still independently identify risks and use the AI output as a cross-check.
- Track **planned vs. actual** metrics for every well and feed this back into the system. This is where the return on AI investment compounds.

## Cross-References

- **Related concept**: [[energy-field-economics]] — well cost is the largest capex component; DWOP optimisation directly reduces cost per well
- **Related concept**: [[fea-structural-analysis]] — casing design and wellhead structural analysis feed into the DWOP
- **Source**: [Career Learnings Seed](../sources/career-learnings-seed.md)
- **Cross-wiki (marine-engineering)**: [AI in Drill Well on Paper (DWOP)](../../../marine-engineering/wiki/entities/ai-dwop.md) -- similar titles (100%); shared tags: drilling, dwop, genai, well-planning; shared keywords: ai, application, automated, cross-references, drill
