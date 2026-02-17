# Technical Specification

This is the technical specification for the spec detailed in @specs/modules/bsee/comprehensive-report-system/spec.md

> Created: 2025-08-06
> Version: 1.1.0
> Last Updated: 2025-08-22
> Status: Enhanced

## Technical Requirements

### Core Functionality
- **Hierarchical Data Organization:** Support block → field → lease hierarchy with automatic parent-child relationships
- **Multi-Level Aggregation:** Aggregate production, well count, and economic metrics across organizational levels
- **Template-Based Reporting:** Flexible template system for different report types and use cases
- **Multi-Format Export:** Generate Excel, PDF, HTML, and JSON outputs from single report definition
- **Interactive Visualizations:** Integrate Plotly charts with drill-down and filtering capabilities
- **Data Validation:** Ensure data consistency and completeness across aggregation levels

### Performance Requirements
- Process block-level reports (1000+ wells) in under 10 minutes
- Support concurrent report generation for multiple organizational units
- Handle datasets up to 5GB without memory overflow
- Maintain <500MB memory footprint during normal operations
- Cache intermediate results for repeated report generation

### Integration Requirements
- Integrate with existing BSEE analysis modules (well_api10, well_api12, production_api10, production_api12)
- Reuse existing data loading and binary file processing
- Maintain compatibility with current visualization templates
- Support existing YAML configuration structure

### Output Requirements
- Excel workbooks with multiple sheets, formatting, and embedded charts
- PDF documents with professional formatting and consistent branding
- Interactive HTML dashboards with responsive design
- JSON data export for programmatic integration
- PNG/SVG chart exports for presentations

## Architecture Design

### Module Structure
```
modules/bsee/reports/
├── __init__.py
├── controller.py         # Main report orchestrator
├── aggregators/
│   ├── __init__.py
│   ├── base.py          # Abstract aggregation base
│   ├── block_aggregator.py
│   ├── field_aggregator.py
│   └── lease_aggregator.py
├── templates/
│   ├── __init__.py
│   ├── base_template.py # Template base class
│   ├── compliance_template.py
│   ├── economic_template.py
│   ├── technical_template.py
│   └── executive_template.py
├── exporters/
│   ├── __init__.py
│   ├── excel_exporter.py
│   ├── pdf_exporter.py
│   ├── html_exporter.py
│   └── json_exporter.py
├── visualizations/
│   ├── __init__.py
│   ├── production_charts.py
│   ├── well_performance.py
│   └── economic_charts.py
└── utils/
    ├── __init__.py
    ├── hierarchy.py     # Organizational hierarchy logic
    └── metrics.py       # Calculated metrics
```

### Class Hierarchy
```
ReportController
├── DataAggregator (ABC)
│   ├── BlockAggregator
│   ├── FieldAggregator
│   └── LeaseAggregator
├── ReportTemplate (ABC)
│   ├── ComplianceTemplate
│   ├── EconomicTemplate
│   ├── TechnicalTemplate
│   └── ExecutiveTemplate
└── ReportExporter (ABC)
    ├── ExcelExporter
    ├── PDFExporter
    ├── HTMLExporter
    └── JSONExporter
```

### Data Flow Architecture
1. **Data Loading** → Load well and production data from binary files
2. **Hierarchy Building** → Establish block → field → lease relationships
3. **Data Aggregation** → Calculate metrics at each organizational level
4. **Template Application** → Apply selected template to aggregated data
5. **Visualization Generation** → Create charts and maps based on template
6. **Multi-Format Export** → Generate outputs in requested formats
7. **Quality Validation** → Verify output completeness and accuracy

## Approach Options

**Option A: Single Monolithic Report Generator**
- Pros: Simple implementation, single entry point, easy to test
- Cons: Hard to extend, limited flexibility, difficult maintenance

**Option B: Modular Template-Based System (Selected)**
- Pros: Extensible, reusable components, template customization, maintainable
- Cons: More complex architecture, multiple interfaces to maintain

**Option C: Configuration-Driven Report Builder**
- Pros: Highly configurable, no code changes for new reports
- Cons: Complex configuration, limited customization, debugging challenges

**Rationale:** The modular template-based approach provides the best balance of flexibility and maintainability. It allows for standardized report formats while enabling customization for specific use cases.

## Data Models

### Organizational Hierarchy
```python
@dataclass
class OrganizationalUnit:
    id: str
    name: str
    type: Literal['block', 'field', 'lease']
    parent_id: Optional[str]
    children: List['OrganizationalUnit']
    
@dataclass  
class WellSummary:
    api_number: str
    lease_id: str
    field_id: str
    block_id: str
    status: str
    spud_date: date
    completion_date: Optional[date]
    total_depth: float
    production_start: Optional[date]

@dataclass
class ProductionMetrics:
    unit_id: str
    unit_type: str
    period_start: date
    period_end: date
    oil_production_bbl: float
    gas_production_mcf: float
    water_production_bbl: float
    well_count: int
    active_well_count: int
```

### Report Configuration Schema
```yaml
report:
  type: block  # block | field | lease
  template: economic  # economic | technical | compliance | executive
  organizational_units:
    - id: "525"
      name: "Block 525"
  
  # Date range for analysis
  date_range:
    start: "2020-01-01"
    end: "2024-12-31"
    
  # Output specifications
  outputs:
    - format: excel
      filename: "block_525_economic_report.xlsx"
    - format: pdf  
      filename: "block_525_economic_report.pdf"
      
  # Report sections to include
  sections:
    - executive_summary
    - production_overview
    - well_performance
    - economic_analysis
    - technical_details
    
  # Visualization options
  charts:
    production_trends: true
    well_performance_scatter: true
    economic_waterfall: true
    geographical_map: true
```

## External Dependencies

### New Dependencies
- **jinja2 (^3.1.0)** - Template engine for report generation
  - **Justification:** Industry standard for template-based document generation
  
- **weasyprint (^60.0)** - HTML to PDF conversion
  - **Justification:** High-quality PDF generation with CSS styling support
  
- **openpyxl (^3.1.0)** - Excel file generation with formatting
  - **Justification:** Rich Excel formatting capabilities beyond pandas
  
- **python-pptx (^0.6.0)** - PowerPoint generation (future)
  - **Justification:** For presentation-ready outputs

### Existing Dependencies (Leveraged)
- pandas - Data manipulation and aggregation
- plotly - Interactive visualization generation
- numpy - Numerical calculations
- loguru - Structured logging
- pyyaml - Configuration file processing

## Performance Optimization Strategies

### Data Processing
- **Lazy Loading:** Load only required data based on organizational unit selection
- **Incremental Aggregation:** Cache intermediate aggregation results
- **Parallel Processing:** Process multiple organizational units concurrently
- **Memory Management:** Stream processing for large datasets

### Caching Strategy
```python
# Redis-like caching for aggregated metrics
cache_key = f"{unit_type}:{unit_id}:{date_range}:{metrics_hash}"
cached_metrics = cache.get(cache_key)
if not cached_metrics:
    metrics = calculate_metrics(data)
    cache.set(cache_key, metrics, ttl=3600)
```

### Database Indexing
- Index binary files by organizational unit for faster retrieval
- Create lookup tables for block → field → lease relationships
- Pre-calculate common metrics for frequently accessed units

## Output Specifications

### Excel Workbook Structure
```
Report Workbook:
├── Executive Summary (Sheet)
├── Production Overview (Sheet)
├── Well Summary (Sheet)
├── Economic Analysis (Sheet)
├── Technical Details (Sheet)
├── Data Sources (Sheet)
└── Charts (Embedded in relevant sheets)
```

### PDF Document Layout
- Header with organizational unit information and report date
- Executive summary with key metrics
- Section-based content with professional formatting
- Embedded charts and tables
- Footer with data sources and generation timestamp

### HTML Dashboard Features
- Responsive design for desktop and mobile
- Interactive Plotly charts with drill-down
- Filterable data tables
- Export buttons for underlying data
- Print-friendly CSS for hard copies

## Security and Compliance

- **Data Access Control:** Read-only access to existing binary data files
- **Input Validation:** Sanitize all organizational unit IDs and date ranges
- **Output Security:** No sensitive data exposure in generated reports
- **Audit Trail:** Log all report generation activities with timestamps
- **Export Control:** Verify user permissions for different output formats