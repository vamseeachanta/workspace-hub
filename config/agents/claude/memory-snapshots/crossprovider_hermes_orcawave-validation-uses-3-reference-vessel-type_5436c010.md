---
name: crossprovider hermes orcawave-validation-uses-3-reference-vessel-type
description: OrcaWave validation uses 3 reference vessel types with documented geometry
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [orcawave, hydrodynamics, reference-data, validation-suite]
---

OrcaWave spec.yml files define 3 benchmark vessels: Barge (80m×40m×10m, 16.4M kg), Ship (≈220m, 9M kg), Spar (D=25m, T=110m, 55M kg). Plus 10 WAMIT validation test cases (cylinders, ellipsoids, pyramids, moonpools). Developers building OrcaWave models should use these as baselines; they live in docs/domains/orcawave/ with full spec definitions including water depth, density, symmetry.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
