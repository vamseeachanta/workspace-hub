# 07 — Methodology

## Purpose

Select the governing standard and method, confirm its applicability to the
problem, and present the governing equations in symbolic form. This section
bridges the "what are we checking" (scope) to "how we check it" (calculations).

## Schema Fields

```yaml
methodology:
  standard: string            # governing code and clause
  method_name: string         # descriptive method name
  applicability:
    - parameter: string       # e.g., "D/t ratio"
      required_range: string  # code limit
      actual_value: string    # value for this problem
      status: enum            # within_limits | outside_limits
  equations:
    - id: string              # equation identifier (e.g., "Eq-01")
      description: string
      symbolic: string        # equation in symbolic form
      reference: string       # code clause and equation number
      variables:
        - symbol: string
          name: string
          defined_in: string  # section reference (e.g., "section 05")
  alternative_methods:
    - name: string
      reason_not_used: string # why this method was not selected
```

## Required Content

- Governing standard, edition, and specific clause
- Applicability check with actual values vs code limits
- At least one equation in symbolic form before numeric substitution
- Variable definitions linking back to inputs (section 05) or materials (section 04)

## Quality Checklist

- [ ] Applicability check is quantitative (actual vs allowed), not just stated
- [ ] Equations are shown symbolically before any numbers are substituted
- [ ] Each equation references its source clause and equation number
- [ ] All variables in the equation are defined and traceable to earlier sections
- [ ] Alternative methods are acknowledged with reason for non-selection

## Example Snippet

```yaml
methodology:
  standard: "DNV-ST-F101 (2021) Section 5.4.2"
  method_name: "Pressure containment (burst) — LRFD format"
  applicability:
    - parameter: "D/t ratio"
      required_range: "15 ≤ D/t ≤ 45"
      actual_value: "15.7"
      status: within_limits
    - parameter: "Material grade"
      required_range: "up to X80"
      actual_value: "X65"
      status: within_limits
  equations:
    - id: "Eq-01"
      description: "Pressure containment resistance"
      symbolic: "p_b = (2 * t_1) / (D_o - t_1) * f_cb * (2 / sqrt(3))"
      reference: "DNV-ST-F101 Eq. 5.8"
      variables:
        - symbol: "t_1"
          name: "Corroded wall thickness"
          defined_in: "section 05, derived from t_nom - t_corr"
        - symbol: "f_cb"
          name: "Characteristic material strength"
          defined_in: "section 04, min(SMYS, SMTS/1.15)"
  alternative_methods:
    - name: "ASME B31.8 Barlow formula"
      reason_not_used: "Project design basis specifies DNV-ST-F101"
```

## Common Mistakes

- No applicability check — method applied outside its valid range
- Jumping straight to numeric substitution without showing the symbolic equation
- Variables in the equation not traced back to a defined input
- Standard cited without the specific clause or equation number
- Alternative methods not discussed — reviewer may question why this method
  was chosen over others
