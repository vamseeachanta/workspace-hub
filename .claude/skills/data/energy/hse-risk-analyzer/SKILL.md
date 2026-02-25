---
name: hse-risk-analyzer
description: Analyze BSEE HSE (Health, Safety, Environment) incident data for risk assessment. Use for operator safety scoring, incident trend analysis, compliance tracking, and ESG-integrated economic evaluation.
capabilities: []
requires: []
see_also: []
---

# HSE Risk Analyzer

Analyze BSEE HSE incident data to assess operational risk, operator safety performance, and integrate safety metrics into economic analysis for Gulf of Mexico operations.

## When to Use

- Assessing operator safety performance before investment decisions
- Analyzing incident trends for specific fields, facilities, or operators
- Calculating risk-adjusted economic metrics (NPV with safety factors)
- Supporting ESG (Environmental, Social, Governance) compliance requirements
- Benchmarking operator safety records across similar assets
- Identifying high-risk operators or facilities for due diligence
- Generating safety-integrated investment analysis reports

## Core Pattern

```
Query Parameters → HSE Database → Aggregate → Score → Integrate with Economics → Report
```

## Implementation

### Data Models

```python
from dataclasses import dataclass, field
from datetime import datetime, date
from typing import Optional, List, Dict, Any
from enum import Enum
import pandas as pd
import numpy as np

class IncidentType(Enum):
    """HSE incident classification types."""
    INJURY = "injury"
    SPILL = "spill"
    EQUIPMENT_FAILURE = "equipment_failure"
    VIOLATION = "violation"

class SeverityLevel(Enum):
    """Incident severity classification."""
    FATALITY = "fatality"
    LOST_TIME = "lost_time"
    RECORDABLE = "recordable"
    NEAR_MISS = "near_miss"
    MINOR = "minor"

@dataclass
class HSEIncidentRecord:
    """Single HSE incident record."""
    bsee_incident_id: str
    incident_date: datetime
    operator: str
    incident_type: IncidentType
    severity: SeverityLevel
    facility_name: Optional[str] = None
    lease_number: Optional[str] = None
    block_number: Optional[str] = None
    field_name: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    description: Optional[str] = None
    penalty_amount: Optional[float] = None
    spill_volume_bbls: Optional[float] = None
    days_away_from_work: Optional[int] = None

    @property
    def severity_weight(self) -> float:
        """Numeric weight for severity calculations."""
        weights = {
            SeverityLevel.FATALITY: 100.0,
            SeverityLevel.LOST_TIME: 25.0,
            SeverityLevel.RECORDABLE: 10.0,
            SeverityLevel.NEAR_MISS: 5.0,
            SeverityLevel.MINOR: 1.0
        }
        return weights.get(self.severity, 1.0)

@dataclass
class OperatorSafetyProfile:
    """Safety profile for an operator."""
    operator_name: str
    total_incidents: int = 0
    fatalities: int = 0
    lost_time_incidents: int = 0
    recordable_incidents: int = 0
    total_penalties: float = 0.0
    total_spill_volume: float = 0.0
    exposure_hours: Optional[float] = None
    years_analyzed: int = 0

    @property
    def trir(self) -> Optional[float]:
        """Total Recordable Incident Rate (per 200,000 hours)."""
        if self.exposure_hours and self.exposure_hours > 0:
            recordable_count = self.fatalities + self.lost_time_incidents + self.recordable_incidents
            return (recordable_count / self.exposure_hours) * 200000
        return None

    @property
    def safety_score(self) -> float:
        """
        Calculated safety score (0-100, higher is safer).

        Based on weighted incident counts and severity.
        """
        if self.total_incidents == 0:
            return 100.0

        weighted_incidents = (
            self.fatalities * 100 +
            self.lost_time_incidents * 25 +
            self.recordable_incidents * 10
        )

        # Normalize to 0-100 scale (inverse - lower incidents = higher score)
        # Assumes max weighted score of 500 per year is "very bad"
        max_weighted = 500 * max(self.years_analyzed, 1)
        score = 100 - min(100, (weighted_incidents / max_weighted) * 100)
        return round(score, 1)

    @property
    def risk_category(self) -> str:
        """Risk category based on safety score."""
        if self.safety_score >= 90:
            return "LOW"
        elif self.safety_score >= 70:
            return "MODERATE"
        elif self.safety_score >= 50:
            return "ELEVATED"
        else:
            return "HIGH"

@dataclass
class RiskAdjustedMetrics:
    """Economic metrics adjusted for HSE risk."""
    base_npv: float
    risk_adjusted_npv: float
    risk_discount_factor: float
    safety_score: float
    risk_category: str
    potential_penalty_exposure: float
    insurance_adjustment: float

    @property
    def npv_impact(self) -> float:
        """NPV reduction due to safety risk."""
        return self.base_npv - self.risk_adjusted_npv

    @property
    def npv_impact_percent(self) -> float:
        """Percentage NPV impact from safety risk."""
        if self.base_npv != 0:
            return (self.npv_impact / abs(self.base_npv)) * 100
        return 0.0
```

### HSE Risk Analyzer

```python
from pathlib import Path
from typing import Optional, List, Dict, Generator
import pandas as pd
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class HSERiskAnalyzer:
    """
    Analyzer for BSEE HSE incident data with risk scoring.

    Provides operator safety assessment, incident trend analysis,
    and risk-adjusted economic calculations.
    """

    # Industry benchmark TRIR (2023 GOM average)
    INDUSTRY_TRIR_BENCHMARK = 0.8

    # Risk discount factors by category
    RISK_DISCOUNT_FACTORS = {
        "LOW": 0.0,
        "MODERATE": 0.05,
        "ELEVATED": 0.10,
        "HIGH": 0.20
    }

    def __init__(self, data_path: Path = None):
        """
        Initialize HSE risk analyzer.

        Args:
            data_path: Path to HSE data directory or database
        """
        self.data_path = data_path or Path("data/modules/hse")
        self._incidents_cache: Optional[pd.DataFrame] = None
        self._penalties_cache: Optional[pd.DataFrame] = None

    def load_incidents(self, csv_path: Path = None) -> pd.DataFrame:
        """
        Load HSE incidents from CSV or database.

        Args:
            csv_path: Optional path to incidents CSV

        Returns:
            DataFrame with incident records
        """
        if csv_path and csv_path.exists():
            df = pd.read_csv(csv_path, parse_dates=['incident_date'])
            self._incidents_cache = df
            return df

        # Try default data path
        default_path = self.data_path / "incidents.csv"
        if default_path.exists():
            df = pd.read_csv(default_path, parse_dates=['incident_date'])
            self._incidents_cache = df
            return df

        raise FileNotFoundError(f"No incidents data found at {csv_path or default_path}")

    def get_operator_profile(
        self,
        operator: str,
        start_date: datetime = None,
        end_date: datetime = None
    ) -> OperatorSafetyProfile:
        """
        Build safety profile for an operator.

        Args:
            operator: Operator name
            start_date: Analysis start date
            end_date: Analysis end date

        Returns:
            OperatorSafetyProfile with incident statistics
        """
        if self._incidents_cache is None:
            self.load_incidents()

        df = self._incidents_cache.copy()

        # Filter by operator
        df = df[df['operator'].str.contains(operator, case=False, na=False)]

        # Filter by date range
        if start_date:
            df = df[df['incident_date'] >= start_date]
        if end_date:
            df = df[df['incident_date'] <= end_date]

        # Calculate years analyzed
        if len(df) > 0:
            date_range = (df['incident_date'].max() - df['incident_date'].min()).days
            years = max(1, date_range / 365)
        else:
            years = 1

        profile = OperatorSafetyProfile(
            operator_name=operator,
            total_incidents=len(df),
            fatalities=len(df[df['severity'] == 'fatality']),
            lost_time_incidents=len(df[df['severity'] == 'lost_time']),
            recordable_incidents=len(df[df['severity'] == 'recordable']),
            total_penalties=df['penalty_amount'].sum() if 'penalty_amount' in df.columns else 0.0,
            total_spill_volume=df['spill_volume_bbls'].sum() if 'spill_volume_bbls' in df.columns else 0.0,
            years_analyzed=int(years)
        )

        return profile

    def analyze_field_risk(
        self,
        field_name: str,
        years: int = 5
    ) -> Dict[str, Any]:
        """
        Analyze HSE risk for a specific field.

        Args:
            field_name: Field name to analyze
            years: Number of years to analyze

        Returns:
            Dictionary with field risk analysis
        """
        if self._incidents_cache is None:
            self.load_incidents()

        df = self._incidents_cache.copy()
        cutoff = datetime.now() - timedelta(days=years * 365)

        # Filter by field and date
        field_df = df[
            (df['field_name'].str.contains(field_name, case=False, na=False)) &
            (df['incident_date'] >= cutoff)
        ]

        # Get unique operators for this field
        operators = field_df['operator'].unique().tolist() if len(field_df) > 0 else []

        # Incident breakdown by type
        type_counts = field_df['incident_type'].value_counts().to_dict() if len(field_df) > 0 else {}
        severity_counts = field_df['severity'].value_counts().to_dict() if len(field_df) > 0 else {}

        # Calculate field risk score
        weighted_sum = (
            severity_counts.get('fatality', 0) * 100 +
            severity_counts.get('lost_time', 0) * 25 +
            severity_counts.get('recordable', 0) * 10 +
            severity_counts.get('near_miss', 0) * 5 +
            severity_counts.get('minor', 0) * 1
        )

        max_expected = 50 * years  # Expected maximum for 5 years
        field_score = 100 - min(100, (weighted_sum / max_expected) * 100)

        return {
            "field_name": field_name,
            "analysis_years": years,
            "total_incidents": len(field_df),
            "operators": operators,
            "incident_types": type_counts,
            "severity_breakdown": severity_counts,
            "field_safety_score": round(field_score, 1),
            "risk_category": self._score_to_category(field_score),
            "total_penalties": field_df['penalty_amount'].sum() if 'penalty_amount' in field_df.columns else 0.0,
            "total_spill_volume": field_df['spill_volume_bbls'].sum() if 'spill_volume_bbls' in field_df.columns else 0.0
        }

    def _score_to_category(self, score: float) -> str:
        """Convert safety score to risk category."""
        if score >= 90:
            return "LOW"
        elif score >= 70:
            return "MODERATE"
        elif score >= 50:
            return "ELEVATED"
        return "HIGH"

    def calculate_risk_adjusted_npv(
        self,
        base_npv: float,
        operator: str,
        include_penalty_exposure: bool = True,
        include_insurance_adjustment: bool = True
    ) -> RiskAdjustedMetrics:
        """
        Calculate risk-adjusted NPV based on operator safety profile.

        Args:
            base_npv: Base NPV before risk adjustment
            operator: Operator name for safety lookup
            include_penalty_exposure: Include potential penalty exposure
            include_insurance_adjustment: Include insurance cost adjustment

        Returns:
            RiskAdjustedMetrics with adjusted values
        """
        profile = self.get_operator_profile(operator)

        # Get risk discount factor
        risk_factor = self.RISK_DISCOUNT_FACTORS.get(profile.risk_category, 0.10)

        # Calculate potential penalty exposure (3-year average * 5)
        penalty_exposure = 0.0
        if include_penalty_exposure and profile.years_analyzed > 0:
            annual_penalties = profile.total_penalties / profile.years_analyzed
            penalty_exposure = annual_penalties * 5  # 5-year project life assumption

        # Calculate insurance adjustment (based on TRIR comparison)
        insurance_adj = 0.0
        if include_insurance_adjustment and profile.trir:
            # Higher TRIR = higher insurance costs
            trir_ratio = profile.trir / self.INDUSTRY_TRIR_BENCHMARK
            insurance_adj = base_npv * 0.02 * max(0, trir_ratio - 1)  # 2% base rate adjustment

        # Calculate risk-adjusted NPV
        risk_adjusted = base_npv * (1 - risk_factor) - penalty_exposure - insurance_adj

        return RiskAdjustedMetrics(
            base_npv=base_npv,
            risk_adjusted_npv=round(risk_adjusted, 2),
            risk_discount_factor=risk_factor,
            safety_score=profile.safety_score,
            risk_category=profile.risk_category,
            potential_penalty_exposure=round(penalty_exposure, 2),
            insurance_adjustment=round(insurance_adj, 2)
        )

    def get_incident_trends(
        self,
        operator: str = None,
        field: str = None,
        years: int = 5,
        frequency: str = 'Y'
    ) -> pd.DataFrame:
        """
        Get incident trends over time.

        Args:
            operator: Filter by operator (optional)
            field: Filter by field (optional)
            years: Number of years to analyze
            frequency: Grouping frequency ('Y' year, 'Q' quarter, 'M' month)

        Returns:
            DataFrame with trend data
        """
        if self._incidents_cache is None:
            self.load_incidents()

        df = self._incidents_cache.copy()
        cutoff = datetime.now() - timedelta(days=years * 365)
        df = df[df['incident_date'] >= cutoff]

        if operator:
            df = df[df['operator'].str.contains(operator, case=False, na=False)]
        if field:
            df = df[df['field_name'].str.contains(field, case=False, na=False)]

        # Group by period
        df['period'] = df['incident_date'].dt.to_period(frequency)

        # Aggregate
        trends = df.groupby('period').agg({
            'bsee_incident_id': 'count',
            'penalty_amount': 'sum' if 'penalty_amount' in df.columns else lambda x: 0,
            'spill_volume_bbls': 'sum' if 'spill_volume_bbls' in df.columns else lambda x: 0
        }).reset_index()

        trends.columns = ['period', 'incident_count', 'total_penalties', 'total_spill_volume']
        trends['period'] = trends['period'].astype(str)

        return trends

    def compare_operators(
        self,
        operators: List[str],
        years: int = 5
    ) -> pd.DataFrame:
        """
        Compare safety profiles across multiple operators.

        Args:
            operators: List of operator names to compare
            years: Number of years to analyze

        Returns:
            DataFrame with operator comparison
        """
        start_date = datetime.now() - timedelta(days=years * 365)

        results = []
        for op in operators:
            profile = self.get_operator_profile(op, start_date=start_date)
            results.append({
                'operator': profile.operator_name,
                'total_incidents': profile.total_incidents,
                'fatalities': profile.fatalities,
                'lost_time': profile.lost_time_incidents,
                'recordable': profile.recordable_incidents,
                'safety_score': profile.safety_score,
                'risk_category': profile.risk_category,
                'total_penalties': profile.total_penalties,
                'total_spill_volume': profile.total_spill_volume
            })

        return pd.DataFrame(results).sort_values('safety_score', ascending=False)
```

### HSE Report Generator

```python
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from pathlib import Path
from datetime import datetime

class HSEReportGenerator:
    """
    Generate interactive HTML reports for HSE risk analysis.
    """

    def __init__(self, analyzer: HSERiskAnalyzer):
        """
        Initialize report generator.

        Args:
            analyzer: HSERiskAnalyzer instance
        """
        self.analyzer = analyzer

    def generate_operator_report(
        self,
        operator: str,
        output_path: Path,
        years: int = 5
    ) -> Path:
        """
        Generate comprehensive operator safety report.

        Args:
            operator: Operator name
            output_path: Output HTML file path
            years: Years to analyze

        Returns:
            Path to generated report
        """
        profile = self.analyzer.get_operator_profile(
            operator,
            start_date=datetime.now() - timedelta(days=years * 365)
        )
        trends = self.analyzer.get_incident_trends(operator=operator, years=years)

        # Create subplots
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=[
                'Incident Trends', 'Severity Breakdown',
                'Safety Score Gauge', 'Penalty History'
            ],
            specs=[
                [{"type": "scatter"}, {"type": "pie"}],
                [{"type": "indicator"}, {"type": "bar"}]
            ]
        )

        # Trend line
        fig.add_trace(
            go.Scatter(
                x=trends['period'],
                y=trends['incident_count'],
                mode='lines+markers',
                name='Incidents'
            ),
            row=1, col=1
        )

        # Severity pie
        severity_data = [
            profile.fatalities,
            profile.lost_time_incidents,
            profile.recordable_incidents,
            profile.total_incidents - profile.fatalities - profile.lost_time_incidents - profile.recordable_incidents
        ]
        severity_labels = ['Fatalities', 'Lost Time', 'Recordable', 'Other']

        fig.add_trace(
            go.Pie(
                labels=severity_labels,
                values=severity_data,
                hole=0.4
            ),
            row=1, col=2
        )

        # Safety score gauge
        fig.add_trace(
            go.Indicator(
                mode="gauge+number",
                value=profile.safety_score,
                title={'text': f"Safety Score ({profile.risk_category})"},
                gauge={
                    'axis': {'range': [0, 100]},
                    'bar': {'color': "darkblue"},
                    'steps': [
                        {'range': [0, 50], 'color': "red"},
                        {'range': [50, 70], 'color': "orange"},
                        {'range': [70, 90], 'color': "yellow"},
                        {'range': [90, 100], 'color': "green"}
                    ]
                }
            ),
            row=2, col=1
        )

        # Penalty bar chart
        fig.add_trace(
            go.Bar(
                x=trends['period'],
                y=trends['total_penalties'],
                name='Penalties ($)'
            ),
            row=2, col=2
        )

        fig.update_layout(
            title=f"HSE Safety Report: {operator}",
            height=800,
            showlegend=True
        )

        # Write to file
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        fig.write_html(str(output_path))

        return output_path

    def generate_comparison_report(
        self,
        operators: List[str],
        output_path: Path,
        years: int = 5
    ) -> Path:
        """
        Generate operator comparison report.

        Args:
            operators: List of operators to compare
            output_path: Output HTML file path
            years: Years to analyze

        Returns:
            Path to generated report
        """
        comparison = self.analyzer.compare_operators(operators, years)

        fig = make_subplots(
            rows=2, cols=1,
            subplot_titles=['Safety Score Comparison', 'Incident Breakdown'],
            specs=[[{"type": "bar"}], [{"type": "bar"}]]
        )

        # Safety score bars
        colors = comparison['risk_category'].map({
            'LOW': 'green',
            'MODERATE': 'yellow',
            'ELEVATED': 'orange',
            'HIGH': 'red'
        })

        fig.add_trace(
            go.Bar(
                x=comparison['operator'],
                y=comparison['safety_score'],
                marker_color=colors,
                name='Safety Score'
            ),
            row=1, col=1
        )

        # Incident breakdown grouped bar
        fig.add_trace(
            go.Bar(x=comparison['operator'], y=comparison['fatalities'], name='Fatalities'),
            row=2, col=1
        )
        fig.add_trace(
            go.Bar(x=comparison['operator'], y=comparison['lost_time'], name='Lost Time'),
            row=2, col=1
        )
        fig.add_trace(
            go.Bar(x=comparison['operator'], y=comparison['recordable'], name='Recordable'),
            row=2, col=1
        )

        fig.update_layout(
            title="Operator Safety Comparison",
            height=700,
            barmode='group'
        )

        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        fig.write_html(str(output_path))

        return output_path
```

## Usage Examples

### Basic Operator Safety Assessment

```python
from worldenergydata.hse import HSERiskAnalyzer

# Initialize analyzer
analyzer = HSERiskAnalyzer()
analyzer.load_incidents(Path("data/hse/incidents.csv"))

# Get operator safety profile
profile = analyzer.get_operator_profile("Chevron")

print(f"Operator: {profile.operator_name}")
print(f"Safety Score: {profile.safety_score}/100 ({profile.risk_category})")
print(f"Total Incidents: {profile.total_incidents}")
print(f"Fatalities: {profile.fatalities}")
print(f"Total Penalties: ${profile.total_penalties:,.2f}")
```

### Field Risk Analysis

```python
# Analyze specific field
field_risk = analyzer.analyze_field_risk("Thunder Horse", years=5)

print(f"Field: {field_risk['field_name']}")
print(f"Risk Category: {field_risk['risk_category']}")
print(f"Safety Score: {field_risk['field_safety_score']}")
print(f"Incidents by Type: {field_risk['incident_types']}")
```

### Risk-Adjusted NPV Calculation

```python
# Calculate risk-adjusted NPV
base_npv = 150_000_000  # $150M base NPV

risk_metrics = analyzer.calculate_risk_adjusted_npv(
    base_npv=base_npv,
    operator="Shell",
    include_penalty_exposure=True,
    include_insurance_adjustment=True
)

print(f"Base NPV: ${risk_metrics.base_npv:,.0f}")
print(f"Risk-Adjusted NPV: ${risk_metrics.risk_adjusted_npv:,.0f}")
print(f"NPV Impact: ${risk_metrics.npv_impact:,.0f} ({risk_metrics.npv_impact_percent:.1f}%)")
print(f"Risk Category: {risk_metrics.risk_category}")
```

### Operator Comparison

```python
# Compare multiple operators
operators = ["Shell", "Chevron", "BP", "ExxonMobil"]
comparison = analyzer.compare_operators(operators, years=5)

print(comparison[['operator', 'safety_score', 'risk_category', 'total_incidents']])
```

### Generate Reports

```python
from worldenergydata.hse import HSEReportGenerator

# Initialize report generator
reporter = HSEReportGenerator(analyzer)

# Generate operator report
report_path = reporter.generate_operator_report(
    operator="Shell",
    output_path=Path("reports/shell_hse_report.html"),
    years=5
)
print(f"Report generated: {report_path}")

# Generate comparison report
comparison_path = reporter.generate_comparison_report(
    operators=["Shell", "Chevron", "BP"],
    output_path=Path("reports/operator_comparison.html"),
    years=5
)
```

## YAML Configuration

```yaml
hse_analysis:
  data_source: "data/modules/hse"

  operator_analysis:
    operator: "Chevron"
    years: 5
    include_subsidiaries: true

  field_analysis:
    fields:
      - "Thunder Horse"
      - "Mars"
      - "Atlantis"
    years: 5

  risk_adjustment:
    include_penalty_exposure: true
    include_insurance_adjustment: true
    custom_discount_factors:
      LOW: 0.0
      MODERATE: 0.05
      ELEVATED: 0.10
      HIGH: 0.20

  reporting:
    output_dir: "reports/hse"
    formats:
      - html
      - csv
    include_charts: true
```

## Integration with NPV Analysis

```python
from worldenergydata.hse import HSERiskAnalyzer
from worldenergydata.economics import NPVCalculator

# Initialize components
hse_analyzer = HSERiskAnalyzer()
npv_calc = NPVCalculator()

# Calculate base NPV
base_result = npv_calc.calculate(
    production_profile=production_df,
    price_assumptions=prices,
    fiscal_terms=terms,
    discount_rate=0.10
)

# Apply HSE risk adjustment
risk_metrics = hse_analyzer.calculate_risk_adjusted_npv(
    base_npv=base_result.npv,
    operator="Shell"
)

print(f"Base NPV: ${base_result.npv:,.0f}")
print(f"Risk-Adjusted NPV: ${risk_metrics.risk_adjusted_npv:,.0f}")
print(f"Safety Risk Category: {risk_metrics.risk_category}")
```

## ESG Compliance Output

```python
# Generate ESG-compliant safety summary
def generate_esg_summary(analyzer: HSERiskAnalyzer, operator: str) -> Dict[str, Any]:
    """Generate ESG-compliant safety summary for reporting."""
    profile = analyzer.get_operator_profile(operator)

    return {
        "operator": operator,
        "reporting_period_years": profile.years_analyzed,
        "safety_metrics": {
            "total_recordable_incident_rate": profile.trir,
            "fatalities": profile.fatalities,
            "lost_time_incidents": profile.lost_time_incidents,
            "recordable_incidents": profile.recordable_incidents,
            "safety_score": profile.safety_score,
            "risk_classification": profile.risk_category
        },
        "environmental_metrics": {
            "total_spill_volume_bbls": profile.total_spill_volume,
            "regulatory_penalties_usd": profile.total_penalties
        },
        "governance_metrics": {
            "compliance_status": "COMPLIANT" if profile.safety_score >= 70 else "REVIEW_REQUIRED"
        }
    }
```

## Notes

- Requires HSE incident data in CSV format or database connection
- Safety scores are normalized 0-100 (higher = safer)
- Risk discount factors are configurable for organization-specific policies
- Integrates with existing NPV and economic analysis modules
- Supports ESG reporting requirements for institutional investors
- TRIR calculations require exposure hours data for accuracy
