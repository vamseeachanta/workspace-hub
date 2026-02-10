---
name: marine-safety-incidents
description: Collect, analyze, and report marine safety incident data from 7 global maritime authorities. Use for incident scraping, safety trend analysis, risk assessment, geographic hotspot identification, and marine safety reporting.
---

# Marine Safety Incidents Skill

Collect, analyze, and report marine safety incident data from global maritime authorities including USCG, NTSB, BSEE, IMO, and more.

## When to Use

- Marine safety incident data collection and scraping
- Safety trend analysis and risk assessment
- Geographic hotspot identification
- Incident type classification and severity analysis
- Environmental impact assessment from marine incidents
- Regulatory compliance reporting
- Root cause analysis

## Prerequisites

- Python environment with `worldenergydata` package installed
- Database connection (PostgreSQL recommended)
- API keys for relevant data sources (if applicable)

## Analysis Types

### 1. Incident Data Collection

Scrape and import incident data from multiple sources.

```yaml
marine_safety:
  collection:
    flag: true
    sources:
      - uscg       # US Coast Guard
      - ntsb       # National Transportation Safety Board
      - bsee       # Bureau of Safety and Environmental Enforcement
      - imo        # International Maritime Organization
      - maib       # UK Marine Accident Investigation Branch
      - atsb       # Australian Transport Safety Bureau
      - tsb        # Canadian Transportation Safety Board
    date_range:
      start: "2020-01-01"
      end: "2024-12-31"
    output:
      database: "marine_safety_db"
      format: "normalized"
```

### 2. Trend Analysis

Analyze incident trends over time.

```yaml
marine_safety:
  trend_analysis:
    flag: true
    grouping:
      - by_year
      - by_month
      - by_incident_type
      - by_severity
    metrics:
      - incident_count
      - fatality_rate
      - injury_rate
      - environmental_impact_score
    output:
      report_file: "results/safety_trends.html"
      data_file: "results/trend_data.csv"
```

### 3. Geographic Analysis

Identify incident hotspots and high-risk areas.

```yaml
marine_safety:
  geographic_analysis:
    flag: true
    regions:
      - gulf_of_mexico
      - north_sea
      - asia_pacific
    clustering:
      method: "dbscan"
      eps: 50  # km
    output:
      map_file: "results/incident_hotspots.html"
      summary: "results/geographic_summary.json"
```

### 4. Risk Assessment

Calculate risk scores for vessel types and operations.

```yaml
marine_safety:
  risk_assessment:
    flag: true
    vessel_types:
      - tanker
      - cargo
      - offshore_platform
      - drilling_rig
    factors:
      - historical_incidents
      - environmental_conditions
      - operational_complexity
    output:
      risk_matrix: "results/risk_matrix.csv"
      recommendations: "results/risk_recommendations.md"
```

## Python API

### Data Collection

```python
from worldenergydata.marine_safety.scrapers import MarineSafetyScraper
from worldenergydata.marine_safety.database import IncidentDatabase

# Initialize scraper
scraper = MarineSafetyScraper()

# Scrape from specific source
incidents = scraper.scrape(
    source="uscg",
    start_date="2023-01-01",
    end_date="2023-12-31"
)

# Store in database
db = IncidentDatabase()
db.insert_incidents(incidents)
print(f"Imported {len(incidents)} incidents")
```

### Incident Analysis

```python
from worldenergydata.marine_safety.analysis import IncidentAnalyzer

# Initialize analyzer
analyzer = IncidentAnalyzer(database_url="postgresql://...")

# Get trend summary
trends = analyzer.get_trends(
    start_date="2020-01-01",
    end_date="2024-12-31",
    grouping="monthly"
)

# Analyze by incident type
type_summary = analyzer.analyze_by_type(
    incident_types=["collision", "grounding", "fire", "explosion"]
)

# Get severity distribution
severity = analyzer.severity_distribution()
```

### Geographic Hotspot Detection

```python
from worldenergydata.marine_safety.analysis import GeographicAnalyzer

# Initialize geographic analyzer
geo = GeographicAnalyzer()

# Find hotspots
hotspots = geo.detect_hotspots(
    region="gulf_of_mexico",
    method="dbscan",
    min_incidents=5
)

# Generate interactive map
geo.generate_map(
    hotspots=hotspots,
    output_file="results/hotspot_map.html"
)
```

### Risk Scoring

```python
from worldenergydata.marine_safety.analysis import RiskAssessor

# Initialize risk assessor
risk = RiskAssessor()

# Calculate risk scores
scores = risk.calculate_risk(
    vessel_type="offshore_platform",
    region="north_sea",
    factors=["weather", "traffic_density", "historical_incidents"]
)

print(f"Risk Score: {scores['overall']:.2f}")
print(f"Risk Level: {scores['level']}")  # LOW, MEDIUM, HIGH, CRITICAL
```

### Reporting

```python
from worldenergydata.marine_safety.visualization import SafetyReportGenerator

# Initialize report generator
reporter = SafetyReportGenerator()

# Generate comprehensive report
report = reporter.generate_report(
    start_date="2023-01-01",
    end_date="2023-12-31",
    sections=[
        "executive_summary",
        "trend_analysis",
        "geographic_distribution",
        "vessel_type_breakdown",
        "recommendations"
    ],
    output_file="results/safety_report.html"
)
```

## CLI Usage

```bash
# Scrape incident data
python -m worldenergydata.marine_safety.cli scrape --source uscg --year 2023

# Analyze trends
python -m worldenergydata.marine_safety.cli analyze --type trends --output trends.html

# Generate risk report
python -m worldenergydata.marine_safety.cli report --format html --output safety_report.html

# Export data
python -m worldenergydata.marine_safety.cli export --format csv --output incidents.csv
```

## Key Classes

| Class | Purpose |
|-------|---------|
| `MarineSafetyScraper` | Multi-source incident scraping |
| `IncidentDatabase` | Database operations and storage |
| `IncidentAnalyzer` | Statistical analysis and trends |
| `GeographicAnalyzer` | Hotspot detection and mapping |
| `RiskAssessor` | Risk scoring and assessment |
| `SafetyReportGenerator` | HTML/PDF report generation |

## Data Sources

| Source | Coverage | Data Types |
|--------|----------|------------|
| USCG | US waters | All marine incidents |
| NTSB | US | Major accidents, investigations |
| BSEE | US OCS | Offshore incidents |
| IMO | International | Global shipping incidents |
| MAIB | UK waters | UK marine accidents |
| ATSB | Australia | Australian marine incidents |
| TSB | Canada | Canadian marine accidents |

## Output Formats

### Incident CSV

```csv
incident_id,date,location_lat,location_lon,vessel_type,incident_type,severity,fatalities,injuries,source
INC001,2023-05-15,28.5,-88.2,tanker,collision,high,0,3,uscg
INC002,2023-06-20,29.1,-94.5,platform,fire,critical,2,5,bsee
```

### Risk Assessment JSON

```json
{
  "assessment_date": "2024-01-15",
  "vessel_type": "offshore_platform",
  "region": "gulf_of_mexico",
  "overall_risk_score": 7.2,
  "risk_level": "HIGH",
  "factors": {
    "historical_incidents": 8.5,
    "weather_exposure": 6.0,
    "traffic_density": 7.0
  },
  "recommendations": [
    "Increase safety inspections",
    "Enhanced weather monitoring"
  ]
}
```

## Best Practices

1. **Rate limiting** - Respect source rate limits when scraping
2. **Data validation** - Validate and deduplicate incoming data
3. **Incremental updates** - Use incremental scraping for efficiency
4. **Geographic accuracy** - Verify coordinates for hotspot analysis
5. **Source attribution** - Always track data provenance

## Related Skills

- [bsee-data-extractor](../bsee-data-extractor/SKILL.md) - BSEE-specific extraction
- [field-analyzer](../field-analyzer/SKILL.md) - Field-level analysis
- [energy-data-visualizer](../energy-data-visualizer/SKILL.md) - Visualization

## References

- USCG Marine Safety Information Portal
- BSEE Incident Statistics
- IMO GISIS Maritime Casualties Database
- DNV Maritime Safety Standards
