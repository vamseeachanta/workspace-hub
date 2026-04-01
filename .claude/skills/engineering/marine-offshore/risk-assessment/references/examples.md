# Risk Assessment — Complete Examples

## Example 1: Complete Mooring System Risk Assessment

```python
import numpy as np
from pathlib import Path

def complete_mooring_risk_assessment(
    design_parameters: dict,
    environmental_parameters: dict,
    n_simulations: int = 10000
) -> dict:
    """

*See sub-skills for full details.*
```

## Well Planning Risk Context

### The Actionability Gap

Standard 5x5 risk matrices capture **what** the risk is and **how severe** it is, but not **who has the authority to mitigate it**. In well planning, this creates a systematic bias:

- Engineers write risks they can act on (operational: mud weight, BOP procedures, casing design)
- Engineers omit risks they understand but cannot control (strategic: downhole tool contracts, rig selection, fleet capacity)
- The risk register becomes operationally complete but strategically incomplete

### Risk Authority Tiers

When building risk registers for well planning, classify every risk into one of three tiers:

| Tier | Authority | Decision Sits With | Example Risks |
|------|-----------|-------------------|---------------|
| **Operational** | Project team | Drilling engineer / superintendent | Lost circulation, wellbore instability, swelling clay, mud contamination |
| **Tactical** | Cross-functional | Project manager + discipline leads | Casing design changes, BOP stack configuration, completion sequence |
| **Strategic** | Outside project | Procurement / fleet / corporate | Downhole tool availability, rig hook load capacity, contract terms, regulatory changes |

### Structured Escalation for Strategic Risks

When a risk falls outside project authority, convert it from a vague register entry into a structured escalation:

```
Risk: [Formation X] requires [capability Y] that current [tool/rig/contract] does not provide.
Impact if unaddressed: [specific consequence — NPT days, sidetrack probability, well objective at risk]
Mitigation lever: [what needs to change — new tool contract, different rig class, regulatory exemption]
Decision owner: [organizational function — procurement, fleet management, regulatory affairs]
Decision timeline: [when the decision must be made relative to spud date]
```

This reframes "we need a better downhole tool" into an actionable request with a clear owner, deadline, and consequence.

### Risk Influence Map

Categorize the project's relationship to each risk:

- **Controls**: Project team can directly mitigate (operational risks)
- **Influences**: Project team provides input but doesn't decide (tactical risks)
- **Observes**: Project team identifies and escalates but has no lever (strategic risks)

A well planning risk register should have risks in all three categories. If the register contains only operational risks, the strategic dimension is being suppressed — not because those risks don't exist, but because the project lacks empowerment to address them.

### Integration with Quantitative Assessment

The Monte Carlo and reliability tools in this skill quantify operational risks effectively. For strategic risks, the quantitative output serves a different purpose — it provides the **business case for escalation**:

```python
# Example: Quantify cost impact of rig capability gap
# This output goes into the escalation template, not the project risk register
rig_gap_risk = assess_hazards([
    Hazard(
        id='STR-001',
        description='Rig hookload insufficient for 9-5/8" casing at TD',
        severity=Severity.MAJOR,          # sidetrack or redesign required

*See sub-skills for full details.*
```
