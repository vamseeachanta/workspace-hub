---
name: data-validation-reporter-1-data-validation
description: 'Sub-skill of data-validation-reporter: 1. Data Validation (+3).'
version: 1.0.0
category: coordination
type: reference
scripts_exempt: true
---

# 1. Data Validation (+3)

## 1. Data Validation


```python
validator = DataValidator(config_path="config/validation.yaml")
results = validator.validate_dataframe(
    df=data,
    required_fields=["id", "value", "timestamp"],
    unique_field="id"
)
```

**Validation checks**:

*See sub-skills for full details.*

## 2. Quality Scoring Algorithm


**Score calculation** (0-100 scale):
- Base score: 100
- Missing required fields: -20
- High missing data (>50%): -30
- Moderate missing data (>20%): -15
- Duplicate records: -2 per duplicate (max -20)
- Type issues: -5 per issue (max -15)

**Status thresholds**:
- ✅ PASS: score ≥ 60
- ❌ FAIL: score < 60

## 3. Interactive Reporting


**4-Panel Plotly Dashboard**:
1. **Quality Score Gauge** - Color-coded indicator (green/yellow/red)
2. **Missing Data Chart** - Bar chart showing missing % per column
3. **Type Issues Chart** - Bar chart of validation errors
4. **Summary Table** - Key metrics overview

**Features**:
- Responsive design
- Interactive hover tooltips
- Zoom and pan controls
- Export to PNG/SVG
- CDN-based Plotly (no local dependencies)

## 4. YAML Configuration


```yaml
# config/validation.yaml
validation:
  required_fields:
    - id
    - timestamp
    - value

  unique_fields:
    - id

*See sub-skills for full details.*
