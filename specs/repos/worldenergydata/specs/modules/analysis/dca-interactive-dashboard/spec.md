# Spec Requirements Document

> Spec: Interactive Decline Curve Analysis Dashboard  
> Created: 2025-08-14
> Status: Planning

## Overview

Implement an interactive web-based dashboard for decline curve analysis (DCA) using the Arps equation, enabling energy professionals to analyze gas production decline curves with real-time parameter adjustment, regression fitting, and production forecasting capabilities. This feature addresses the need for quick, accessible production analysis tools that can be deployed in seconds rather than requiring expensive enterprise software.

### Future Update Prompt

For future modifications to this spec, use the following prompt:
```
Update the DCA interactive dashboard spec to include:
- Additional decline models (modified hyperbolic, stretched exponential)
- Multi-well analysis capabilities
- Economic analysis integration
- Export functionality for reports
- API endpoints for programmatic access
Maintain compatibility with existing Arps equation implementation and preserve the interactive real-time adjustment features.
```

## User Stories

### Production Engineer Analysis Workflow

As a **Production Engineer**, I want to quickly analyze gas well production decline curves, so that I can forecast future production and make informed decisions about well management.

The engineer uploads production data from a CSV file containing date and gas rate columns. They use the interactive sliders to adjust the Arps equation parameters (qi, Di, b) while watching the fitted curve update in real-time on the plot. When satisfied with the visual fit, they can also click the regression button to automatically optimize the parameters. The forecast extends into the future based on their selected time horizon, and cumulative production is calculated instantly, providing key metrics for economic evaluation and reserve estimation.

### Data Analyst Research Workflow  

As an **Energy Data Analyst**, I want to perform reproducible decline curve analysis with parameter sensitivity testing, so that I can understand production behavior and uncertainty ranges.

The analyst loads historical production data and uses the regression feature to establish baseline parameters. They then manually adjust individual parameters using the sliders to understand sensitivity and create different production scenarios. The dark-themed interface reduces eye strain during extended analysis sessions, and the responsive layout works on both desktop and laptop screens for field office use.

### Consultant Rapid Assessment

As an **Energy Consultant**, I want to perform quick DCA assessments during client meetings, so that I can provide immediate insights without switching to complex software.

The consultant can launch the app in seconds and either use sample data or quickly paste client data. The intuitive interface allows them to demonstrate different decline scenarios to clients in real-time, showing how parameter changes affect long-term production forecasts and cumulative volumes.

## Spec Scope

1. **Dash Web Application Framework** - Interactive web app using Plotly Dash with dark theme and responsive layout
2. **Arps Equation Implementation** - Full hyperbolic and exponential decline curve models with proper mathematical handling
3. **Interactive Parameter Controls** - Real-time sliders for qi (initial rate), Di (decline rate), and b (hyperbolic exponent)
4. **Nonlinear Regression Fitting** - Automated parameter optimization using scipy.optimize with button trigger
5. **Production Forecasting** - Configurable forecast period with cumulative production calculations
6. **Data Input System** - CSV file upload and sample data generation for testing

## Out of Scope

- Database integration or data persistence
- User authentication and multi-user support
- Advanced decline models beyond Arps equation
- Economic analysis or NPV calculations
- API endpoints or programmatic access
- Export functionality for reports or charts
- Multi-well batch analysis
- Production data quality checks or outlier detection

## Expected Deliverable

1. **Standalone Python application** - Single Python file that runs locally with `python dca_app.py` command
2. **Interactive parameter adjustment** - Moving sliders immediately updates the decline curve on the plot
3. **Automated regression fitting** - Clicking "Run Regression" button fits parameters to historical data
4. **Visual production forecast** - Historical and forecast data displayed on the same plot with clear distinction
5. **Cumulative production display** - Text output showing total cumulative production value

## Spec Documentation

- Tasks: @specs/modules/analysis/dca-interactive-dashboard/tasks.md
- Technical Specification: @specs/modules/analysis/dca-interactive-dashboard/sub-specs/technical-spec.md
- Tests Specification: @specs/modules/analysis/dca-interactive-dashboard/sub-specs/tests.md

## Success Story Context

This spec is inspired by a real-world success story where a complete interactive DCA web app was created in just 13 seconds using AI assistance. The resulting "toy" application, while not replacing enterprise software, demonstrates the power of rapid prototyping for individual users who need quick analysis tools. Key achievements include:

- ✅ Load your production data
- ✅ Adjust parameters with sliders  
- ✅ Run regression with one click
- ✅ Forecast into the future
- ✅ Instant cumulative calculations

The philosophy: "Don't miss the forest for the trees... at the individual user level, these 'toys' are amazing."