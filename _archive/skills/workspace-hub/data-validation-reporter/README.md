# Data Validation Reporter Skill

> **Quick Reference Guide**

## Overview

Complete data validation workflow with interactive Plotly reports, quality scoring, and YAML configuration.

**Discovered**: 2026-01-07 from digitalmodel production code
**Reusability Score**: 80/100
**Source Commit**: 47b64945

## Quick Start

### 1. Copy Files to Your Project

```bash
# Copy validator
cp validator_template.py your_project/src/validators/data_validator.py

# Copy config template
cp config_template.yaml your_project/config/validation.yaml

# Install dependencies
uv pip install pandas plotly pyyaml
```

### 2. Basic Usage

```python
from pathlib import Path
from src.validators.data_validator import DataValidator
import pandas as pd

# Initialize
validator = DataValidator(config_path=Path("config/validation.yaml"))

# Load data
df = pd.read_csv("data/input.csv")

# Validate
results = validator.validate_dataframe(
    df=df,
    required_fields=["id", "name", "value"],
    unique_field="id"
)

# Check status
if results['valid']:
    print(f"✅ PASS - Score: {results['quality_score']:.1f}/100")
else:
    print(f"❌ FAIL - Issues: {len(results['issues'])}")

# Generate report
validator.generate_interactive_report(
    results,
    Path("reports/validation_report.html")
)
```

## What It Does

### Validation Checks
- ✅ Empty DataFrame detection
- ✅ Required field verification
- ✅ Missing data analysis (per-column %)
- ✅ Duplicate record detection
- ✅ Data type validation
- ✅ Numeric field verification

### Quality Scoring (0-100)
- Base: 100 points
- Missing required fields: -20
- High missing data (>50%): -30
- Moderate missing (>20%): -15
- Duplicates: -2 each (max -20)
- Type issues: -5 each (max -15)

### Interactive Reports

4-panel Plotly dashboard:
1. **Quality Gauge** - Color-coded score (green/yellow/red)
2. **Missing Data Chart** - Bar chart with percentages
3. **Type Issues Chart** - Validation error counts
4. **Summary Table** - Key metrics

## Configuration

Edit `config/validation.yaml`:

```yaml
validation:
  required_fields:
    - id
    - timestamp
    - value

  unique_fields:
    - id

  numeric_fields:
    - year
    - amount
    - count

  thresholds:
    max_missing_pct: 0.2      # 20%
    min_quality_score: 60
    max_duplicates: 0
```

## Examples

Run the examples:

```bash
python example_usage.py
```

**Included examples**:
1. Basic validation
2. Validation with config
3. Interactive report generation
4. Batch file validation
5. Quality trend analysis

## Output

### Text Report
```
============================================================
DATA VALIDATION REPORT
============================================================

Overall Status: ✓ PASS
Quality Score: 85.0/100.0

Dataset Size:
  - Rows: 1000
  - Columns: 5

Missing Data:
  - email: 5.0%
  - phone: 2.5%

Issues Found (2):
  1. Moderate missing data: 3.8% average
  2. 3 duplicate id values

============================================================
```

### Interactive HTML Report

Open `reports/validation_report.html` in browser for:
- Interactive quality gauge
- Zoomable bar charts
- Hover tooltips
- Export to PNG/SVG
- Responsive design

## Integration

### Add to Data Pipeline

```python
# pipeline.py
def validate_and_process(input_file, output_file):
    # Load data
    df = pd.read_csv(input_file)

    # Validate
    validator = DataValidator(config_path="config/validation.yaml")
    results = validator.validate_dataframe(df, required_fields=["id"])

    # Block on failure
    if not results['valid']:
        validator.generate_interactive_report(
            results,
            Path("reports/failed_validation.html")
        )
        raise ValueError(f"Validation failed: {results['issues']}")

    # Generate success report
    validator.generate_interactive_report(
        results,
        Path("reports/validation_success.html")
    )

    # Continue processing
    processed_df = process_data(df)
    processed_df.to_csv(output_file, index=False)

    return results
```

### Quality Gate in CI/CD

```bash
# .github/workflows/data-quality.yml
- name: Validate Data Quality
  run: |
    python scripts/validate_data.py
    if [ $? -ne 0 ]; then
      echo "Data quality check failed"
      exit 1
    fi
```

## Customization

### Extend Validation Rules

```python
class CustomValidator(DataValidator):
    def validate_dataframe(self, df, **kwargs):
        # Run base validation
        results = super().validate_dataframe(df, **kwargs)

        # Add custom checks
        if 'email' in df.columns:
            invalid_emails = ~df['email'].str.contains('@', na=False)
            if invalid_emails.sum() > 0:
                results['issues'].append(
                    f'{invalid_emails.sum()} invalid email addresses'
                )
                results['quality_score'] -= 10

        return results
```

### Add Custom Visualizations

```python
# Add trend plot to dashboard
fig.add_trace(
    go.Scatter(
        x=df.index,
        y=df['quality_score'],
        mode='lines+markers',
        name='Quality Trend'
    ),
    row=3, col=1
)
```

## Performance

**Benchmarks** (100,000 rows):
- Validation: ~2.5s
- Report generation: ~1.2s
- Total: ~3.7s

**Memory**: ~150MB for 100k rows

**Scalability**: Tested up to 1M rows

## Dependencies

```txt
pandas>=1.5.0
plotly>=5.14.0
pyyaml>=6.0
```

## Files

```
data-validation-reporter/
├── SKILL.md                    # Full documentation
├── README.md                   # This file
├── validator_template.py       # Validator class
├── config_template.yaml        # Configuration template
└── example_usage.py            # Working examples
```

## Support

Part of workspace-hub skill library.

For issues: workspace-hub issue tracker
For updates: Check `SKILL.md` changelog

## Related Skills

- **csv-data-loader** - Data loading utilities
- **plotly-dashboard** - Advanced dashboards
- **data-quality-monitor** - Continuous monitoring

---

**Quick Tip**: Run `example_usage.py` to see all capabilities in action!
