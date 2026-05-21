# Interactive force-by-force review before engineering calculation plans

Use when an engineering-calculation issue is explicitly opened as an interactive discussion thread before implementation, especially marine/offshore force and moment packages.

## Pattern

1. **Surface the live GitHub issue first.**
   - If the user asks to start adding comments, give the clickable issue URL and current issue state before doing deeper repo inspection.
   - Do not bury the thread link under process narration; the immediate deliverable is enabling the user to comment.

2. **Treat issue comments as engineering input, not noise.**
   - Pull decisions from comments into a decision ledger before drafting the canonical plan.
   - Preserve unresolved items as blockers/questions rather than filling gaps from assumptions.

3. **Force-by-force discussion sequence**
   - Establish coordinate frame, sign convention, datum, and CoG reference before component calculations.
   - Then discuss components one at a time: `X`, `Y`, `Z` if retained, `K`, `M`, `N`, then result/component presentation.
   - For each component, capture: model/source, sign convention, application point, moment arm/reference, units/rounding, chart/table requirements, and report wording.

4. **Plan only after the interactive decisions are stable.**
   - The plan should cite user comment decisions and remaining blockers.
   - If the user is still actively correcting force conventions or report presentation, keep the issue in resource-intel/discussion mode; do not present the plan as approval-ready.

5. **Scope discipline**
   - Keep revision issues bounded to the existing package unless the user explicitly folds in new physics.
   - Split new hull-current effects, mooring stiffness, class/IMO compliance, propeller race, tug loads, current-profile variation, or bank effects into separate issues when they materially change the model class.

## Report-specific reminders

- When the user requests component/resultant comparisons or removals, reflect that explicitly in the plan’s output contract.
- For schematics, define what the drawing must prove: axes, datum, CoG, force line of action, moment sense, and default-case values.
- For rounded engineering tables, separate display rounding from calculation precision when traceability matters.