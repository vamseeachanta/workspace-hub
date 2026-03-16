# 13 — Conclusions

## Purpose

State the adequacy conclusion, identify governing checks, and confirm code
compliance. This section is the final engineering judgment — it must be
unambiguous and self-contained so it can be quoted in design reports.

## Schema Fields

```yaml
conclusions:
  adequacy: string            # clear adequacy statement (scalar string)
  governing_check: string     # governing check identification (scalar string)
  recommendations:            # optional — list of action items
    - string
  compliance_statement: string  # optional — code compliance summary
```

> **Renderer Mapping Note:** The methodology recommends `adequacy_statement`
> (not `adequacy`), `governing_checks[]` (list of structured objects with
> check/utilization/standard/clause), `code_compliance[]` (list of objects),
> and `conditions_of_use[]`. The renderer uses `adequacy` (scalar string),
> `governing_check` (scalar string), optional `recommendations[]` (list of
> strings), and optional `compliance_statement` (scalar string). Encode
> utilization ratios and conditions of use into the string values.

## Required Content

- Unambiguous adequacy statement in `adequacy`
- Governing check identification with utilization ratio in `governing_check`
- Code compliance summary in `compliance_statement`
- Any conditions or caveats in `recommendations`

## Quality Checklist

- [ ] `adequacy` is a scalar string (not `adequacy_statement`)
- [ ] `governing_check` is a scalar string (not `governing_checks[]` list)
- [ ] `compliance_statement` is a scalar string (not `code_compliance[]` list)
- [ ] Adequacy statement is self-contained (readable without the full calc)
- [ ] Recommendations are actionable (not vague)

## Example Snippet

```yaml
conclusions:
  adequacy: >
    The 12-inch export pipeline with 20.6 mm nominal wall thickness is
    adequate for pressure containment, external pressure collapse, and
    combined loading per DNV-ST-F101 (2021) for the 25-year design life.
  governing_check: >
    Pressure containment (burst) — utilization 0.618 per DNV-ST-F101
    Section 5.4.2, Eq. 5.8. 38.2% remaining capacity.
  recommendations:
    - "Monitor corrosion rate annually; re-assess if rate exceeds 0.1 mm/yr"
    - "Confirm mill test certificates match X65 PSL2 requirements before fabrication"
  compliance_statement: >
    All pressure and collapse checks comply with DNV-ST-F101 (2021).
    Valid for operating temperature -10 to 80 degC and maximum design
    pressure 345 barg.
```

## Common Mistakes

- Using `adequacy_statement` instead of `adequacy` (renderer requires `adequacy`)
- Using `governing_checks` as a list of dicts instead of `governing_check` scalar
- Using `code_compliance` as a list of dicts instead of `compliance_statement` scalar
- Including `conditions_of_use[]` (not consumed — encode in `compliance_statement`)
- Vague conclusion ("the pipeline is OK") instead of specific adequacy statement
