---
name: orcawave-aqwa-benchmark-automated-validation-in-pipeline
description: 'Sub-skill of orcawave-aqwa-benchmark: Automated Validation in Pipeline.'
version: 1.0.0
category: engineering
type: reference
scripts_exempt: true
---

# Automated Validation in Pipeline

## Automated Validation in Pipeline


```yaml
# .github/workflows/diffraction-validation.yml

name: Diffraction Benchmark Validation

on:
  push:
    paths:
      - 'orcawave_results/**'
      - 'aqwa_results/**'

*See sub-skills for full details.*
