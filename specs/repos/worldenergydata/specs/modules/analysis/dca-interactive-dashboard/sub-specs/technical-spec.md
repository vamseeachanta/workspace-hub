# Technical Specification

This is the technical specification for the spec detailed in @specs/modules/analysis/dca-interactive-dashboard/spec.md

> Created: 2025-08-14
> Version: 1.0.0

## Technical Requirements

### Core Functionality
- **Arps Decline Equation Implementation**
  - Hyperbolic form: q(t) = qi / (1 + b * Di * t)^(1/b) for b ≠ 0
  - Exponential form: q(t) = qi * exp(-Di * t) for b = 0
  - Handle edge cases and numerical stability
  - Time units in years, rate units in Mcf/day or similar

- **Interactive Web Interface**
  - Single-page application using Plotly Dash
  - Dark theme with plotly_dark template
  - Responsive layout adapting to screen size
  - Real-time updates without page refresh

- **Data Input and Processing**
  - CSV file upload component using dcc.Upload
  - Two-column format: Date and Gas Rate
  - Sample data generation for demonstration
  - Date parsing with pandas.to_datetime
  - Handle missing values and data gaps

- **Parameter Controls**
  - Slider for qi (initial production rate): 0-10000 Mcf/day
  - Slider for Di (initial decline rate): 0-2 /year  
  - Slider for b (hyperbolic exponent): 0-2
  - Slider for forecast period: 1-20 years
  - Numeric display of current values

- **Regression Capabilities**
  - Nonlinear least squares using scipy.optimize.curve_fit
  - Bounds constraints on parameters
  - Error handling for convergence failures
  - Update sliders with fitted values

- **Visualization Requirements**
  - Time series plot with plotly.graph_objects
  - Historical data as scatter points
  - Fitted curve as continuous line
  - Forecast extension in different color/style
  - Legend distinguishing data types
  - Axis labels with units

- **Calculations and Output**
  - Cumulative production using numerical integration
  - Display total cumulative in text format
  - Update calculations on parameter change
  - Format numbers with appropriate precision

## Approach Options

**Option A: Multi-file Architecture**
- Pros: Separation of concerns, easier testing, modular design
- Cons: More complex setup, multiple files to manage, harder to share

**Option B: Single-file Application** (Selected)
- Pros: Easy to run and share, self-contained, quick deployment
- Cons: Less modular, harder to test individual components

**Rationale:** Single-file approach selected for rapid deployment and ease of use, aligning with the "13 seconds to create" philosophy and individual user focus.

## Implementation Architecture

### Application Structure
```python
# Main application structure
app = dash.Dash(__name__)

# Layout components
- Header with title
- Upload component
- Parameter sliders panel  
- Graph display area
- Regression button
- Cumulative production display

# Callbacks
- @app.callback for file upload
- @app.callback for parameter updates
- @app.callback for regression fitting
- @app.callback for plot updates
```

### Data Flow
1. User uploads CSV or uses sample data
2. Data parsed into pandas DataFrame
3. Parameters adjusted via sliders
4. Arps equation calculates decline curve
5. Plot updates with historical + forecast
6. Cumulative production calculated and displayed
7. Optional: Regression fits parameters to data

### Mathematical Implementation
```python
def arps_equation(t, qi, Di, b):
    """Calculate production rate using Arps equation"""
    if b == 0:
        return qi * np.exp(-Di * t)
    else:
        return qi / (1 + b * Di * t) ** (1/b)

def cumulative_production(time_array, rate_array):
    """Calculate cumulative production using trapezoidal rule"""
    return np.trapz(rate_array, time_array)
```

## External Dependencies

### Required Packages
- **dash** (>=2.0.0) - Web application framework
  - Justification: Core framework for interactive web apps
- **plotly** (>=5.0.0) - Interactive plotting library
  - Justification: Required for dash graphs and visualizations
- **pandas** (>=1.3.0) - Data manipulation
  - Justification: CSV reading and time series handling
- **numpy** (>=1.21.0) - Numerical computations
  - Justification: Array operations and mathematical functions
- **scipy** (>=1.7.0) - Scientific computing
  - Justification: Nonlinear regression with curve_fit

### Development Dependencies
- **dash-bootstrap-components** (optional) - Enhanced UI components
  - Justification: Better styling and responsive layouts if needed

## Performance Considerations

- **Real-time Updates**: Callbacks should execute in <100ms for smooth interaction
- **Data Limits**: Handle up to 10,000 data points efficiently
- **Memory Usage**: Keep data in memory, no database required
- **Browser Compatibility**: Support modern browsers (Chrome, Firefox, Safari, Edge)

## Security Considerations

- **Input Validation**: Validate CSV format and data types
- **Parameter Bounds**: Enforce reasonable limits on all parameters
- **Error Handling**: Graceful degradation for invalid inputs
- **Local Execution**: No network requests or external data access

## User Interface Design

### Layout Structure
```
+------------------------------------------+
|          DCA Interactive Dashboard       |
+------------------------------------------+
| [Upload CSV] or [Use Sample Data]        |
+------------------------------------------+
| Parameters:                              |
| qi: [====slider====] 1000 Mcf/day       |
| Di: [====slider====] 0.5 /year          |
| b:  [====slider====] 0.8                |
| Forecast: [==slider==] 5 years          |
| [Run Regression]                         |
+------------------------------------------+
|                                          |
|         [Interactive Plot Area]          |
|                                          |
+------------------------------------------+
| Cumulative Production: 1,234,567 Mcf    |
+------------------------------------------+
```

### Theme and Styling
- Dark background (#111111)
- Plotly dark theme for graphs
- High contrast for readability
- Consistent color scheme
- Professional appearance

## Testing Strategy

- **Unit Tests**: Test Arps equation and cumulative calculations
- **Integration Tests**: Test data upload and processing pipeline
- **UI Tests**: Manual testing of slider interactions
- **Regression Tests**: Verify fitting algorithm convergence
- **Edge Cases**: Zero values, missing data, extreme parameters