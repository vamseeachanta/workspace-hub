# Tests Specification

This is the tests coverage details for the spec detailed in @specs/modules/analysis/decline-curve-analysis/spec.md

> Created: 2025-07-25
> Version: 1.0.0

## Test Coverage

### Unit Tests

**DeclineCurveAnalyzer Class**
- Test initialization with valid production data
- Test initialization with invalid/empty data
- Test parameter validation and constraints
- Test model fitting methods individually
- Test best model selection logic

**Decline Curve Models**
- Test exponential decline equation accuracy
- Test hyperbolic decline equation accuracy
- Test harmonic decline equation accuracy
- Test modified hyperbolic transition
- Test edge cases (b=0, b=1, D=0)

**Parameter Estimation**
- Test convergence with known synthetic data
- Test parameter bounds enforcement
- Test handling of poor initial guesses
- Test optimization failure scenarios
- Test uncertainty quantification

**Data Preprocessing**
- Test outlier detection algorithms
- Test missing data interpolation
- Test intervention period identification
- Test data normalization

### Integration Tests

**Full Decline Analysis Workflow**
- Test complete analysis from raw data to forecasts
- Test integration with ProductionAPI12Analysis
- Test configuration parameter handling
- Test output file generation

**Multi-Well Analysis**
- Test batch processing of multiple wells
- Test aggregation of field-level decline
- Test performance with large datasets

### Regression Tests

**Benchmark Validation**
- Test against petroleum engineering textbook examples
- Test against Excel-based decline curve tools
- Test reproducibility of results
- Test backward compatibility

### Performance Tests

**Optimization Performance**
- Test fitting speed for various data sizes
- Test memory usage with large datasets
- Test parallel processing efficiency

## Test Data Requirements

### Synthetic Test Cases
1. **Perfect Exponential Decline**
   - qi = 1000 bbl/day, D = 0.1/month
   - 24 months of data, no noise

2. **Hyperbolic Decline with Noise**
   - qi = 500 bbl/day, D = 0.15/month, b = 0.5
   - 36 months with 5% Gaussian noise

3. **Harmonic Decline with Outliers**
   - qi = 800 bbl/day, D = 0.08/month
   - 18 months with 3 outlier points

4. **Real Field Data**
   - Use anonymized BSEE production data
   - Include workover effects
   - Variable production history lengths

## Mocking Requirements

**External Data Sources**
- Mock BSEE API responses for testing
- Mock file I/O for configuration loading

**Visualization Libraries**
- Mock matplotlib/plotly for headless testing
- Capture plot data for validation

**Time-based Tests**
- Mock datetime for consistent test results
- Test forecast date calculations

## Expected Test Outcomes

### Accuracy Requirements
- Parameter estimation: ±5% of true values for synthetic data
- Model selection: >90% accuracy for clear decline types
- Forecasts: ±10% of actual for 6-month predictions

### Performance Benchmarks
- Single well analysis: <1 second
- 100 well batch: <30 seconds
- Memory usage: <500MB for 1000 wells

### Error Handling
- Graceful failure with insufficient data
- Clear error messages for invalid inputs
- Recovery from optimization failures

## Test Implementation Example

```python
def test_exponential_decline_fitting():
    """Test exponential decline curve fitting accuracy"""
    # Generate synthetic exponential decline data
    time = np.arange(0, 24, 1)  # 24 months
    qi = 1000  # initial rate
    D = 0.1   # decline rate
    production = qi * np.exp(-D * time)
    
    # Create analyzer and fit
    analyzer = DeclineCurveAnalyzer(production, time)
    params = analyzer.fit_exponential()
    
    # Assert parameters within tolerance
    assert abs(params['qi'] - qi) / qi < 0.05
    assert abs(params['D'] - D) / D < 0.05
    assert params['r_squared'] > 0.99
```