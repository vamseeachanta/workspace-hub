---
name: well-production-dashboard
description: Create interactive well production dashboards with real-time monitoring, verification integration, economic metrics, and multi-format exports. Use for well performance analysis, field aggregation, production forecasting, and API-driven dashboards.
capabilities: []
requires: []
see_also: []
---

# Well Production Dashboard Skill

Interactive dashboard system for well production visualization, analysis, and monitoring with Flask REST API, verification integration, and comprehensive export capabilities.

## When to Use

- Interactive well production dashboards
- Real-time well monitoring and alerts
- Production decline analysis and forecasting
- Field-level aggregation and comparison
- Well economic metrics (NPV, decline rates, ROI)
- Data quality verification integration
- Multi-format exports (PDF, Excel, JSON)
- REST API for dashboard data access

## Prerequisites

- Python environment with `worldenergydata` package installed
- BSEE well production data
- Flask (included in dependencies) for API features

## Dashboard Types

### 1. Basic Well Dashboard

Create interactive dashboard for well analysis.

```yaml
well_production_dashboard:
  basic:
    flag: true
    title: "Well Production Dashboard"
    wells:
      - "API_12345"
      - "API_67890"
    date_range:
      start: "2020-01-01"
      end: "2024-12-31"
    output:
      html_file: "reports/well_dashboard.html"
```

### 2. Field Aggregation Dashboard

Aggregate wells to field level with statistics.

```yaml
well_production_dashboard:
  field_aggregation:
    flag: true
    field_name: "ANCHOR"
    aggregation:
      - total_production
      - mean_production
      - std_deviation
      - well_count
    comparison_fields:
      - "JULIA"
      - "JACK"
    output:
      field_report: "reports/field_comparison.html"
```

### 3. Real-Time Monitoring Dashboard

Enable real-time updates with WebSocket.

```yaml
well_production_dashboard:
  real_time:
    flag: true
    enable_real_time: true
    update_interval_ms: 60000
    websocket_port: 8765
    api_port: 5000
    alerts:
      production_threshold: 1000  # BBL/day
      decline_alert: 0.15  # 15% decline triggers alert
    output:
      dashboard_port: 5000
```

### 4. Economic Analysis Dashboard

Dashboard with financial metrics.

```yaml
well_production_dashboard:
  economics:
    flag: true
    wells:
      - "API_12345"
    metrics:
      - npv
      - decline_rate
      - roi
      - payback_period
    economic_params:
      discount_rate: 0.10
      oil_price: 75.0  # $/BBL
      opex_per_bbl: 12.0
    forecast_periods: 24
    output:
      economics_report: "reports/well_economics.html"
```

## Python API

### Dashboard Initialization

```python
from worldenergydata.well_production_dashboard import (
    WellProductionDashboard,
    WellDashboardConfig,
    WellMetrics,
    FieldAggregator,
    DashboardAPI,
    DashboardCLI
)

# Create configuration
config = WellDashboardConfig(
    title="Well Production Dashboard",
    enable_verification=True,
    enable_real_time=False,
    cache_ttl=300,  # 5 minutes
    quality_threshold=0.8,
    api_port=5000,
    export_formats=['pdf', 'excel']
)

# Initialize dashboard
dashboard = WellProductionDashboard(config)
print(f"Dashboard initialized: {config.title}")
```

### Load Well Data

```python
import pandas as pd
from datetime import datetime

# Load from DataFrame
production_data = pd.read_csv('well_production.csv')
dashboard.load_well_data(data=production_data)

# Or load using BSEE query optimizer
dashboard.load_well_data(
    well_ids=['API_12345', 'API_67890'],
    start_date=datetime(2020, 1, 1),
    end_date=datetime(2024, 12, 31)
)

print(f"Loaded {len(dashboard.well_data)} production records")
```

### YAML Configuration Loading

```python
# Load dashboard from YAML config
dashboard = WellProductionDashboard.from_yaml('config/dashboard_config.yaml')

# Example YAML config file structure:
# dashboard:
#   title: "Production Analysis"
#   enable_verification: true
#   cache_ttl: 300
#   quality_threshold: 0.8
# wells:
#   - id: "API_12345"
#   - id: "API_67890"
# filters:
#   date_range:
#     start: "2020-01-01"
#     end: "2024-12-31"
```

### Well Metrics Calculations

```python
from worldenergydata.well_production_dashboard import WellMetrics

# NPV Calculation
cash_flows = [-1500, 200, 400, 600, 800, 700, 500, 400, 300, 200]
npv = WellMetrics.calculate_npv(cash_flows, discount_rate=0.10)
print(f"Well NPV: ${npv:,.2f}M")

# Decline Rate Analysis
production = [1000, 950, 900, 860, 820, 785, 750, 720, 690, 665]
decline_rate = WellMetrics.calculate_decline_rate(production)
print(f"Decline Rate: {decline_rate:.2%}")

# Economic Indicators
revenue = 5_000_000
opex = 1_200_000
capex = 2_500_000

indicators = WellMetrics.calculate_economic_indicators(revenue, opex, capex)
print(f"Profit: ${indicators['profit']:,.0f}")
print(f"Profit Margin: {indicators['profit_margin']:.1%}")
print(f"ROI: {indicators['roi']:.1%}")
print(f"Payback Period: {indicators['payback_period']:.1f} years")
```

### Production Forecasting

```python
import pandas as pd
from worldenergydata.well_production_dashboard import WellMetrics

# Historical production data
historical = pd.Series([1000, 950, 900, 860, 820, 785, 750, 720, 690, 665])

# Forecast 12 months
forecast = WellMetrics.forecast_production(historical, periods=12)

print("Production Forecast:")
print(forecast[['forecast', 'lower_bound', 'upper_bound']].head())

# forecast columns:
# - forecast: predicted production
# - lower_bound: 80% confidence lower
# - upper_bound: 120% confidence upper
```

### Field Aggregation

```python
from worldenergydata.well_production_dashboard import FieldAggregator
import pandas as pd

# Load well data
well_data = pd.DataFrame({
    'date': ['2024-01', '2024-01', '2024-02', '2024-02'],
    'well_id': ['W1', 'W2', 'W1', 'W2'],
    'oil_production': [1000, 1200, 950, 1150],
    'gas_production': [500, 600, 480, 580],
    'water_production': [200, 250, 220, 270]
})

# Aggregate to field level
field_data = FieldAggregator.aggregate_field_data(well_data, 'ANCHOR')
print(field_data)
# Shows: date, oil_production, gas_production, water_production, well_count, field

# Rollup with statistics
rollup = FieldAggregator.rollup_field_data(well_data, 'ANCHOR')
print(rollup.columns)
# Includes: sum, mean, std for each production type

# Compare two fields
field1 = FieldAggregator.rollup_field_data(well_data_1, 'ANCHOR')
field2 = FieldAggregator.rollup_field_data(well_data_2, 'JULIA')

comparison = FieldAggregator.compare_fields(field1, field2)
print(f"Performance Ratio: {comparison['performance_ratio']:.2f}")
print(f"Trend Comparison: {comparison['trend_comparison']:.2f}")
```

### REST API Integration

```python
from worldenergydata.well_production_dashboard import DashboardAPI

# Initialize API with dashboard
api = DashboardAPI(dashboard)

# Run Flask server
api.run(host='0.0.0.0', port=5000, debug=False)

# Available endpoints:
# GET /api/health         - Health check
# GET /api/wells          - List all wells
# GET /api/wells/<id>     - Get specific well data
# GET /api/dashboard/data - Get complete dashboard data
```

### CLI Usage

```python
from worldenergydata.well_production_dashboard import DashboardCLI

# Initialize CLI
cli = DashboardCLI()

# Run with config file
cli.run(config_path='config/dashboard.yaml')

# Or configure programmatically
cli.configure({
    'title': 'Production Dashboard',
    'enable_verification': True,
    'cache_ttl': 300
})

# Export dashboard
result = cli.export(
    format='pdf',
    output_path='reports/dashboard_export.pdf'
)
print(f"Export saved: {result}")

# Get export options
options = cli.get_export_parameters()
print(options)
# format: ['pdf', 'excel', 'json', 'all']
# include_verification: bool
# include_charts: bool
# include_raw_data: bool
```

### Dashboard Export

```python
from worldenergydata.well_production_dashboard import (
    WellProductionDashboard,
    WellDashboardConfig
)
from worldenergydata.well_production_dashboard.export_manager import (
    WellDashboardExportManager,
    ExportConfiguration
)

# Configure dashboard
dashboard = WellProductionDashboard(WellDashboardConfig(
    title="Production Analysis",
    export_formats=['pdf', 'excel']
))

# Load data
dashboard.load_well_data(well_ids=['API_12345'])

# Configure export
export_config = ExportConfiguration(
    formats=['pdf', 'excel', 'json'],
    include_verification=True,
    include_charts=True,
    include_raw_data=True,
    include_field_aggregation=True
)

# Export dashboard
results = dashboard.export_dashboard('reports/analysis', export_config)

for result in results:
    print(f"Exported: {result.format} -> {result.path}")
    print(f"  Success: {result.success}")
    print(f"  File size: {result.file_size} bytes")
```

### Verification Integration

```python
# Dashboard with verification enabled
config = WellDashboardConfig(
    title="Verified Dashboard",
    enable_verification=True,
    quality_threshold=0.8  # 80% quality minimum
)

dashboard = WellProductionDashboard(config)

# Load data - verification runs automatically
dashboard.load_well_data(well_ids=['API_12345'])

# Check verification results
if dashboard.verification_enabled:
    results = dashboard.verification_results
    for well_id, result in results.items():
        print(f"{well_id}: Quality Score = {result.quality_score:.2%}")
        if result.quality_score < 0.8:
            print(f"  Warning: Below quality threshold!")
```

### Caching and Performance

```python
# Dashboard with caching
config = WellDashboardConfig(
    title="High-Performance Dashboard",
    cache_ttl=600,  # 10 minute cache
    enable_verification=True
)

dashboard = WellProductionDashboard(config)

# Monitor cache performance
print(f"Cache hits: {dashboard.cache_hits}")
print(f"Total requests: {dashboard.total_requests}")
print(f"Hit rate: {dashboard.cache_hits/dashboard.total_requests:.1%}")

# Clear cache if needed
dashboard.cache_manager.clear()
```

## Command Line Interface

```bash
# Run dashboard server
python -m worldenergydata.well_production_dashboard.cli run --config config/dashboard.yaml

# Export dashboard
python -m worldenergydata.well_production_dashboard.cli export --format pdf --output reports/export.pdf

# List available options
python -m worldenergydata.well_production_dashboard.cli --help

# Verbose mode for debugging
python -m worldenergydata.well_production_dashboard.cli -v run --config config/dashboard.yaml
```

## Key Classes

| Class | Purpose |
|-------|---------|
| `WellProductionDashboard` | Main dashboard controller |
| `WellDashboardConfig` | Dashboard configuration |
| `WellMetrics` | Financial and production metrics |
| `FieldAggregator` | Field-level aggregation |
| `DashboardAPI` | Flask REST API |
| `DashboardCLI` | Command-line interface |
| `WellDashboardExportManager` | Export to PDF/Excel/JSON |
| `QueryOptimizer` | BSEE data loading optimization |
| `DashboardCacheManager` | Caching for performance |

## REST API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/health` | GET | Health check |
| `/api/wells` | GET | List all wells |
| `/api/wells/<well_id>` | GET | Get well data |
| `/api/dashboard/data` | GET | Full dashboard data |

## Export Formats

| Format | Contents |
|--------|----------|
| PDF | Charts, tables, verification metadata |
| Excel | Raw data, calculations, summaries |
| JSON | Structured data for integration |

## Configuration Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `title` | string | "Well Production Dashboard" | Dashboard title |
| `enable_verification` | bool | True | Enable data verification |
| `enable_real_time` | bool | False | Real-time updates |
| `cache_ttl` | int | 300 | Cache lifetime (seconds) |
| `quality_threshold` | float | 0.8 | Minimum quality score |
| `websocket_port` | int | 8765 | WebSocket port |
| `api_port` | int | 5000 | REST API port |
| `auth_enabled` | bool | True | Enable authentication |
| `export_formats` | list | ['pdf', 'excel'] | Available exports |

## Best Practices

1. **Enable verification** - Always validate data quality before analysis
2. **Use caching** - Set appropriate TTL for performance
3. **Configure exports** - Include verification metadata in reports
4. **Monitor performance** - Track cache hit rates
5. **Use YAML configs** - Version control dashboard configurations

## Related Skills

- [bsee-data-extractor](../bsee-data-extractor/SKILL.md) - BSEE data loading
- [npv-analyzer](../npv-analyzer/SKILL.md) - Economic analysis
- [fdas-economics](../fdas-economics/SKILL.md) - Field development economics
- [energy-data-visualizer](../energy-data-visualizer/SKILL.md) - Visualizations

## References

- Flask REST API Documentation
- Plotly Interactive Charts
- BSEE Data Standards
