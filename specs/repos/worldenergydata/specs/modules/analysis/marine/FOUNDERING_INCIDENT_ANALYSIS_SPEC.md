# Marine Safety: Comprehensive Incident Analysis & Exploration Module

## Executive Summary

This specification defines a **general-purpose marine incident analysis module** to explore, categorize, and analyze ALL types of marine incidents and their root causes across multiple HSE data sources. The module provides a flexible framework for investigating incident patterns, causal relationships, and safety trends with interactive visualizations and customizable filtering capabilities.

---

## 1. Overview

### 1.1 Purpose

Create a comprehensive incident exploration and analysis module that enables:

1. **Multi-dimensional Incident Analysis**
   - Explore ANY incident category (collisions, groundings, fires, foundering, machinery failure, etc.)
   - Identify root causes and contributing factors
   - Analyze causal relationships and patterns
   
2. **Flexible Categorization**
   - Incident type classification (primary and secondary events)
   - Root cause analysis (human factors, equipment failure, environmental, procedural)
   - Severity assessment and consequence analysis
   
3. **Comparative Studies**
   - Compare incident types across time, vessel types, regions
   - Benchmark safety performance by operator, flag state, vessel class
   - Identify emerging risks and trends

**Example Use Cases:**
- "Find all foundering incidents caused by hatch/door malfunctions"
- "Analyze collision incidents due to poor visibility and operator fatigue"
- "Compare machinery failure rates across vessel types"
- "Identify seasonal patterns in grounding incidents"
- "Analyze fire/explosion incidents by ignition source"

### 1.2 Data Sources

The module will analyze data from:

| Source | Files | Key Fields | Coverage |
|--------|-------|------------|----------|
| **IMO GISIS** | `GISIS-MCIR-*.csv` | Casualty event, Description | 1900-2025 |
| **UK MAIB** | `maib_occurrences.csv` | Main_Event_L1/L2/L3, Description | 2021-2024 |
| **Canadian TSB** | `occurrence.csv` | AccIncTypeDisplay, Summary | Historical |
| **US DLP Historical** | `Accidents_1995-2012.csv` | AccidentEvent1/2/3, Narrative | 1995-2012 |
| **BSEE Offshore** | `fy-*/cy-*.xlsx` | Incident type, narrative | 2007-2023 |

### 1.3 Module Location

```
src/worldenergydata/modules/marine_safety/analysis/
├── __init__.py
├── incidents/
│   ├── __init__.py
│   ├── explorer.py              # Main incident exploration engine
│   ├── categorizer.py           # Incident categorization
│   ├── cause_analyzer.py        # Root cause analysis
│   ├── pattern_detector.py      # Pattern detection & trends
│   ├── comparative_analyzer.py  # Comparative analysis
│   └── config.py               # Configuration management
├── filters/
│   ├── __init__.py
│   ├── incident_filters.py     # Multi-criteria filtering
│   ├── text_analyzers.py       # NLP/text pattern matching
│   └── query_builder.py        # Dynamic query construction
├── visualizations/
│   ├── __init__.py
│   ├── incident_charts.py      # General incident charts
│   ├── causal_analysis.py      # Cause-effect visualizations
│   ├── comparative_charts.py   # Comparison visualizations
│   └── geospatial.py           # Geographic analysis
└── reports/
    ├── __init__.py
    ├── report_generator.py     # HTML report generation
    ├── templates/              # Report templates
    └── exporters.py            # CSV/JSON export
```

---

## 2. Functional Requirements

### 2.1 Flexible Incident Exploration

**FR-1: Multi-Source Data Integration**
- Unified data model for incidents across all sources
- Standardized field mapping and normalization
- Deduplication across overlapping sources
- Cross-referencing between databases

**FR-2: Dynamic Incident Categorization**
- Support for ALL incident types (see INCIDENT_TAXONOMY.md)
- Multi-level classification (primary, secondary, tertiary)
- Flexible category definitions via configuration
- User-defined custom categories

**FR-3: Advanced Filtering System**

Support multi-criteria filtering:

```python
class IncidentFilter:
    """Multi-dimensional incident filtering"""
    
    # Incident Type Filters
    incident_types: List[str]           # Primary incident classification
    sub_types: List[str]                # Secondary classification
    severity_levels: List[str]          # Casualty severity
    
    # Temporal Filters
    date_range: Tuple[date, date]       # Start/end dates
    seasons: List[str]                  # Winter, Spring, Summer, Fall
    time_of_day: List[str]              # Day, Night, Twilight
    
    # Vessel Filters
    vessel_types: List[str]             # Cargo, Tanker, Passenger, etc.
    flag_states: List[str]              # Country flags
    vessel_age_range: Tuple[int, int]   # Min/max age
    tonnage_range: Tuple[float, float]  # Min/max tonnage
    
    # Geographic Filters
    regions: List[str]                  # Geographic regions
    location_types: List[str]           # Port, Open Sea, Coastal, etc.
    coordinates_box: Dict               # Lat/lon bounding box
    
    # Causal Filters
    root_causes: List[str]              # Primary causes
    contributing_factors: List[str]     # Secondary factors
    human_factors: List[str]            # Human-related causes
    equipment_failures: List[str]       # Equipment issues
    
    # Text Search
    keywords: List[str]                 # Free-text keywords
    exclude_keywords: List[str]         # Exclusion patterns
    min_confidence: float               # Classification confidence
    
    # Outcome Filters
    has_fatalities: bool                # Incidents with deaths
    has_injuries: bool                  # Incidents with injuries
    vessel_lost: bool                   # Total vessel loss
    pollution_event: bool               # Environmental damage
```

**FR-4: Text-Based Cause Detection**

Flexible pattern matching engine:

```python
class CauseDetector:
    """Detects causes from incident descriptions"""
    
    def detect_causes(self, text: str, 
                     cause_patterns: Dict[str, List[str]]) -> List[Dict]:
        """
        Extract causes from text using regex patterns
        
        Returns:
            [
                {
                    'cause_category': 'equipment_failure',
                    'cause_type': 'hatch_door_malfunction',
                    'confidence': 0.92,
                    'matched_patterns': ['hatch cover failure'],
                    'context': 'vessel foundered after hatch cover failure'
                }
            ]
        """
```

### 2.2 Analysis Capabilities

**FR-4: Statistical Analysis**
- Incident frequency by year, month, season
- Vessel type distribution
- Geographic clustering
- Casualty severity trends
- Root cause analysis

**FR-5: Comparative Analysis**
- Hatch/door failures vs. other foundering causes
- Vessel age correlation
- Weather/sea state conditions
- Flag state comparison
- Vessel type risk profiles

**FR-6: Time Series Analysis**
- Trend analysis over decades
- Seasonal patterns
- Regulatory impact assessment
- Safety improvement tracking

### 2.3 Reporting & Visualization

**FR-7: Interactive HTML Reports** (MANDATORY per project standards)

Must include:
- **Executive Summary Dashboard**
  - Total incidents, deaths, vessel losses
  - Key statistics and trends
  - Critical findings

- **Time Series Charts** (Plotly)
  - Incidents per year with trend lines
  - Seasonal heatmaps
  - Moving averages

- **Vessel Analysis Charts** (Plotly)
  - Distribution by vessel type (bar/pie)
  - Vessel age vs. incident rate (scatter)
  - Tonnage distribution (histogram)

- **Geographic Maps** (Plotly)
  - Incident locations (scatter mapbox)
  - Hot spot analysis (density heatmap)
  - Regional clustering

- **Root Cause Analysis** (Plotly)
  - Pareto charts of failure modes
  - Contributing factors (sunburst)
  - Fault tree visualization

- **Comparative Dashboards**
  - Hatch/door vs. other causes
  - Flag state comparison
  - Operator performance

**FR-8: CSV Data Export**
- Filtered incident dataset
- Analysis results tables
- Statistical summaries

---

## 3. Technical Architecture

### 3.1 Data Pipeline

```
┌─────────────────┐
│  Raw Data       │
│  (CSV/Excel)    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Data Loader    │
│  - Normalize    │
│  - Validate     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  SQLite Cache   │
│  (marine_safety │
│   .db)          │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Incident       │
│  Detector       │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Classifier     │
│  (Hatch/Door)   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Analyzer       │
│  (Statistics)   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Report         │
│  Generator      │
│  (HTML + CSV)   │
└─────────────────┘
```

### 3.2 Core Classes

#### 3.2.1 FounderingDetector

```python
class FounderingDetector:
    """Detects foundering incidents across multiple data sources"""
    
    def __init__(self, db_path: str):
        """Initialize with database connection"""
        
    def load_incidents(self, 
                      sources: List[str] = None,
                      date_range: Tuple[date, date] = None) -> pd.DataFrame:
        """Load incidents from specified sources"""
        
    def detect_foundering(self, df: pd.DataFrame) -> pd.DataFrame:
        """Filter for foundering events"""
        
    def classify_by_cause(self, df: pd.DataFrame) -> pd.DataFrame:
        """Classify incidents by primary cause"""
```

#### 3.2.2 HatchDoorClassifier

```python
class HatchDoorClassifier:
    """Classifies incidents involving hatch/door malfunctions"""
    
    def __init__(self, patterns: Dict[str, List[str]] = None):
        """Initialize with text patterns"""
        
    def analyze_text(self, text: str) -> Dict[str, Any]:
        """Analyze text for hatch/door keywords"""
        
    def classify_incidents(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add hatch/door classification columns"""
        
    def extract_failure_modes(self, df: pd.DataFrame) -> pd.DataFrame:
        """Identify specific failure mechanisms"""
```

#### 3.2.3 FounderingAnalyzer

```python
class FounderingAnalyzer:
    """Statistical analysis of foundering incidents"""
    
    def __init__(self, df: pd.DataFrame):
        """Initialize with incident dataframe"""
        
    def temporal_analysis(self) -> Dict[str, pd.DataFrame]:
        """Analyze trends over time"""
        
    def vessel_analysis(self) -> Dict[str, pd.DataFrame]:
        """Analyze by vessel characteristics"""
        
    def geographic_analysis(self) -> Dict[str, pd.DataFrame]:
        """Geographic clustering and patterns"""
        
    def causal_analysis(self) -> Dict[str, pd.DataFrame]:
        """Root cause and contributing factors"""
```

#### 3.2.4 FounderingReportGenerator

```python
class FounderingReportGenerator:
    """Generates interactive HTML reports"""
    
    def __init__(self, analyzer: FounderingAnalyzer):
        """Initialize with analyzer results"""
        
    def generate_html_report(self, output_path: str):
        """Generate comprehensive HTML report with Plotly charts"""
        
    def export_csv_datasets(self, output_dir: str):
        """Export filtered data and analysis results"""
```

### 3.3 Database Schema Extension

Add to existing `marine_safety.db`:

```sql
-- Incident classification table
CREATE TABLE incident_classifications (
    classification_id INTEGER PRIMARY KEY,
    incident_id INTEGER NOT NULL,
    classification_type VARCHAR(50) NOT NULL,  -- 'foundering', 'hatch_door', etc.
    confidence_score DECIMAL(3,2),
    detected_patterns TEXT,  -- JSON array of matched patterns
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (incident_id) REFERENCES incidents(incident_id)
);

-- Analysis cache
CREATE TABLE analysis_cache (
    cache_id INTEGER PRIMARY KEY,
    analysis_type VARCHAR(100) NOT NULL,
    parameters TEXT,  -- JSON
    result_data TEXT,  -- JSON
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP
);
```

---

## 4. Implementation Plan

### Phase 1: Foundation (Week 1)

**Tasks:**
1. Create module directory structure
2. Define data models and schemas
3. Implement data loader with normalization
4. Set up SQLite database integration
5. Write unit tests for data loading

**Deliverables:**
- `src/worldenergydata/modules/marine_safety/analysis/foundering/` structure
- Data loading pipeline functional
- Test coverage > 80%

### Phase 2: Detection & Classification (Week 2)

**Tasks:**
1. Implement `FounderingDetector` class
2. Implement `HatchDoorClassifier` with pattern matching
3. Create filtering pipeline
4. Build incident categorization logic
5. Write comprehensive tests

**Deliverables:**
- Working detection engine
- Classifier with validated patterns
- Test coverage > 85%

### Phase 3: Analysis Engine (Week 3)

**Tasks:**
1. Implement `FounderingAnalyzer` class
2. Build statistical analysis functions
3. Create temporal, vessel, and geographic analysis
4. Implement causal analysis
5. Write analysis tests

**Deliverables:**
- Complete analysis engine
- Statistical outputs validated
- Test coverage > 85%

### Phase 4: Visualization & Reporting (Week 4)

**Tasks:**
1. Implement `FounderingReportGenerator`
2. Create Plotly visualization library
3. Build interactive HTML report template
4. Implement CSV export functionality
5. Create example reports

**Deliverables:**
- Interactive HTML reports with Plotly
- CSV export functionality
- Sample reports generated

### Phase 5: CLI & Documentation (Week 5)

**Tasks:**
1. Create CLI interface
2. Write comprehensive documentation
3. Create usage examples
4. Performance optimization
5. Final testing and validation

**Deliverables:**
- CLI tool functional
- Complete documentation
- User guide with examples

---

## 5. Configuration Example

```yaml
# config/analysis/foundering_hatch_door_analysis.yml

meta:
  library: worldenergydata
  module: marine_safety
  analysis_type: foundering_hatch_door
  label: foundering_incident_analysis_v1

data_sources:
  enabled:
    - imo_gisis
    - uk_maib
    - canadian_tsb
    - us_dlp_historical
  
  date_range:
    start: 1990-01-01
    end: 2025-12-31

detection:
  foundering_keywords:
    - foundering
    - sinking
    - sank
    - capsized
    - total loss
    - vessel lost
    
  hatch_door_patterns:
    hatch:
      - hatch cover failure
      - cargo hatch
      - hatch not closed
      - hatch seal
      - unsecured hatch
    door:
      - watertight door
      - door failure
      - door malfunction
      - cargo door
      - access door
    
  min_confidence: 0.7
  
  exclude_patterns:
    - collision
    - grounding
    - fire
    - explosion

analysis:
  temporal:
    enabled: true
    groupings:
      - year
      - quarter
      - month
      - season
    
  vessel:
    enabled: true
    dimensions:
      - vessel_type
      - vessel_age
      - gross_tonnage
      - flag_state
      
  geographic:
    enabled: true
    clustering: true
    hotspot_threshold: 3
    
  causal:
    enabled: true
    factors:
      - weather
      - sea_state
      - vessel_condition
      - operational

reporting:
  format: html
  interactive: true
  visualization_library: plotly
  
  sections:
    - executive_summary
    - temporal_analysis
    - vessel_analysis
    - geographic_analysis
    - causal_analysis
    - recommendations
    
  export:
    csv: true
    json: true
    
output:
  directory: reports/marine_safety/foundering
  filename_pattern: "foundering_hatch_door_{date}.html"
  csv_directory: data/results/foundering
```

---

## 6. Expected Outputs

### 6.1 Console Output Example

```
Marine Safety Foundering Analysis
==================================

Loading data from sources:
  ✓ IMO GISIS (1,525 incidents)
  ✓ UK MAIB (5,878 incidents)
  ✓ Canadian TSB (86,290 incidents)
  ✓ US DLP Historical (93,238 incidents)

Total incidents loaded: 187,931

Detecting foundering events...
  ✓ Found 3,427 foundering incidents

Classifying by hatch/door malfunction...
  ✓ Identified 287 incidents with hatch/door issues
  ✓ Confidence scores: 84% high, 12% medium, 4% low

Analyzing patterns...
  ✓ Temporal analysis complete
  ✓ Vessel analysis complete
  ✓ Geographic analysis complete
  ✓ Causal analysis complete

Generating reports...
  ✓ HTML report: reports/marine_safety/foundering/report_2025-01-15.html
  ✓ CSV export: data/results/foundering/incidents_2025-01-15.csv
  ✓ Statistics: data/results/foundering/stats_2025-01-15.csv

Analysis Complete!
==================
Total foundering incidents: 3,427
Hatch/door related: 287 (8.4%)
Time period: 1990-2025
Most common vessel type: General Cargo (42%)
Highest risk period: Winter months (Dec-Feb)
```

### 6.2 HTML Report Sections

1. **Executive Dashboard**
   - KPI cards (total incidents, deaths, vessels lost)
   - Trend sparklines
   - Key findings callouts

2. **Temporal Analysis**
   - Line chart: Incidents per year
   - Heatmap: Seasonal patterns
   - Bar chart: Monthly distribution

3. **Vessel Analysis**
   - Pie chart: Distribution by vessel type
   - Scatter plot: Vessel age vs. incident rate
   - Histogram: Tonnage distribution
   - Table: Top 10 vessel types at risk

4. **Geographic Analysis**
   - Interactive map: Incident locations
   - Heatmap: Geographic hotspots
   - Bar chart: Incidents by region

5. **Root Cause Analysis**
   - Pareto chart: Failure modes
   - Sunburst chart: Contributing factors
   - Sankey diagram: Failure progression

6. **Recommendations**
   - Risk mitigation strategies
   - Inspection focus areas
   - Regulatory considerations

### 6.3 CSV Exports

**incidents_filtered.csv**
```csv
incident_id,date,vessel_name,vessel_type,imo_number,flag_state,location,latitude,longitude,casualty_type,hatch_door_issue,confidence_score,description,source
C1000594,2024-11-01,DANA,General Cargo,8104553,Zanzibar,Mediterranean Sea,32.7,23.0,Foundering,hatch_cover_failure,0.92,"Vessel foundered after hatch cover failure in rough seas",IMO_GISIS
...
```

**statistics_summary.csv**
```csv
metric,value,percentage,notes
total_incidents,3427,100.0,All foundering incidents 1990-2025
hatch_door_related,287,8.4,Incidents with hatch/door issues
high_confidence,241,7.0,Confidence > 0.8
medium_confidence,34,1.0,Confidence 0.6-0.8
low_confidence,12,0.3,Confidence < 0.6
total_fatalities,1247,N/A,Deaths across all incidents
hatch_door_fatalities,98,7.9,Deaths in hatch/door incidents
```

---

## 7. Testing Strategy

### 7.1 Unit Tests

```python
# tests/modules/marine_safety/analysis/test_foundering_detector.py

def test_load_incidents_from_multiple_sources():
    """Test loading and normalizing data from multiple sources"""
    
def test_detect_foundering_events():
    """Test foundering event detection logic"""
    
def test_hatch_door_pattern_matching():
    """Test pattern matching for hatch/door keywords"""
    
def test_confidence_score_calculation():
    """Test classification confidence scoring"""
```

### 7.2 Integration Tests

```python
# tests/modules/marine_safety/analysis/test_foundering_integration.py

def test_end_to_end_analysis_pipeline():
    """Test complete analysis pipeline from load to report"""
    
def test_report_generation_with_plotly():
    """Test HTML report generation with all charts"""
    
def test_csv_export_integrity():
    """Test CSV export data integrity"""
```

### 7.3 Test Data

Create synthetic test dataset:
```python
# tests/modules/marine_safety/fixtures/foundering_test_data.py

SAMPLE_INCIDENTS = [
    {
        'incident_id': 'TEST001',
        'date': '2020-01-15',
        'vessel_name': 'TEST VESSEL 1',
        'casualty_event': 'Flooding/foundering - foundering',
        'description': 'Vessel sank after cargo hatch cover failure during storm',
        'vessel_type': 'General Cargo',
        'expected_classification': 'hatch_door',
        'expected_confidence': 0.95
    },
    # ... more test cases
]
```

---

## 8. Success Criteria

- [ ] Module successfully loads data from all sources
- [ ] Foundering detection accuracy > 95%
- [ ] Hatch/door classification precision > 80%
- [ ] All visualizations render correctly in HTML report
- [ ] Test coverage > 85%
- [ ] Performance: Analyze 100K+ incidents in < 2 minutes
- [ ] HTML reports are fully interactive with Plotly
- [ ] CSV exports are complete and accurate
- [ ] Documentation is comprehensive and clear

---

## 9. Future Enhancements

### Phase 2 Enhancements
1. **Machine Learning Classification**
   - Train ML model for better pattern recognition
   - Use NLP for narrative analysis
   - Automated root cause extraction

2. **Predictive Analytics**
   - Risk scoring for active vessels
   - Predictive maintenance recommendations
   - Early warning systems

3. **Real-time Monitoring**
   - Integration with live incident feeds
   - Automated alerts for high-risk patterns
   - Dashboard updates

4. **Advanced Visualizations**
   - 3D temporal-geographic visualization
   - Network analysis of related incidents
   - VR/AR incident reconstruction

---

## 10. References

- **IMO GISIS**: Global Integrated Shipping Information System
- **UK MAIB**: Marine Accident Investigation Branch
- **TSB Canada**: Transportation Safety Board
- **BSEE**: Bureau of Safety and Environmental Enforcement
- **SOLAS Convention**: Safety of Life at Sea regulations
- **IMO MSC/Circ.1291**: Watertight doors and hatch covers

---

**Document Version**: 1.0  
**Created**: 2025-01-15  
**Author**: Marine Safety Analysis Team  
**Status**: Ready for Implementation
