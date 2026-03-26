---
created: "2026-03-26T23:25:00.000Z"
title: Automate OrcaWave vessel hull analysis on licensed machine
area: tooling
files: []
---

## Problem

No automated pipeline for generating OrcaWave vessel hull analysis models. Same licensed-machine constraint as OrcaFlex. Simpler scope than the OrcaFlex work — serves as a proving ground for the LLM-driven model generation approach.

## Scope

**Focus:** vessel hull analysis using OrcaWave (hydrodynamic diffraction analysis).

**Structures:** vessel hulls for installation vessels (service vessels and full-size installation vessels).

## Solution

Same YAML-based input approach as OrcaFlex — OrcaWave also uses YAML input files:
1. Gather and review existing OrcaWave YAML model files
2. Map hull structures to primary key files (same pattern as OrcaFlex)
3. Prepare LLM input files for hull definitions
4. LLM-driven generation of OrcaWave YAML input files — 100% semantic match against benchmarks
5. Validate files load and run in OrcaWave without errors

## Priority

**Tackle first** — simpler than OrcaFlex, proves the LLM-driven generation approach before scaling to the full OrcaFlex structure set.
