---
name: metocean-statistics-data-requirements
description: 'Sub-skill of metocean-statistics: Data Requirements (+3).'
version: 1.0.0
category: data
type: reference
scripts_exempt: true
---

# Data Requirements (+3)

## Data Requirements


**Minimum Record Lengths:**
- Block maxima (annual): Minimum 10 years recommended
- Peak-over-threshold: Minimum 3 years with high-frequency data
- Monthly statistics: Minimum 3 years for seasonal patterns
- Directional analysis: Minimum 1 year continuous data

**Data Quality:**
- Check for gaps and document missing periods
- Validate against neighboring stations
- Remove spurious values (instrument errors)
- Ensure consistent time zone and conventions


## Distribution Fitting


**GEV Fitting:**
- Use maximum likelihood estimation (MLE)
- Check shape parameter range (-0.5 to 0.5 typical for ocean waves)
- Validate with QQ plots and probability plots
- Consider regional frequency analysis for short records

**Threshold Selection for POT:**
- Use mean residual life plot
- Test sensitivity to threshold choice
- Ensure independence of peaks (declustering)
- Typical threshold: 90th-95th percentile


## Uncertainty Quantification


**Always Report:**
- Confidence intervals for return levels
- Sample size and data availability
- Distribution fit quality metrics
- Assumptions and limitations

**Validation Methods:**
- Split-sample testing
- Cross-validation with nearby stations
- Comparison with historical extremes
- Sensitivity analysis


## Design Applications


**Conservative Approach:**
- Use upper confidence interval for design
- Consider climate change trends
- Account for measurement uncertainty
- Apply appropriate safety factors
