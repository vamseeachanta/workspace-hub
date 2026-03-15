# 13 — Conclusions

## Purpose

State the adequacy conclusion, identify governing checks, and confirm code
compliance. This section is the final engineering judgment — it must be
unambiguous and self-contained so it can be quoted in design reports.

## Schema Fields

```yaml
conclusions:
  adequacy_statement: string   # clear pass/fail statement
  governing_checks:
    - check: string
      utilization: number
      standard: string
      clause: string
  code_compliance:
    - standard: string
      status: enum             # compliant | non_compliant | partially_compliant
      notes: string
  recommendations:
    - string                   # actions, caveats, or conditions on the conclusion
  conditions_of_use:
    - string                   # constraints under which the conclusion is valid
```

## Required Content

- Unambiguous adequacy statement (adequate / inadequate / conditionally adequate)
- Governing check identification with utilization ratio
- Code compliance statement for each standard cited in section 03
- Any conditions or caveats on the conclusion

## Quality Checklist

- [ ] Adequacy statement is self-contained (readable without the full calc)
- [ ] Governing check is explicitly named with its utilization ratio
- [ ] Code compliance lists every standard from the design basis
- [ ] Conditions of use match the validity range from section 02
- [ ] Recommendations are actionable (not vague)

## Example Snippet

```yaml
conclusions:
  adequacy_statement: >
    The 12-inch export pipeline with 20.6 mm nominal wall thickness is
    adequate for pressure containment, external pressure collapse, and
    combined loading per DNV-ST-F101 (2021) for the 25-year design life.
  governing_checks:
    - check: "Pressure containment (burst)"
      utilization: 0.618
      standard: "DNV-ST-F101"
      clause: "Section 5.4.2, Eq. 5.8"
  code_compliance:
    - standard: "DNV-ST-F101 (2021)"
      status: compliant
      notes: "All pressure and collapse checks pass within allowable limits"
  recommendations:
    - "Monitor corrosion rate annually; re-assess if rate exceeds 0.1 mm/yr"
    - "Confirm mill test certificates match X65 PSL2 requirements before fabrication"
  conditions_of_use:
    - "Valid for operating temperature range -10 to 80 degC"
    - "Valid for maximum design pressure of 345 barg"
    - "Assumes uniform wall thickness — local thinning requires separate assessment"
```

## Common Mistakes

- Vague conclusion ("the pipeline is OK") instead of specific adequacy statement
- Governing check not identified — conclusion does not say what limits the design
- Code compliance missing for a standard cited in the design basis
- No conditions of use — conclusion appears unconditional when it is not
- Recommendations are generic ("further study recommended") without specifics
