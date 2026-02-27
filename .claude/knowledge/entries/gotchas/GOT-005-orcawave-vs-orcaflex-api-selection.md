---
id: GOT-005
type: gotcha
title: "OrcaWave and OrcaFlex share OrcFxAPI but require different API classes"
category: data
tags: [orcawave, orcaflex, orcfxapi, api-selection]
repos: [workspace-hub, digitalmodel]
confidence: 0.95
created: "2026-02-26"
last_validated: "2026-02-26"
source_type: manual
related: [GOT-002]
status: active
access_count: 0
---

# OrcaWave vs OrcaFlex API Selection

## Symptom

Code imports `OrcFxAPI` and then uses `Model()` for `.owd/.owr` workflows or expects `SaveModelView` in OrcaWave runs.

## Reality

Both products use `OrcFxAPI`, but not the same class:

- OrcaWave: `OrcFxAPI.Diffraction` for frequency-domain diffraction/radiation (`.yml`, `.owd`, `.owr`)
- OrcaFlex: `OrcFxAPI.Model` for time-domain structural dynamics (`.dat`, `.sim`)

`SaveModelView` is available in OrcaFlex `Model`, not in OrcaWave `Diffraction`.

## Fix

Select API class by analysis domain before implementation:

- Use `Diffraction` for RAOs, added mass/damping, QTF and OrcaWave restart workflows.
- Use `Model` for time-series dynamics, line/riser/mooring simulation, and model-view exports.

## Source

Validated during WRK-322 restart verification on 2026-02-26 via skills/docs checks in workspace-hub.
