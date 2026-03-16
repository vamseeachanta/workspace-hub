---
name: yaml-workflow-executor-basic-structure
description: 'Sub-skill of yaml-workflow-executor: Basic Structure (+3).'
version: 1.1.0
category: development
type: reference
scripts_exempt: true
---

# Basic Structure (+3)

## Basic Structure


```yaml
# config/workflows/analysis.yaml

task: analyze_data

input:
  data_path: data/raw/measurements.csv
  schema_path: config/schemas/measurements.json  # optional

output:

*See sub-skills for full details.*

## Data Transformation Config


```yaml
task: transform_data

input:
  data_path: data/raw/source.csv

output:
  data_path: data/processed/transformed.csv

parameters:

*See sub-skills for full details.*

## Report Generation Config


```yaml
task: generate_report

input:
  data_path: data/processed/results.csv

output:
  report_path: reports/monthly_analysis.html

parameters:

*See sub-skills for full details.*

## Multi-Step Workflow


```yaml
task: pipeline

steps:
  - name: extract
    task: transform_data
    input:
      data_path: data/raw/source.csv
    output:
      data_path: data/staging/extracted.csv

*See sub-skills for full details.*
