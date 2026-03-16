---
name: well-production-dashboard
description: Create interactive well production dashboards with real-time monitoring,
  verification integration, economic metrics, and multi-format exports. Use for well
  performance analysis, field aggregation, production forecasting, and API-driven
  dashboards.
capabilities: []
requires: []
see_also:
- well-production-dashboard-1-basic-well-dashboard
- well-production-dashboard-command-line-interface
- well-production-dashboard-rest-api-endpoints
- well-production-dashboard-export-formats
- well-production-dashboard-configuration-options
tags: []
category: data
version: 1.0.0
---

# Well Production Dashboard

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
```

*See sub-skills for full details.*

### REST API Integration

```python
from worldenergydata.well_production_dashboard import DashboardAPI

api = DashboardAPI(dashboard)
api.run(host='0.0.0.0', port=5000, debug=False)

# Endpoints:
# GET /api/health         - Health check
# GET /api/wells          - List all wells
# GET /api/wells/<id>     - Get specific well data
# GET /api/dashboard/data - Get complete dashboard data
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

## Related Skills

- [bsee-data-extractor](../bsee-data-extractor/SKILL.md) - BSEE data loading
- [npv-analyzer](../npv-analyzer/SKILL.md) - Economic analysis
- [fdas-economics](../fdas-economics/SKILL.md) - Field development economics
- [energy-data-visualizer](../energy-data-visualizer/SKILL.md) - Visualizations

## References

- Flask REST API Documentation
- Plotly Interactive Charts
- BSEE Data Standards

## Sub-Skills

- [Best Practices](best-practices/SKILL.md)
- [1. Basic Well Dashboard (+3)](1-basic-well-dashboard/SKILL.md)
- [Command Line Interface](command-line-interface/SKILL.md)
- [REST API Endpoints](rest-api-endpoints/SKILL.md)
- [Export Formats](export-formats/SKILL.md)
- [Configuration Options](configuration-options/SKILL.md)
