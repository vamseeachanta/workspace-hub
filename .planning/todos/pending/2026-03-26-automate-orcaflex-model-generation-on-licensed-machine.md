---
created: "2026-03-26T23:18:43.089Z"
title: Automate OrcaFlex model generation on licensed machine
area: tooling
files: []
---

## Problem

Currently no automated pipeline for generating working OrcaFlex models. OrcaFlex requires a license server, so model generation must run on a licensed machine. The goal is to generate OrcaFlex models for all subsea structures currently catalogued in document intelligence — turning extracted structural data into runnable simulation models.

## Solution

Build an automation workflow that:
- Runs on a machine with OrcaFlex license access
- Reads structure definitions from document intelligence (all catalogued subsea structures)
- Generates valid OrcaFlex model files (.dat/.sim) for each structure
- Validates that generated models can be opened and run in OrcaFlex

TBD: specific licensed machine target, OrcaFlex Python API vs batch scripting approach, document intelligence query interface for structure data.
