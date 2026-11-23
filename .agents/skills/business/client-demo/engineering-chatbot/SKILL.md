---
name: engineering-chatbot-demo
version: 1.0.0
category: business/client-demo
description: "GTM demo execution for engineering AI chatbot presentations \u2014 system\
  \ prompt authoring, demo scripting, ROI capture"
type: reference
capabilities:
- system_prompt_design
- demo_script_builder
- calculation_template_builder
- knowledge_base_structuring
- pilot_feedback_capture
- chatbot_pitch_delivery
requires: []
trigger: manual
---

# Engineering Chatbot Demo Skill

> Full GTM workflow for presenting engineering AI chatbots to clients — covers system prompt design through ROI capture. Reusable template for any new engineering discipline.

## System Prompt Template

Produce discipline-specific system prompts in this order:

1. **Role definition** — "You are a senior [discipline] engineer with X years of [domain] experience"
2. **Core competencies** — domain-specific bullet list (6–10 items)
3. **Primary codes & standards** — with version years (e.g. API 2A-WSD 22nd Ed. 2014)
4. **Calculation capabilities** — formula notation, accepted inputs/outputs
5. **Persona and Tone** — precision · practicality · caution · transparency
6. **Known Limitations** — hallucination risk, no proprietary data, no software execution
7. **Standard disclaimer** — "Outputs are preliminary engineering estimates requiring QA review"

## Demo Script Builder (15–20 min flow)

| Phase | Duration | Content |
|-------|----------|---------|
| Hook | 2 min | Live lookup: "What does API 2A say about pile fatigue?" |
| Calculation | 5 min | Step-by-step calc: formula → substitution → result → acceptance check |
| Data processing | 4 min | Paste inspection data → AI generates corrosion rate summary table |
| Document gen | 4 min | AI drafts scope of work or memo from bullet points |
| Q&A | 5 min | Open questions; capture objections |

## Calculation Template Format

```
### [Calc Name]
**Code ref:** API/DNV/ISO clause X.Y.Z
**Formula:** σ = F / A
**Inputs:** F = [value] kN, A = [value] m²
**Result:** σ = [value] MPa
**Acceptance:** σ ≤ F_y / 1.67 = [value] MPa → PASS/FAIL
```

## Knowledge Base Structuring

Structure markdown KB files for reliable AI citation:
- Top-level `##` headings per topic (AI retrieves by heading)
- Tables for code values (yield strengths, load factors, limits)
- Numbered clauses matching source document numbering
- `> Note:` callouts for exceptions or applicability limits

## Pilot Feedback Capture

After each demo session record:
- **Time savings estimate:** "Task X took Y hours; AI did it in Z minutes"
- **Q&A log:** questions asked + AI answer quality (Good / Needs refinement / Wrong)
- **Objections:** capture verbatim; map to rebuttal
- **ROI metric:** hours saved × billable rate / demo session cost

## Chatbot Pitch Delivery

| Tier | Description | Price signal |
|------|-------------|--------------|
| T1 | Read-only assistant (Q&A, code lookups) | Project-based |
| T2 | T1 + calculation templates + doc generation | Retainer |
| T3 | T2 + custom KB + pilot + 3-month support | Enterprise |

**Objection handling:**
- *"It hallucinates"* → Show disclaimer; position as senior-engineer-reviewer tool, not replacement
- *"Our data is proprietary"* → Explain no-training policy; local-deploy option (T3)
- *"Too expensive"* → Anchor to billable hours saved in pilot log
