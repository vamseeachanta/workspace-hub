# Metocean Data APIs Research Report

> **Document Type**: Research & Analysis
> **Date**: 2026-01-26
> **Module**: data-procurement/metocean
> **Status**: Complete

## Executive Summary

This document provides a comprehensive inventory of publicly available metocean (meteorological + oceanographic) data APIs worldwide. The research covers global/international sources, regional meteorological agencies, and specialized ocean data providers. Each source is evaluated for API availability, authentication requirements, data types, and usage constraints.

---

## 1. Global/International Sources

### 1.1 NOAA National Data Buoy Center (NDBC)

**Overview**: The NDBC operates a network of buoys and coastal stations providing real-time meteorological and oceanographic data.

| Attribute | Details |
|-----------|---------|
| **API Type** | HTTP File Access / Text Files |
| **Base URL** | `https://www.ndbc.noaa.gov/data/realtime2/` |
| **Authentication** | None required (Open Access) |
| **Rate Limits** | No official limits; courtesy limits apply |
| **Data Format** | Text files (whitespace-delimited), parseable as CSV |

**Data Types Available**:
- `stdmet` - Standard meteorological (air temp, pressure, wind, visibility)
- `spec` - Spectral wave summaries
- `swden` - Spectral wave density
- `swdir` - Spectral wave direction
- `ocean` - Oceanographic (water temp, salinity, waves)
- `adcp` - Acoustic Doppler Current Profiler (currents at depth)
- `cwind` - Continuous winds (high-frequency)

**Access Pattern**:
```
https://www.ndbc.noaa.gov/data/realtime2/{STATION_ID}.{datatype}
Example: https://www.ndbc.noaa.gov/data/realtime2/41001.txt
```

**Coverage**: 45 days of real-time data; historical data available separately

**Python Libraries**:
- [ndbc-api](https://github.com/CDJellen/ndbc-api) - Comprehensive Python wrapper
- [NDBC](https://pypi.org/project/NDBC/) - Alternative package

**Sources**:
- [NDBC Data Access FAQ](https://www.ndbc.noaa.gov/faq/rt_data_access.shtml)
- [NDBC Web Data Guide (PDF)](https://www.ndbc.noaa.gov/docs/ndbc_web_data_guide.pdf)

---

### 1.2 NOAA CO-OPS (Tides & Currents)

**Overview**: Center for Operational Oceanographic Products and Services provides tide, current, and water level data.

| Attribute | Details |
|-----------|---------|
| **API Type** | REST API |
| **Base URL** | `https://api.tidesandcurrents.noaa.gov/api/prod/` |
| **Authentication** | None required (Open Access) |
| **Rate Limits** | Not explicitly documented |
| **Data Format** | JSON, XML, CSV |

**API Endpoints**:
- **Data Retrieval**: `/datagetter` - Main data access
- **Metadata**: `https://api.tidesandcurrents.noaa.gov/mdapi/prod/`

**Data Types Available**:
- Water levels (verified, preliminary, predictions)
- Tide predictions (high/low, hourly heights)
- Currents (speed, direction)
- Air temperature
- Water temperature (**NOTE: Discontinued after 2024**)
- Barometric pressure
- Wind speed/direction
- Visibility

**Example API Call**:
```
https://api.tidesandcurrents.noaa.gov/api/prod/datagetter?
  date=today
  &station=9414290
  &product=water_level
  &datum=MLLW
  &time_zone=gmt
  &units=english
  &format=json
```

**Tools**:
- [API URL Builder](https://tidesandcurrents.noaa.gov/api-helper/url-generator.html)

**Sources**:
- [CO-OPS Data Retrieval API](https://api.tidesandcurrents.noaa.gov/api/prod/)
- [Web Services Info](https://tidesandcurrents.noaa.gov/web_services_info.html)

---

### 1.3 Copernicus Marine Service (CMEMS)

**Overview**: EU-funded service providing ocean analysis, forecasts, and reanalysis data globally.

| Attribute | Details |
|-----------|---------|
| **API Type** | REST, OPeNDAP, ERDDAP, WMS |
| **Portal** | `https://data.marine.copernicus.eu/` |
| **Authentication** | Required - Free registration |
| **Rate Limits** | Varies by product; generous for registered users |
| **Data Format** | NetCDF, JSON, GeoTIFF |

**Key Products**:
- **GLOBAL_ANALYSISFORECAST_PHY_001_024** - Global ocean physics (currents, temperature, salinity)
- **GLOBAL_ANALYSISFORECAST_WAV_001_027** - Global waves (3-hourly, 1/12 degree)
- **GLOBAL_MULTIYEAR_PHY_001_030** - Historical reanalysis

**Data Types Available**:
- Sea surface temperature (SST) and anomalies
- Ocean currents (surface and subsurface)
- Significant wave height, period, direction
- Stokes drift
- Wind waves and swell partitions
- Salinity
- Sea level height

**Access Methods**:
1. **Copernicus Marine Toolbox (Python)**: `copernicusmarine` package
2. **OPeNDAP**: Direct data streaming via URL
3. **ERDDAP**: RESTful API for near-real-time in-situ data
4. **WMS**: Map image services

**Python Example**:
```python
import copernicusmarine

# Download subset
copernicusmarine.subset(
    dataset_id="cmems_mod_glo_phy-cur_anfc_0.083deg_PT6H-i",
    variables=["uo", "vo"],
    minimum_longitude=-10,
    maximum_longitude=10,
    minimum_latitude=35,
    maximum_latitude=45,
    start_datetime="2024-01-01",
    end_datetime="2024-01-02"
)
```

**Coverage**: Global; forecasts up to 10 days; reanalysis from 1993

**Sources**:
- [CMEMS Data Access](https://marine.copernicus.eu/access-data/)
- [OPeNDAP/ERDDAP Access](https://marine.copernicus.eu/news/access-data-opendap-erddap-api)

---

### 1.4 ECMWF (European Centre for Medium-Range Weather Forecasts)

**Overview**: Leading source of atmospheric and ocean model data, operates Climate Data Store (CDS).

| Attribute | Details |
|-----------|---------|
| **API Type** | REST API, CDS API |
| **Portal** | `https://cds.climate.copernicus.eu/` |
| **Authentication** | Required - Free registration + API token |
| **Rate Limits** | Queue-based system |
| **Data Format** | GRIB2, NetCDF |

**Open Data (No Registration)**:
- Real-time IFS and AIFS forecasts
- 0.25 degree resolution
- Creative Commons CC-BY-4.0 license

**Data Types Available**:
- Wave parameters (significant height, period, direction)
- Ocean surface currents
- Sea surface temperature
- Wind at 10m
- Mean sea level pressure

**Access Methods**:
1. **Open Data Package**: `pip install ecmwf-opendata`
2. **CDS API**: `pip install cdsapi`
3. **THREDDS**: OPeNDAP streaming

**Python Example (Open Data)**:
```python
from ecmwf.opendata import Client

client = Client()
client.retrieve(
    type="fc",
    stream="wave",
    step=["0", "24", "48"],
    param=["swh", "mwp"],
    target="wave_forecast.grib2"
)
```

**Configuration (~/.cdsapirc)**:
```
url: https://cds.climate.copernicus.eu/api
key: {YOUR_UID}:{YOUR_API_KEY}
```

**Sources**:
- [ECMWF Open Data](https://www.ecmwf.int/en/forecasts/datasets/open-data)
- [Climate Data Store](https://cds.climate.copernicus.eu/)
- [ecmwf-opendata GitHub](https://github.com/ecmwf/ecmwf-opendata)

---

### 1.5 WMO Information System 2.0 (WIS 2.0)

**Overview**: Global data sharing framework replacing the GTS, operational since January 2025.

| Attribute | Details |
|-----------|---------|
| **API Type** | OGC API - Records, MQTT |
| **Portal** | Through national nodes |
| **Authentication** | Varies by data provider |
| **Status** | Operational (Jan 2025) |

**Architecture Components**:
- WIS2 Nodes - Data publication
- Global Discovery Catalogue - Metadata search
- Global Broker - Real-time notifications
- Global Cache - Data delivery

**Coverage**: 60+ countries, 80+ nodes, millions of data granules daily

**Note**: WIS 2.0 is primarily a distribution mechanism rather than a direct data API. Access typically goes through national meteorological services.

**Sources**:
- [WMO WIS 2.0](https://wmo.int/wis-20)
- [WIS 2.0 Implementation](https://community.wmo.int/en/activity-areas/wis/wis2-implementation)

---

## 2. Regional Meteorological Services

### 2.1 MET Norway (Norwegian Meteorological Institute)

**Overview**: Comprehensive free API with excellent wave and ocean forecasting for Northwestern Europe.

| Attribute | Details |
|-----------|---------|
| **API Type** | REST API, THREDDS |
| **Base URL** | `https://api.met.no/` |
| **Authentication** | None required (User-Agent header recommended) |
| **Rate Limits** | Reasonable use expected |
| **Data Format** | JSON, XML, NetCDF |
| **License** | Norwegian License for Open Government Data (NLOD) |

**Key Services**:
- **Oceanforecast 2.0** - Ocean forecasts for Northwestern Europe
- **Locationforecast 2.0** - Weather for any location
- **THREDDS** - Dataset archive with OPeNDAP access
- **Frost 0.9** - Historical observation data

**Wave Models**:
- WAM-800m (Norwegian coast)
- NORA3 (3km resolution hindcast)
- NORA10 (Norwegian Sea, North Sea, Barents Sea)

**Data Types Available**:
- Significant wave height
- Wave period and direction
- Sea level
- Ocean currents
- SST
- Salinity profiles

**Python Package**:
```bash
pip install metocean-api
```

```python
from metocean_api import ts

# Download wave data
df = ts.download(
    product='NORA3_wave_sub',
    lat=60.0,
    lon=5.0,
    start_time='2020-01-01',
    stop_time='2020-01-31'
)
```

**Sources**:
- [MET Weather API](https://api.met.no/)
- [MET Ocean Portal](https://ocean.met.no/)
- [Data Portal](https://data.met.no/)
- [metocean-api Documentation](https://metocean-api.readthedocs.io/)

---

### 2.2 UK Met Office

**Overview**: Marine data service with shelf seas models; some data now exclusively via UKMCAS service.

| Attribute | Details |
|-----------|---------|
| **API Type** | REST API (DataPoint), FTP |
| **Portal** | `https://www.metoffice.gov.uk/services/data/` |
| **Authentication** | API Key required |
| **License** | Open Government Licence (OGL) |

**Products**:
- Global ocean analysis and 7-day forecast (0.25 degree)
- NW European Atlantic shelf analysis and 6-day forecast (1.5km resolution)
- Surface wave analysis and 6-day forecast (1.5km resolution)

**Data Delivery**: FTP (daily delivery)

**Note**: For Copernicus Marine users, data is available via CMEMS for limited time; UKMCAS becomes exclusive source.

**Third-Party Access**:
Open-Meteo provides UK Met Office data via their API (CC BY-SA 4.0 license, 4-hour delay)

**Sources**:
- [Met Office Marine Data Service](https://www.metoffice.gov.uk/services/data/met-office-marine-data-service)
- [DataPoint API Reference](https://www.metoffice.gov.uk/services/data/datapoint/api-reference)

---

### 2.3 Australian Bureau of Meteorology (BOM)

**Overview**: Comprehensive marine data including BLUElink ocean forecasting initiative.

| Attribute | Details |
|-----------|---------|
| **API Type** | FTP, Limited REST API (Prototype) |
| **Portal** | `https://www.bom.gov.au/` |
| **Authentication** | API key for REST API |
| **Data Format** | JSON, HTML, AXF |

**Data Sources**:
- BLUElink ocean forecasting (currents, SST forecasts)
- Marine forecasts (wind, weather, sea, swell)
- Real-time observations (satellite imagery, wave height, SST)

**FTP Access**: `ftp://ftp.bom.gov.au/anon/gen/`

**Developer Portal**: `https://developer.bom.gov.au/`

**Third-Party Options**:
- **weatherOz** (R package) - DPIRD, DES Queensland, BOM data
- **weather-au** (Python) - Unofficial BOM API wrapper
- **Open-Meteo BOM API** - ACCESS-G model data

**Sources**:
- [BOM Weather Data Services](https://www.bom.gov.au/catalogue/data-feeds.shtml)
- [Open-Meteo BOM API](https://open-meteo.com/en/docs/bom-api)

---

### 2.4 Japan Meteorological Agency (JMA)

**Overview**: Operates marine observatories and ocean data buoys; limited direct API access.

| Attribute | Details |
|-----------|---------|
| **API Type** | Primarily web portal/FTP |
| **Portal** | `https://www.jma.go.jp/jma/en/menu.html` |
| **Authentication** | None for public data |
| **Data Licensing** | JMBSC for commercial redistribution |

**Data Available**:
- Ocean waves (Northwestern Pacific, Sea of Japan, Sea of Okhotsk)
- Sea surface temperature
- Ocean currents
- Tide levels
- Drifting buoy observations

**Data Portals**:
- [Distribution Marine Forecasts](https://www.jma.go.jp/bosai/en_umimesh/)
- [Sea Waves](https://www.data.jma.go.jp/waveinf/chart/awjp_e.html)
- [Ocean Data Buoy Observations](https://www.data.jma.go.jp/kaiyou/db/vessel_obs/data-report/html/buoy/buoy_e.php)

**Third-Party Access**:
Open-Meteo JMA API provides limited data due to licensing restrictions

**Sources**:
- [JMA Marine Homepage](https://www.jma.go.jp/jma/en/menu.html)
- [Open-Meteo JMA API](https://open-meteo.com/en/docs/jma-api)

---

## 3. Specialized Ocean Data Services

### 3.1 IOOS (US Integrated Ocean Observing System)

**Overview**: National network with regional associations providing comprehensive ocean data via ERDDAP and OPeNDAP.

| Attribute | Details |
|-----------|---------|
| **API Type** | ERDDAP, OPeNDAP, SOS, WMS/WCS |
| **Catalog** | `https://data.ioos.us/` |
| **Authentication** | None required (Open Access) |
| **Data Format** | NetCDF, CSV, JSON |

**Data Assembly Centers**:
- Glider DAC - Underwater glider data
- Animal Telemetry DAC - Marine animal tracking
- HF Radar DAC - Surface currents

**Regional Associations** (11 total, examples):
- PacIOOS (Pacific Islands)
- GCOOS (Gulf of Mexico)
- NERACOOS (Northeast)
- SECOORA (Southeast)

**ERDDAP Access**:
```
https://coastwatch.pfeg.noaa.gov/erddap/
https://www.pacioos.hawaii.edu/erddap/
```

**Data Types**:
- Glider profiles (T, S, currents)
- HF Radar surface currents
- Buoy observations
- Model outputs

**Sources**:
- [IOOS Data Access](https://ioos.noaa.gov/data/access-ioos-data/)
- [PacIOOS ERDDAP](https://www.pacioos.hawaii.edu/data/erddap/)

---

### 3.2 HYCOM (HYbrid Coordinate Ocean Model)

**Overview**: Global ocean model providing currents, temperature, and salinity via OPeNDAP/THREDDS.

| Attribute | Details |
|-----------|---------|
| **API Type** | OPeNDAP, THREDDS, NCSS |
| **Base URL** | `https://tds.hycom.org/thredds/` |
| **Authentication** | None required |
| **Data Format** | NetCDF |
| **Resolution** | 1/12 degree global, 1/25 degree regional |

**Available Datasets**:
- HYCOM + NCODA Global 1/12 Analysis (2008-present)
- HYCOM + NCODA Global 1/12 Reanalysis (1992-2012)
- HYCOM + NCODA Gulf of Mexico 1/25 Analysis (2003-present)

**Data Variables**:
- Water temperature
- Salinity
- Eastward current (water_u)
- Northward current (water_v)
- Sea surface height

**OPeNDAP URL Pattern**:
```
https://tds.hycom.org/thredds/dodsC/GLBv0.08/expt_93.0/uv3z
```

**NCEI ERDDAP**:
```
https://www.ncei.noaa.gov/erddap/griddap/Hycom_sfc_3d.html
```

**Sources**:
- [HYCOM Data Server](https://www.hycom.org/dataserver)
- [HYCOM THREDDS](https://www.hycom.org/dataserver/294-thredds)

---

### 3.3 Open-Meteo Marine API

**Overview**: Free, open-source API aggregating multiple wave models globally.

| Attribute | Details |
|-----------|---------|
| **API Type** | REST API |
| **Base URL** | `https://api.open-meteo.com/v1/marine` |
| **Authentication** | None required |
| **Rate Limits** | None for non-commercial use |
| **Data Format** | JSON |
| **License** | CC BY 4.0 |

**Data Sources Aggregated**:
- DWD (German Weather Service) - 28km global
- Copernicus Marine (MeteoFrance) - 5km European
- ECMWF
- NOAA NCEP

**Data Variables**:
- Wave height, period, direction (total, wind waves, swell)
- Ocean currents (velocity, direction)
- Sea surface temperature
- Sea level height (with tides)

**Example Request**:
```
https://api.open-meteo.com/v1/marine?
  latitude=52.52
  &longitude=13.41
  &hourly=wave_height,wave_direction,wave_period,
          ocean_current_velocity,ocean_current_direction,
          sea_surface_temperature
```

**Forecast Range**: 7 days hourly

**Historical Data**: Available via API

**Sources**:
- [Open-Meteo Marine API](https://open-meteo.com/en/docs/marine-weather-api)
- [GitHub Repository](https://github.com/open-meteo/open-meteo)

---

### 3.4 Storm Glass API

**Overview**: Commercial API aggregating multiple meteorological sources for marine weather.

| Attribute | Details |
|-----------|---------|
| **API Type** | REST API |
| **Base URL** | `https://api.stormglass.io/v2/` |
| **Authentication** | API Key required |
| **Rate Limits** | Tiered by subscription |
| **Data Format** | JSON |

**Data Sources**:
- NOAA
- Meteo-France
- UK Met Office
- DWD (Germany)
- FCOO (Denmark)
- FMI (Finland)
- YR (Norway)
- SMHI (Sweden)
- ICON (global)

**Data Variables**:
- Wave height, direction, period
- Swell (primary, secondary)
- Wind waves
- Currents (speed, direction)
- SST
- Tides
- Ice cover/thickness

**Pricing**: Free tier available; paid plans for commercial use

**Forecast Range**: Up to 10 days

**Sources**:
- [Storm Glass Marine Weather](https://stormglass.io/marine-weather/)
- [Storm Glass Pricing](https://stormglass.io/pricing/)

---

### 3.5 Sofar Ocean (Spotter API)

**Overview**: Commercial API for Spotter buoy network data - largest privately-owned marine weather sensor network.

| Attribute | Details |
|-----------|---------|
| **API Type** | REST API |
| **Documentation** | `https://docs.sofarocean.com/` |
| **Authentication** | API Key required (device owners) |
| **Data Format** | JSON |

**Data Collected**:
- Wave spectra
- Wind speed/direction
- Sea surface temperature
- Atmospheric pressure
- Smart Mooring extensions (water level, subsurface temp)

**Network**: 1.5+ million daily observations globally

**Use Case**: Primarily for Spotter device owners; data available for research partnerships

**Sources**:
- [Sofar Spotter Platform](https://www.sofarocean.com/products/spotter)
- [Sofar API Documentation](https://docs.sofarocean.com/spotter-and-smart-mooring/spotter-data)

---

## 4. Comparison Matrix

| Source | Auth Required | Real-time | Historical | Waves | Currents | SST | Tides | Format |
|--------|--------------|-----------|------------|-------|----------|-----|-------|--------|
| NOAA NDBC | No | Yes | 45 days | Yes | Yes | Yes | No | Text |
| NOAA CO-OPS | No | Yes | Yes | No | Yes | Discontinued | Yes | JSON/XML/CSV |
| CMEMS | Yes (Free) | Yes | 1993+ | Yes | Yes | Yes | No | NetCDF/JSON |
| ECMWF Open | No | Yes | Limited | Yes | Yes | Yes | No | GRIB2 |
| ECMWF CDS | Yes (Free) | Yes | Extensive | Yes | Yes | Yes | No | NetCDF/GRIB |
| MET Norway | No | Yes | Yes | Yes | Yes | Yes | No | JSON/NetCDF |
| UK Met Office | Yes | Yes | Limited | Yes | Yes | Yes | No | Various |
| BOM Australia | Partial | Yes | Yes | Yes | Yes | Yes | Yes | JSON |
| JMA Japan | No | Yes | Limited | Yes | Yes | Yes | Yes | Web/FTP |
| IOOS | No | Yes | Yes | Yes | Yes | Yes | No | NetCDF/JSON |
| HYCOM | No | No | 1992+ | No | Yes | Yes | No | NetCDF |
| Open-Meteo | No | Yes | Yes | Yes | Yes | Yes | Yes | JSON |
| Storm Glass | Yes | Yes | Yes | Yes | Yes | Yes | Yes | JSON |
| Sofar | Yes | Yes | Yes | Yes | No | Yes | Yes* | JSON |

---

## 5. Recommended Integration Priority

### Tier 1 - High Priority (Open Access, Comprehensive)
1. **NOAA NDBC** - Best US buoy/coastal data, no auth
2. **NOAA CO-OPS** - Excellent tides/currents API
3. **Open-Meteo Marine** - Free global coverage, JSON API
4. **IOOS ERDDAP** - Extensive US regional data

### Tier 2 - Medium Priority (Registration Required)
5. **Copernicus Marine (CMEMS)** - Best European/global analysis
6. **ECMWF Open Data** - High-quality forecasts
7. **MET Norway** - Excellent Northwest Europe coverage

### Tier 3 - Specialized/Regional
8. **HYCOM** - Ocean model data for currents
9. **UK Met Office** - UK/European shelf seas
10. **BOM Australia** - Australian waters
11. **JMA** - Northwest Pacific

### Tier 4 - Commercial/Partnerships
12. **Storm Glass** - Multi-source aggregation
13. **Sofar Ocean** - Device-based network

---

## 6. Implementation Recommendations

### 6.1 Suggested Module Structure
```
src/worldenergydata/modules/metocean/
    __init__.py
    config.py           # API keys, endpoints
    constants.py        # Enums, region definitions

    clients/
        base_client.py      # Abstract base class
        ndbc_client.py      # NOAA NDBC
        coops_client.py     # NOAA Tides & Currents
        cmems_client.py     # Copernicus Marine
        openmeteo_client.py # Open-Meteo Marine
        met_norway_client.py
        hycom_client.py
        ioos_erddap_client.py

    data/
        cache_manager.py    # Data caching
        downloaders.py      # Bulk download utilities

    analysis/
        wave_analysis.py
        current_analysis.py
        climatology.py

    cli.py              # CLI commands
```

### 6.2 Key Design Patterns
- **Abstract base client** for consistent interface across sources
- **Caching layer** for expensive API calls
- **Rate limiting** built into each client
- **Async support** for bulk downloads
- **Data normalization** to common schema (CF conventions)

### 6.3 Priority Data Types for Energy Applications
1. **Waves** - Offshore platform/vessel operations
2. **Currents** - Subsea operations, pipeline design
3. **Wind** - Offshore wind farms
4. **SST** - Environmental monitoring
5. **Tides** - Port operations, platform access

---

## 7. Sources Summary

### Official Documentation
- [NDBC Data Access](https://www.ndbc.noaa.gov/faq/rt_data_access.shtml)
- [NOAA CO-OPS API](https://api.tidesandcurrents.noaa.gov/api/prod/)
- [Copernicus Marine Service](https://marine.copernicus.eu/access-data/)
- [ECMWF Open Data](https://www.ecmwf.int/en/forecasts/datasets/open-data)
- [MET Norway API](https://api.met.no/)
- [IOOS Data Access](https://ioos.noaa.gov/data/access-ioos-data/)
- [HYCOM Data Server](https://www.hycom.org/dataserver)
- [Open-Meteo Marine API](https://open-meteo.com/en/docs/marine-weather-api)
- [Storm Glass API](https://stormglass.io/marine-weather/)

### Python Libraries
- [ndbc-api](https://github.com/CDJellen/ndbc-api)
- [copernicusmarine](https://pypi.org/project/copernicusmarine/)
- [ecmwf-opendata](https://github.com/ecmwf/ecmwf-opendata)
- [cdsapi](https://github.com/ecmwf/cdsapi)
- [metocean-api](https://metocean-api.readthedocs.io/)
- [erddapy](https://github.com/ioos/erddapy)
