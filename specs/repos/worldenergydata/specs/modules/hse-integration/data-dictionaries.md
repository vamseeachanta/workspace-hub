# HSE Data Dictionaries

> Created: 2026-01-09
> Purpose: Map BSEE data sources to WorldEnergyData HSE database schema
> Status: Complete

## Overview

This document maps data fields from BSEE (Bureau of Safety and Environmental Enforcement) HSE data sources to the WorldEnergyData database schema. These mappings guide data import, validation, and transformation logic.

## Database Schema Summary

### Five SQLAlchemy Models:

1. **HSEIncident** - Base incident model (all incident types inherit from this)
2. **InjuryIncident** - Personnel injury incidents
3. **SpillIncident** - Oil/chemical spill incidents
4. **ViolationIncident** - Regulatory violations and civil penalties
5. **EquipmentFailure** - Equipment failure incidents

---

## Data Source 1: BSEE Incident Investigation Database

**Source URL**: https://www.bsee.gov/what-we-do/incident-investigations/offshore-incident-investigations

**Data Format**: PDF investigation reports (Panel and District reports), incident summaries

**Access Method**: Public download of PDF reports

### Reportable Incidents (30 CFR 250.188)

**Regulatory Definition**: Incidents requiring BSEE notification and investigation include:
- Fatalities
- Injuries requiring evacuation for medical treatment
- Loss of well control
- Fires or explosions
- Collisions resulting in damage >$25,000
- Damage to safety systems
- Structural damage to platforms
- Crane incidents
- Unplanned evacuation

### Mapping: Investigation Reports → HSEIncident Base Model

| BSEE Report Field | Database Column | Data Type | Constraints | Notes |
|-------------------|-----------------|-----------|-------------|-------|
| Incident ID / Report Number | `bsee_incident_id` | String (50) | UNIQUE, NOT NULL | Primary identifier from BSEE |
| Incident Date | `incident_date` | DateTime | NOT NULL | Date/time of incident occurrence |
| Operator Name | `operator` | String (200) | NOT NULL, Index | Operating company name |
| Facility Name | `facility_name` | String (200) | Index | Platform, rig, or vessel name |
| Lease Number | `lease_number` | String (50) | Index | OCS lease identifier |
| Block Number | `block_number` | String (50) | Index | Geographic block designation |
| Field Name | `field_name` | String (100) | Index | Field name if applicable |
| Latitude | `latitude` | Float | Range: 18-31 (GOM) | Decimal degrees |
| Longitude | `longitude` | Float | Range: -98 to -80 (GOM) | Decimal degrees |
| Incident Type | `incident_type` | Enum | Values: injury, spill, equipment_failure, violation | Primary classification |
| Severity | `severity` | Enum | Values: fatality, lost_time, recordable, near_miss, minor | Incident severity level |
| Incident Description | `description` | Text | NULL allowed | Narrative description |
| Root Cause | `root_cause` | Text | NULL allowed | Determined root cause |
| Corrective Actions | `corrective_actions` | Text | NULL allowed | Actions taken/planned |
| Investigation Status | `investigation_status` | String (50) | NULL allowed | Open, Closed, In Progress |
| Report Date | `created_at` | DateTime | Auto-generated | Record creation timestamp |
| Last Updated | `updated_at` | DateTime | Auto-updated | Record modification timestamp |

### Mapping: Investigation Reports → InjuryIncident Model

**Applies to incidents where `incident_type = 'injury'`**

| BSEE Report Field | Database Column | Data Type | Constraints | Notes |
|-------------------|-----------------|-----------|-------------|-------|
| Incident ID | `id` | Integer | FOREIGN KEY → hse_incidents.id | Links to base incident |
| Injury Type / Nature | `injury_type` | String (100) | NULL allowed | Fracture, laceration, burn, etc. |
| Body Part Affected | `body_part_affected` | String (100) | NULL allowed | Head, hand, back, etc. |
| Days Away from Work | `days_away_from_work` | Integer | >= 0 | Lost work days (0 if none) |
| Restricted Duty Days | `restricted_duty_days` | Integer | >= 0 | Days on light duty |
| Medical Treatment Required | `medical_treatment` | Boolean | NOT NULL | True if medical care needed |
| Hospitalization Required | `hospitalization_required` | Boolean | NOT NULL | True if admitted to hospital |

**Injury Severity Classification Logic**:
- **Fatality**: Death occurred
- **Lost Time**: `days_away_from_work > 0`
- **Recordable**: Medical treatment required OR `days_away_from_work > 0` OR `restricted_duty_days > 0`
- **Near Miss**: No injury but potential for injury
- **Minor**: First aid only, no lost time

**Data Quality Issues**:
- Injury descriptions vary in detail across reports
- Body part terminology not standardized (need normalization)
- Days away from work sometimes estimated if worker hasn't returned
- Medical treatment vs first aid distinction can be unclear

---

## Data Source 2: BSEE Civil Penalties Database

**Source URL**: https://www.bsee.gov/what-we-do/safety-enforcement/civil-penalties-program

**Data Format**: Tabular data by fiscal year (CSV/Excel likely available)

**Access Method**: Public download or web scraping from BSEE enforcement portal

### Civil Penalties Program Overview

**Maximum Penalty**: $55,764 per day per violation (adjusted annually for inflation)

**Violation Types**:
- Threats to life (including aquatic life)
- Threats to property
- Threats to mineral deposits
- Threats to marine, coastal, or human environment
- Oil spill financial responsibility violations

**Penalty Process**:
1. INC (Incident of Non-Compliance) issued
2. Operator fails to correct OR harm/threat occurs
3. Civil penalty assessed
4. Operator pays or appeals

### Mapping: Civil Penalties → HSEIncident Base Model

| BSEE Penalty Field | Database Column | Data Type | Constraints | Notes |
|-------------------|-----------------|-----------|-------------|-------|
| INC Number | `bsee_incident_id` | String (50) | UNIQUE, NOT NULL | INC identifier |
| Incident Date | `incident_date` | DateTime | NOT NULL | Date violation occurred |
| Operator Name | `operator` | String (200) | NOT NULL, Index | Operating company |
| Facility Name | `facility_name` | String (200) | Index | Platform/rig where violation occurred |
| Lease Number | `lease_number` | String (50) | Index | OCS lease |
| Field Name | `field_name` | String (100) | Index | Field if applicable |
| Incident Type | `incident_type` | Enum | Fixed: 'violation' | All penalty records are violations |
| Severity | `severity` | Enum | Derived from penalty amount | See severity mapping below |
| Description | `description` | Text | NULL allowed | Violation description |

### Mapping: Civil Penalties → ViolationIncident Model

**Applies to incidents where `incident_type = 'violation'`**

| BSEE Penalty Field | Database Column | Data Type | Constraints | Notes |
|-------------------|-----------------|-----------|-------------|-------|
| INC ID | `id` | Integer | FOREIGN KEY → hse_incidents.id | Links to base incident |
| Violation Type | `violation_type` | String (200) | NULL allowed | Category of violation |
| Regulation Cited | `regulation_cited` | String (200) | NULL allowed | CFR citation (e.g., 30 CFR 250.188) |
| Penalty Amount | `penalty_amount` | Float | >= 0 | Dollar amount of penalty |
| Penalty Status | `penalty_status` | Enum | Values: proposed, assessed, paid, appealed | Current status |
| Compliance Deadline | `compliance_deadline` | DateTime | NULL allowed | Date to achieve compliance |
| Compliance Status | `compliance_status` | Enum | Values: open, closed, overdue | Compliance tracking |

**Severity Mapping from Penalty Amount**:
- **Critical**: Penalty >= $200,000 (severe violations)
- **Lost Time**: Penalty >= $50,000 and < $200,000 (serious violations)
- **Recordable**: Penalty >= $10,000 and < $50,000 (moderate violations)
- **Minor**: Penalty < $10,000 (administrative violations)

**Data Quality Issues**:
- Penalty amounts may be reduced on appeal (track original vs final)
- Some violations span multiple dates (use earliest date)
- Violation type categorization not standardized in source data
- CFR citations sometimes missing or incomplete

**Regulation Citation Examples**:
- 30 CFR 250.188 - Reporting of incidents
- 30 CFR 250.198 - Well control
- 30 CFR 250.401 - Platforms and structures
- 30 CFR 250.1000 - Plugging and abandonment

---

## Data Source 3: BSEE Safety Statistics Portal

**Source URL**: https://www.data.bsee.gov/ (BSEE Data Center)

**Alternate URLs**:
- https://www.bsee.gov/newsroom/library/annual-report (Annual Reports)
- https://www.bsee.gov/stats-facts/offshore-incident-statistics (Incident Statistics)
- https://www.bsee.gov/stats-facts/offshore-incident-statistics/spills-archive (Spills 1964-present)

**Data Format**: Online query interface, downloadable datasets (CSV/Excel), annual PDF reports

**Access Method**: Web scraping with Scrapy/Selenium, direct downloads where available

### Data Center Query Results

**Available Data**:
- Company approvals
- Incidents of Non-Compliance (INCs)
- Platform structures
- Pipeline information
- Offshore statistics (aggregated)

### Mapping: Aggregated Statistics → Safety Metrics

**Note**: This data source provides aggregated statistics, NOT individual incident records. Used for validation and benchmarking, not primary incident data.

| BSEE Statistic | Use in WorldEnergyData | Data Type | Notes |
|----------------|------------------------|-----------|-------|
| Total Recordable Incidents (by year) | Validate TRIR calculations | Integer | Industry benchmark |
| Lost Time Incidents (by year) | Validate LTIR calculations | Integer | Industry benchmark |
| Fatalities (by year) | Validate fatality counts | Integer | Critical metric |
| Total Spills (by year) | Validate spill counts | Integer | Environmental metric |
| Total Spill Volume (by year) | Validate spill intensity | Float (barrels) | Environmental metric |
| Total Man-Hours Worked (by year) | Safety metrics denominator | Float | Industry-wide exposure |

**Safety Metrics Formulas (for validation)**:
- **TRIR** = (Recordable Incidents × 200,000) / Total Man-Hours
- **LTIR** = (Lost Time Incidents × 200,000) / Total Man-Hours
- **Spill Intensity** = Total Spill Volume / Total Production Volume

### Mapping: Spills Archive → SpillIncident Model

**Spills Archive URL**: https://www.bsee.gov/stats-facts/offshore-incident-statistics/spills-archive

**Historical Data**: 1964-present spill summaries

| BSEE Spills Field | Database Column | Data Type | Constraints | Notes |
|-------------------|-----------------|-----------|-------------|-------|
| Spill Date | `incident_date` | DateTime | NOT NULL | Date of spill occurrence |
| Operator | `operator` | String (200) | NOT NULL | Operating company |
| Facility | `facility_name` | String (200) | Index | Platform or vessel |
| Lease/Block | `lease_number`, `block_number` | String (50) | Index | Geographic identifiers |
| Substance Type | `substance_type` | String (100) | NULL allowed | Crude oil, condensate, drilling fluid, etc. |
| Volume (barrels) | `volume_barrels` | Float | > 0 | Spill volume in barrels |
| Volume (gallons) | `volume_gallons` | Float | > 0 | Auto-calculated: barrels × 42 |
| Cause | `root_cause` | Text | NULL allowed | Spill cause description |
| Environmental Impact | `environmental_impact` | Text | NULL allowed | Impact assessment |
| Cleanup Status | `cleanup_status` | String (50) | NULL allowed | Open, In Progress, Completed |
| Cleanup Cost | `cleanup_cost` | Float | >= 0 | Dollar amount if available |

**Spill Severity Classification**:
- **Major Spill**: Volume >= 50 barrels (2,100 gallons)
- **Moderate Spill**: Volume >= 10 barrels and < 50 barrels
- **Minor Spill**: Volume < 10 barrels

**Substance Type Taxonomy**:
- **Crude Oil**: Raw petroleum
- **Condensate**: Light hydrocarbon liquid
- **Diesel**: Fuel oil
- **Drilling Fluid**: Mud system components
- **Produced Water**: Formation water
- **Hydraulic Fluid**: Equipment hydraulic systems
- **Other Chemicals**: Various process chemicals

**Data Quality Issues**:
- Historical data (pre-2000) may have incomplete volume estimates
- Substance type terminology evolves over time (need normalization)
- Cleanup cost often not reported for minor spills
- Environmental impact assessments vary in detail

---

## Data Source 4: BSEE Equipment Failure Reports (SafeOCS Program)

**Source**: SafeOCS near-miss and equipment failure reporting program

**Data Format**: Annual PDF reports with aggregated statistics, District Investigation Reports

**Access Method**: PDF parsing, manual data entry for historical reports

### 2017 Equipment Failure Statistics (Reference Data)

**Total Failures**: 1,129 blowout preventer (BOP) component failures in Gulf of Mexico

**Failure Distribution**:
- Subsea failures: 1,044 (92.5%)
- Surface failures: 85 (7.5%)
- Failures when rigs NOT operating: 902 (83.8%)
- Failures when rigs operating: 127 (16.2%)

**Failure Type Breakdown**:
- External leaks: 49%
- Internal leaks: 24.4%
- Mechanical damage: 7.2%
- Control system: 4.1%
- Other: 15.3%

### Mapping: Equipment Failures → HSEIncident Base Model

| SafeOCS Field | Database Column | Data Type | Constraints | Notes |
|---------------|-----------------|-----------|-------------|-------|
| Failure Report ID | `bsee_incident_id` | String (50) | UNIQUE, NOT NULL | Report identifier |
| Failure Date | `incident_date` | DateTime | NOT NULL | Date failure occurred |
| Operator | `operator` | String (200) | NOT NULL | Operating company |
| Facility | `facility_name` | String (200) | Index | Rig/platform name |
| Lease/Block | `lease_number`, `block_number` | String (50) | Index | Location identifiers |
| Incident Type | `incident_type` | Enum | Fixed: 'equipment_failure' | All SafeOCS records |
| Severity | `severity` | Enum | Derived from impact | See severity mapping below |
| Description | `description` | Text | NULL allowed | Failure description |

### Mapping: Equipment Failures → EquipmentFailure Model

**Applies to incidents where `incident_type = 'equipment_failure'`**

| SafeOCS Field | Database Column | Data Type | Constraints | Notes |
|---------------|-----------------|-----------|-------------|-------|
| Report ID | `id` | Integer | FOREIGN KEY → hse_incidents.id | Links to base incident |
| Equipment Type | `equipment_type` | String (100) | NOT NULL | BOP, crane, HVAC, etc. |
| Equipment ID / Serial | `equipment_id` | String (100) | NULL allowed | Specific equipment identifier |
| Failure Mode | `failure_mode` | String (200) | NULL allowed | External leak, internal leak, mechanical, etc. |
| Downtime Hours | `downtime_hours` | Float | >= 0 | Hours out of service |
| Repair Cost | `repair_cost` | Float | >= 0 | Dollar amount if available |
| PM Status | `preventive_maintenance_status` | String (50) | NULL allowed | Last maintenance date/status |

**Equipment Type Taxonomy**:
- **BOP (Blowout Preventer)**: Annular, ram, control system
- **Crane**: Pedestal crane, overhead crane
- **HVAC**: Heating, ventilation, air conditioning
- **Fire/Gas Systems**: Detection and suppression
- **Power Generation**: Generators, electrical distribution
- **Drilling Equipment**: Top drive, mud pumps, rotary table
- **Production Equipment**: Separators, compressors, pumps
- **Safety Systems**: ESD, gas detection, fire suppression

**Failure Mode Categories**:
- **External Leak**: Fluid leaking to external environment
- **Internal Leak**: Fluid bypassing seals internally
- **Mechanical Damage**: Structural damage, wear, fatigue
- **Control System Failure**: Instrumentation, electrical, software
- **Hydraulic Failure**: Hydraulic system malfunction
- **Corrosion**: Material degradation
- **Fatigue**: Cyclic loading failure
- **Human Error**: Incorrect operation or maintenance

**Severity Mapping for Equipment Failures**:
- **Critical**: Failure resulted in shutdown, well control event, or safety system failure
- **Lost Time**: Downtime > 24 hours OR repair cost > $100,000
- **Recordable**: Downtime > 4 hours OR repair cost > $10,000
- **Near Miss**: Failure detected before causing downtime (preventive maintenance)
- **Minor**: Downtime < 4 hours AND repair cost < $10,000

**Data Quality Issues**:
- Equipment IDs not always recorded consistently
- Downtime hours estimates vary in accuracy
- Repair costs often incomplete or unavailable
- PM status tracking inconsistent across operators
- Failure mode descriptions vary in technical detail

---

## Data Normalization Requirements

### Operator Name Normalization

**Issue**: Company names appear in multiple formats across BSEE sources
- "Shell Offshore Inc."
- "Shell Offshore, Inc."
- "Shell Offshore"
- "Shell"

**Solution**: Create operator name normalization lookup table
```python
OPERATOR_NORMALIZATION = {
    'shell offshore inc': 'Shell Offshore Inc.',
    'shell offshore, inc.': 'Shell Offshore Inc.',
    'shell offshore': 'Shell Offshore Inc.',
    'bp exploration & production': 'BP Exploration & Production Inc.',
    'chevron usa inc': 'Chevron U.S.A. Inc.',
    # ... additional mappings
}
```

### Geographic Coordinate Validation

**Gulf of Mexico Boundaries**:
- Latitude: 18°N to 31°N
- Longitude: -98°W to -80°W

**Validation Rules**:
- Reject coordinates outside GOM boundaries
- Flag coordinates on land (compare to coastline database)
- Verify lease/block matches coordinate location

### Date/Time Handling

**BSEE Date Formats Observed**:
- MM/DD/YYYY
- YYYY-MM-DD
- "Month DD, YYYY"
- Sometimes only year available for historical data

**Standardization**:
- Convert all to ISO 8601: YYYY-MM-DDTHH:MM:SS
- If time unknown, use 00:00:00
- If day unknown, use 01
- Store timezone as UTC

### Volume Conversions

**Oil/Chemical Volume**:
- BSEE reports in barrels AND gallons
- 1 barrel = 42 US gallons
- Store both: `volume_barrels` and `volume_gallons`
- Auto-calculate if only one value provided

**Production Volume** (for spill intensity):
- Production reported in barrels of oil equivalent (BOE)
- Natural gas converted: 6,000 cubic feet = 1 BOE

---

## Data Validation Rules

### Required Fields Validation

**HSEIncident Base Model**:
- `bsee_incident_id`: Must be unique across all incidents
- `incident_date`: Must be valid date, not future date
- `operator`: Must not be empty string, max 200 characters
- `incident_type`: Must be one of: injury, spill, equipment_failure, violation
- `severity`: Must be one of: fatality, lost_time, recordable, near_miss, minor

### Cross-Model Validation

**InjuryIncident**:
- If `severity = 'fatality'` in base model, `days_away_from_work` should be NULL
- If `severity = 'lost_time'`, `days_away_from_work` must be > 0
- `days_away_from_work` + `restricted_duty_days` should be reasonable (< 365 days)

**SpillIncident**:
- `volume_barrels` and `volume_gallons` must be consistent (barrels × 42 = gallons)
- If `severity = 'major'`, `volume_barrels` should be >= 50
- `cleanup_cost` should be reasonable relative to `volume_barrels`

**ViolationIncident**:
- If `penalty_status = 'paid'`, `penalty_amount` must be > 0
- If `compliance_status = 'overdue'`, `compliance_deadline` must be past date
- `regulation_cited` should match CFR format: "30 CFR XXX.XXX"

**EquipmentFailure**:
- If `downtime_hours` > 0, `repair_cost` should typically be > 0
- If `severity = 'critical'`, `downtime_hours` should be > 24
- `equipment_type` should match taxonomy

### Referential Integrity

**Well/Operator Linkage**:
- `lease_number` + `block_number` should match existing BSEE production database
- `operator` should match operator of record for lease
- `field_name` should match known field names in production database

**Temporal Validation**:
- `incident_date` should be within operational period of `facility_name`
- `incident_date` should be after lease `effective_date`

---

## Data Import Priority and Sequencing

### Phase 1: Historical Data Bootstrap (Recommended Order)

1. **Start with Civil Penalties Database** (simplest structure)
   - Well-structured tabular data
   - Complete penalty records with amounts
   - Tests ViolationIncident model
   - Estimated records: 5,000-10,000 (2000-present)

2. **Import Spills Archive** (1964-present)
   - Historical spill summaries available
   - Tests SpillIncident model
   - Establishes baseline environmental metrics
   - Estimated records: 20,000-30,000 spills

3. **Import Equipment Failure Reports** (annual summaries)
   - Tests EquipmentFailure model
   - Validates safety metrics calculations
   - Estimated records: 10,000-15,000 failures

4. **Import Incident Investigation Reports** (most complex)
   - PDF parsing required
   - Tests HSEIncident + InjuryIncident models
   - Most detailed incident information
   - Estimated records: 3,000-5,000 investigations

### Phase 2: Ongoing Updates

- **Weekly**: Check for new investigation reports
- **Monthly**: Import new civil penalties data
- **Quarterly**: Update equipment failure statistics
- **Annually**: Import SafeOCS annual report data

---

## Estimated Record Counts (Gulf of Mexico, 2000-2025)

| Data Source | Estimated Records | Update Frequency |
|-------------|------------------|------------------|
| Civil Penalties (INCs) | 8,000-12,000 | Weekly |
| Spills (all sizes) | 25,000-35,000 | Monthly |
| Equipment Failures | 12,000-18,000 | Quarterly |
| Incident Investigations | 4,000-6,000 | Weekly |
| **Total HSE Incidents** | **49,000-71,000** | Varies |

**Storage Requirements**:
- Average incident record: ~2 KB (with TEXT fields)
- Total database size estimate: 100-150 MB (incidents only)
- With indexes and relationships: 200-250 MB

---

## Data Quality Scoring

### Quality Dimensions

**Completeness Score** (0-100):
- Required fields populated: 40 points
- Optional fields populated: 30 points
- Related records linked: 20 points
- Geographic coordinates present: 10 points

**Accuracy Score** (0-100):
- Coordinates within valid range: 25 points
- Operator name normalized: 25 points
- Dates valid and reasonable: 25 points
- Cross-validation with production data: 25 points

**Timeliness Score** (0-100):
- Reported within 24 hours: 100 points
- Reported within 1 week: 75 points
- Reported within 1 month: 50 points
- Reported > 1 month: 25 points

**Overall Data Quality Score**:
```
Overall Score = (Completeness × 0.4) + (Accuracy × 0.4) + (Timeliness × 0.2)
```

**Quality Thresholds**:
- **Excellent**: Score >= 90
- **Good**: Score >= 75 and < 90
- **Fair**: Score >= 60 and < 75
- **Poor**: Score < 60

Flag records with Poor quality for manual review.

---

## Implementation Notes for Importers

### Base Importer Class Requirements

**All importers must implement**:
1. `validate_required_fields()` - Check required fields present
2. `normalize_operator_name()` - Standardize company names
3. `validate_coordinates()` - Check lat/long within range
4. `parse_date()` - Handle multiple date formats
5. `calculate_quality_score()` - Compute data quality metrics
6. `deduplicate_incidents()` - Detect duplicate records
7. `link_to_production_data()` - Match to wells/leases

### Deduplication Strategy

**Primary Key**: `bsee_incident_id` (unique across all sources)

**Fuzzy Matching** (when BSEE ID missing):
- Match on: `operator` + `facility_name` + `incident_date` (within 24 hours)
- If multiple matches, select record with highest quality score
- Flag potential duplicates for manual review

### Error Handling

**Invalid Data Actions**:
- **Missing required field**: Log error, skip record, continue import
- **Invalid enum value**: Log warning, use "other" or NULL, continue import
- **Out-of-range coordinate**: Log warning, set coordinate to NULL, continue import
- **Future date**: Log error, skip record, continue import
- **Duplicate incident_id**: Log error, skip record, continue import

**Error Logging**:
- Store import errors in separate `hse_import_errors` table
- Include: timestamp, source file, line number, error type, error message, raw data
- Generate import summary report after each run

---

## Version History

| Version | Date | Changes | Author |
|---------|------|---------|--------|
| 1.0.0 | 2026-01-09 | Initial data dictionary creation | AI Agent (research phase) |

---

**End of Data Dictionaries Document**

This document completes Phase 1 Task 1.5. Next phase: Database Schema Implementation (Phase 2) with TDD approach.
