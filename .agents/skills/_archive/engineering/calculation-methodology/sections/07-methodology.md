# 07 — Methodology

## Purpose

Select the governing standard and method, confirm its applicability to the
problem, and present the governing equations in symbolic form. This section
bridges the "what are we checking" (scope) to "how we check it" (calculations).

## Schema Fields

```yaml
methodology:
  description: string         # narrative description of the approach
  standard: string            # governing code and clause
  equations:
    - id: string              # equation identifier (e.g., "eq1", "1")
      name: string            # descriptive equation name
      latex: string           # equation in LaTeX notation
      description: string     # what this equation computes
      variables:              # optional — variable definitions
        - symbol: string
          description: string
          unit: string        # optional
```

> **Renderer Mapping Note:** The methodology recommends `method_name`,
> structured `applicability` checks, `symbolic` (not `latex`), `reference`
> per equation, and `alternative_methods`. The renderer does not consume
> these fields. Use `latex` (not `symbolic`) for equation notation. Encode
> applicability checks and method selection rationale in `description`.
> Each equation needs `id`, `name`, `latex`, and `description`.

## Required Content

- Governing standard, edition, and specific clause (in `standard` field)
- Narrative description of the approach
- At least one equation with LaTeX notation
- Variable definitions linking back to inputs (section 05) or materials (section 04)

## Quality Checklist

- [ ] Equations use `latex` field (not `symbolic`)
- [ ] Each equation has `id`, `name`, `latex`, and `description`
- [ ] All variables in the equation are defined with `symbol` and `description`
- [ ] `standard` field includes edition year and clause reference
- [ ] Applicability rationale is included in `description`

## Example Snippet

```yaml
methodology:
  description: >
    Sacrificial anode CP design for an offshore jacket in tropical waters.
    Calculates current demand at initial, mean, and final conditions, then
    sizes anodes to meet the total charge requirement over design life.
    Method is applicable for D/t ratio 15–45 (actual: 15.7) and material
    grades up to X80 (actual: X65).
  standard: "DNV-RP-B401 (2011) Cathodic Protection Design"
  equations:
    - id: eq1
      name: "Current demand"
      latex: "I_c = A_c \\cdot i_c \\cdot f_c"
      description: "Current demand for coated structure (§7.4.1)"
    - id: eq2
      name: "Total anode mass"
      latex: "M_a = \\frac{I_{cm} \\cdot t_f \\cdot 8760}{u_f \\cdot \\varepsilon}"
      description: "Net anode mass requirement (§7.7.1)"
      variables:
        - symbol: "I_{cm}"
          description: "Mean current demand"
          unit: "A"
        - symbol: "t_f"
          description: "Design life"
          unit: "years"
        - symbol: "u_f"
          description: "Anode utilisation factor"
        - symbol: "\\varepsilon"
          description: "Anode electrochemical capacity"
          unit: "Ah/kg"
```

## Common Mistakes

- Using `symbolic` instead of `latex` (renderer requires `latex`)
- Including `method_name`, `applicability`, or `alternative_methods` fields
  (not consumed by renderer — silently dropped)
- Jumping straight to numeric substitution without showing the symbolic equation
- Variables in the equation not traced back to a defined input
- Standard cited without the specific clause or equation number
