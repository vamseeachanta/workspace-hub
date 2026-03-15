# 06 — Assumptions

## Purpose

List every assumption explicitly with a justification and classification as
conservative or best-estimate. Assumptions are engineering decisions — they
must be visible so reviewers can challenge them and so future revisions know
what was assumed vs measured.

## Schema Fields

```yaml
assumptions:
  - id: string                # sequential identifier (e.g., "A-01")
    statement: string         # clear, testable statement
    justification: string     # why this assumption is reasonable
    type: enum                # conservative | best_estimate | neutral
    impact: enum              # high | medium | low
    revisit_trigger: string   # condition that would invalidate this assumption
```

## Required Content

- Numbered list of all assumptions
- Each assumption has a justification (not just the statement)
- Classification as conservative, best-estimate, or neutral
- Impact rating indicating sensitivity of results to this assumption

## Quality Checklist

- [ ] Every assumption is a testable statement (not vague)
- [ ] Conservative assumptions are identified so reviewers see margin sources
- [ ] High-impact assumptions link to sensitivity analysis in section 10
- [ ] Revisit triggers define when the assumption must be re-evaluated
- [ ] No hidden assumptions — if a parameter in section 05 is "assumed," it
      must appear here with justification

## Example Snippet

```yaml
assumptions:
  - id: "A-01"
    statement: "Pipeline is fully restrained axially beyond 2 km from ends"
    justification: >
      Friction from soil cover and pipeline weight exceeds thermal expansion
      force at distances greater than 2 km. Confirmed by anchor length
      calculation in PRJ-CALC-005.
    type: conservative
    impact: medium
    revisit_trigger: "Route change reducing buried length below 2 km"

  - id: "A-02"
    statement: "Corrosion allowance of 3 mm applied uniformly"
    justification: >
      Based on 25-year design life and 0.1 mm/yr corrosion rate from
      corrosion study CR-2026-001, rounded up to provide margin.
    type: conservative
    impact: high
    revisit_trigger: "Corrosion monitoring data showing rate above 0.1 mm/yr"
```

## Common Mistakes

- Assumption stated without justification ("assumed 3 mm corrosion allowance")
- All assumptions marked "conservative" without demonstrating why
- High-impact assumptions not carried forward to sensitivity analysis
- Assumptions buried in calculation text instead of listed here
- Missing revisit trigger — no one knows when to re-check the assumption
