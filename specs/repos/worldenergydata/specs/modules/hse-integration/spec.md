# HSE Integration Specification

> Created: 2025-01-09
> Status: Planning
> Priority: High
> Effort: XL (10-12 weeks)

## Overview

Integrate BSEE (Bureau of Safety and Environmental Enforcement) Health, Safety, and Environment incident databases into WorldEnergyData to provide safety-informed economic analysis capabilities. This creates a unique competitive differentiator versus commercial alternatives (Aries $15K+/seat, PHDWin $20K+/seat) that focus solely on economics without safety integration.

**Critical Distinction**: This HSE module focuses on **offshore oil & gas incidents** from BSEE (platform injuries, well spills, drilling accidents, environmental violations). This is separate from:
- `marine_safety` module: Maritime shipping incidents (vessel collisions, USCG, IMO)
- `pipeline_safety` data: Onshore pipeline incidents (PHMSA)
- `bsee` module: Production and economic data (well data, NPV analysis)

## Business Value

### Competitive Advantage
- **Aries ($15K+/seat)**: Economics-only analysis, no HSE integration, separate safety workflow required
- **PHDWin ($20K+/seat)**: Production forecasting focus, no safety data integration, blind to operational risks
- **WorldEnergyData (Free)**: Unified safety-economic analysis, BSEE HSE data integration, zero incremental cost

### Target Users
- **Risk Managers**: Identify high-risk operators and assets before investment commitments
- **ESG Analysts**: Integrate safety performance into sustainability scoring
- **Investment Committees**: Make safety-informed capital allocation decisions with quantified operational risk
- **Regulatory Compliance**: Demonstrate due diligence in safety assessment
- **Insurance Underwriters**: Provide historical safety data for premium calculations and risk assessment

## Data Sources

### BSEE HSE Incident Databases (To Be Researched - Phase 1)

**Primary Data Sources**:
1. **BSEE Incident Investigation Reports**
   - URL: https://www.bsee.gov/stats-facts/incidents
   - Format: CSV downloads, potentially web scraping
   - Content: Detailed incident reports (injuries, fatalities, equipment failures)
   - Update Frequency: Real-time as investigations complete

2. **BSEE Civil Penalties Database**
   - URL: https://www.bsee.gov/enforcement-litigation/civil-penalties
   - Format: CSV downloads, searchable database
   - Content: Environmental violations, regulatory enforcement actions
   - Update Frequency: Monthly updates

3. **BSEE Safety Statistics Portal**
   - URL: https://www.bsee.gov/stats-facts/offshore-incident-statistics
   - Format: Excel/CSV downloads, annual reports
   - Content: Aggregated injury rates, spill records, facility incidents
   - Update Frequency: Annual with quarterly updates

4. **BSEE Equipment Failure Reports**
   - URL: To be determined in research phase
   - Format: Structured database or web scraping
   - Content: Equipment failure tracking, maintenance records
   - Update Frequency: To be determined

**Data Fields (Expected)**:
- Incident ID, Date, Time, Location (lat/lon, block, lease)
- Operator name, Facility name, Well name (linkage to production data)
- Incident type (injury, spill, equipment failure, violation)
- Severity (fatality, lost time injury, recordable, near miss)
- Spill volume, substance type, environmental impact
- Root cause, investigation findings, corrective actions
- Civil penalty amount, violation type, compliance status

## Module Architecture

### Directory Structure (Parallel to marine_safety Module)

```
src/worldenergydata/modules/hse/
├── __init__.py
├── config.py                       # HSE configuration management
├── cli.py                          # Command-line interface
├── database/
│   ├── __init__.py
│   ├── models.py                   # SQLAlchemy models (Injury, Spill, Violation, EquipmentFailure)
│   ├── db_manager.py               # Database operations
│   └── init_db.py                  # Schema initialization
├── importers/
│   ├── __init__.py
│   ├── base_importer.py            # Base importer class
│   ├── bsee_incidents_importer.py  # BSEE incident investigation reports
│   ├── bsee_penalties_importer.py  # BSEE civil penalties database
│   ├── bsee_statistics_importer.py # BSEE safety statistics portal
│   └── bsee_equipment_importer.py  # Equipment failure reports
├── processors/
│   ├── __init__.py
│   ├── base_processor.py           # Base processor class
│   ├── data_cleaner.py             # Data cleaning pipeline
│   ├── data_normalizer.py          # Standardization
│   ├── safety_metrics.py           # Safety metrics calculation (TRIR, LTIR, DART)
│   └── risk_scorer.py              # Operational risk scoring algorithm
├── analysis/
│   ├── __init__.py
│   ├── operator_benchmarking.py    # Compare operator safety performance
│   ├── field_risk_profiles.py      # Field-level risk assessment
│   ├── trend_analysis.py           # Safety trend identification
│   └── esg_reporting.py            # ESG compliance report generation
├── integration/
│   ├── __init__.py
│   ├── bsee_production_linker.py   # Link HSE incidents to wells/operators
│   ├── npv_risk_adjuster.py        # Risk-adjusted NPV calculations
│   └── economic_report_enhancer.py # Add HSE flags to economic reports
├── scrapers/
│   ├── __init__.py
│   ├── base_scraper.py             # Base scraper framework
│   └── bsee_web_scraper.py         # BSEE website scraping
├── utils/
│   ├── __init__.py
│   ├── validators.py               # Data validation
│   └── logger.py                   # Logging utilities
└── README.md                       # Module documentation
```

### Database Schema

**Core Models**:

```python
class HSEIncident(Base):
    """Base HSE incident model"""
    __tablename__ = 'hse_incidents'

    id = Column(Integer, primary_key=True)
    bsee_incident_id = Column(String, unique=True, nullable=False)
    incident_date = Column(DateTime, nullable=False)
    operator = Column(String, nullable=False)
    facility_name = Column(String)
    lease_number = Column(String)
    block_number = Column(String)
    field_name = Column(String)
    latitude = Column(Float)
    longitude = Column(Float)
    incident_type = Column(Enum('injury', 'spill', 'equipment_failure', 'violation'))
    severity = Column(Enum('fatality', 'lost_time', 'recordable', 'near_miss', 'minor'))
    description = Column(Text)
    root_cause = Column(Text)
    corrective_actions = Column(Text)
    investigation_status = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)

class InjuryIncident(Base):
    """Personnel injury incidents"""
    __tablename__ = 'hse_injuries'

    id = Column(Integer, ForeignKey('hse_incidents.id'), primary_key=True)
    injury_type = Column(String)
    body_part_affected = Column(String)
    days_away_from_work = Column(Integer)
    restricted_duty_days = Column(Integer)
    medical_treatment = Column(Boolean)
    hospitalization_required = Column(Boolean)

class SpillIncident(Base):
    """Oil/chemical spill incidents"""
    __tablename__ = 'hse_spills'

    id = Column(Integer, ForeignKey('hse_incidents.id'), primary_key=True)
    substance_type = Column(String)  # crude oil, condensate, drilling fluid, etc.
    volume_barrels = Column(Float)
    volume_gallons = Column(Float)
    environmental_impact = Column(Text)
    cleanup_status = Column(String)
    cleanup_cost = Column(Float)

class ViolationIncident(Base):
    """Regulatory violations and civil penalties"""
    __tablename__ = 'hse_violations'

    id = Column(Integer, ForeignKey('hse_incidents.id'), primary_key=True)
    violation_type = Column(String)
    regulation_cited = Column(String)
    penalty_amount = Column(Float)
    penalty_status = Column(Enum('proposed', 'assessed', 'paid', 'appealed'))
    compliance_deadline = Column(DateTime)
    compliance_status = Column(Enum('open', 'closed', 'overdue'))

class EquipmentFailure(Base):
    """Equipment failure incidents"""
    __tablename__ = 'hse_equipment_failures'

    id = Column(Integer, ForeignKey('hse_incidents.id'), primary_key=True)
    equipment_type = Column(String)
    equipment_id = Column(String)
    failure_mode = Column(String)
    downtime_hours = Column(Float)
    repair_cost = Column(Float)
    preventive_maintenance_status = Column(String)
```

## Integration with Existing Modules

### Link to BSEE Production Module

```python
# src/worldenergydata/modules/hse/integration/bsee_production_linker.py

class BSEEProductionLinker:
    """Links HSE incidents to wells, operators, and production data"""

    def link_incidents_to_wells(self, incident_df, wells_df):
        """Match HSE incidents to specific wells via lease/block"""
        # Match by lease_number, block_number, field_name
        # Create relationships: incident → well → operator → production data
        pass

    def link_incidents_to_operators(self, incident_df, operators_df):
        """Aggregate HSE incidents by operator"""
        # Group incidents by operator
        # Calculate operator-level safety metrics
        pass

    def link_incidents_to_fields(self, incident_df, fields_df):
        """Aggregate HSE incidents by field"""
        # Group incidents by field_name
        # Calculate field-level risk scores
        pass
```

### Risk-Adjusted NPV Calculations

```python
# src/worldenergydata/modules/hse/integration/npv_risk_adjuster.py

class NPVRiskAdjuster:
    """Adjusts NPV calculations based on HSE risk scores"""

    def calculate_risk_adjusted_npv(self, base_npv, operator_risk_score, field_risk_score):
        """
        Risk-adjusted NPV = Base NPV × (1 - risk_factor)

        risk_factor = (operator_risk_weight × operator_risk_score +
                      field_risk_weight × field_risk_score)
        """
        operator_risk_weight = 0.6
        field_risk_weight = 0.4

        risk_factor = (operator_risk_weight * operator_risk_score +
                       field_risk_weight * field_risk_score)

        risk_adjusted_npv = base_npv * (1 - risk_factor)
        return risk_adjusted_npv

    def calculate_insurance_premium_adjustment(self, base_premium, safety_history):
        """Adjust insurance premiums based on safety history"""
        # Better safety record → lower premiums
        pass
```

## Safety Metrics Calculation

### Key Safety Metrics (Industry Standard)

```python
# src/worldenergydata/modules/hse/processors/safety_metrics.py

class SafetyMetricsCalculator:
    """Calculate industry-standard safety metrics"""

    def calculate_trir(self, recordable_injuries, total_hours_worked):
        """
        Total Recordable Incident Rate (TRIR)
        TRIR = (Number of recordable injuries × 200,000) / Total hours worked
        200,000 = 100 employees working 40 hours/week for 50 weeks
        """
        return (recordable_injuries * 200000) / total_hours_worked

    def calculate_ltir(self, lost_time_injuries, total_hours_worked):
        """
        Lost Time Incident Rate (LTIR)
        LTIR = (Number of lost time injuries × 200,000) / Total hours worked
        """
        return (lost_time_injuries * 200000) / total_hours_worked

    def calculate_dart(self, days_away_restricted_transfer, total_hours_worked):
        """
        Days Away, Restricted, or Transferred Rate (DART)
        """
        return (days_away_restricted_transfer * 200000) / total_hours_worked

    def calculate_spill_intensity(self, total_spill_volume, total_production):
        """
        Spill intensity per barrel of production
        Spill Intensity = Total spill volume / Total production volume
        """
        return total_spill_volume / total_production if total_production > 0 else 0
```

### Operational Risk Scoring Algorithm

```python
# src/worldenergydata/modules/hse/processors/risk_scorer.py

class OperationalRiskScorer:
    """Calculate operational risk scores (0-1 scale)"""

    def calculate_operator_risk_score(self, operator_incidents):
        """
        Operator risk score based on weighted incident history
        Higher score = higher risk (0 = no risk, 1 = extreme risk)
        """
        weights = {
            'fatality': 1.0,
            'lost_time': 0.6,
            'recordable': 0.3,
            'spill_major': 0.8,
            'spill_minor': 0.4,
            'violation': 0.5
        }

        # Normalize by exposure (total hours worked or production volume)
        # Compare to industry benchmarks
        # Return 0-1 risk score
        pass

    def calculate_field_risk_score(self, field_incidents, field_characteristics):
        """
        Field risk score based on incident history and operational complexity
        Factors: water depth, reservoir type, environmental sensitivity
        """
        # Complex deepwater fields → higher baseline risk
        # Incident history modifies baseline
        pass
```

## ESG Compliance Reporting

### ESG Data Export Format

```python
# src/worldenergydata/modules/hse/analysis/esg_reporting.py

class ESGReporter:
    """Generate ESG-compliant safety reports"""

    def generate_esg_safety_report(self, operator, time_period):
        """
        Generate ESG safety metrics report
        Format compatible with GRI, SASB, TCFD standards
        """
        report = {
            'operator': operator,
            'reporting_period': time_period,
            'safety_metrics': {
                'trir': self.calculate_trir(operator, time_period),
                'ltir': self.calculate_ltir(operator, time_period),
                'fatalities': self.count_fatalities(operator, time_period),
                'recordable_injuries': self.count_recordables(operator, time_period)
            },
            'environmental_metrics': {
                'total_spills': self.count_spills(operator, time_period),
                'spill_volume_barrels': self.sum_spill_volume(operator, time_period),
                'spill_intensity': self.calculate_spill_intensity(operator, time_period)
            },
            'compliance_metrics': {
                'violations_count': self.count_violations(operator, time_period),
                'total_penalties_usd': self.sum_penalties(operator, time_period),
                'open_violations': self.count_open_violations(operator, time_period)
            }
        }
        return report
```

## Testing Strategy (TDD Approach)

### Test Coverage Requirements
- **Minimum**: 80% code coverage
- **Target**: 90% code coverage
- **Critical Paths**: 100% coverage for risk scoring and NPV integration

### Test Structure

```
tests/modules/hse/
├── __init__.py
├── conftest.py                         # pytest fixtures
├── fixtures/
│   ├── sample_incidents.csv            # Sample BSEE incident data
│   ├── sample_injuries.json            # Sample injury data
│   ├── sample_spills.json              # Sample spill data
│   └── sample_violations.json          # Sample violation data
├── database/
│   ├── test_models.py                  # SQLAlchemy model tests
│   └── test_db_manager.py              # Database operation tests
├── importers/
│   ├── test_bsee_incidents_importer.py
│   ├── test_bsee_penalties_importer.py
│   └── test_bsee_statistics_importer.py
├── processors/
│   ├── test_safety_metrics.py          # TRIR/LTIR calculation tests
│   ├── test_risk_scorer.py             # Risk scoring algorithm tests
│   └── test_data_normalizer.py
├── analysis/
│   ├── test_operator_benchmarking.py
│   ├── test_field_risk_profiles.py
│   └── test_esg_reporting.py
├── integration/
│   ├── test_bsee_production_linker.py  # Integration tests
│   ├── test_npv_risk_adjuster.py
│   └── test_integration_end_to_end.py  # Full pipeline tests
└── scrapers/
    └── test_bsee_web_scraper.py
```

### Example TDD Test Cases

```python
# tests/modules/hse/processors/test_safety_metrics.py

import pytest
from worldenergydata.hse.processors.safety_metrics import SafetyMetricsCalculator

def test_trir_calculation_zero_injuries():
    """Test TRIR calculation with zero injuries"""
    calculator = SafetyMetricsCalculator()
    trir = calculator.calculate_trir(recordable_injuries=0, total_hours_worked=1000000)
    assert trir == 0.0

def test_trir_calculation_standard_case():
    """Test TRIR calculation with standard input"""
    calculator = SafetyMetricsCalculator()
    trir = calculator.calculate_trir(recordable_injuries=5, total_hours_worked=1000000)
    expected_trir = (5 * 200000) / 1000000  # = 1.0
    assert trir == expected_trir

def test_trir_calculation_industry_benchmark():
    """Test TRIR calculation against industry benchmark"""
    calculator = SafetyMetricsCalculator()
    # Industry benchmark for offshore oil & gas: ~1.5 TRIR
    trir = calculator.calculate_trir(recordable_injuries=7, total_hours_worked=1000000)
    assert trir < 2.0  # Should be better than 2.0 for good performers
```

## Implementation Phases

### Phase 1: Data Source Research (Week 1)
- Research BSEE HSE incident databases
- Document API endpoints or download methods
- Create data dictionaries for all incident types
- Design sample data fixtures for testing

### Phase 2: Database Schema (Week 2)
- Write tests for HSE incident models
- Implement SQLAlchemy models (Injury, Spill, Violation, EquipmentFailure)
- Create database migrations
- Build schema validation tests

### Phase 3: Data Import (Weeks 3-4)
- Write tests for BSEE HSE importers
- Implement Scrapy spiders or CSV importers for BSEE data
- Build data normalization processors
- Create data quality validators

### Phase 4: Safety Metrics (Week 5)
- Write tests for safety calculations
- Implement TRIR, LTIR, DART calculations
- Build spill severity scoring
- Create compliance status tracking

### Phase 5: Risk Scoring (Weeks 6-7)
- Write tests for operational risk scoring
- Implement risk scoring algorithms
- Build operator safety benchmarking
- Create field risk profiles

### Phase 6: Integration (Weeks 8-9)
- Write tests for BSEE production integration
- Link HSE incidents to wells/operators in existing BSEE module
- Integrate risk scores into NPV calculations
- Add HSE flags to economic reports

### Phase 7: ESG Reporting (Week 10)
- Write tests for ESG report generation
- Implement ESG data exporters (GRI, SASB, TCFD formats)
- Build compliance dashboards
- Create automated reporting

### Phase 8: Documentation & Launch (Weeks 11-12)
- Complete API documentation
- Write user guides and examples
- Create migration guide from Excel
- Publish release notes
- Update roadmap.md Phase 0 to mark as completed

## Success Criteria

- [ ] All 4 BSEE HSE incident databases successfully ingested
- [ ] Safety metrics (TRIR, LTIR, DART) automatically calculated and cached
- [ ] Operational risk scores integrated into NPV analysis
- [ ] ESG compliance reports generated in GRI/SASB/TCFD formats
- [ ] 90%+ test coverage with pytest
- [ ] Integration with existing BSEE production module complete
- [ ] Zero-cost competitive advantage vs Aries/PHDWin demonstrated
- [ ] Documentation complete with user guides and examples

## References

- BSEE Incidents: https://www.bsee.gov/stats-facts/incidents
- BSEE Safety Statistics: https://www.bsee.gov/stats-facts/offshore-incident-statistics
- BSEE Civil Penalties: https://www.bsee.gov/enforcement-litigation/civil-penalties
- GRI Standards: https://www.globalreporting.org/standards/
- SASB Oil & Gas Standards: https://www.sasb.org/standards/
- OSHA Recordkeeping: https://www.osha.gov/recordkeeping/
