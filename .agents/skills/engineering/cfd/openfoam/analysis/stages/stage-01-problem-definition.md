# Stage 1: Problem Definition

> Maps to calculation-methodology Phase 1 (sections 01-02)

## Entry

- User describes the CFD analysis needed (geometry, flow, what to compute)
- Or: user provides an analysis template YAML

## Actions

1. **Define objective** — what quantity is being computed (drag force, wave loading, pressure distribution)?
2. **Bound the scope** — steady vs transient, 2D vs 3D, turbulence model, single vs multiphase
3. **Set acceptance criteria** — target convergence, validation benchmarks, engineering limits
4. **Select template** — match to closest `references/analysis-templates/*.yaml`
5. **Create analysis YAML** — populate metadata, inputs, methodology sections

## Analysis YAML Structure

```yaml
analysis:
  title: "descriptive title"
  objective: "what is being proved"
  type: steady_rans | transient_rans | vof_multiphase | laminar
  
geometry:
  source: blockMesh | stl | step | gmsh
  description: "what the geometry represents"
  # type-specific fields (dimensions, file paths, etc.)

flow:
  fluid: water | air | custom
  velocity: {value: 1.0, unit: m/s}
  # type-specific fields (Re, wave params, etc.)

mesh:
  method: blockMesh | snappyHexMesh | gmsh
  target_cells: 50000
  # refinement zones, boundary layers

solver:
  application: simpleFoam | interFoam | pimpleFoam | icoFoam
  end_time: 2000
  write_interval: 100

acceptance:
  convergence: {p: 1e-4, U: 1e-4}
  validation: "compare Cd with Morison / published data"
```

## Exit Gate

- [ ] Analysis YAML created with all required sections
- [ ] Objective is specific (not "run CFD" — state what is being computed)
- [ ] Acceptance criteria defined (convergence targets + engineering validation)
- [ ] Template selected or custom config justified
