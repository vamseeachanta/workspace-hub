# Stage 5: Post-Processing and Validation

> Maps to calculation-methodology Phase 5 (sections 10-13)

## Entry

- Converged solution from Stage 4

## Result Extraction

### Force Coefficients
```bash
# If forceCoeffs function object was configured:
cat postProcessing/forces/0/coefficient.dat | tail -1
# Columns: Time Cd Cl CmPitch CmRoll CmYaw Cs
```

### Probe Data
```bash
cat postProcessing/probes/0/p    # pressure at probe points
cat postProcessing/probes/0/U    # velocity at probe points
```

### y+ Check
```bash
source /usr/lib/openfoam/openfoam2312/etc/bashrc 2>/dev/null || true
<solver> -postProcess -func yPlus -latestTime
cat postProcessing/yPlus/0/yPlus.dat
```

### Field Export
```bash
foamToVTK -latestTime    # → VTK/ directory for ParaView/pyvista
```

## Validation Methods

| Method | When to Use | How |
|--------|-------------|-----|
| Benchmark comparison | Always (first analysis of a type) | Compare with tutorial results or published data |
| Analytical comparison | When closed-form exists | e.g., Cd for cylinder at known Re |
| Mesh independence | Critical results | Run 3 mesh levels, check <2% variation |
| Grid Convergence Index | Formal reports | GCI per Roache (1997) |
| Code comparison | High-consequence analyses | Compare with AQWA/Morison/other tool |

## Sensitivity Analysis

For calculation-methodology Phase 5 §10 (Sensitivity), sweep the top 3 uncertain parameters:

```yaml
sensitivity:
  parameters:
    - {name: "mesh_refinement", values: [0.5x, 1x, 2x], result_field: "Cd"}
    - {name: "inlet_velocity", values: [0.8, 1.0, 1.2], result_field: "Fd"}
    - {name: "turbulence_model", values: [kEpsilon, kOmegaSST], result_field: "Cd"}
```

## Validation Verdict

```yaml
# Written to <case>/validation-verdict.yaml
validation:
  mesh_independence:
    status: pass | fail
    coarse: {cells: 25000, Cd: 1.05}
    medium: {cells: 50000, Cd: 1.02}
    fine: {cells: 100000, Cd: 1.01}
    variation: "1%"
  benchmark:
    status: pass | fail
    reference: "Cd = 1.0 for cylinder at Re=100 (Tritton 1959)"
    computed: 1.02
    error: "2%"
  engineering_check:
    status: pass | fail
    limit: "Cd < 2.0 per DNV-RP-C205"
    computed: 1.02
```

## Exit Gate

- [ ] All required quantities extracted (forces, pressures, coefficients)
- [ ] y+ values in acceptable range for chosen wall treatment
- [ ] At least one validation method applied
- [ ] Sensitivity analysis on ≥2 parameters (if not benchmark-only)
- [ ] Validation verdict written to `<case>/validation-verdict.yaml`
