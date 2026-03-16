---
name: orcaflex-modeling-basic-analysis-configuration
description: 'Sub-skill of orcaflex-modeling: Basic Analysis Configuration (+1).'
version: 2.0.0
category: engineering
type: reference
scripts_exempt: true
---

# Basic Analysis Configuration (+1)

## Basic Analysis Configuration


```yaml
# configs/analysis_config.yml

basename: project_name

default:
  analysis:
    file_type: yml
    file_path_pattern: null  # Optional glob pattern


*See sub-skills for full details.*

## Universal Runner Configuration


```yaml
# For batch processing with universal runner

default:
  analysis:
    file_type: yml
    file_path_pattern: "*.yml"  # Process all YAML files

orcaflex:
  universal_runner:

*See sub-skills for full details.*
