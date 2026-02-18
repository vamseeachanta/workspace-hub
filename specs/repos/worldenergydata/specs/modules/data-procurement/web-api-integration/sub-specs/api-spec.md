# API Specification

This is the API specification for the spec detailed in @specs/modules/data-procurement/web-api-integration/spec.md

> Created: 2025-09-01
> Version: 1.0.0

## Internal API Endpoints

### GET /api/v1/data/bsee/production

**Purpose:** Retrieve BSEE production data via API instead of file downloads
**Parameters:**
- `api_number` (string, optional): Well API number (10 or 12 digit)
- `lease_number` (string, optional): Lease identifier
- `block_id` (string, optional): Block identifier
- `start_date` (string, required): Start date in YYYY-MM-DD format
- `end_date` (string, required): End date in YYYY-MM-DD format
- `aggregation` (string, optional): daily|monthly|yearly (default: monthly)
- `use_cache` (boolean, optional): Enable caching (default: true)

**Response:**
```json
{
  "status": "success",
  "data": [
    {
      "api_number": "177164011400",
      "lease_number": "G24323",
      "production_date": "2024-01-01",
      "oil_bbls": 15234.5,
      "gas_mcf": 8923.2,
      "water_bbls": 3421.1,
      "days_on_production": 28
    }
  ],
  "metadata": {
    "source": "bsee_api",
    "cached": false,
    "response_time_ms": 234,
    "total_records": 150
  }
}
```

**Errors:**
- `400`: Invalid parameters
- `404`: No data found for criteria
- `429`: Rate limit exceeded
- `503`: External API unavailable

### GET /api/v1/data/bsee/wells

**Purpose:** Retrieve well information from BSEE APIs
**Parameters:**
- `api_number` (string, optional): Specific well API
- `block_id` (string, optional): Block identifier
- `water_depth_min` (number, optional): Minimum water depth in feet
- `water_depth_max` (number, optional): Maximum water depth in feet
- `status` (string, optional): active|plugged|abandoned
- `include_directional` (boolean, optional): Include directional survey data

**Response:**
```json
{
  "status": "success",
  "data": [
    {
      "api_number": "177164011400",
      "well_name": "A-15",
      "block": "MC 243",
      "water_depth_ft": 3256,
      "total_depth_ft": 18500,
      "spud_date": "2020-03-15",
      "status": "active",
      "operator": "Shell",
      "directional_data": {
        "surface_latitude": 28.1234,
        "surface_longitude": -89.5678,
        "bottom_hole_latitude": 28.1345,
        "bottom_hole_longitude": -89.5789
      }
    }
  ],
  "metadata": {
    "source": "bsee_api",
    "cached": true,
    "cache_expires": "2024-01-02T12:00:00Z"
  }
}
```

### GET /api/v1/data/eia/prices

**Purpose:** Fetch energy price data from EIA API
**Parameters:**
- `series_id` (string, required): EIA series identifier
- `start_date` (string, required): Start date
- `end_date` (string, required): End date
- `frequency` (string, optional): daily|weekly|monthly|annual

**Response:**
```json
{
  "status": "success",
  "data": [
    {
      "date": "2024-01-01",
      "series_id": "PET.RWTC.D",
      "value": 73.25,
      "units": "dollars_per_barrel"
    }
  ],
  "metadata": {
    "source": "eia_api",
    "series_name": "Crude Oil Prices: West Texas Intermediate",
    "last_updated": "2024-01-02T06:00:00Z"
  }
}
```

### GET /api/v1/data/noaa/weather

**Purpose:** Retrieve weather and ocean conditions from NOAA
**Parameters:**
- `latitude` (number, required): Location latitude
- `longitude` (number, required): Location longitude
- `start_date` (string, required): Start date
- `end_date` (string, required): End date
- `parameters` (array, optional): wind_speed|wave_height|temperature

**Response:**
```json
{
  "status": "success",
  "data": [
    {
      "timestamp": "2024-01-01T12:00:00Z",
      "latitude": 28.5,
      "longitude": -89.5,
      "wind_speed_kts": 15.5,
      "wind_direction_deg": 225,
      "wave_height_m": 2.1,
      "wave_period_s": 8.5,
      "air_temperature_c": 22.3
    }
  ],
  "metadata": {
    "source": "noaa_api",
    "station": "NDBC_42040",
    "data_quality": "verified"
  }
}
```

### POST /api/v1/data/aggregate

**Purpose:** Aggregate data from multiple sources
**Parameters:**
```json
{
  "sources": ["bsee", "eia", "noaa"],
  "filters": {
    "api_number": "177164011400",
    "start_date": "2024-01-01",
    "end_date": "2024-01-31"
  },
  "aggregation": {
    "group_by": ["api_number", "month"],
    "metrics": ["sum", "average", "max"]
  }
}
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "production": {...},
    "prices": {...},
    "weather": {...}
  },
  "correlations": {
    "price_vs_production": 0.82,
    "weather_impact_score": 0.15
  }
}
```

## External API Integrations

### BSEE Data APIs
- **Well Data**: https://www.data.bsee.gov/api/wells
- **Production Data**: https://www.data.bsee.gov/api/production
- **Lease Data**: https://www.data.bsee.gov/api/leases
- **Authentication**: API key required (request from BSEE)

### EIA Energy APIs
- **Base URL**: https://api.eia.gov/v2/
- **Authentication**: API key required (free registration)
- **Rate Limit**: 10,000 requests per day
- **Documentation**: https://www.eia.gov/opendata/

### NOAA Weather APIs
- **Base URL**: https://api.weather.gov/
- **Authentication**: None required for public data
- **Rate Limit**: Fair use policy
- **Documentation**: https://www.weather.gov/documentation/services-web-api

## WebSocket Endpoints (Future Enhancement)

### WS /ws/v1/data/stream

**Purpose:** Real-time data streaming (future implementation)
**Message Format:**
```json
{
  "type": "subscribe",
  "channels": ["bsee.production", "eia.prices"],
  "filters": {
    "api_numbers": ["177164011400", "177164011401"]
  }
}
```

## Health &amp; Monitoring Endpoints

### GET /api/v1/health

**Purpose:** Service health check
**Response:**
```json
{
  "status": "healthy",
  "services": {
    "bsee_api": "operational",
    "eia_api": "operational",
    "noaa_api": "degraded",
    "cache": "operational",
    "database": "operational"
  },
  "uptime_seconds": 864000
}
```

### GET /api/v1/metrics

**Purpose:** API performance metrics
**Response:**
```json
{
  "requests_total": 125432,
  "cache_hit_rate": 0.92,
  "average_response_time_ms": 245,
  "external_api_failures": 12,
  "rate_limit_hits": 3
}
```