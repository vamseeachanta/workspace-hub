# Tests Specification

This is the tests coverage details for the spec detailed in @specs/modules/analysis/npv-calculation-accuracy/spec.md

> Created: 2025-07-25
> Version: 1.0.0

## Test Coverage

### Unit Tests

**NPV Calculation Engine**
- Test custom NPV function with known cash flow sequences against Excel benchmarks
- Test discount rate application accuracy (annual vs monthly conversion)
- Test period timing handling (Period 0 for CAPEX, Period 1+ for operations)
- Test edge cases (zero cash flows, negative cash flows, single period)
- Test input validation (invalid discount rates, malformed cash flow arrays)

**Cash Flow Construction**
- Test revenue calculation from production data and oil prices
- Test OPEX calculation from production volumes and unit costs
- Test CAPEX integration timing and amount
- Test cash flow aggregation (monthly to annual if needed)

**Data Input Processing**
- Test oil price extraction from Excel files
- Test production data alignment with Excel analysis periods
- Test configuration parameter loading and validation

### Integration Tests

**Excel Alignment Validation**
- Test NPV calculation against known Excel results for Jack/St. Malo field data
- Test with multiple discount rates (8%, 10%, 12%) to verify rate application
- Test with different CAPEX scenarios ($1.46B Excel-aligned vs $5.2B config)
- Test with varying oil price datasets (BRENT vs WTI)

**End-to-End Workflow**
- Test complete NPV analysis workflow from YAML config to final results
- Test multiple field configurations to ensure consistency
- Test error handling when Excel reference data is unavailable

### Performance Tests

**Calculation Speed**
- Benchmark NPV calculation performance vs previous numpy-financial implementation
- Test with large datasets (multiple years of monthly data)

### Mocking Requirements

**Excel File Access**
- Mock Excel file reading for unit tests with known cash flow data
- Mock oil price data extraction with controlled price scenarios
- Mock production data with synthetic datasets for isolated testing

**File System Operations**
- Mock result file writing for testing without creating actual output files
- Mock configuration file loading for isolated testing scenarios