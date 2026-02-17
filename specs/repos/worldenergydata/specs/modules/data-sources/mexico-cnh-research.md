# Mexico CNH Data Sources Research

> **Date**: 2026-01-26
> **Status**: Complete

## Data Portals

### Primary Portals
| Portal | URL | Purpose |
|--------|-----|---------|
| **SIH** | https://sih.hidrocarburos.gob.mx/ | Interactive statistics dashboard |
| **Producción** | https://produccion.hidrocarburos.gob.mx/ | Production dashboard (public testing) |
| **Mapa** | https://mapa.hidrocarburos.gob.mx/ | Spatial/geographic data |
| **Datos Abiertos** | https://datos.gob.mx/busca/organization/cnh | Open data platform |

### Secondary Resources
- **SENER SIH**: https://sih-hidrocarburos.energia.gob.mx/
- **PEMEX BDI**: https://ebdi.pemex.com/bdi/ (Institutional Database)

## About CNH

- **Comisión Nacional de Hidrocarburos** - Government regulator since 2009
- Manages **35,000+ wells** drilled since late 1800s
- **11+ petabytes** of seismic and well data
- Operates the National Data Repository (CNIH)

## Available Data

### Through SIH Dashboard
- National production volumes (oil, gas)
- Exploration/extraction statistics
- Contract area information
- Resources and reserves
- Field and well information

### Through Open Data Portal
- Well production data (pozos productores)
- Field information
- Operator statistics

### Through Map Portal
- Spatial well locations
- Contract areas
- Field boundaries
- Infrastructure

## Well Identifier Format (Clave del Pozo)

### Regulatory Framework
- Defined in **Lineamientos de perforación de pozos** (Well Drilling Guidelines)
- Detailed in **Anexo III** (Annex III): https://cnh.gob.mx/media/2556/pozos-anexo-iii.pdf
- All operators must follow CNH nomenclature standards

### General Format
Mexican well identifiers typically follow:
```
CAMPO-NUMERO[-TIPO]

Examples:
- CANTARELL-1
- AYIN-101
- KU-MALOOB-ZAAP-15D
```

### Components
- **Campo (Field)**: Field name
- **Número**: Sequential well number in field
- **Tipo (optional)**: Well type suffix (D=development, E=exploration)

### Historical PEMEX Naming
Older wells may use PEMEX-era naming conventions with different patterns.

## Implementation Strategy

### Approach: Selenium + Data Portal Parsing

**Why Selenium Required:**
- No public REST API available
- Interactive dashboards require JavaScript execution
- Data exports triggered via UI interactions
- Session/authentication handling

### Target Data Flows

1. **SIH Dashboard Scraping**
   - Navigate to well/production sections
   - Apply filters (date, field, operator)
   - Trigger Excel/CSV exports
   - Download and parse files

2. **Open Data Downloads**
   - Direct CSV downloads from datos.gob.mx
   - Less scraping required
   - More stable but less complete

3. **Map Portal Queries**
   - May have hidden API endpoints
   - Check network traffic for REST calls

### Selenium Configuration

```yaml
selenium:
  browser: chrome
  headless: true
  implicit_wait: 10
  page_load_timeout: 60
  download_dir: ./data/mexico_cnh/downloads
  user_agent_rotation: false  # Conservative approach
  screenshot_on_failure: true
```

### Page Object Pattern

```python
class SIHDashboardPage:
    URL = "https://sih.hidrocarburos.gob.mx/"

    def navigate_to_production(self)
    def select_date_range(self, start, end)
    def select_field(self, field_name)
    def export_to_excel(self) -> Path
    def wait_for_download(self) -> Path
```

## Key Considerations

### Language
- Interface is in **Spanish**
- Column names in Spanish
- Need translation mapping for data fields

### Common Spanish Terms
| Spanish | English |
|---------|---------|
| Pozo | Well |
| Campo | Field |
| Producción | Production |
| Petróleo | Oil |
| Gas | Gas |
| Operador | Operator |
| Perforación | Drilling |
| Extracción | Extraction |

### Rate Limiting
- Be very conservative (1 req/sec max)
- Dashboard may be slow/unreliable
- Implement circuit breaker pattern

### Data Quality
- Historical data may have gaps
- Field names may change over time
- Some data only in PDF reports

## Coordinates

- **System**: UTM Zone 14/15 (depends on location)
- **Datum**: WGS84 or ITRF92
- **Transform**: Will need UTM → WGS84 conversion

## Sources

- [SIH Dashboard](https://sih.hidrocarburos.gob.mx/)
- [CNH Official Site](https://www.gob.mx/cnh)
- [CNH Well Guidelines (Anexo III)](https://cnh.gob.mx/media/2556/pozos-anexo-iii.pdf)
- [Open Data Portal](https://datos.gob.mx/busca/organization/cnh)
