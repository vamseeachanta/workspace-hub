# Prompt Evolution Document

> Spec: Well Production Dashboard
> Created: 2025-01-13
> Module: Analysis

## Initial Prompt

**Date:** 2025-01-13  
**User:** Initial spec creation request

```
Create an interactive web-based dashboard for visualizing and analyzing well production data, economic metrics, and operational performance with real-time updates and comprehensive reporting capabilities.
```

## Prompt Evolution

### Context: Dashboard Requirements
**Date:** 2025-01-13  
**Analysis:** Interactive visualization system design

The user requires a comprehensive dashboard focused on:
1. **Interactive Visualizations**: Real-time, responsive charts and graphs
2. **Economic Metrics**: NPV, revenue, OPEX calculations and display
3. **Operational Performance**: Production trends and KPIs
4. **Reporting Capabilities**: Export and sharing functionality

## Prompt Analysis

### Key Requirements Extracted
1. **Web-Based Interface**: Browser-accessible dashboard
2. **Interactive Components**: User-driven data exploration
3. **Real-Time Updates**: Live data refresh capabilities
4. **Economic Analysis**: Financial metrics and calculations
5. **Reporting Features**: Export to PDF/Excel formats

### Technical Scope
- **Framework**: Plotly/Dash for interactive visualizations
- **Backend**: Python-based API with FastAPI/Flask
- **Data Processing**: Pandas for aggregations
- **Authentication**: Role-based access control
- **Export**: PDF and Excel generation

### User Personas Identified
1. **Energy Professional**: Needs production trends and economics
2. **Field Manager**: Requires multi-well comparisons
3. **Executive**: Wants high-level summaries and KPIs

## Decisions Made

1. **Technology Stack**: Plotly/Dash for proven Python integration
2. **Component Architecture**: Reusable visualization components
3. **Caching Strategy**: Redis/memory cache for performance
4. **API Design**: RESTful endpoints for data access
5. **Responsive Design**: Mobile-friendly layouts

## Success Metrics

- Dashboard loads in <3 seconds
- Charts refresh in <500ms
- Support 50+ concurrent users
- Handle 1M+ data points efficiently
- 100% browser compatibility (Chrome, Firefox, Safari, Edge)
- Zero critical bugs in production

## Implementation Strategy

### Phase 1: Core Dashboard
- Basic layout and navigation
- Essential production charts
- Simple data connections

### Phase 2: Interactive Features
- Advanced filtering and drill-down
- Comparative analysis tools
- Real-time data updates

### Phase 3: Advanced Analytics
- Economic calculations
- Trend analysis
- Predictive visualizations

### Phase 4: Export & Integration
- PDF/Excel export
- API endpoints
- External system integration

## Technical Considerations

1. **Performance**: Optimize for large datasets
2. **Scalability**: Handle growing user base
3. **Usability**: Intuitive interface design
4. **Security**: Secure authentication and data access
5. **Maintainability**: Clean, modular codebase

## Visual Design Principles

1. **Clarity**: Clear, uncluttered visualizations
2. **Consistency**: Uniform color schemes and layouts
3. **Accessibility**: WCAG compliance for all users
4. **Responsiveness**: Adapt to different screen sizes
5. **Interactivity**: Intuitive user interactions

## Notes

- Dashboard is critical for operational decision-making
- Must integrate seamlessly with verification system
- Performance crucial for user adoption
- Real-time capabilities differentiate from static reports
- Consider future mobile app potential

## Curated Prompt for Reuse

```
Create a comprehensive web-based production dashboard with the following capabilities:

1. **Dashboard Infrastructure**: Build a Plotly/Dash application with responsive design, authentication, and role-based access control

2. **Well Detail Views**: Implement individual well pages showing:
   - Production time series charts
   - Economic metrics (NPV, revenue, OPEX)
   - Operational KPIs
   - Historical comparisons

3. **Field Aggregation Module**: Create field-level views with:
   - Multi-well comparison charts
   - Aggregated production metrics
   - Performance ranking tables
   - Trend identification tools

4. **Interactive Visualizations**: Develop components for:
   - Configurable chart types
   - Dynamic filtering and drill-down
   - Time range selection
   - Data export options

5. **Export Module**: Enable:
   - PDF report generation
   - Excel data export
   - Chart image downloads
   - Scheduled report delivery

Technical Requirements:
- Initial load time <3 seconds
- Support 50+ concurrent users
- Handle 1M+ data points
- API response time <200ms
- Mobile-responsive design

The dashboard should serve three user types:
- Energy Professionals needing detailed analysis
- Field Managers requiring comparative views
- Executives wanting high-level summaries
```