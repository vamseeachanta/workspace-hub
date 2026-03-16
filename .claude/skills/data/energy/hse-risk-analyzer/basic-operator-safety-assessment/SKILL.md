---
name: hse-risk-analyzer-basic-operator-safety-assessment
description: 'Sub-skill of hse-risk-analyzer: Basic Operator Safety Assessment (+4).'
version: 1.0.0
category: data
type: reference
scripts_exempt: true
---

# Basic Operator Safety Assessment (+4)

## Basic Operator Safety Assessment


```python
from worldenergydata.hse import HSERiskAnalyzer

# Initialize analyzer
analyzer = HSERiskAnalyzer()
analyzer.load_incidents(Path("data/hse/incidents.csv"))

# Get operator safety profile
profile = analyzer.get_operator_profile("Chevron")

print(f"Operator: {profile.operator_name}")
print(f"Safety Score: {profile.safety_score}/100 ({profile.risk_category})")
print(f"Total Incidents: {profile.total_incidents}")
print(f"Fatalities: {profile.fatalities}")
print(f"Total Penalties: ${profile.total_penalties:,.2f}")
```


## Field Risk Analysis


```python
# Analyze specific field
field_risk = analyzer.analyze_field_risk("Thunder Horse", years=5)

print(f"Field: {field_risk['field_name']}")
print(f"Risk Category: {field_risk['risk_category']}")
print(f"Safety Score: {field_risk['field_safety_score']}")
print(f"Incidents by Type: {field_risk['incident_types']}")
```


## Risk-Adjusted NPV Calculation


```python
# Calculate risk-adjusted NPV
base_npv = 150_000_000  # $150M base NPV

risk_metrics = analyzer.calculate_risk_adjusted_npv(
    base_npv=base_npv,
    operator="Shell",
    include_penalty_exposure=True,
    include_insurance_adjustment=True
)

print(f"Base NPV: ${risk_metrics.base_npv:,.0f}")
print(f"Risk-Adjusted NPV: ${risk_metrics.risk_adjusted_npv:,.0f}")
print(f"NPV Impact: ${risk_metrics.npv_impact:,.0f} ({risk_metrics.npv_impact_percent:.1f}%)")
print(f"Risk Category: {risk_metrics.risk_category}")
```


## Operator Comparison


```python
# Compare multiple operators
operators = ["Shell", "Chevron", "BP", "ExxonMobil"]
comparison = analyzer.compare_operators(operators, years=5)

print(comparison[['operator', 'safety_score', 'risk_category', 'total_incidents']])
```


## Generate Reports


```python
from worldenergydata.hse import HSEReportGenerator

# Initialize report generator
reporter = HSEReportGenerator(analyzer)

# Generate operator report
report_path = reporter.generate_operator_report(
    operator="Shell",
    output_path=Path("reports/shell_hse_report.html"),
    years=5
)
print(f"Report generated: {report_path}")

# Generate comparison report
comparison_path = reporter.generate_comparison_report(
    operators=["Shell", "Chevron", "BP"],
    output_path=Path("reports/operator_comparison.html"),
    years=5
)
```
