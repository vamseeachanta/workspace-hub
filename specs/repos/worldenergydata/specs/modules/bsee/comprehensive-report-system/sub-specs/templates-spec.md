# Report Templates Specification

This is the report templates specification for the spec detailed in @specs/modules/bsee/comprehensive-report-system/spec.md

> Created: 2025-08-06
> Version: 1.0.0

## Overview

This specification defines the standardized report templates that will be available in the comprehensive well and production reporting system. Each template serves specific business use cases and provides consistent formatting across organizational levels.

## Template Architecture

### Base Template Structure
All report templates inherit from a base template that provides:
- Consistent header and footer formatting
- Standard data validation and aggregation
- Common metrics calculations
- Shared visualization components
- Multi-format export capabilities

### Template Inheritance Hierarchy
```
BaseReportTemplate
├── ComplianceTemplate
├── EconomicTemplate  
├── TechnicalTemplate
├── ExecutiveTemplate
└── CustomTemplate (future)
```

## Template Specifications

### 1. Compliance Template

**Purpose:** Regulatory compliance reporting and government submissions

**Target Users:** Regulatory analysts, compliance officers, government relations

**Key Sections:**
- **Regulatory Overview** - Permit status, compliance metrics, violations
- **Production Compliance** - Production quotas vs. actual, deviation analysis
- **Environmental Metrics** - Water production, gas flaring, spill incidents
- **Well Status Summary** - Active/inactive wells, P&A requirements
- **Safety Performance** - Incident rates, safety metrics, inspection results

**Visualizations:**
- Compliance trend charts over time
- Production vs. quota comparison charts
- Environmental impact dashboards
- Safety performance scorecards

**Output Formats:** Excel (primary), PDF (for submissions)

**Data Requirements:**
```yaml
compliance_template:
  required_data:
    - well_status_data
    - production_data
    - environmental_data
    - incident_data
    - permit_data
  date_granularity: monthly
  historical_period: 24_months
```

### 2. Economic Template

**Purpose:** Financial analysis and investment decision support

**Target Users:** Asset managers, investment analysts, executives

**Key Sections:**
- **Executive Summary** - Key financial metrics, ROI, payback period
- **Production Economics** - Revenue analysis, operating costs, netback calculations
- **Well Economics** - Individual well NPV, break-even analysis, decline curves
- **Capital Investment** - CAPEX analysis, drilling costs, facility investments
- **Comparative Analysis** - Peer benchmarking, field-to-field comparisons

**Visualizations:**
- NPV waterfall charts
- Production decline curves with economic overlays
- Cost structure breakdowns
- ROI trend analysis
- Capital efficiency metrics

**Output Formats:** Excel (detailed), PDF (executive summary), HTML (interactive dashboard)

**Economic Calculations:**
```python
# Key economic metrics
npv_10_percent = calculate_npv(cash_flows, discount_rate=0.10)
payback_period = calculate_payback_period(cash_flows)
roi = (total_revenue - total_costs) / total_costs
netback = oil_price - (transport_cost + processing_cost + royalties)
```

### 3. Technical Template

**Purpose:** Engineering analysis and operational optimization

**Target Users:** Reservoir engineers, production engineers, operations managers

**Key Sections:**
- **Reservoir Performance** - Pressure analysis, recovery factors, drive mechanisms
- **Well Performance** - Production profiles, artificial lift analysis, workover history
- **Facilities Utilization** - Processing capacity, bottlenecks, optimization opportunities
- **Development Planning** - Drilling locations, completion designs, field development
- **Technical Benchmarking** - Performance vs. analog fields, best practices

**Visualizations:**
- Production type curves and decline analysis
- Bubble charts showing well performance vs. completion parameters
- Facility utilization heat maps
- Reservoir pressure maps and contours
- Development timeline Gantt charts

**Output Formats:** Excel (primary), PDF (technical reports)

**Technical Calculations:**
```python
# Production analysis
decline_rate = calculate_decline_rate(production_data)
eur = calculate_eur(production_data, decline_parameters)
recovery_factor = cumulative_production / ooip
artificial_lift_efficiency = (actual_rate / theoretical_rate) * 100
```

### 4. Executive Template

**Purpose:** High-level summary for C-suite and board presentations

**Target Users:** Executives, board members, investors

**Key Sections:**
- **Performance Dashboard** - KPI summary, traffic light indicators
- **Strategic Metrics** - Production growth, reserves additions, capital efficiency
- **Financial Highlights** - Revenue, EBITDA, free cash flow
- **Operational Excellence** - Safety metrics, environmental performance
- **Market Position** - Competitive benchmarking, market share

**Visualizations:**
- Executive dashboard with KPI gauges
- Trend charts for key metrics
- Geographic heat maps showing asset performance
- Comparative charts vs. industry benchmarks
- Strategic milestone timeline

**Output Formats:** PDF (primary), PowerPoint (future), HTML (dashboard)

**Executive KPIs:**
```yaml
executive_kpis:
  production:
    - total_oil_production_bopd
    - production_growth_rate
    - wells_online_count
  financial:
    - revenue_per_barrel
    - operating_margin
    - capex_efficiency
  operational:
    - safety_incident_rate
    - environmental_compliance_score
    - well_uptime_percentage
```

## Template Implementation Details

### Jinja2 Template Structure
```jinja2
{# Base template structure #}
<!DOCTYPE html>
<html>
<head>
    <title>{{ report_title }}</title>
    <style>{{ css_styles }}</style>
</head>
<body>
    <header>
        {% include 'partials/header.html' %}
    </header>
    
    <main>
        {% block content %}
        <!-- Template-specific content -->
        {% endblock %}
    </main>
    
    <footer>
        {% include 'partials/footer.html' %}
    </footer>
</body>
</html>
```

### Excel Template Structure
```python
# Excel workbook template configuration
excel_template = {
    'compliance': {
        'sheets': [
            'Executive Summary',
            'Production Compliance',
            'Environmental Metrics',
            'Well Status',
            'Data Sources'
        ],
        'formatting': {
            'headers': {'bold': True, 'color': '#4472C4'},
            'data': {'font_size': 10, 'alignment': 'center'},
            'charts': {'style': 'professional', 'colors': 'corporate'}
        }
    }
}
```

### PDF Styling
```css
/* PDF-specific CSS */
@page {
    size: letter;
    margin: 1in;
}

.executive-summary {
    page-break-after: always;
    background-color: #f8f9fa;
    padding: 20px;
}

.chart-container {
    page-break-inside: avoid;
    margin: 20px 0;
}

.data-table {
    font-size: 10pt;
    border-collapse: collapse;
    width: 100%;
}
```

## Template Configuration Schema

```yaml
template_config:
  compliance:
    sections:
      executive_summary:
        enabled: true
        include_charts: true
        chart_types: ['compliance_trend', 'quota_comparison']
      
      production_compliance:
        enabled: true
        date_range: 24  # months
        include_deviations: true
        threshold_alerts: true
        
      environmental_metrics:
        enabled: true
        metrics: ['water_production', 'gas_flaring', 'spills']
        
    formatting:
      logo_path: 'assets/company_logo.png'
      color_scheme: 'corporate_blue'
      font_family: 'Arial'
      
    exports:
      excel:
        include_raw_data: true
        password_protect: false
      pdf:
        include_appendix: true
        watermark: 'CONFIDENTIAL'
```

## Template Customization

### Variable Substitution
Templates support variable substitution for:
- Company branding (logos, colors, fonts)
- Report metadata (dates, organizational units)
- Calculated metrics and KPIs
- Chart styling and formatting
- Footer information and disclaimers

### Conditional Content
```jinja2
{% if organizational_unit.type == 'block' %}
    <h2>Block {{ organizational_unit.id }} Summary</h2>
    {% include 'sections/block_overview.html' %}
{% elif organizational_unit.type == 'field' %}
    <h2>Field {{ organizational_unit.name }} Analysis</h2>
    {% include 'sections/field_details.html' %}
{% endif %}
```

### Custom Metrics
```python
# Custom metric definitions per template
template_metrics = {
    'economic': [
        'npv_10_percent',
        'irr',
        'payback_period',
        'break_even_oil_price'
    ],
    'technical': [
        'decline_rate',
        'recovery_factor',
        'well_spacing_efficiency',
        'completion_effectiveness'
    ]
}
```

## Template Validation

### Data Requirements Check
- Verify all required data sources are available
- Validate date ranges and data completeness
- Check for missing critical fields
- Ensure data quality meets template standards

### Output Quality Assurance
- Validate chart generation and formatting
- Verify calculation accuracy
- Check export format integrity
- Test template rendering across different data sizes

### Template Testing Framework
```python
class TemplateTest:
    def test_compliance_template_rendering(self):
        """Test compliance template with sample data"""
        data = load_test_data('compliance_sample.json')
        template = ComplianceTemplate()
        report = template.generate(data)
        
        assert report.sections['executive_summary'] is not None
        assert len(report.charts) >= 3
        assert report.validate_output()
```

## Template Maintenance

### Version Control
- Templates versioned independently from core system
- Backward compatibility for template API changes
- Migration scripts for template updates
- Template change documentation

### Performance Monitoring
- Template rendering time metrics
- Memory usage during report generation
- Export format quality checks
- User feedback and improvement tracking