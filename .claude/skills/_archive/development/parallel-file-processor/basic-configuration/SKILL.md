---
name: parallel-file-processor-basic-configuration
description: 'Sub-skill of parallel-file-processor: Basic Configuration.'
version: 1.1.0
category: development
type: reference
scripts_exempt: true
---

# Basic Configuration

## Basic Configuration


```yaml
# config/parallel_processing.yaml

scan:
  directory: "data/raw/"
  recursive: true

  include_patterns:
    - "*.csv"
    - "*.xlsx"

*See sub-skills for full details.*
