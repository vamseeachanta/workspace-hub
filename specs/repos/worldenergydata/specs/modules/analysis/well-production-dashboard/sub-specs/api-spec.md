# API Specification

This is the API specification for the spec detailed in @specs/modules/analysis/well-production-dashboard/spec.md

> Created: 2025-01-13
> Version: 1.0.0
> Module: Analysis

## API Overview

The Well Production Dashboard API provides RESTful endpoints for data retrieval, dashboard configuration, and export functionality.

### Base URL
```
/api/v1/dashboard
```

### Authentication
- JWT Bearer token authentication
- Session-based authentication for web clients
- API key authentication for external systems

### Response Format
```json
{
    "status": "success",
    "data": {},
    "meta": {
        "timestamp": "2025-01-13T10:30:00Z",
        "version": "1.0.0",
        "request_id": "req_12345"
    }
}
```

## Core Endpoints

### 1. Well Data Endpoints

#### GET /wells
**Purpose:** List all available wells
**Parameters:**
- `field`: Filter by field (optional)
- `status`: Filter by status (active/inactive)
- `page`: Page number (default: 1)
- `limit`: Items per page (default: 100)
**Response:**
```json
{
    "wells": [
        {
            "well_id": "W-001",
            "name": "Eagle Ford Well 1",
            "field": "Eagle Ford",
            "status": "active",
            "last_production_date": "2024-12-31"
        }
    ],
    "pagination": {
        "total": 500,
        "page": 1,
        "pages": 5
    }
}
```

#### GET /wells/{well_id}
**Purpose:** Get detailed well information
**Response:**
```json
{
    "well_id": "W-001",
    "name": "Eagle Ford Well 1",
    "field": "Eagle Ford",
    "operator": "Energy Corp",
    "spud_date": "2020-01-15",
    "completion_date": "2020-03-20",
    "current_status": "producing",
    "coordinates": {
        "latitude": 28.7041,
        "longitude": -98.1234
    },
    "production_summary": {
        "total_oil": 1500000,
        "total_gas": 7500000,
        "total_water": 500000,
        "last_month_oil": 5000,
        "last_month_gas": 25000
    }
}
```

#### GET /wells/{well_id}/production
**Purpose:** Get well production time series
**Parameters:**
- `start_date`: ISO date string
- `end_date`: ISO date string
- `frequency`: daily/monthly/yearly (default: monthly)
- `metrics`: Comma-separated list (oil,gas,water)
**Response:**
```json
{
    "well_id": "W-001",
    "data": [
        {
            "date": "2024-01-01",
            "oil": 5000,
            "gas": 25000,
            "water": 1000,
            "oil_price": 75.50,
            "gas_price": 3.25
        }
    ],
    "units": {
        "oil": "bbl/day",
        "gas": "mcf/day",
        "water": "bbl/day"
    }
}
```

#### GET /wells/{well_id}/economics
**Purpose:** Get well economic metrics
**Response:**
```json
{
    "well_id": "W-001",
    "metrics": {
        "npv": 15000000,
        "irr": 0.35,
        "payback_months": 18,
        "total_revenue": 25000000,
        "total_opex": 5000000,
        "total_capex": 8000000,
        "profit_margin": 0.48
    },
    "monthly_cashflow": [
        {
            "month": "2024-01",
            "revenue": 500000,
            "opex": 50000,
            "net_cashflow": 450000
        }
    ]
}
```

### 2. Field Aggregation Endpoints

#### GET /fields
**Purpose:** List all fields
**Response:**
```json
{
    "fields": [
        {
            "field_id": "F-001",
            "name": "Eagle Ford",
            "well_count": 150,
            "active_wells": 120,
            "total_production": {
                "oil": 10000000,
                "gas": 50000000
            }
        }
    ]
}
```

#### GET /fields/{field_id}/aggregation
**Purpose:** Get field-level aggregated metrics
**Parameters:**
- `start_date`: ISO date string
- `end_date`: ISO date string
- `group_by`: well/operator/status
**Response:**
```json
{
    "field_id": "F-001",
    "aggregations": {
        "total_wells": 150,
        "active_wells": 120,
        "total_production": {
            "oil": 750000,
            "gas": 3750000,
            "water": 250000
        },
        "average_production": {
            "oil": 6250,
            "gas": 31250
        },
        "top_producers": [
            {
                "well_id": "W-001",
                "oil": 8000,
                "gas": 40000
            }
        ]
    }
}
```

#### GET /fields/{field_id}/comparison
**Purpose:** Compare wells within a field
**Parameters:**
- `wells`: Comma-separated well IDs
- `metric`: oil/gas/revenue/npv
- `period`: last_month/last_year/lifetime
**Response:**
```json
{
    "comparison": [
        {
            "well_id": "W-001",
            "metric_value": 5000,
            "rank": 1,
            "percentile": 95
        },
        {
            "well_id": "W-002",
            "metric_value": 4500,
            "rank": 2,
            "percentile": 90
        }
    ]
}
```

### 3. Dashboard Configuration

#### GET /dashboard/config
**Purpose:** Get user dashboard configuration
**Response:**
```json
{
    "user_id": "user_123",
    "default_view": "field_overview",
    "preferences": {
        "theme": "light",
        "chart_type": "line",
        "date_range": "last_year",
        "refresh_interval": 300
    },
    "saved_filters": [
        {
            "name": "Active Wells",
            "filters": {"status": "active"}
        }
    ]
}
```

#### PUT /dashboard/config
**Purpose:** Update dashboard configuration
**Body:**
```json
{
    "default_view": "well_detail",
    "preferences": {
        "theme": "dark",
        "chart_type": "bar"
    }
}
```

#### POST /dashboard/layouts
**Purpose:** Save custom dashboard layout
**Body:**
```json
{
    "name": "Executive View",
    "layout": {
        "components": [
            {
                "type": "kpi_card",
                "position": {"x": 0, "y": 0, "w": 3, "h": 2}
            }
        ]
    }
}
```

### 4. Chart Data Endpoints

#### GET /charts/production
**Purpose:** Get production chart data
**Parameters:**
- `wells`: Comma-separated well IDs
- `start_date`: ISO date string
- `end_date`: ISO date string
- `chart_type`: line/bar/area
**Response:**
```json
{
    "chart_data": {
        "x": ["2024-01", "2024-02", "2024-03"],
        "series": [
            {
                "name": "W-001",
                "y": [5000, 4800, 4900],
                "type": "scatter"
            }
        ],
        "layout": {
            "title": "Production Trend",
            "xaxis": {"title": "Date"},
            "yaxis": {"title": "Production (bbl/day)"}
        }
    }
}
```

#### GET /charts/economics
**Purpose:** Get economic charts data
**Parameters:**
- `wells`: Well IDs
- `metric`: npv/irr/cashflow
- `chart_type`: waterfall/bar/pie
**Response:**
```json
{
    "chart_data": {
        "type": "waterfall",
        "data": [
            {"name": "Revenue", "value": 1000000},
            {"name": "OPEX", "value": -200000},
            {"name": "CAPEX", "value": -300000},
            {"name": "Net", "value": 500000}
        ]
    }
}
```

### 5. Export Endpoints

#### POST /export/pdf
**Purpose:** Generate PDF report
**Body:**
```json
{
    "type": "well_report",
    "well_id": "W-001",
    "sections": ["summary", "production", "economics"],
    "date_range": {
        "start": "2024-01-01",
        "end": "2024-12-31"
    }
}
```
**Response:**
```json
{
    "export_id": "exp_12345",
    "status": "processing",
    "estimated_time": 30
}
```

#### POST /export/excel
**Purpose:** Export data to Excel
**Body:**
```json
{
    "wells": ["W-001", "W-002"],
    "data_types": ["production", "economics"],
    "format": "pivot_table"
}
```

#### GET /export/{export_id}
**Purpose:** Download exported file
**Response:** Binary file download
**Headers:**
```
Content-Type: application/pdf
Content-Disposition: attachment; filename="report.pdf"
```

### 6. Real-time Updates

#### WebSocket /ws/dashboard
**Purpose:** Real-time dashboard updates
**Message Format:**
```json
{
    "type": "subscribe",
    "channels": ["well.W-001", "field.F-001"]
}
```
**Update Format:**
```json
{
    "type": "data_update",
    "channel": "well.W-001",
    "data": {
        "production": {
            "oil": 5100,
            "gas": 25500
        },
        "timestamp": "2025-01-13T10:30:00Z"
    }
}
```

## Search and Filter API

### POST /search
**Purpose:** Advanced search across wells
**Body:**
```json
{
    "query": "high producing",
    "filters": {
        "field": "Eagle Ford",
        "production_min": 5000,
        "status": "active"
    },
    "sort": {
        "field": "production",
        "order": "desc"
    }
}
```

### GET /filters/options
**Purpose:** Get available filter options
**Response:**
```json
{
    "fields": ["Eagle Ford", "Permian", "Bakken"],
    "operators": ["Energy Corp", "Oil Co"],
    "statuses": ["active", "inactive", "suspended"],
    "date_ranges": [
        {"label": "Last Month", "value": "last_month"},
        {"label": "Last Year", "value": "last_year"}
    ]
}
```

## Performance Endpoints

### GET /analytics/kpis
**Purpose:** Get key performance indicators
**Response:**
```json
{
    "kpis": {
        "total_production": 1000000,
        "active_wells": 450,
        "average_efficiency": 0.85,
        "total_revenue": 75000000,
        "month_over_month_growth": 0.05
    }
}
```

### GET /analytics/trends
**Purpose:** Get trend analysis
**Parameters:**
- `metric`: production/revenue/costs
- `period`: 30d/90d/1y
**Response:**
```json
{
    "trend": {
        "direction": "increasing",
        "change_percent": 5.2,
        "forecast_next_period": 1050000
    }
}
```

## Error Handling

### Error Response Format
```json
{
    "status": "error",
    "error": {
        "code": "DASH_001",
        "message": "Well not found",
        "details": {
            "well_id": "W-999"
        }
    }
}
```

### Error Codes
| Code | Description |
|------|-------------|
| DASH_001 | Resource not found |
| DASH_002 | Invalid date range |
| DASH_003 | Insufficient permissions |
| DASH_004 | Export generation failed |
| DASH_005 | Invalid chart configuration |
| DASH_006 | Rate limit exceeded |

## Rate Limiting

- **Standard tier**: 1000 requests/hour
- **Premium tier**: 10000 requests/hour
- **Export endpoints**: 100 requests/hour
- **WebSocket connections**: 10 per user

## SDK Examples

### JavaScript/TypeScript
```javascript
import { DashboardClient } from '@worldenergydata/dashboard-sdk';

const client = new DashboardClient({
    apiKey: 'your_api_key',
    baseUrl: 'https://api.worldenergydata.com'
});

// Get well data
const wellData = await client.wells.get('W-001');

// Subscribe to updates
client.subscribe('well.W-001', (update) => {
    console.log('New data:', update);
});

// Export report
const report = await client.export.pdf({
    wellId: 'W-001',
    sections: ['summary', 'production']
});
```

### Python
```python
from worldenergydata.dashboard import DashboardAPI

api = DashboardAPI(api_key="your_key")

# Get production data
production = api.get_well_production(
    well_id="W-001",
    start_date="2024-01-01",
    end_date="2024-12-31"
)

# Generate chart
chart = api.create_chart(
    wells=["W-001", "W-002"],
    chart_type="line",
    metric="oil_production"
)

# Export to Excel
export_id = api.export_excel(
    wells=["W-001"],
    data_types=["production", "economics"]
)
```