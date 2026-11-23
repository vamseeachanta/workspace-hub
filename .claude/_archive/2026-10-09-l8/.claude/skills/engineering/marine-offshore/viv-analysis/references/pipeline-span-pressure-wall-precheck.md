# Pipeline free-span VIV + pressure wall precheck

## Trigger

Use this reference when a user asks for pipeline VIV span analysis and also needs a quick wall-thickness pressure check. The VIV/free-span workflow should not treat pressure containment as the whole design, but pressure wall adequacy is a useful prerequisite before span/fatigue screening.

## Digitalmodel pressure-capacity basis

For quick pressure-only wall checks, prefer the `digitalmodel` pipe capacity implementation where available:

- `src/digitalmodel/structural/pipe_capacity/PipeSizing.py`
- `src/digitalmodel/structural/pipe_capacity/pipe_capacity.py`
- `src/digitalmodel/structural/pipe_capacity/common/PipeCapacity.py`

The observed modified Barlow branch logic was:

- Thin-wall branch: `t = P * D / (2 * S_allow)`
- Thick-wall branch: `t = P * D / (2 * S_allow + P)`
- Branch threshold: `D / t >= 30`

Where:

- `P` = design pressure, psi
- `D` = outside diameter, in
- `S_allow = SMYS * design_factor * weld_factor * temperature_factor`

## Example: 12 in OD, 3000 psi, Pe = 0, E = T = 1.0

Using an ASME-style design factor `F = 0.72`:

- X42: required pressure wall ≈ `0.567 in`
- X52: required pressure wall ≈ `0.462 in`
- X60: required pressure wall ≈ `0.403 in`
- X65: required pressure wall ≈ `0.385 in`
- X70: required pressure wall ≈ `0.357 in`
- X80: required pressure wall ≈ `0.313 in`

With corrosion allowance `0.125 in` and mill tolerance `12.5%`, nominal wall ≈ `(required + CA) / (1 - 0.125)`:

- X42: `0.791 in`
- X52: `0.671 in`
- X60: `0.603 in`
- X65: `0.582 in`
- X70: `0.551 in`
- X80: `0.500 in`

A `12 in x 0.75 in WT` X52 pipe passes this pressure-only check under those assumptions.

## Use in VIV span analysis

Before or alongside VIV free-span calculations, capture:

1. Wall-thickness basis: nominal WT, corrosion allowance, mill tolerance, SMYS/grade, code/design factor.
2. Effective section properties: use corroded/minimum WT for stress and fatigue unless the governing code says otherwise.
3. Span inputs: span length, seabed end fixity, submerged weight, axial force/tension, pressure effects, internal/external fluid densities.
4. Metocean inputs: near-bed current velocity profile, turbulence, directionality, marine growth.
5. Code basis: DNV-RP-F105 / DNV-ST-F101 or project-specific acceptance criteria.

## Guardrail

Do not present pressure containment as final pipeline wall adequacy. Final pipeline design also needs collapse/external pressure, propagation buckling, local buckling, installation, hydrotest, thermal, strain, on-bottom stability, and VIV/free-span fatigue checks.
