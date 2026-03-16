---
name: orcaflex-modeling-project-setup
description: 'Sub-skill of orcaflex-modeling: Project Setup (+2).'
version: 2.0.0
category: engineering
type: reference
scripts_exempt: true
---

# Project Setup (+2)

## Project Setup


1. Always use the standardized folder structure
2. Keep original .dat files in `.dat/original/`
3. Use descriptive YAML configuration names
4. Version control configuration files, not .sim files


## Batch Processing


1. Start with mock mode to validate configuration
2. Use pattern matching for related analyses
3. Monitor logs for failures
4. Archive results with timestamps


## Performance


1. Use parallel processing for independent runs
2. Limit workers based on available licenses
3. Run compute-intensive jobs overnight
4. Clean up intermediate files after processing
