---
created: "2026-03-26T23:18:43.089Z"
title: Automate OrcaFlex model generation on licensed machine
area: tooling
files: []
---

## Problem

No automated pipeline for generating working OrcaFlex models from existing analysis data. OrcaFlex requires a license server, so generation must run on a licensed machine. We already have OrcaFlex analysis for various structures — the goal is to automate producing input files via LLMs, generate lookup curves from parametric analysis, and deliver these to clients.

## Scope

**Structures:** risers, pipelines, rigid jumpers, and others catalogued in document intelligence.

**Vessels:** installation vessels (service vessels and full-size installation vessels).

**Deliverable:** parametric analysis results and lookup curves for clients.

## Solution

1. **Gather and review** all existing OrcaFlex model files (YAML-based)
2. **Map structures to primary keys** — divide OrcaFlex YAML files into individual primary key files, group/map various structures to their corresponding primary key files
3. **Prepare LLM input files** — structured inputs that LLMs can consume to produce OrcaFlex input artifact files directly
4. **LLM-driven generation** — from LLM input file to OrcaFlex input file, must be a 100% semantic match (one-to-one) against benchmark examples
5. **Validation** — generated files must load into OrcaFlex without errors, output must match benchmarks exactly
6. **Parametric analysis** — run parametric sweeps and produce lookup curves

## Benchmarking

Benchmark examples exist from manual programming. The pipeline must reproduce these exactly — 100% semantic match on input files, matching output.

## Priority

Tackle **after** the OrcaWave vessel hull analysis todo (simpler scope, proves the approach first).
