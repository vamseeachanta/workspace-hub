# 08 — Calculations

## Purpose

Execute the methodology step-by-step with clause references, numeric
substitutions, intermediate results, and hand-checks. This is the core
computational section — every step must be traceable and reproducible.

## Schema Fields

```yaml
calculations:
  - step: integer             # step number (e.g., 1, 2, 3)
    description: string       # what this step computes
    detail: string            # optional — formula, substitution, or narrative
    code_clause: string       # optional — code clause or equation reference
    intermediate_results:     # optional
      - name: string
        value: number
        unit: string          # optional
```

> **Renderer Mapping Note:** The methodology recommends `id` (string),
> `reference`, `formula`, `substitution`, `result{value,unit}`, and
> `hand_check` as separate fields. The renderer uses `step` (integer, not
> `id`), `code_clause` (not `reference`), and a single `detail` string
> (not separate `formula`/`substitution`). Combine symbolic formula and
> numeric substitution into `detail`. Hand-check results can go in
> `intermediate_results` or the next step's `detail`.

## Required Content

- Sequential calculation steps with `step` number and `description`
- Code clause references in `code_clause`
- Intermediate results shown (not just final answer)

## Quality Checklist

- [ ] Each step uses integer `step` field (not string `id`)
- [ ] Code clause references use `code_clause` (not `reference`)
- [ ] Symbolic form and substitution combined in `detail`
- [ ] Intermediate results are shown and have units
- [ ] Unit consistency is maintained throughout

## Example Snippet

```yaml
calculations:
  - step: 1
    description: "Corroded wall thickness"
    detail: "t_1 = t_nom - t_fab - t_corr = 20.6 - 1.0 - 3.0 = 16.6 mm"
    code_clause: "DNV-ST-F101 Sec. 5.4.2"
    intermediate_results:
      - name: "Corroded wall thickness"
        value: 16.6
        unit: "mm"

  - step: 2
    description: "Pressure containment resistance"
    detail: "p_b = (2 × t_1) / (D_o - t_1) × f_cb × (2/√3) = (2 × 16.6) / (323.9 - 16.6) × 450 × 1.1547 = 55.8 MPa"
    code_clause: "DNV-ST-F101 Eq. 5.8"
    intermediate_results:
      - name: "Geometry ratio 2t/(D-t)"
        value: 0.1081
```

## Common Mistakes

- Using `id` instead of `step` (renderer requires integer `step`)
- Using `reference` instead of `code_clause`
- Putting formula and substitution in separate `formula`/`substitution` fields
  (renderer uses single `detail` string)
- Including `result` or `hand_check` sub-objects (not consumed by renderer)
- Showing only final result without intermediate steps
