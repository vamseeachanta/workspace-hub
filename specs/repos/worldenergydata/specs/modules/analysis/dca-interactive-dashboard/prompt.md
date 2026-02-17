# Prompt Documentation

## Original User Prompt

> Date: 2025-08-14
> Context: Energy data analysis dashboard requirements

"Create an interactive decline curve analysis dashboard that implements the Arps equation for gas production analysis. The dashboard should have real-time parameter adjustment using sliders for qi, Di, and b parameters, with immediate visual updates. Include regression fitting capability and production forecasting. Use Plotly Dash with a dark theme. This should be deployable as a standalone Python application that can be run locally."

## Refined Prompt for Reuse

To recreate or extend this spec, use the following comprehensive prompt:

```
Create a complete interactive decline curve analysis (DCA) dashboard specification for the worldenergydata repository:

CORE REQUIREMENTS:
1. Implement Arps equation for hyperbolic and exponential decline curves
2. Interactive web interface using Plotly Dash with dark theme
3. Real-time parameter adjustment with sliders (qi, Di, b)
4. Automated regression fitting using scipy.optimize
5. Production forecasting with configurable time horizons
6. CSV file upload and sample data generation
7. Cumulative production calculations

TECHNICAL DETAILS:
- Single-file Python application (dca_dashboard.py)
- Located in src/worldenergydata/dashboards/
- Dependencies: dash, plotly, scipy, pandas, numpy
- Performance: &lt;100ms response time for slider updates
- Forecast accuracy: Within 5% of manual calculations

USER PERSONAS:
- Production Engineers: Quick well analysis and forecasting
- Data Analysts: Parameter sensitivity testing
- Consultants: Real-time demonstration during meetings

QUALITY REQUIREMENTS:
- Launch time &lt;3 seconds
- Responsive design for desktop and laptop
- Intuitive interface for non-technical users
- Error handling for data issues and non-convergence

SUCCESS METRICS:
- Complete implementation in under 1 hour
- Works with standard BSEE production data formats
- Matches results from commercial DCA software
```

## Context and Background

### Problem Statement
Energy professionals need quick access to decline curve analysis tools without relying on expensive enterprise software. Current solutions require complex installations, licenses, and training.

### Solution Approach
Create a lightweight, interactive web dashboard that can be deployed instantly on any machine with Python. Focus on core DCA functionality with real-time interactivity.

### Inspiration
Based on a real-world success story where a complete DCA app was created in 13 seconds using AI assistance, demonstrating the power of rapid prototyping for individual users.

## Key Technical Decisions

1. **Framework Choice**: Plotly Dash chosen for rapid development and built-in interactivity
2. **Single-File Design**: Simplifies deployment and reduces complexity
3. **Dark Theme**: Reduces eye strain during extended analysis sessions
4. **Real-Time Updates**: Prioritizes responsiveness over feature complexity
5. **Local Deployment**: Avoids cloud infrastructure requirements

## Evolution Points

For future enhancements, consider:
- Multi-well batch analysis
- Additional decline models (Duong, stretched exponential)
- Economic analysis integration (NPV, IRR)
- Export functionality (PDF reports, Excel)
- API endpoints for programmatic access
- Production data quality checks
- Uncertainty quantification
- Database persistence

## Related Specifications

- **decline-curve-analysis**: Core DCA engine implementation
- **production-api12-analysis**: BSEE data integration
- **well-production-dashboard**: Comprehensive production analytics

## Implementation Notes

### Critical Success Factors
1. **Speed**: Application must be usable within seconds of launch
2. **Simplicity**: Interface must be intuitive without training
3. **Accuracy**: Results must match commercial software
4. **Reliability**: Must handle edge cases gracefully

### Common Pitfalls to Avoid
- Over-engineering the solution
- Adding unnecessary features
- Complex installation requirements
- Poor error messages
- Slow response times

## Prompt Engineering Tips

When extending this spec:
1. Be specific about mathematical models needed
2. Define exact UI components and layout
3. Specify performance requirements clearly
4. Include sample data formats
5. Describe user workflows in detail
6. List explicit success criteria

## Curated Reuse Prompt

```
/create-spec "dca-interactive-dashboard-v2" analysis enhanced

Extend the existing DCA dashboard with:
- Modified hyperbolic decline model
- Stretched exponential decline model
- Multi-well comparison view
- P10/P50/P90 probabilistic forecasts
- Export to PDF/Excel reports
- RESTful API endpoints
- User session management
- Production data validation
- Automated outlier detection
- Economic limit calculations

Maintain backward compatibility with existing Arps implementation.
Use existing UI components and dark theme.
Target 200ms max response time for all operations.
```