---
name: write-spec
type: command
plugin: product-management
source: https://github.com/anthropics/knowledge-work-plugins
---

# /write-spec - Write a Feature Specification

Write a feature specification or product requirements document (PRD).

## Usage

```
/write-spec <feature name or problem description>
```

## Workflow

### 1. Understand the Feature

Accept any of:
- A feature name ("SSO support")
- A problem statement ("Enterprise customers keep asking for centralized auth")
- A user request ("Users want to export their data as CSV")
- A vague idea ("We should do something about onboarding drop-off")

### 2. Gather Context

Ask conversationally for:
- **User problem**: What problem does this solve? Who experiences it?
- **Target users**: Which user segment(s) does this serve?
- **Success metrics**: How will we know this worked?
- **Constraints**: Technical constraints, timeline, regulatory requirements, dependencies
- **Prior art**: Has this been attempted before? Are there existing solutions?

### 3. Pull Context from Connected Tools

If project tracker, knowledge base, or design tools are connected, search for related tickets, research documents, and mockups to inform the spec.

### 4. Generate the PRD

Produce a structured PRD with:
- **Problem Statement**: The user problem, who is affected, and impact (2-3 sentences)
- **Goals**: 3-5 specific, measurable outcomes
- **Non-Goals**: 3-5 things explicitly out of scope
- **User Stories**: Standard format, grouped by persona
- **Requirements**: Categorized as Must-Have (P0), Nice-to-Have (P1), Future (P2)
- **Success Metrics**: Leading and lagging indicators with targets
- **Open Questions**: Tagged with who needs to answer
- **Timeline Considerations**: Hard deadlines, dependencies, phasing

### 5. Review and Iterate

After generating:
- Ask the user if any sections need adjustment
- Offer to expand on specific sections
- Offer to create follow-up artifacts (design brief, engineering ticket breakdown, stakeholder pitch)

## Tips

- Be opinionated about scope. Tight and well-defined beats expansive and vague.
- If the idea is too big for one spec, suggest breaking it into phases.
- Success metrics should be specific and measurable.
- Non-goals are as important as goals.
