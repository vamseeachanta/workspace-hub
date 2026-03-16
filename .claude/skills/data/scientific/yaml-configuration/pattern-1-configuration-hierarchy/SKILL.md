---
name: yaml-configuration-pattern-1-configuration-hierarchy
description: 'Sub-skill of yaml-configuration: Pattern 1: Configuration Hierarchy
  (+2).'
version: 1.0.0
category: data
type: reference
scripts_exempt: true
---

# Pattern 1: Configuration Hierarchy (+2)

## Pattern 1: Configuration Hierarchy


```yaml
# Global defaults
defaults: &defaults
  version: 1.0
  units: "SI"
  precision: 6

# Project-specific configs inherit defaults
project_a:
  <<: *defaults

*See sub-skills for full details.*

## Pattern 2: Environment-Specific Configs


```yaml
# development.yaml
database:
  host: "localhost"
  port: 5432

# production.yaml
database:
  host: "prod-server.example.com"
  port: 5432
```

## Pattern 3: Parameterized Templates


```yaml
# template.yaml
analysis:
  name: "${PROJECT_NAME}"
  water_depth: ${WATER_DEPTH}
  wave_height: ${HS}
```
