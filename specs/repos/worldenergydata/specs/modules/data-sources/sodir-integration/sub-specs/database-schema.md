# Database Schema

This is the database schema implementation for the spec detailed in @specs/modules/data-sources/sodir-integration/spec.md

> Created: 2025-07-23
> Version: 1.0.0

## Data Storage Strategy

Since WorldEnergyData uses a file-based storage approach with CSV, Excel, and YAML files rather than a traditional database, this specification defines the file structure and data schemas for SODIR data storage.

## File Structure Schema

### Base Directory Structure
```
data/modules/sodir/
├── cache/                          # API response cache
│   ├── blocks/                     # Cached block data by date
│   ├── wellbores/                  # Cached wellbore data by date  
│   ├── fields/                     # Cached field data by date
│   ├── discoveries/                # Cached discovery data by date
│   └── surveys/                    # Cached survey data by date
├── raw/                            # Raw JSON responses
│   ├── blocks_YYYY-MM-DD.json
│   ├── wellbores_YYYY-MM-DD.json
│   ├── fields_YYYY-MM-DD.json
│   ├── discoveries_YYYY-MM-DD.json
│   └── surveys_YYYY-MM-DD.json
├── processed/                      # Processed data files
│   ├── sodir_blocks.csv
│   ├── sodir_wellbores.csv
│   ├── sodir_fields.csv
│   ├── sodir_discoveries.csv
│   └── sodir_surveys.csv
└── analysis_data/                  # Analysis-ready datasets
    ├── combined_data_for_analysis/
    │   ├── all_sodir_blocks.csv
    │   ├── all_sodir_wells.csv
    │   └── sodir_bsee_combined.csv
    └── field_specific/
        └── [field_name]/
            ├── production_data.csv
            └── well_data.csv
```

## Data Schema Definitions

### Blocks Data Schema (sodir_blocks.csv)

| Column | Data Type | Description | Source Field |
|--------|-----------|-------------|--------------|
| npdid_block | int64 | Unique SODIR block identifier | npdidBlock |
| block_name | string | Block designation (e.g., "30/11") | blockName |
| block_area_km2 | float64 | Block area in square kilometers | blockArea |
| block_status | string | Current block status | blockStatus |
| allocation_date | datetime64 | Date block was allocated | allocationDate |
| expiry_date | datetime64 | Block allocation expiry date | expiryDate |
| operator_company | string | Current operator company | operatorCompany |
| geometry_wkt | string | Well-Known Text geometry | blockGeometry |
| geometry_centroid_lat | float64 | Centroid latitude (WGS84) | calculated |
| geometry_centroid_lng | float64 | Centroid longitude (WGS84) | calculated |
| water_depth_min_m | float64 | Minimum water depth in meters | waterDepthMin |
| water_depth_max_m | float64 | Maximum water depth in meters | waterDepthMax |
| main_area | string | Main geological area | mainArea |
| data_collection_date | datetime64 | Date data was collected | system |
| data_source | string | Always "SODIR" | system |

### Wellbores Data Schema (sodir_wellbores.csv)

| Column | Data Type | Description | Source Field |
|--------|-----------|-------------|--------------|
| npdid_wellbore | int64 | Unique SODIR wellbore identifier | npdidWellbore |
| wellbore_name | string | Official wellbore name | wellboreName |
| wellbore_type | string | Type (EXPLORATION, DEVELOPMENT, etc.) | wellboreType |
| wellbore_status | string | Current status | wellboreStatus |
| drilling_operator | string | Company operating the drilling | drillingOperator |
| spud_date | datetime64 | Date drilling commenced | spudDate |
| completion_date | datetime64 | Date drilling completed | completionDate |
| total_depth_m | float64 | Total depth in meters | totalDepth |
| water_depth_m | float64 | Water depth in meters | waterDepth |
| surface_latitude | float64 | Surface location latitude (WGS84) | converted from nsDeg |
| surface_longitude | float64 | Surface location longitude (WGS84) | converted from ewDeg |
| bottom_latitude | float64 | Bottom hole latitude (WGS84) | converted from bottomNsDeg |
| bottom_longitude | float64 | Bottom hole longitude (WGS84) | converted from bottomEwDeg |
| npdid_field | int64 | Associated field ID | npdidField |
| npdid_discovery | int64 | Associated discovery ID | npdidDiscovery |
| main_area | string | Main geological area | mainArea |
| drilling_facility | string | Drilling facility name | drillingFacility |
| entry_date | datetime64 | Date entered in SODIR | entryDate |
| data_collection_date | datetime64 | Date data was collected | system |
| data_source | string | Always "SODIR" | system |

### Fields Data Schema (sodir_fields.csv)

| Column | Data Type | Description | Source Field |
|--------|-----------|-------------|--------------|
| npdid_field | int64 | Unique SODIR field identifier | npdidField |
| field_name | string | Official field name | fieldName |
| field_operator | string | Current field operator | fieldOperator |
| discovery_date | datetime64 | Date of discovery | discoveryDate |
| field_status | string | Development status | fieldStatus |
| production_start_date | datetime64 | First production date | productionStartDate |
| recoverable_oil_mill_sm3 | float64 | Recoverable oil million Sm³ | recoverableOil |
| recoverable_gas_bill_sm3 | float64 | Recoverable gas billion Sm³ | recoverableGas |
| recoverable_condensate_mill_sm3 | float64 | Recoverable condensate million Sm³ | recoverableCondensate |
| remaining_oil_mill_sm3 | float64 | Remaining oil million Sm³ | remainingOil |
| remaining_gas_bill_sm3 | float64 | Remaining gas billion Sm³ | remainingGas |
| main_area | string | Main geological area | mainArea |
| supply_base | string | Primary supply base | supplyBase |
| field_center_latitude | float64 | Field center latitude (WGS84) | converted |
| field_center_longitude | float64 | Field center longitude (WGS84) | converted |
| water_depth_m | float64 | Water depth in meters | waterDepth |
| data_collection_date | datetime64 | Date data was collected | system |
| data_source | string | Always "SODIR" | system |

### Discoveries Data Schema (sodir_discoveries.csv)

| Column | Data Type | Description | Source Field |
|--------|-----------|-------------|--------------|
| npdid_discovery | int64 | Unique SODIR discovery identifier | npdidDiscovery |
| discovery_name | string | Official discovery name | discoveryName |
| discovery_year | int32 | Year of discovery | discoveryYear |
| hydrocarbon_type | string | Primary hydrocarbon (OIL, GAS, OIL/GAS) | hydrocarbon |
| resource_class | string | Resource classification | resourceClass |
| discovery_operator | string | Company making discovery | discoveryOperator |
| main_area | string | Main geological area | mainArea |
| discovery_latitude | float64 | Discovery location latitude (WGS84) | converted |
| discovery_longitude | float64 | Discovery location longitude (WGS84) | converted |
| water_depth_m | float64 | Water depth in meters | waterDepth |
| geological_age | string | Primary geological age | geologicalAge |
| data_collection_date | datetime64 | Date data was collected | system |
| data_source | string | Always "SODIR" | system |

### Surveys Data Schema (sodir_surveys.csv)

| Column | Data Type | Description | Source Field |
|--------|-----------|-------------|--------------|
| npdid_survey | int64 | Unique SODIR survey identifier | npdidSurvey |
| survey_name | string | Official survey name | surveyName |
| survey_type | string | Type of survey | surveyType |
| acquisition_year | int32 | Year of acquisition | acquisitionYear |
| survey_company | string | Company conducting survey | surveyCompany |
| survey_area_km2 | float64 | Survey area in square kilometers | surveyArea |
| main_area | string | Main geological area | mainArea |
| survey_geometry_wkt | string | Survey area geometry (WKT) | surveyGeometry |
| data_quality | string | Survey data quality rating | dataQuality |
| data_collection_date | datetime64 | Date data was collected | system |
| data_source | string | Always "SODIR" | system |

## Data Processing Rules

### Data Type Enforcement
- All date fields use pandas datetime64 with timezone-aware UTC timestamps
- Numeric fields with missing values use pandas nullable integer (Int64) and float (Float64) dtypes
- String fields are stored as pandas string dtype with null handling
- Coordinate fields are stored as float64 with 6 decimal places precision

### Data Validation Rules
- `npdid_*` fields must be positive integers and unique within each dataset
- Coordinate fields must be within Norwegian Continental Shelf bounds (approximately 4°E-32°E, 57°N-81°N)
- Date fields must be reasonable (not before 1900, not more than 1 year in future)
- Depth measurements must be positive values
- Resource estimates must be non-negative values

### Data Normalization
- Company names standardized using fuzzy matching against known operator list  
- Status codes mapped to standardized values for cross-regional comparison
- Coordinate systems converted from UTM zones to WGS84 decimal degrees
- Units converted from metric to imperial for specific analysis compatibility

## Index and Performance Considerations

### File Indexing Strategy
- Primary CSV files sorted by npdid for efficient lookups
- Date-partitioned cache files for temporal queries
- Compressed storage using gzip for large datasets

### Memory Optimization
- Categorical data types for repetitive string fields (status, company names)
- Chunked processing for large datasets exceeding available memory
- Lazy loading with pandas iterators for analysis workflows

### Integration with Existing BSEE Data
- Common field naming conventions where applicable (e.g., latitude, longitude, water_depth_m)
- Consistent data types for cross-regional analysis
- Unified analysis schema combining SODIR and BSEE data in sodir_bsee_combined.csv

## Cache Management

### Cache File Structure
```
data/modules/sodir/cache/
├── blocks/
│   ├── 2025-07-23_blocks.json     # Daily cache files
│   └── cache_metadata.yml         # Cache metadata and TTL info
├── wellbores/
│   ├── 2025-07-23_wellbores.json
│   └── cache_metadata.yml
└── [similar structure for other data types]
```

### Cache Metadata Schema (cache_metadata.yml)
```yaml
cache_info:
  created_date: "2025-07-23T10:30:00Z"
  expiry_date: "2025-07-24T10:30:00Z"
  ttl_hours: 24
  record_count: 15847
  file_size_mb: 12.3
  last_modified: "2025-07-23T10:30:00Z"
  checksum: "sha256:abc123..."
```

## Migration and Compatibility

### Version Management
- Schema version stored in each file header comment
- Backward compatibility maintained for major schema changes
- Migration scripts provided for schema updates

### BSEE Integration Points
- Consistent coordinate reference systems (WGS84 for all geographic data)
- Compatible date formats (ISO 8601 UTC timestamps)
- Standardized company name lookup tables
- Unified analysis ready datasets for cross-regional comparison