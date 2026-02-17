# Technical Specification

This is the technical specification for the spec detailed in @specs/modules/analysis/decline-curve-analysis/spec.md

> Created: 2025-07-25
> Version: 1.0.0

## Technical Requirements

### Decline Curve Models
- **Arps' Exponential Decline**: q(t) = qi * e^(-D*t)
- **Arps' Hyperbolic Decline**: q(t) = qi / (1 + b*D*t)^(1/b)
- **Arps' Harmonic Decline**: q(t) = qi / (1 + D*t) [special case where b=1]
- **Modified Hyperbolic**: Transition from hyperbolic to exponential at terminal decline rate

### Parameter Definitions
- **qi**: Initial production rate (bbl/day or mcf/day)
- **D**: Nominal decline rate (1/time)
- **b**: Hyperbolic exponent (0 ≤ b ≤ 1)
- **Dmin**: Terminal decline rate for modified hyperbolic

### Data Requirements
- Minimum 6 months of production history
- Monthly or daily production rates
- Handling of zero production periods
- Outlier detection and removal capabilities

### Calculation Methods
- Non-linear least squares for parameter estimation
- Rate-time, rate-cumulative, and log-rate vs time analysis
- Diagnostic plots for model selection
- Statistical goodness-of-fit metrics (R², RMSE, AIC)

## Approach Options

**Option A: scipy.optimize Implementation** (Selected)
- Pros: Robust optimization algorithms, well-tested, good performance
- Cons: Requires careful initial parameter estimation

**Option B: Custom Gradient Descent**
- Pros: Full control over optimization
- Cons: More development effort, potential numerical stability issues

**Option C: sklearn Machine Learning**
- Pros: Modern approach, handles non-linearity well
- Cons: Overkill for deterministic models, less interpretable

**Rationale:** scipy.optimize provides proven optimization algorithms (curve_fit, minimize) ideal for non-linear parameter estimation in decline curve analysis. This approach balances accuracy, performance, and implementation complexity.

## Implementation Architecture

### Core Components

1. **DeclineCurveAnalyzer Class**
   ```python
   class DeclineCurveAnalyzer:
       def __init__(self, production_data):
           self.data = production_data
           self.models = {}
           
       def fit_exponential(self):
           # Implement exponential decline fitting
           
       def fit_hyperbolic(self):
           # Implement hyperbolic decline fitting
           
       def fit_harmonic(self):
           # Implement harmonic decline fitting
           
       def select_best_model(self):
           # Model selection based on AIC/BIC
   ```

2. **Data Preprocessing Module**
   - Remove outliers using IQR or z-score methods
   - Handle missing data interpolation
   - Identify and exclude intervention periods
   - Normalize time series data

3. **Parameter Estimation**
   - Initial parameter guess algorithms
   - Bounded optimization to ensure physical constraints
   - Multiple starting points to avoid local minima
   - Uncertainty quantification using parameter covariance

4. **Forecasting Engine**
   - Forward production projection
   - Cumulative production calculation
   - EUR estimation with cutoff rates
   - Monte Carlo simulation for uncertainty

## Integration Points

- **Input**: Uses api12_df from ProductionAPI12Analysis
- **Configuration**: Reads from cfg dict for analysis parameters
- **Output**: Returns decline parameters, forecasts, and visualizations
- **Storage**: Saves results to CSV/Excel in results folder

## Performance Considerations

- Vectorized calculations using numpy
- Caching of fitted parameters
- Parallel processing for multiple wells
- Memory-efficient handling of large datasets

## External Dependencies

- **scipy**: For optimization algorithms (curve_fit, minimize)
- **numpy**: For numerical calculations
- **pandas**: For data manipulation
- **matplotlib/plotly**: For visualization
- **statsmodels**: For statistical metrics (optional)