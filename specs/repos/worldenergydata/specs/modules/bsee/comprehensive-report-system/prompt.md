# Prompt Evolution Document

> Spec: Comprehensive Report System
> Created: 2025-08-06
> Module: BSEE

## Initial Prompt

**Date:** 2025-08-06  
**User:** Initial spec creation request

```
Comprehensive Well and production report (by block, field, lease). Should be able to:
- Technical data is given here
  - .agent-os\specs\modules\bsee\2025-08-06-comprehensive-reports\sub-specs\go_by
```

## Prompt Evolution

### Update 1: Enhanced Spec Format
**Date:** 2025-08-22  
**User:** Mature the spec with enhanced modular system

```
mature the spec 'specs\modules\bsee\comprehensive-reports' with enhanced spec modular system. 
refere latest spec 'specs\modules\bsee\financial-analysis-sme-code' if you actually needed
```

## Prompt Analysis

### Key Requirements Extracted
1. **Multi-Level Reporting**: Generate reports at block, field, and lease levels
2. **Well Data Integration**: Include comprehensive well technical data
3. **Production Analytics**: Aggregate and analyze production metrics
4. **Reference Data**: Use provided technical data samples as go-by
5. **Enhanced Spec Format**: Follow the enhanced modular spec system

### Scope Definition
- **Block Level**: Geographical area reporting with field aggregation
- **Field Level**: Field-specific reporting with lease aggregation  
- **Lease Level**: Individual lease reporting with well-level details
- **Data Sources**: BSEE well and production data repositories

### Technical Context
- **Domain**: BSEE offshore oil and gas data
- **Hierarchy**: Block > Field > Lease > Well
- **Key Metrics**: Production volumes, well counts, operational status
- **Output Formats**: Excel, PDF, HTML reports

## Decisions Made

1. **Template System**: Implement Jinja2-based template engine for flexible report generation
2. **Aggregation Strategy**: Bottom-up aggregation from well to lease to field to block
3. **Export Formats**: Support Excel (primary), PDF, HTML, and JSON
4. **Visualization**: Include Plotly charts for production trends and comparisons
5. **Performance**: Implement caching for frequently accessed aggregations

## Success Metrics

- Generate reports for 100+ leases in <60 seconds
- Support all three organizational levels seamlessly
- Achieve >95% data consistency across aggregation levels
- Provide 5+ standard report templates
- Export to at least 3 different formats

## Notes

- The go-by folder contains sample Excel reports showing expected format
- Reports should match industry-standard presentation formats
- Integration with existing BSEE analysis modules is critical
- Performance optimization needed for large dataset processing
- Consider future expansion to include economic indicators

## Questions for Clarification

1. Should reports include historical trend analysis or just current snapshots?
2. Are there specific regulatory compliance sections required?
3. Do we need role-based access control for different report sections?
4. Should the system support scheduled/automated report generation?
5. What is the expected report update frequency (daily, monthly, quarterly)?

## Learning Opportunities

This implementation will enhance agent knowledge in:
- Hierarchical data aggregation patterns
- Report template systems and generation
- Multi-format export capabilities
- Performance optimization for large datasets
- Industry-standard report formatting

## Session Log

### 2025-08-06 - Initial Spec Creation
- Created comprehensive spec with enhanced format
- Defined three-level reporting hierarchy
- Established template-based architecture
- Designed aggregation framework

### 2025-08-22 - Spec Enhancement
- Added prompt.md for prompt evolution tracking
- Created task_summary.md for progress tracking
- Enhanced spec.md with executive summary and diagrams
- Updated tasks.md with detailed time estimates
- Added mermaid diagrams for system architecture
- Aligned with enhanced modular spec system