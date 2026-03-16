---
name: metocean-data-fetcher-data-sources
description: 'Sub-skill of metocean-data-fetcher: Data Sources.'
version: 1.0.0
category: data
type: reference
scripts_exempt: true
---

# Data Sources

## Data Sources


| Source | Data Types | Client Class | API Type |
|--------|-----------|--------------|----------|
| NOAA NDBC | Waves, wind, SST, pressure, currents | `NDBCClient` | HTTP/Text |
| NOAA CO-OPS | Tides, water levels, currents, predictions | `COOPSClient` | REST JSON |
| Open-Meteo | Wave/swell/current forecasts (coordinate-based) | `OpenMeteoClient` | REST JSON |
| IOOS ERDDAP | Buoy, glider, HF radar, gridded data | `ERDDAPClient` | ERDDAP |
| MET Norway | Ocean/weather forecasts (North Atlantic/Arctic) | `MetNorwayClient` | REST JSON |
