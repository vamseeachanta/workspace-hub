# Marine Safety Incidents Database - Comprehensive Specification

**Version:** 1.0.0
**Date:** 2025-10-02
**Status:** Planning
**Module:** HSE (Health, Safety, Environment) - Marine Safety

---

## Executive Summary

Create a comprehensive, global marine safety incidents database covering all types of marine operations (commercial, offshore energy, recreational, fishing) across all geographic regions. The system will automatically collect, normalize, and analyze incident data from 7 major sources with historical data going back as far as available. This will serve as a holistic HSE database for safety trend analysis, risk assessment, regulatory compliance, research, and operational benchmarking.

---

## Table of Contents

1. [Scope & Requirements](#scope--requirements)
2. [Database Schema](#database-schema)
3. [Data Sources](#data-sources)
4. [Module Structure](#module-structure)
5. [Data Collection Pipeline](#data-collection-pipeline)
6. [Analysis Capabilities](#analysis-capabilities)
7. [API Endpoints](#api-endpoints)
8. [Implementation Roadmap](#implementation-roadmap)
9. [Technical Stack](#technical-stack)

---

## Scope & Requirements

### Geographic Coverage
- ✅ **US Waters** - USCG, NTSB jurisdiction
- ✅ **International Waters** - IMO jurisdiction
- ✅ **All Regions** - Gulf of Mexico, North Sea, Pacific, Atlantic, Arctic, etc.

### Marine Operations Covered
- ✅ Commercial shipping vessels
- ✅ Offshore oil & gas operations (platforms, rigs, vessels)
- ✅ Recreational boating
- ✅ Fishing vessels
- ✅ Passenger vessels (cruise ships, ferries)
- ✅ Tugboats and workboats
- ✅ Support vessels

### Land & Shore Operations
- ✅ Shore-based facilities (ports, terminals, refineries)
- ✅ Offshore platforms/rigs (classified as "at sea")
- ✅ Land-based support operations (logistics, maintenance)
- ✅ Pipeline incidents (subsea and shoreline)
- ✅ Coastal facilities

### Time Period
- **Historical**: As far back as data sources provide (1990s+)
- **Current**: Ongoing automated updates
- **Target**: Minimum 25+ years of historical data

---

## Database Schema

### Overview
**Architecture**: Normalized relational database (Option B)
- Optimized for complex queries and analysis
- Maintains data integrity with foreign keys
- Supports efficient joins and aggregations
- CSV exports for compatibility

### Core Tables

#### 1. `incidents` (Primary Table)
```sql
CREATE TABLE incidents (
    -- Primary Key
    incident_id VARCHAR(50) PRIMARY KEY,

    -- Temporal Data
    incident_date DATE NOT NULL,
    incident_time TIME,
    report_date DATE,

    -- Location Data
    latitude DECIMAL(10, 8),
    longitude DECIMAL(11, 8),
    location_description TEXT,
    country_code VARCHAR(3),
    state_province VARCHAR(100),
    water_body VARCHAR(200),
    port_name VARCHAR(200),

    -- Incident Classification
    incident_type VARCHAR(100) NOT NULL,
    incident_subtype VARCHAR(100),
    severity_level VARCHAR(50),
    incident_category VARCHAR(100),

    -- Outcomes
    fatalities INT DEFAULT 0,
    injuries INT DEFAULT 0,
    missing_persons INT DEFAULT 0,
    property_damage_usd DECIMAL(15, 2),
    vessel_total_loss BOOLEAN DEFAULT FALSE,

    -- Environmental Impact
    environmental_impact BOOLEAN DEFAULT FALSE,
    oil_spill_volume_gallons DECIMAL(12, 2),
    chemical_spill BOOLEAN DEFAULT FALSE,
    wildlife_impact TEXT,

    -- Weather & Conditions
    weather_conditions VARCHAR(200),
    sea_state VARCHAR(100),
    visibility VARCHAR(100),
    wind_speed_knots INT,

    -- Investigation & Analysis
    root_cause TEXT,
    contributing_factors TEXT,
    investigation_status VARCHAR(100),
    regulatory_violations TEXT,
    corrective_actions TEXT,
    lessons_learned TEXT,

    -- Administrative
    reporting_agency VARCHAR(100),
    source_url TEXT,
    source_document_id VARCHAR(200),
    data_quality_score DECIMAL(3, 2),
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- Indexes for common queries
    INDEX idx_date (incident_date),
    INDEX idx_location (latitude, longitude),
    INDEX idx_type (incident_type),
    INDEX idx_severity (severity_level)
);
```

#### 2. `vessels`
```sql
CREATE TABLE vessels (
    vessel_id VARCHAR(50) PRIMARY KEY,
    vessel_name VARCHAR(200),
    imo_number VARCHAR(20) UNIQUE,
    vessel_type VARCHAR(100),
    vessel_subtype VARCHAR(100),
    flag_country VARCHAR(3),
    built_year INT,
    gross_tonnage INT,
    length_meters DECIMAL(8, 2),
    beam_meters DECIMAL(8, 2),
    engine_type VARCHAR(100),
    classification_society VARCHAR(100),
    owner_name VARCHAR(200),
    operator_name VARCHAR(200),
    INDEX idx_type (vessel_type),
    INDEX idx_flag (flag_country)
);
```

#### 3. `incident_vessels` (Junction Table)
```sql
CREATE TABLE incident_vessels (
    id INT AUTO_INCREMENT PRIMARY KEY,
    incident_id VARCHAR(50),
    vessel_id VARCHAR(50),
    vessel_role VARCHAR(100), -- 'primary', 'collision_partner', 'assisting', 'damaged'
    vessel_damage_level VARCHAR(50),
    vessel_position VARCHAR(100), -- 'at_fault', 'victim', 'neutral'
    FOREIGN KEY (incident_id) REFERENCES incidents(incident_id),
    FOREIGN KEY (vessel_id) REFERENCES vessels(vessel_id),
    INDEX idx_incident (incident_id),
    INDEX idx_vessel (vessel_id)
);
```

#### 4. `companies`
```sql
CREATE TABLE companies (
    company_id VARCHAR(50) PRIMARY KEY,
    company_name VARCHAR(200) NOT NULL,
    company_type VARCHAR(100), -- 'operator', 'owner', 'charterer', 'manager'
    country_code VARCHAR(3),
    industry_sector VARCHAR(100),
    active_status BOOLEAN DEFAULT TRUE,
    safety_record_score DECIMAL(5, 2),
    INDEX idx_name (company_name),
    INDEX idx_type (company_type)
);
```

#### 5. `incident_companies` (Junction Table)
```sql
CREATE TABLE incident_companies (
    id INT AUTO_INCREMENT PRIMARY KEY,
    incident_id VARCHAR(50),
    company_id VARCHAR(50),
    company_role VARCHAR(100), -- 'vessel_owner', 'operator', 'charterer', 'facility_owner'
    responsibility_level VARCHAR(50),
    FOREIGN KEY (incident_id) REFERENCES incidents(incident_id),
    FOREIGN KEY (company_id) REFERENCES companies(company_id)
);
```

#### 6. `investigations`
```sql
CREATE TABLE investigations (
    investigation_id VARCHAR(50) PRIMARY KEY,
    incident_id VARCHAR(50),
    investigating_agency VARCHAR(200),
    investigation_type VARCHAR(100), -- 'preliminary', 'full', 'formal', 'criminal'
    start_date DATE,
    completion_date DATE,
    report_url TEXT,
    final_report_available BOOLEAN DEFAULT FALSE,
    findings_summary TEXT,
    recommendations TEXT,
    status VARCHAR(50),
    FOREIGN KEY (incident_id) REFERENCES incidents(incident_id),
    INDEX idx_incident (incident_id),
    INDEX idx_agency (investigating_agency)
);
```

#### 7. `personnel`
```sql
CREATE TABLE personnel (
    person_id INT AUTO_INCREMENT PRIMARY KEY,
    incident_id VARCHAR(50),
    person_role VARCHAR(100), -- 'captain', 'crew', 'passenger', 'pilot', 'shore_worker'
    outcome VARCHAR(50), -- 'uninjured', 'injured', 'fatal', 'missing'
    injury_severity VARCHAR(50),
    age_range VARCHAR(20),
    experience_years INT,
    certification_status VARCHAR(100),
    FOREIGN KEY (incident_id) REFERENCES incidents(incident_id),
    INDEX idx_incident (incident_id)
);
```

#### 8. `incident_types` (Reference Table)
```sql
CREATE TABLE incident_types (
    type_id INT AUTO_INCREMENT PRIMARY KEY,
    type_name VARCHAR(100) UNIQUE NOT NULL,
    category VARCHAR(100),
    severity_weight DECIMAL(3, 2),
    description TEXT
);
```

#### 9. `data_sources`
```sql
CREATE TABLE data_sources (
    source_id INT AUTO_INCREMENT PRIMARY KEY,
    source_name VARCHAR(100) NOT NULL,
    source_agency VARCHAR(200),
    source_url TEXT,
    data_format VARCHAR(50),
    update_frequency VARCHAR(50),
    last_scraped TIMESTAMP,
    records_count INT,
    active_status BOOLEAN DEFAULT TRUE
);
```

#### 10. `locations` (Geographic Reference)
```sql
CREATE TABLE locations (
    location_id INT AUTO_INCREMENT PRIMARY KEY,
    location_name VARCHAR(200),
    location_type VARCHAR(100), -- 'port', 'waterway', 'offshore_field', 'region'
    country_code VARCHAR(3),
    latitude DECIMAL(10, 8),
    longitude DECIMAL(11, 8),
    water_body VARCHAR(200),
    jurisdiction VARCHAR(100),
    INDEX idx_coords (latitude, longitude)
);
```

### Incident Type Categories

```
1. Collision
   - Ship-to-ship
   - Ship-to-structure
   - Allision (moving vessel to stationary object)

2. Grounding
   - Hard grounding
   - Soft grounding
   - Stranding

3. Fire/Explosion
   - Engine room fire
   - Cargo fire
   - Accommodation fire
   - Explosion
   - Blowout (offshore)

4. Capsizing/Sinking
   - Capsizing
   - Sinking
   - Flooding
   - Stability loss

5. Personnel Injury/Fatality
   - Fall overboard
   - Slip/trip/fall
   - Struck by object
   - Caught in machinery
   - Exposure

6. Environmental
   - Oil spill
   - Chemical spill
   - Hazmat release
   - Wildlife impact

7. Equipment Failure
   - Main engine failure
   - Auxiliary systems failure
   - Navigation equipment failure
   - Safety equipment failure
   - Structural failure

8. Navigation Error
   - Wrong course
   - Improper lookout
   - Chart/GPS error

9. Weather-Related
   - Storm damage
   - Hurricane/typhoon
   - Ice damage
   - Fog-related

10. Security/Piracy
    - Piracy attack
    - Armed robbery
    - Terrorism
    - Stowaway

11. Pollution
    - Illegal discharge
    - Ballast water violation
    - Air emissions

12. Other
    - Towing casualty
    - Mooring failure
    - Loading/unloading incident
    - Bunkering incident
```

---

## Data Sources

### 1. USCG Marine Casualty Reports (Priority 1)
**URL**: https://www.dco.uscg.mil/Our-Organization/Assistant-Commandant-for-Prevention-Policy-CG-5P/Inspections-Compliance-CG-5PC-/Office-of-Investigations-Casualty-Analysis/Marine-Casualty-Reports/

**Coverage**: US waters, US-flagged vessels worldwide
**Data Format**: PDF reports, searchable database
**Historical**: 1990s - present
**Update Frequency**: Ongoing, reports published after investigation completion

**Key Data Fields**:
- Incident date, location (lat/lon)
- Vessel details (IMO, name, type, flag)
- Casualties (fatalities, injuries)
- Investigation findings and recommendations
- Contributing factors

**Collection Method**:
- Web scraping of report index
- PDF text extraction for detailed reports
- API integration if available

---

### 2. NTSB Investigation Database (Priority 2)
**URL**: https://www.ntsb.gov/Pages/home.aspx

**Coverage**: Major marine accidents in US waters
**Data Format**: Searchable database, detailed reports
**Historical**: 1960s - present
**Update Frequency**: Ongoing

**Key Data Fields**:
- Detailed investigation reports
- Root cause analysis
- Safety recommendations
- Docket materials (photos, witness statements)

**Collection Method**:
- API: https://data.ntsb.gov/carol-main-public/
- Database queries by accident type "Marine"
- Report parsing and extraction

---

### 3. BTS Waterborne Transportation Statistics (Priority 3)
**URL**: https://www.bts.gov/content/waterborne-transportation-safety-and-property-damage-data-related-vessel-casualties

**Coverage**: US waterborne transportation
**Data Format**: CSV, Excel downloads
**Historical**: 1990s - present
**Update Frequency**: Annual

**Key Data Fields**:
- Aggregate statistics
- Property damage costs
- Trends over time
- By vessel type and location

**Collection Method**:
- Direct CSV/Excel downloads
- Automated periodic fetching

---

### 4. USCG Boating Statistics (Priority 4)
**URL**: https://uscgboating.org/statistics/accident_statistics.php

**Coverage**: Recreational boating accidents in US
**Data Format**: PDF reports, Excel files
**Historical**: 1990s - present
**Update Frequency**: Annual

**Key Data Fields**:
- Recreational vessel accidents
- Fatalities and injuries
- Accident causes
- By state and waterway

**Collection Method**:
- PDF and Excel downloads
- Data extraction and normalization

---

### 5. IMCA Safety Statistics (Priority 5)
**URL**: https://www.imca-int.com/resources/safety/safety-statistics/

**Coverage**: International offshore marine contractors
**Data Format**: PDF reports, online data
**Historical**: 1990s - present
**Update Frequency**: Annual

**Key Data Fields**:
- Offshore marine operations
- Diving incidents
- ROV operations
- Lost time incidents (LTI)

**Collection Method**:
- PDF downloads and parsing
- Web scraping of online statistics

---

### 6. IMO Casualty Database (Priority 6)
**URL**: https://www.imo.org/en/ourwork/iiis/pages/casualty.aspx

**Coverage**: International commercial shipping
**Data Format**: GISIS database (Global Integrated Shipping Information System)
**Historical**: 1990s - present
**Update Frequency**: Ongoing

**Key Data Fields**:
- International incidents
- Serious casualties
- Very serious casualties
- Investigation reports from member states

**Collection Method**:
- GISIS portal access (may require credentials)
- Data export and API if available

---

### 7. III Insurance Statistics (Priority 7)
**URL**: https://www.iii.org/fact-statistic/facts-statistics-marine-accidents

**Coverage**: Insurance industry perspective, US focus
**Data Format**: Web pages, downloadable reports
**Historical**: 2000s - present
**Update Frequency**: Annual

**Key Data Fields**:
- Insurance claims data
- Cost trends
- Risk analysis
- Industry statistics

**Collection Method**:
- Web scraping
- Report downloads

---

## Module Structure

```
data/modules/marine_safety/
├── README.md
├── DATA_DICTIONARY.md
├── raw/                                    # Raw scraped data
│   ├── uscg/
│   │   ├── reports/
│   │   └── metadata.json
│   ├── ntsb/
│   ├── bts/
│   ├── uscg_boating/
│   ├── imca/
│   ├── imo/
│   └── iii/
├── processed/                              # Cleaned and normalized
│   ├── incidents.csv
│   ├── vessels.csv
│   ├── companies.csv
│   ├── investigations.csv
│   └── metadata/
├── database/                               # SQL database files
│   ├── schema.sql
│   ├── marine_safety.db (SQLite for dev)
│   └── migrations/
├── archive/                                # Historical versions
└── exports/                                # CSV exports by category

src/worldenergydata/modules/marine_safety/
├── __init__.py
├── scrapers/                               # Data collection
│   ├── __init__.py
│   ├── base_scraper.py
│   ├── uscg_scraper.py
│   ├── ntsb_scraper.py
│   ├── bts_scraper.py
│   ├── uscg_boating_scraper.py
│   ├── imca_scraper.py
│   ├── imo_scraper.py
│   └── iii_scraper.py
├── processors/                             # Data processing
│   ├── __init__.py
│   ├── data_normalizer.py
│   ├── location_geocoder.py
│   ├── vessel_matcher.py
│   └── company_resolver.py
├── database/                               # Database management
│   ├── __init__.py
│   ├── db_manager.py
│   ├── models.py (SQLAlchemy models)
│   └── queries.py
├── analysis/                               # Analysis tools
│   ├── __init__.py
│   ├── trend_analyzer.py
│   ├── geographic_analyzer.py
│   ├── risk_calculator.py
│   └── root_cause_analyzer.py
├── visualization/                          # Dashboards and plots
│   ├── __init__.py
│   ├── dashboards.py
│   ├── maps.py
│   └── charts.py
├── api/                                    # API endpoints
│   ├── __init__.py
│   ├── routes.py
│   └── schemas.py
├── utils/                                  # Utilities
│   ├── __init__.py
│   ├── config.py
│   ├── logger.py
│   └── validators.py
└── cli.py                                  # Command-line interface

tests/modules/marine_safety/
├── test_scrapers.py
├── test_processors.py
├── test_database.py
├── test_analysis.py
└── test_api.py

docs/modules/marine_safety/
├── USER_GUIDE.md
├── API_DOCUMENTATION.md
├── DATA_SOURCES.md
├── ANALYSIS_EXAMPLES.md
└── notebooks/
    ├── 01_data_exploration.ipynb
    ├── 02_trend_analysis.ipynb
    ├── 03_geographic_analysis.ipynb
    └── 04_risk_assessment.ipynb
```

---

## Data Collection Pipeline

### Phase 1: Initial Data Collection (One-time)
```python
# Pseudocode for initial collection
for source in data_sources:
    scraper = get_scraper(source)
    historical_data = scraper.fetch_historical()
    raw_data = store_raw(historical_data)
    processed_data = normalize_and_validate(raw_data)
    database.insert_batch(processed_data)
```

### Phase 2: Automated Updates (Scheduled)
```yaml
Schedule:
  Daily:
    - USCG casualty reports (check for new reports)
    - NTSB updates

  Weekly:
    - IMCA statistics updates
    - IMO casualty database

  Monthly:
    - BTS statistics (check for new releases)
    - USCG boating statistics
    - III insurance reports
```

### Data Processing Pipeline

```
1. SCRAPE
   ├── HTTP requests / API calls
   ├── HTML parsing (BeautifulSoup, Scrapy)
   ├── PDF extraction (PyPDF2, pdfplumber)
   └── Error handling and retry logic

2. EXTRACT
   ├── Text extraction from documents
   ├── Regex patterns for structured data
   ├── Table parsing
   └── Metadata extraction

3. TRANSFORM
   ├── Data normalization
   ├── Date/time standardization
   ├── Location geocoding
   ├── Vessel ID matching (IMO lookup)
   ├── Company name normalization
   └── Incident type classification

4. VALIDATE
   ├── Required field checking
   ├── Data type validation
   ├── Range checking (lat/lon, dates)
   ├── Cross-reference validation
   └── Duplicate detection

5. ENRICH
   ├── Geocoding (address → lat/lon)
   ├── Vessel lookup (IMO database)
   ├── Weather data integration
   ├── Company information lookup
   └── Related incident linking

6. LOAD
   ├── Database insertion
   ├── CSV export
   ├── Update indexes
   ├── Generate summaries
   └── Data quality reporting
```

### Deduplication Strategy
```python
def detect_duplicates(new_incident, existing_incidents):
    """
    Match based on:
    - Date (within 24 hours)
    - Location (within 5 nautical miles)
    - Vessel name/IMO (exact or fuzzy match)
    - Incident type (same category)

    Score similarity and merge if > 85% match
    """
    pass
```

---

## Analysis Capabilities

### 1. Trend Analysis Over Time
```python
class TrendAnalyzer:
    def incidents_by_year(self, incident_type=None, region=None):
        """Time series of incident counts"""

    def fatality_trends(self, by_vessel_type=True):
        """Trend in fatalities over time"""

    def seasonal_patterns(self):
        """Identify seasonal incident patterns"""

    def moving_averages(self, window='1Y'):
        """Calculate moving averages for smoothing"""
```

### 2. Geographic Analysis
```python
class GeographicAnalyzer:
    def incident_hotspots(self, radius_km=50):
        """Identify geographic clustering"""

    def regional_risk_map(self):
        """Generate risk heatmap"""

    def port_safety_scores(self):
        """Rank ports by safety record"""

    def trade_route_analysis(self):
        """Analyze incidents along major shipping lanes"""
```

### 3. Root Cause Analysis
```python
class RootCauseAnalyzer:
    def primary_causes(self, incident_type):
        """Distribution of root causes"""

    def contributing_factors(self):
        """Common contributing factors"""

    def human_factors_analysis(self):
        """Analyze human error patterns"""

    def equipment_failure_patterns(self):
        """Common equipment failures"""
```

### 4. Risk Assessment
```python
class RiskCalculator:
    def vessel_type_risk(self):
        """Risk scores by vessel type"""

    def company_safety_rating(self, company_id):
        """Company safety performance"""

    def route_risk_score(self, origin, destination):
        """Risk score for specific route"""

    def predictive_risk_model(self, features):
        """ML-based risk prediction"""
```

### 5. Statistical Summaries
```python
class SummaryStatistics:
    def overall_statistics(self):
        """Total incidents, fatalities, costs"""

    def by_vessel_type(self):
        """Statistics broken down by vessel type"""

    def by_region(self):
        """Regional statistics"""

    def by_incident_type(self):
        """Incident type distributions"""
```

### 6. Comparison with BSEE Data
```python
class BSEEComparison:
    def offshore_platform_incidents(self):
        """Compare offshore incidents across sources"""

    def gulf_of_mexico_analysis(self):
        """Detailed GoM incident analysis"""

    def regulatory_compliance(self):
        """Track compliance trends"""
```

---

## API Endpoints

### RESTful API Design

#### Base URL
```
http://localhost:5000/api/v1/marine-safety/
```

#### Endpoints

##### 1. Incidents
```
GET    /incidents                    # List all incidents (paginated)
GET    /incidents/{id}               # Get specific incident
GET    /incidents/search             # Search with filters
GET    /incidents/statistics         # Summary statistics
POST   /incidents                    # Add new incident (admin)
PUT    /incidents/{id}               # Update incident (admin)
DELETE /incidents/{id}               # Delete incident (admin)
```

**Query Parameters** (for list/search):
```
?date_from=YYYY-MM-DD
?date_to=YYYY-MM-DD
?incident_type=collision
?severity=high
?region=gulf_of_mexico
?vessel_type=tanker
?fatalities_min=1
?latitude=29.5
?longitude=-90.5
?radius_km=50
?limit=100
?offset=0
```

**Example Response**:
```json
{
  "total": 1543,
  "page": 1,
  "limit": 100,
  "incidents": [
    {
      "incident_id": "USCG-2023-1234",
      "date": "2023-03-15",
      "location": {
        "latitude": 29.5,
        "longitude": -90.5,
        "description": "Gulf of Mexico, 50nm SE of New Orleans"
      },
      "incident_type": "Collision",
      "severity": "Major",
      "vessels": [
        {
          "name": "MV Example",
          "imo": "1234567",
          "type": "Container Ship"
        }
      ],
      "casualties": {
        "fatalities": 0,
        "injuries": 3
      },
      "investigation_status": "Complete"
    }
  ]
}
```

##### 2. Vessels
```
GET /vessels                      # List vessels
GET /vessels/{id}                 # Get vessel details
GET /vessels/{id}/incidents       # All incidents involving vessel
GET /vessels/search               # Search vessels
```

##### 3. Companies
```
GET /companies                    # List companies
GET /companies/{id}               # Company details
GET /companies/{id}/incidents     # All incidents involving company
GET /companies/{id}/safety-score  # Safety rating
```

##### 4. Analysis
```
GET /analysis/trends              # Time series trends
GET /analysis/hotspots            # Geographic hotspots
GET /analysis/root-causes         # Root cause distribution
GET /analysis/statistics          # Summary statistics
GET /analysis/risk-scores         # Risk assessment
```

**Example**:
```
GET /analysis/trends?metric=incidents&group_by=year&incident_type=collision
```

##### 5. Geographic
```
GET /geographic/regions           # List regions with statistics
GET /geographic/search            # Search by lat/lon/radius
GET /geographic/heatmap           # Density data for mapping
```

##### 6. Export
```
GET /export/csv                   # Export as CSV
GET /export/json                  # Export as JSON
GET /export/excel                 # Export as Excel
```

---

## Implementation Roadmap

### Phase 1: Foundation (Weeks 1-4)
**Goals**: Set up infrastructure, database, and basic collection

**Tasks**:
- [ ] Create module structure
- [ ] Design and implement database schema
- [ ] Set up SQLAlchemy models
- [ ] Create base scraper class
- [ ] Implement data normalizer
- [ ] Set up logging and error handling
- [ ] Create configuration management
- [ ] Write initial tests

**Deliverables**:
- Database schema implemented
- Base infrastructure code
- Configuration files
- Initial test suite

---

### Phase 2: Data Collection - US Sources (Weeks 5-8)
**Goals**: Implement scrapers for priority US sources

**Tasks**:
- [ ] USCG Marine Casualty scraper
- [ ] NTSB investigation database scraper
- [ ] BTS statistics downloader
- [ ] USCG Boating statistics scraper
- [ ] Data processing pipeline
- [ ] Deduplication logic
- [ ] Initial data load (historical)

**Deliverables**:
- 4 working scrapers
- Historical US data collected
- Processing pipeline functional

---

### Phase 3: Data Collection - International (Weeks 9-12)
**Goals**: Add international sources

**Tasks**:
- [ ] IMCA statistics scraper
- [ ] IMO casualty database integration
- [ ] III insurance statistics scraper
- [ ] Cross-source deduplication
- [ ] Data enrichment (geocoding, vessel lookup)
- [ ] Historical international data load

**Deliverables**:
- All 7 scrapers functional
- Complete historical database
- Enrichment pipeline working

---

### Phase 4: Analysis Tools (Weeks 13-16)
**Goals**: Build analysis capabilities

**Tasks**:
- [ ] Trend analyzer implementation
- [ ] Geographic analyzer with mapping
- [ ] Root cause analyzer
- [ ] Risk calculator
- [ ] Statistical summary generator
- [ ] BSEE comparison module
- [ ] Jupyter notebooks for analysis

**Deliverables**:
- Analysis tools functional
- Example notebooks
- Analysis documentation

---

### Phase 5: API & Visualization (Weeks 17-20)
**Goals**: Create API and dashboards

**Tasks**:
- [ ] REST API implementation (Flask/FastAPI)
- [ ] API documentation (Swagger/OpenAPI)
- [ ] Dashboard development (Plotly Dash or Streamlit)
- [ ] Interactive maps (Folium or Mapbox)
- [ ] Chart generation (Plotly)
- [ ] Export functionality
- [ ] User authentication (optional)

**Deliverables**:
- REST API functional
- Interactive dashboard
- API documentation

---

### Phase 6: Automation & Testing (Weeks 21-24)
**Goals**: Automated updates and comprehensive testing

**Tasks**:
- [ ] Scheduled scraping (Celery or cron)
- [ ] Automated data processing pipeline
- [ ] Comprehensive test suite (pytest)
- [ ] Integration tests
- [ ] Performance testing
- [ ] Error monitoring and alerting
- [ ] Documentation completion

**Deliverables**:
- Automated update system
- Complete test coverage
- Full documentation

---

### Phase 7: Deployment & Optimization (Weeks 25-28)
**Goals**: Production deployment and optimization

**Tasks**:
- [ ] Production database setup (PostgreSQL)
- [ ] API deployment (Docker, cloud)
- [ ] Dashboard deployment
- [ ] Performance optimization
- [ ] Caching implementation
- [ ] Monitoring and logging
- [ ] User guide and training

**Deliverables**:
- Production system
- Performance optimized
- User documentation

---

## Technical Stack

### Core Technologies
```yaml
Language: Python 3.9+
Package Manager: UV

Data Collection:
  - Scrapy 2.12.0 (web scraping framework)
  - Selenium (browser automation)
  - BeautifulSoup4 (HTML parsing)
  - requests (HTTP library)
  - PyPDF2 / pdfplumber (PDF extraction)

Data Processing:
  - pandas (data manipulation)
  - numpy (numerical operations)
  - geopy (geocoding)
  - fuzzywuzzy (fuzzy matching)
  - dateutil (date parsing)

Database:
  - SQLAlchemy (ORM)
  - PostgreSQL (production)
  - SQLite (development/testing)
  - Alembic (migrations)

Analysis:
  - scikit-learn (machine learning)
  - scipy (statistical analysis)
  - statsmodels (time series)

Visualization:
  - matplotlib (static plots)
  - plotly (interactive charts)
  - folium (maps)
  - seaborn (statistical visualization)

API:
  - FastAPI (modern Python API framework)
  - Pydantic (data validation)
  - uvicorn (ASGI server)

Dashboard:
  - Streamlit or Plotly Dash
  - Mapbox GL (interactive maps)

Testing:
  - pytest (testing framework)
  - pytest-cov (coverage)
  - pytest-mock (mocking)

Automation:
  - Celery (task queue)
  - Redis (message broker)
  - APScheduler (scheduled tasks)

Deployment:
  - Docker (containerization)
  - Docker Compose (multi-container)
  - GitHub Actions (CI/CD)
```

### Configuration Files

#### `config/marine_safety_config.yaml`
```yaml
database:
  type: postgresql
  host: localhost
  port: 5432
  name: marine_safety
  user: ${DB_USER}
  password: ${DB_PASSWORD}

scrapers:
  user_agent: "WorldEnergyData Marine Safety Bot/1.0"
  timeout: 30
  retry_attempts: 3
  delay_between_requests: 1.0

  uscg:
    enabled: true
    base_url: "https://www.dco.uscg.mil"
    update_frequency: "daily"

  ntsb:
    enabled: true
    api_url: "https://data.ntsb.gov/carol-main-public/api/"
    update_frequency: "daily"

  # ... other sources

geocoding:
  service: "nominatim"  # or "google", "mapbox"
  cache_enabled: true

analysis:
  default_time_window: "10Y"
  hotspot_radius_km: 50
  risk_score_weights:
    fatalities: 10.0
    injuries: 3.0
    property_damage: 1.0
    environmental_impact: 5.0

api:
  host: "0.0.0.0"
  port: 5000
  debug: false
  page_size_default: 100
  page_size_max: 1000

logging:
  level: INFO
  file: "logs/marine_safety.log"
  max_bytes: 10485760  # 10MB
  backup_count: 5
```

---

## Data Quality & Validation

### Data Quality Score
Each incident record receives a quality score (0.00-1.00) based on:
- **Completeness** (40%): Percentage of fields populated
- **Accuracy** (30%): Validation checks passed
- **Consistency** (20%): Cross-reference validation
- **Timeliness** (10%): Reporting delay

### Validation Rules
```python
validation_rules = {
    'required_fields': ['incident_id', 'incident_date', 'incident_type', 'location'],
    'date_range': {'min': '1990-01-01', 'max': 'today'},
    'latitude_range': (-90, 90),
    'longitude_range': (-180, 180),
    'severity_levels': ['Minor', 'Moderate', 'Major', 'Catastrophic'],
    'fatalities': {'min': 0, 'max': 10000},
    'imo_number': r'^\d{7}$'  # 7 digits
}
```

---

## Security & Privacy

### Data Access Controls
- Public API: Read-only access to incident statistics
- Authenticated API: Full incident details (requires API key)
- Admin API: Write access (requires admin credentials)

### PII Handling
- Personal names redacted unless public record
- Crew/passenger details aggregated only
- Company names included (public information)

### Compliance
- GDPR considerations for international data
- US public records laws
- Attribution requirements for data sources

---

## Performance Targets

### Database Performance
- Query response < 200ms for simple queries
- Complex analysis < 2 seconds
- Support 10,000+ concurrent reads
- Incident insertion < 50ms

### API Performance
- API response < 500ms (95th percentile)
- Support 100 requests/second
- Dashboard load < 3 seconds

### Data Collection
- Historical data collection: 4-6 weeks
- Daily updates: < 30 minutes
- Zero data loss during collection

---

## Success Metrics

### Coverage
- ✅ 7 data sources integrated
- ✅ 25+ years historical data
- ✅ 50,000+ incidents documented
- ✅ 95%+ of major incidents captured

### Quality
- ✅ Average data quality score > 0.85
- ✅ < 5% duplicate records
- ✅ 90%+ incidents geocoded

### Usage
- ✅ API uptime > 99.5%
- ✅ Dashboard available 24/7
- ✅ 100+ analysis queries/month
- ✅ User documentation complete

---

## Future Enhancements (Phase 8+)

### Machine Learning
- Predictive risk modeling
- Anomaly detection
- Automated incident classification
- Natural language processing for reports

### Real-time Integration
- Live USCG incident feed
- Real-time AIS vessel tracking
- Weather data integration
- Alert system for high-risk conditions

### Advanced Analytics
- Network analysis (company/vessel connections)
- Causation modeling
- Economic impact analysis
- Insurance actuarial modeling

### Visualization
- 3D vessel track visualization
- VR incident reconstruction
- Interactive timeline explorer
- Mobile app

---

## Documentation Requirements

### Technical Documentation
- [ ] Database schema documentation
- [ ] API reference (OpenAPI/Swagger)
- [ ] Scraper developer guide
- [ ] Data dictionary
- [ ] Architecture diagrams

### User Documentation
- [ ] User guide (getting started)
- [ ] Analysis cookbook (examples)
- [ ] Data quality guide
- [ ] FAQ
- [ ] Video tutorials

### Operational Documentation
- [ ] Deployment guide
- [ ] Maintenance procedures
- [ ] Troubleshooting guide
- [ ] Backup/recovery procedures

---

## Risk Assessment & Mitigation

### Technical Risks
| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Website structure changes | High | Medium | Implement robust scrapers with fallbacks |
| API rate limiting | Medium | Medium | Implement rate limiting and caching |
| Large data volume | High | Low | Use database indexing and pagination |
| Data quality issues | Medium | Medium | Implement validation and quality scoring |

### Operational Risks
| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Incomplete historical data | Medium | Medium | Multiple source cross-referencing |
| Source access restrictions | Low | High | Establish relationships with agencies |
| Data privacy concerns | Low | High | Implement PII redaction |
| Maintenance overhead | Medium | Medium | Automate monitoring and updates |

---

## Appendix

### A. Incident Type Taxonomy (Expanded)
See full taxonomy in `docs/INCIDENT_TAXONOMY.md`

### B. Data Source API Documentation
See `docs/DATA_SOURCE_APIS.md`

### C. Database Optimization Guide
See `docs/DATABASE_OPTIMIZATION.md`

### D. Sample Analysis Notebooks
See `docs/notebooks/`

---

**Document Version History**

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0.0 | 2025-10-02 | Claude Code | Initial comprehensive specification |

---

**Approvals**

- [ ] Technical Review
- [ ] Data Quality Review
- [ ] Security Review
- [ ] User Acceptance
- [ ] Implementation Approval

---

**Next Steps**

1. Review and approve this specification
2. Prioritize any additional requirements
3. Begin Phase 1 implementation
4. Establish data source relationships
5. Set up development environment
