# Prompt Evolution Document

> Spec: Well Data Verification System
> Created: 2025-01-13
> Module: Analysis

## Initial Prompt

**Date:** 2025-01-13  
**User:** Initial spec creation request

```
Implement a comprehensive well data verification system that provides systematic workflows for validating production data accuracy, ensuring data quality, and identifying anomalies before analysis and reporting.
```

## Prompt Evolution

### Context: Verification System Requirements
**Date:** 2025-01-13  
**Analysis:** System design for data quality assurance

The user requires a comprehensive verification system focused on:
1. **Manual Workflows**: Guided validation processes for analysts
2. **Automated Checks**: Quality monitoring and anomaly detection
3. **Audit Trails**: Complete tracking for compliance

## Prompt Analysis

### Key Requirements Extracted
1. **Verification Workflows**: Step-by-step validation processes
2. **Data Quality Framework**: Automated validation and monitoring
3. **Anomaly Detection**: Identification of outliers and issues
4. **Audit System**: Complete activity tracking and compliance
5. **Reporting**: Comprehensive verification documentation

### Technical Scope
- **Domain**: Well production data verification
- **Focus**: Data quality and accuracy
- **Integration**: BSEE data sources and Excel benchmarks
- **Output**: PDF and Excel verification reports

### User Personas Identified
1. **Data Analyst**: Needs manual verification workflows
2. **QA Engineer**: Requires automated monitoring
3. **Compliance Officer**: Needs audit trails

## Decisions Made

1. **Modular Architecture**: Separate engines for workflow, validation, and reporting
2. **Configuration-Driven**: YAML-based validation rules for flexibility
3. **Progressive Validation**: Multi-stage checks for comprehensive coverage
4. **Immutable Audit Logs**: Ensure compliance and traceability
5. **Excel Integration**: Cross-reference capabilities with existing benchmarks

## Success Metrics

- Process 1000+ wells in under 30 seconds
- Zero false negatives in critical validation rules
- 100% audit trail coverage for all verification activities
- Sub-second validation rule evaluation
- Comprehensive reports generated within 2 minutes

## Implementation Strategy

### Phase 1: Core Infrastructure
- Validation engine framework
- Rule processing system
- Basic workflow implementation

### Phase 2: Advanced Features
- Anomaly detection algorithms
- Excel benchmark integration
- Automated quality monitoring

### Phase 3: Reporting & Compliance
- Report generation system
- Audit trail implementation
- Compliance documentation

## Technical Considerations

1. **Performance**: Optimize for large dataset processing
2. **Scalability**: Support concurrent validation sessions
3. **Extensibility**: Easy addition of new validation rules
4. **Integration**: Seamless connection with existing modules
5. **Usability**: Intuitive workflow guidance for users

## Notes

- Verification system is foundational for data quality assurance
- Must integrate with existing BSEE data processing pipelines
- Audit trails critical for regulatory compliance
- Performance crucial for large-scale data validation
- Flexibility needed for evolving validation requirements

## Curated Prompt for Reuse

```
Create a comprehensive well data verification system with the following capabilities:

1. **Verification Workflows**: Implement guided, step-by-step validation processes that walk users through data verification checkpoints with clear documentation

2. **Data Quality Framework**: Build automated validation rules, outlier detection, and completeness checks using YAML-based configurable rules

3. **Cross-Reference Module**: Enable comparison with Excel benchmarks and generate discrepancy reports

4. **Audit System**: Implement complete activity tracking with timestamped logs, user tracking, and change history for compliance

5. **Report Generation**: Create comprehensive verification reports in both PDF and Excel formats with detailed findings

Technical Requirements:
- Process 1000+ wells in under 30 seconds
- Support concurrent validation sessions
- Real-time anomaly detection
- Immutable audit trails
- Integration with BSEE data sources

The system should serve three primary user types:
- Data Analysts needing manual verification workflows
- QA Engineers requiring automated monitoring
- Compliance Officers needing complete audit trails
```