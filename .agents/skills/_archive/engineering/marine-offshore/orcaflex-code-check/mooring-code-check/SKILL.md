---
name: orcaflex-code-check-mooring-code-check
description: 'Sub-skill of orcaflex-code-check: Mooring Code Check (+1).'
version: 1.0.0
category: engineering
type: reference
scripts_exempt: true
---

# Mooring Code Check (+1)

## Mooring Code Check


```yaml
# configs/mooring_code_check.yml

code_check:
  standard: "API_RP_2SK"
  edition: "2015"

  mooring:
    lines:
      - name: "Leg_1"
        line_type: "Chain_R4_84mm"
        mbl: 8500.0  # kN - Minimum Breaking Load
      - name: "Leg_2"
        line_type: "Chain_R4_84mm"
        mbl: 8500.0

    safety_factors:
      intact:
        static: 1.67    # API RP 2SK Table 2
        dynamic: 1.82
      damaged:
        static: 1.25
        dynamic: 1.43

    load_conditions:
      - name: "100-year intact"
        condition: "intact"
        load_type: "dynamic"
      - name: "100-year damaged"
        condition: "damaged"
        load_type: "dynamic"

  output:
    report_path: "reports/code_check/"
    format: "html"
```


## Riser Code Check


```yaml
# configs/riser_code_check.yml

code_check:
  standard: "DNV_OS_F201"
  edition: "2021"

  riser:
    name: "SCR"
    material:
      grade: "X65"
      smys: 448.0   # MPa
      smts: 531.0   # MPa
      young_modulus: 207000.0  # MPa

    geometry:
      od: 0.2731    # m
      wt: 0.0159    # m (wall thickness)

    design_factors:
      gamma_SC: 1.04   # Safety class factor
      gamma_m: 1.15    # Material factor
      gamma_F: 1.10    # Load factor
      alpha_U: 1.00    # Material strength factor

    checks:
      - "hoop_stress"
      - "longitudinal_stress"
      - "equivalent_stress"
      - "collapse"
      - "propagation_buckling"

  output:
    report_path: "reports/riser_code_check/"
```
