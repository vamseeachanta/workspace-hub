# Stage 2: Case Setup

> Maps to calculation-methodology Phase 2-3 (sections 03-07)

## Entry

- Analysis YAML from Stage 1

## Actions

1. **Create case directory** from analysis YAML
2. **Generate system dicts** — controlDict, fvSchemes, fvSolution (refer to `openfoam` skill §1)
3. **Set boundary conditions** — match flow type to BC patterns
4. **Configure turbulence** — select model, set initial field values
5. **Set function objects** — forceCoeffs, probes, yPlus as needed

## Solver Configuration by Analysis Type

| Analysis Type | Solver | Algorithm | Turbulence | Key Dicts |
|--------------|--------|-----------|------------|-----------|
| steady_rans | simpleFoam | SIMPLE | kOmegaSST | controlDict, fvSchemes (steady), fvSolution (SIMPLE) |
| transient_rans | pimpleFoam | PIMPLE | kOmegaSST | + adjustTimeStep, maxCo |
| vof_multiphase | interFoam | PIMPLE | laminar or kOmegaSST | + setFieldsDict, alpha.water, p_rgh |
| laminar | icoFoam | PISO | none | minimal setup |

## Function Objects (auto-configured)

```cpp
functions
{
    forces
    {
        type            forceCoeffs;
        libs            (forces);
        writeControl    timeStep;
        writeInterval   1;
        patches         (<structure_patches>);
        rho             rhoInf;
        rhoInf          1025;       // seawater
        CofR            (0 0 0);
        liftDir         (0 0 1);
        dragDir         (1 0 0);
        pitchAxis       (0 1 0);
        magUInf         <from_analysis_yaml>;
        lRef            <from_geometry>;
        Aref            <from_geometry>;
    }
}
```

## Exit Gate

- [ ] Case directory created with 0/, constant/, system/
- [ ] All dict files valid (no missing fields, correct dimensions)
- [ ] Boundary conditions consistent with mesh patches
- [ ] Function objects configured for required outputs
