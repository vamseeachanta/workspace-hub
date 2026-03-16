---
name: metocean-data-fetcher
description: Fetch real-time and historical metocean data from NDBC, CO-OPS, Open-Meteo,
  ERDDAP, and MET Norway. Use for buoy data retrieval, tidal observations, marine
  forecasts, and multi-source data fusion.
capabilities: []
requires: []
see_also:
- metocean-data-fetcher-data-sources
- metocean-data-fetcher-single-station-fetch-ndbc-buoy
- metocean-data-fetcher-ndbc-client
- metocean-data-fetcher-metocean-api-met-norway-nora3era5
- metocean-data-fetcher-station-management
- metocean-data-fetcher-csv-exporter
- metocean-data-fetcher-data-harmonization
- metocean-data-fetcher-1-gulf-of-mexico-buoy-survey
tags: []
category: data
version: 1.0.0
---

# Metocean Data Fetcher

## When to Use

- Fetch buoy data, Get wave data, Download NDBC observations
- Get tidal data, Fetch currents from CO-OPS
- Get marine forecast, Download metocean time series
- Fetch historical waves, Get real-time oceanographic data
- Multi-source data fusion for validation
- Gulf of Mexico buoy surveys
- North Atlantic ocean forecasts

## Related Skills

- [bsee-data-extractor](../bsee-data-extractor/SKILL.md) - BSEE offshore data
- [marine-safety-incidents](../marine-safety-incidents/SKILL.md) - Marine safety analysis
- [field-analyzer](../field-analyzer/SKILL.md) - Offshore field analysis
- [energy-data-visualizer](../energy-data-visualizer/SKILL.md) - Data visualization

## References

- NDBC: https://www.ndbc.noaa.gov/
- CO-OPS: https://tidesandcurrents.noaa.gov/
- Open-Meteo: https://open-meteo.com/en/docs/marine-weather-api
- ERDDAP: https://coastwatch.pfeg.noaa.gov/erddap/
- MET Norway: https://api.met.no/

## Sub-Skills

- [Best Practices](best-practices/SKILL.md)

## Sub-Skills

- [Data Sources](data-sources/SKILL.md)
- [Single Station Fetch (NDBC Buoy) (+5)](single-station-fetch-ndbc-buoy/SKILL.md)
- [NDBC Client (+4)](ndbc-client/SKILL.md)
- [metocean-api (MET Norway NORA3/ERA5) (+2)](metocean-api-met-norway-nora3era5/SKILL.md)
- [Station Management (+6)](station-management/SKILL.md)
- [CSV Exporter (+2)](csv-exporter/SKILL.md)
- [Data Harmonization](data-harmonization/SKILL.md)
- [1. Gulf of Mexico Buoy Survey (+2)](1-gulf-of-mexico-buoy-survey/SKILL.md)
