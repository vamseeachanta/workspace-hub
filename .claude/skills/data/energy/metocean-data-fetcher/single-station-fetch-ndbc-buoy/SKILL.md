---
name: metocean-data-fetcher-single-station-fetch-ndbc-buoy
description: 'Sub-skill of metocean-data-fetcher: Single Station Fetch (NDBC Buoy)
  (+5).'
version: 1.0.0
category: data
type: reference
scripts_exempt: true
---

# Single Station Fetch (NDBC Buoy) (+5)

## Single Station Fetch (NDBC Buoy)


```yaml
metocean:
  source: ndbc
  station_id: "41001"  # Mid-Atlantic buoy
  fetch_type: realtime
  parameters:
    - wave_height
    - wave_period
    - wind_speed
    - wind_direction
    - sea_surface_temp
  output:
    format: csv
    path: "data/ndbc_41001.csv"
```

## Regional Station Discovery


```yaml
metocean:
  discovery:
    source: ndbc
    bbox:
      lon_min: -98
      lon_max: -88
      lat_min: 25
      lat_max: 31
    active_only: true
  output:
    format: json
    path: "data/gom_stations.json"
```

## Historical Time Series


```yaml
metocean:
  source: ndbc
  station_id: "41001"
  fetch_type: historical
  date_range:
    start: "2024-01-01"
    end: "2024-12-31"
  parameters:
    - wave_height

*See sub-skills for full details.*

## Multi-Source Fusion


```yaml
metocean:
  fusion:
    sources:
      - source: ndbc
        station_id: "41001"
      - source: open_meteo
        coordinates:
          lat: 34.68
          lon: -72.66

*See sub-skills for full details.*

## CO-OPS Tidal Data


```yaml
metocean:
  source: coops
  station_id: "8761724"  # Grand Isle, LA
  fetch_type: water_level
  date_range:
    start: "2024-01-01"
    end: "2024-01-31"
  datum: MLLW
  verified: true
  output:
    format: csv
    path: "data/grand_isle_tides.csv"
```

## Coordinate-Based Forecast (Open-Meteo)


```yaml
metocean:
  source: open_meteo
  coordinates:
    lat: 28.5
    lon: -88.5
  forecast_days: 7
  parameters:
    - wave_height
    - wave_period

*See sub-skills for full details.*
