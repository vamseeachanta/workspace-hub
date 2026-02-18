# Prompt Documentation

## Original User Prompt

> Date: 2025-07-25
> Context: Core decline curve analysis engine requirements

"Implement a comprehensive decline curve analysis module for the worldenergydata repository that supports Arps' decline equations (exponential, hyperbolic, and harmonic). Include parameter estimation using nonlinear regression, outlier detection, and production forecasting capabilities. This should integrate with the existing ProductionAPI12Analysis class and work with BSEE production data."

## Refined Prompt for Reuse

To recreate or extend this spec, use the following comprehensive prompt:

```
Create a complete decline curve analysis (DCA) engine specification for worldenergydata:

CORE REQUIREMENTS:
1. Implement all three Arps decline models:
   - Exponential: q(t) = qi * exp(-Di*t)
   - Hyperbolic: q(t) = qi / (1 + b*Di*t)^(1/b)
   - Harmonic: q(t) = qi / (1 + Di*t)
2. Parameter estimation using scipy.optimize
3. Automated model selection based on statistical criteria
4. Production forecasting with EUR calculations
5. Data preprocessing and outlier detection
6. Integration with ProductionAPI12Analysis class

TECHNICAL SPECIFICATIONS:
- Module: src/worldenergydata/production/decline_curve_analysis.py
- Class: DeclineCurveAnalyzer
- Dependencies: numpy, pandas, scipy, matplotlib
- Performance: Process 10 years of monthly data in &lt;1 second
- Accuracy: R² &gt; 0.95 for typical decline curves

ADVANCED FEATURES:
- Initial parameter guess algorithms
- Parameter bounds and constraints
- Goodness-of-fit metrics (R², RMSE, AIC, BIC)
- Workover/intervention period detection
- Missing data interpolation
- Uncertainty quantification
- Diagnostic plots (log-rate, rate-cumulative)

SUCCESS CRITERIA:
- Matches results from commercial DCA software
- Handles edge cases gracefully
- Comprehensive test coverage (&gt;90%)
- Clear API documentation
```

## Context and Background

### Problem Statement
Production engineers need robust decline curve analysis tools to forecast well production, estimate reserves, and make economic decisions. Current open-source solutions lack comprehensive features and reliability.

### Solution Approach
Build a professional-grade DCA engine that implements industry-standard Arps equations with advanced parameter estimation, data preprocessing, and visualization capabilities.

### Technical Foundation
Based on SPE (Society of Petroleum Engineers) best practices and Arps' seminal 1945 paper on decline curve analysis.

## Key Technical Decisions

1. **Algorithm Choice**: scipy.optimize.curve_fit for parameter estimation
2. **Model Selection**: AIC/BIC criteria for automatic model selection
3. **Data Preprocessing**: IQR method for outlier detection
4. **Architecture**: Modular design with separate preprocessing, fitting, and forecasting components
5. **Integration**: Direct integration with ProductionAPI12Analysis for BSEE data

## Evolution Points

For future enhancements, consider:
- Additional decline models (Duong, stretched exponential, power law)
- Machine learning-based parameter estimation
- Probabilistic forecasting (P10/P50/P90)
- Type curve matching
- Multi-phase flow analysis
- Water cut trending
- Gas-oil ratio analysis
- Pressure-normalized analysis

## Related Specifications

- **dca-interactive-dashboard**: Web interface for this engine
- **production-api12-analysis**: Data source integration
- **well-production-dashboard**: Comprehensive analytics platform

## Implementation Notes

### Mathematical Foundations

#### Arps Equations
1. **Exponential** (b = 0):
   - Rate: $q(t) = q_i e^{-D_i t}$
   - Cumulative: $Q(t) = \frac{q_i - q(t)}{D_i}$

2. **Hyperbolic** (0 &lt; b &lt; 1):
   - Rate: $q(t) = \frac{q_i}{(1 + bD_i t)^{1/b}}$
   - Cumulative: $Q(t) = \frac{q_i^b}{D_i(1-b)}[q_i^{1-b} - q(t)^{1-b}]$

3. **Harmonic** (b = 1):
   - Rate: $q(t) = \frac{q_i}{1 + D_i t}$
   - Cumulative: $Q(t) = \frac{q_i}{D_i} \ln\left(\frac{q_i}{q(t)}\right)$

### Critical Success Factors
1. **Accuracy**: Results must match commercial software
2. **Robustness**: Handle poor quality data gracefully
3. **Performance**: Sub-second processing for typical datasets
4. **Usability**: Clear API with sensible defaults

### Common Pitfalls to Avoid
- Poor initial parameter guesses causing non-convergence
- Not handling production anomalies (shut-ins, workovers)
- Overfitting to noisy data
- Ignoring physical constraints on parameters
- Poor handling of zero or negative production values

## Prompt Engineering Tips

When extending this spec:
1. Specify exact mathematical formulations
2. Define parameter constraints and bounds
3. Include data quality requirements
4. Specify integration points clearly
5. Define test scenarios with expected outcomes
6. Include performance benchmarks

## Curated Reuse Prompt

```
/create-spec "decline-curve-analysis-v2" analysis enhanced

Extend the existing DCA engine with:
- Duong decline model for unconventional wells
- Stretched exponential decline model
- Power law exponential decline model
- Machine learning parameter estimation using neural networks
- Probabilistic forecasting with Monte Carlo simulation
- Type curve generation and matching
- Multi-phase (oil, gas, water) analysis
- Pressure and temperature corrections
- Economic limit calculations with variable costs
- Automated report generation

Maintain backward compatibility with existing Arps models.
Target 2x performance improvement using parallel processing.
Include comprehensive validation against SPE test cases.
```

## Testing Strategy

### Unit Tests
- Each decline model with known solutions
- Parameter estimation with synthetic data
- Edge cases (zero production, missing data)

### Integration Tests
- Full workflow with BSEE data
- Model selection logic
- Forecast accuracy validation

### Performance Tests
- Large dataset processing (&gt;10 years monthly)
- Parallel processing efficiency
- Memory usage optimization

### Validation Tests
- Comparison with commercial software
- SPE benchmark problems
- Real field data with known EUR