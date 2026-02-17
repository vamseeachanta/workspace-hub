# Spec Requirements Document

> Spec: Comprehensive Report System
> Created: 2025-08-06
> Status: Planning
> Module: bsee
> Variant: enhanced

## Prompt Summary

**Original Request:** Comprehensive Well and production report (by block, field, lease). Should be able to:
- Technical data is given here
  - .agent-os\specs\modules\bsee\2025-08-06-comprehensive-reports\sub-specs\go_by

**Context Provided:** 
- Enhanced spec instructions from AssetUtilities repository
- Request for comprehensive reporting capabilities across different organizational levels
- Need for block, field, and lease-based reporting

**Clarifications Made:**
1. Block, field, and lease represent different organizational hierarchies for offshore oil & gas data
2. Reports should aggregate well and production data at each organizational level
3. Output format and delivery methods need to be defined
4. Integration with existing analysis modules is required

**Reuse Notes:** 
- Existing BSEE analysis modules: well_api10.py, well_api12.py, production_api10.py, production_api12.py
- Current lease reporting script: build_lease_report_final.py
- Block data processing: BlockData class
- Plotly visualization capabilities already established

**Prompt Evolution:** From basic reporting request to comprehensive multi-level report generation system with hierarchical data organization

## Executive Summary

### Business Impact
This comprehensive reporting system will enable energy analysts to generate standardized reports at block, field, and lease levels, reducing manual report generation time by 80% and providing consistent data presentation across different organizational hierarchies. The system will support decision-making for asset acquisition, field development, and regulatory compliance.

### Technical Overview
The solution involves creating a unified reporting framework that aggregates well and production data across three organizational levels: individual leases (smallest unit), fields (collection of leases), and blocks (geographical areas). Reports will include production summaries, well performance metrics, economic indicators, and visual analytics with export capabilities to multiple formats.

### Resource Requirements
- **Estimated Effort:** 3-4 weeks (120-160 hours)
- **Dependencies:** Existing BSEE data modules, visualization libraries, export utilities
- **Team:** 1 developer with data analysis and reporting experience

### Risk Assessment
- **Data Consistency:** Risk of inconsistent aggregation across levels; mitigation through comprehensive validation
- **Performance:** Large datasets may cause slow report generation; mitigation via caching and incremental processing  
- **User Adoption:** Complex interface may hinder adoption; mitigation through intuitive CLI and templates

## System Overview

The Comprehensive Report System creates a unified reporting framework for offshore energy data analysis. It provides standardized reports across organizational hierarchies with rich visualizations and multiple export formats.

```mermaid
graph TB
    subgraph "Data Sources"
        A[Well Data]
        B[Production Data]
        C[Block Data]
        D[Field Data]
        E[Lease Data]
    end
    
    subgraph "Report Engine"
        F[Report Controller]
        G[Data Aggregator]
        H[Template Engine]
        I[Visualization Engine]
    end
    
    subgraph "Report Types"
        J[Block Reports]
        K[Field Reports]
        L[Lease Reports]
        M[Comparative Reports]
    end
    
    subgraph "Output Formats"
        N[Excel Workbooks]
        O[PDF Documents]
        P[HTML Reports]
        Q[JSON Data]
        R[Interactive Dashboards]
    end
    
    A --> G
    B --> G
    C --> G
    D --> G
    E --> G
    
    F --> G
    G --> H
    H --> I
    
    F --> J
    F --> K
    F --> L
    F --> M
    
    J --> N
    J --> O
    K --> N
    K --> P
    L --> N
    L --> O
    M --> P
    M --> R
    
    style F fill:#f9f,stroke:#333,stroke-width:4px
    style G fill:#bbf,stroke:#333,stroke-width:2px
    style I fill:#9f9,stroke:#333,stroke-width:2px
```

### Architecture Notes
- **Hierarchical Processing:** Reports can drill down from block → field → lease levels
- **Template System:** Standardized templates ensure consistent formatting across report types
- **Multi-Format Output:** Single report definition generates multiple output formats
- **Performance Optimization:** Incremental aggregation and caching for large datasets

## Overview

Implement a comprehensive reporting system for well and production data that enables users to generate detailed reports organized by block, field, and lease hierarchies. The system will provide standardized templates, interactive visualizations, and multiple export formats to support various business use cases from regulatory compliance to investment analysis.

### Future Update Prompt

For future modifications to this spec, use the following prompt:
```
Update the comprehensive well and production reports spec to include:
- New report types or organizational levels
- Additional data sources or metrics
- Enhanced visualization requirements
- New export formats or delivery methods
- Integration with external systems or databases
Maintain compatibility with existing templates and ensure consistent data aggregation across all levels.
```

## User Stories

### Asset Manager Creating Block Performance Report

As an asset manager, I want to generate a comprehensive block performance report for Block 525, so that I can evaluate the overall productivity and identify high-performing fields within the block.

The manager executes `python -m worldenergydata.bsee report --type block --id 525 --format excel`. The system aggregates all well and production data within Block 525, groups by fields, calculates cumulative production metrics, identifies top-performing wells, and generates a multi-sheet Excel workbook with production trends, well summaries, and field comparisons. The report includes visual charts and executive summary metrics.

### Regulatory Analyst Generating Lease Compliance Report

As a regulatory analyst, I want to create detailed lease reports for multiple leases simultaneously, so that I can ensure compliance with production requirements and identify potential issues.

The analyst runs `python -m worldenergydata.bsee report --type lease --ids G12345,G12346,G12347 --template compliance --format pdf`. The system generates standardized compliance reports for each lease including production history, well status, environmental metrics, and regulatory milestones. Each PDF report follows the same template structure for consistent review and approval processes.

### Investment Analyst Comparing Field Economics

As an investment analyst, I want to generate comparative field reports with economic metrics, so that I can evaluate potential acquisition targets across different fields.

The analyst executes `python -m worldenergydata.bsee report --type field --comparison true --metrics economic --output dashboard`. The system creates an interactive HTML dashboard comparing multiple fields across key economic indicators including NPV estimates, production rates, well performance, and development costs. The dashboard allows filtering and drill-down into individual well data.

## Spec Scope

1. **Multi-Level Report Engine** - Implement hierarchical reporting system supporting block, field, and lease organization levels
2. **Template System** - Create standardized report templates for different use cases (compliance, economic, technical, executive)
3. **Data Aggregation Framework** - Build robust aggregation logic that maintains data integrity across organizational levels
4. **Visualization Integration** - Integrate interactive charts and maps using existing Plotly capabilities
5. **Multi-Format Export** - Support Excel, PDF, HTML, JSON, and interactive dashboard outputs

## Out of Scope

- Real-time data integration (uses existing binary data files)
- Custom report designer GUI (uses predefined templates)
- Automated report scheduling (manual execution only)
- External data source integration beyond existing BSEE modules
- Advanced statistical modeling or forecasting (basic metrics only)

## Expected Deliverable

1. CLI command `python -m worldenergydata.bsee report` with comprehensive options for report type, organizational level, and output format
2. Standardized report templates covering 5+ business use cases with consistent formatting and metrics
3. Multi-format export capability generating Excel workbooks, PDF documents, and interactive HTML dashboards
4. Performance capable of processing block-level reports (1000+ wells) in under 10 minutes with comprehensive visualizations

## Data Flow Architecture

```mermaid
flowchart TD
    subgraph "Data Collection"
        A1[Binary WAR Files]
        A2[OGORA Production]
        A3[Well Headers]
        A4[Directional Surveys]
    end
    
    subgraph "Data Processing"
        B1[Data Parser]
        B2[Data Validator]
        B3[Data Normalizer]
        B4[Hierarchy Builder]
    end
    
    subgraph "Aggregation Engine"
        C1[Well Aggregator]
        C2[Lease Aggregator]
        C3[Field Aggregator]
        C4[Block Aggregator]
    end
    
    subgraph "Report Generation"
        D1[Template Selector]
        D2[Context Builder]
        D3[Variable Injector]
        D4[Format Renderer]
    end
    
    subgraph "Output Delivery"
        E1[Excel Generator]
        E2[PDF Creator]
        E3[HTML Builder]
        E4[JSON Exporter]
    end
    
    A1 --> B1
    A2 --> B1
    A3 --> B1
    A4 --> B1
    
    B1 --> B2
    B2 --> B3
    B3 --> B4
    
    B4 --> C1
    C1 --> C2
    C2 --> C3
    C3 --> C4
    
    C4 --> D1
    D1 --> D2
    D2 --> D3
    D3 --> D4
    
    D4 --> E1
    D4 --> E2
    D4 --> E3
    D4 --> E4
    
    style A1 fill:#e1f5fe
    style C4 fill:#c8e6c9
    style E1 fill:#fff9c4
```

## Report Template Architecture

```mermaid
classDiagram
    class BaseReportTemplate {
        +name: str
        +version: str
        +sections: List
        +render(data: Dict)
        +validate(data: Dict)
    }
    
    class ComplianceTemplate {
        +regulatory_sections: List
        +compliance_metrics: Dict
        +generate_compliance_summary()
    }
    
    class EconomicTemplate {
        +financial_sections: List
        +npv_calculations: Dict
        +generate_economic_analysis()
    }
    
    class OperationalTemplate {
        +operational_sections: List
        +performance_metrics: Dict
        +generate_operational_report()
    }
    
    class ExecutiveTemplate {
        +summary_sections: List
        +key_indicators: Dict
        +generate_executive_summary()
    }
    
    class TechnicalTemplate {
        +technical_sections: List
        +well_details: Dict
        +generate_technical_report()
    }
    
    BaseReportTemplate <|-- ComplianceTemplate
    BaseReportTemplate <|-- EconomicTemplate
    BaseReportTemplate <|-- OperationalTemplate
    BaseReportTemplate <|-- ExecutiveTemplate
    BaseReportTemplate <|-- TechnicalTemplate
```

## Aggregation Hierarchy

```mermaid
graph BT
    subgraph "Well Level"
        W1[Well 001]
        W2[Well 002]
        W3[Well 003]
        W4[Well 004]
        W5[Well 005]
        W6[Well 006]
    end
    
    subgraph "Lease Level"
        L1[Lease G12345]
        L2[Lease G12346]
        L3[Lease G12347]
    end
    
    subgraph "Field Level"
        F1[Field Alpha]
        F2[Field Beta]
    end
    
    subgraph "Block Level"
        B1[Block 525]
    end
    
    W1 --> L1
    W2 --> L1
    W3 --> L2
    W4 --> L2
    W5 --> L3
    W6 --> L3
    
    L1 --> F1
    L2 --> F1
    L3 --> F2
    
    F1 --> B1
    F2 --> B1
    
    style B1 fill:#ffeb3b
    style F1 fill:#8bc34a
    style F2 fill:#8bc34a
    style L1 fill:#03a9f4
    style L2 fill:#03a9f4
    style L3 fill:#03a9f4
```

## Spec Documentation

### Primary Documents
- Prompt Evolution: @specs/modules/bsee/comprehensive-report-system/prompt.md
- Task Summary: @specs/modules/bsee/comprehensive-report-system/task_summary.md
- Tasks: @specs/modules/bsee/comprehensive-report-system/tasks.md
- Technical Specification: @specs/modules/bsee/comprehensive-report-system/sub-specs/technical-spec.md

### Sub-Specifications  
- Report Templates: @specs/modules/bsee/comprehensive-report-system/sub-specs/templates-spec.md
- Tests Specification: @specs/modules/bsee/comprehensive-report-system/sub-specs/tests.md
- Go-By References: @specs/modules/bsee/comprehensive-report-system/sub-specs/go_by/

### Related Specifications
- Existing BSEE Analysis: @src/worldenergydata/modules/bsee/analysis/
- Current Lease Reporting: @src/worldenergydata/modules/bsee/analysis/custom_scripts/Roy/may/build_lease_report_final.py
- Block Data Processing: @src/worldenergydata/modules/bsee/data/_from_bin/block_data.py

### External Resources
- BSEE Data Center: https://www.data.bsee.gov/
- Plotly Documentation: https://plotly.com/python/
- AssetUtilities Visualization: @assetutilities:common/visualization/