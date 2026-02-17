# Canada AER/BCER Data Sources Research

> **Date**: 2026-01-26
> **Status**: Complete

## Alberta Energy Regulator (AER) / Petrinex

### Data Portal
- **Petrinex Public Data**: https://www.petrinex.ca/PD/Pages/APD.aspx
- **AER Data Hub**: https://www.aer.ca/providing-information/data-and-reports/data-hub
- **AER General Well Data**: https://www.aer.ca/providing-information/data-and-reports/activity-and-data/general-well-data

### API Access
```
https://www.petrinex.gov.ab.ca/publicdata/API/Files/{Jurisdiction}/Infra/{FileName}/{FileFormat}
```

### Available Data (CSV/XML)

| Dataset | Update Frequency | Notes |
|---------|-----------------|-------|
| Well Infrastructure | Daily | Basic well info |
| Conventional Volumetrics | Daily | Production (5 year rolling) |
| Facility Licence | Daily | Facility data |
| Vent Flow/Gas Migration | Daily | Safety data |
| Well Casing Failures | Daily | Integrity issues |
| Well Pad ID | Daily | Multi-well pads |
| Well Production Data File | Monthly | All Alberta 1962-present (~700K records) |

### Contact
- Information requests: informationrequest@aer.ca

---

## BC Energy Regulator (BCER)

### Data Portal
- **GIS Open Data Portal**: https://data-bc-er.opendata.arcgis.com/
- **Data Centre**: https://www.bc-er.ca/data-reports/data-centre/
- **Legacy Well Lookup**: https://www.bc-er.ca/energy-professionals/online-systems/reports-well-data/

### GIS Services
- **Type**: ArcGIS Online/Hub with REST API
- **WMS**: openmaps.gov.bc.ca
- **Formats**: GeoJSON, KML, CSV, Shapefile

### Coordinate System
- **CRS**: NAD_1983_BC_Environment_Albers
- **EPSG**: 3005
- **Geographic CRS**: NAD83

### Available Spatial Data Packages
- Administrative boundaries
- OGAA Associated Oil & Gas Activities
- Well and Facility locations
- Pipeline data
- Construction Corridors
- Geophysical data
- Water and Waste Disposal

### Contact
- Data inquiries: systems@bc-er.ca

---

## Canadian UWI (Unique Well Identifier) Format

### Standard
- **Developed by**: CAPP (Canadian Association of Petroleum Producers), 1965
- **Adopted by**: PPDM (Professional Petroleum Data Management)
- **Length**: 16 characters

### Format Structure
```
SSS.LL-SS-TTT-RRWM.EE

Example: 100.16-09-010-09W1.00

Position | Field | Description
---------|-------|------------
1        | S     | Survey System (1=DLS, 2=NTS, 3=FPS)
2-3      | SS    | Location Exception Code
4        | .     | Separator
5-6      | LL    | Legal Subdivision (01-16)
7        | -     | Separator
8-9      | SS    | Section (01-36)
10       | -     | Separator
11-13    | TTT   | Township (001-126)
14       | -     | Separator
15-16    | RR    | Range (01-34)
17       | W     | West of Meridian indicator
18       | M     | Meridian (1-6)
19       | .     | Separator
20-21    | EE    | Event Sequence Code (00-99)
```

### DLS (Dominion Land Survey) Format
- Used in Alberta, Saskatchewan, Manitoba
- Survey System Code: `1`
- Format: `1SS.LL-SS-TTT-RRWM.EE`

### NTS (National Topographic System) Format
- Used in BC, Yukon, NWT
- Survey System Code: `2`
- Format: `2SS.A-XX-Y-ZZZ-A-NN.EE`

### CWIS (Canadian Well Identification System) - New Standard
- Developed 2012-2014 by PPDM
- Three identifiers: Well ID, Wellbore ID, Well Reporting ID
- Permanent and unique (no amendments like UWI)
- Not limited to 99 event sequences

---

## Implementation Strategy

### Phase 1: AER/Petrinex
1. Implement Petrinex API client for CSV downloads
2. Parse well infrastructure and volumetric data
3. Handle UWI parsing (DLS format primary)

### Phase 2: BCER
1. Implement ArcGIS REST client
2. Query well/facility feature services
3. Handle NTS UWI format
4. Coordinate transformation (EPSG:3005 → WGS84)

### Shared Components
- UWI parser supporting both DLS and NTS formats
- Coordinate system utilities (NAD83 variants)
- Unit conversion (metric system)

---

## Key Differences from US Data

| Aspect | Canada | US (Texas/BSEE) |
|--------|--------|-----------------|
| Identifier | UWI (16 char) | API Number (10-14 digit) |
| Units | Metric (m³, m) | Imperial (bbl, ft) |
| Coordinate System | NAD83 variants | NAD27/WGS84 |
| Survey System | DLS/NTS | PLSS |

---

## Sources

- [Petrinex Alberta Public Data](https://www.petrinex.ca/PD/Pages/APD.aspx)
- [BCER GIS Open Data Portal](https://data-bc-er.opendata.arcgis.com/)
- [PPDM Canadian Well Identification System](https://ppdm.org/ppdm/PPDM/IPDS/Well_Identification/Canadian_Well_Id_System_Standard_/PPDM/CWIS_Standard.aspx)
- [AER UWI Description (PDF)](https://static.aer.ca/prd/documents/applications/UWI-Description.pdf)
