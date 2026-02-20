---
name: economic-sensitivity-analyzer
version: "1.0.0"
category: data
description: "Perform advanced economic sensitivity analysis for oil & gas investments including spider diagrams, 2D surfaces, breakeven analysis, and decision tree analysis."
command: /economic-sensitivity-analyzer
author: worldenergydata
tags:
  - economics
  - sensitivity
  - analysis
  - visualization
  - decision-support
---

# Economic Sensitivity Analyzer Skill

## Overview

The Economic Sensitivity Analyzer provides advanced visualization and analysis tools for understanding how economic parameters affect project NPV. While the npv-analyzer provides basic sensitivity analysis, this skill focuses on multi-dimensional sensitivity visualization, breakeven analysis, and decision support tools.

## When to Use

Use this skill when you need to:
- Create spider diagrams showing multi-parameter sensitivity
- Generate 2D sensitivity surfaces (contour plots) for two-variable interactions
- Calculate and visualize breakeven prices (oil, gas, or combined)
- Build scenario comparison matrices for management presentations
- Perform decision tree analysis for staged investments
- Create executive-ready sensitivity dashboards

## Core Classes

### SensitivityParameter

```python
# ABOUTME: Defines a parameter for sensitivity analysis with range and display settings
# ABOUTME: Supports linear and percentage-based parameter variations

from dataclasses import dataclass, field
from typing import List, Optional, Callable
from enum import Enum
import numpy as np


class ParameterType(Enum):
    """Type of parameter variation."""
    ABSOLUTE = "absolute"  # Vary by absolute values (e.g., $50, $60, $70)
    PERCENTAGE = "percentage"  # Vary by percentage (-30%, -20%, ..., +30%)
    MULTIPLIER = "multiplier"  # Vary by multiplier (0.7, 0.8, ..., 1.3)


@dataclass
class SensitivityParameter:
    """
    Configuration for a sensitivity analysis parameter.

    Attributes:
        name: Parameter identifier (e.g., "oil_price", "capex")
        display_name: Human-readable name for charts
        base_value: Base case value
        param_type: How to vary the parameter
        variations: List of variation points
        unit: Display unit (e.g., "$/bbl", "MM$")
        color: Chart color for this parameter
    """
    name: str
    display_name: str
    base_value: float
    param_type: ParameterType = ParameterType.PERCENTAGE
    variations: List[float] = field(default_factory=lambda: [-30, -20, -10, 0, 10, 20, 30])
    unit: str = ""
    color: str = "#1f77b4"

    def get_values(self) -> List[float]:
        """Generate actual parameter values from variations."""
        if self.param_type == ParameterType.ABSOLUTE:
            return self.variations
        elif self.param_type == ParameterType.PERCENTAGE:
            return [self.base_value * (1 + v/100) for v in self.variations]
        elif self.param_type == ParameterType.MULTIPLIER:
            return [self.base_value * v for v in self.variations]
        return self.variations

    def get_labels(self) -> List[str]:
        """Generate display labels for chart axes."""
        if self.param_type == ParameterType.PERCENTAGE:
            return [f"{v:+.0f}%" for v in self.variations]
        elif self.param_type == ParameterType.MULTIPLIER:
            return [f"{v:.1f}x" for v in self.variations]
        else:
            return [f"{v:.1f}" for v in self.variations]
```

### SpiderDiagramAnalyzer

```python
# ABOUTME: Creates spider (radar) diagrams showing multi-parameter sensitivity
# ABOUTME: Normalizes NPV changes to percentage basis for fair comparison

from dataclasses import dataclass
from typing import Dict, List, Tuple, Optional, Callable
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots


@dataclass
class SpiderResult:
    """Results from spider diagram analysis."""
    parameters: List[str]
    variations: List[float]  # Common variation percentages
    npv_changes: Dict[str, List[float]]  # param_name -> [npv_pct_change, ...]
    base_npv: float
    most_sensitive: str
    least_sensitive: str


class SpiderDiagramAnalyzer:
    """
    Generates spider (radar) diagrams for multi-parameter sensitivity analysis.

    Spider diagrams show how NPV changes when each parameter is varied
    by the same percentage, allowing direct comparison of parameter sensitivity.

    Usage:
        analyzer = SpiderDiagramAnalyzer(npv_calculator)
        result = analyzer.analyze(parameters)
        fig = analyzer.create_spider_chart(result)
    """

    def __init__(self, npv_calculator: Callable[[Dict[str, float]], float]):
        """
        Initialize analyzer with NPV calculation function.

        Args:
            npv_calculator: Function that takes parameter dict and returns NPV
        """
        self.npv_calculator = npv_calculator

    def analyze(
        self,
        parameters: List[SensitivityParameter],
        variations: List[float] = None
    ) -> SpiderResult:
        """
        Perform spider diagram sensitivity analysis.

        Args:
            parameters: List of parameters to analyze
            variations: Percentage variations to test (default: -30 to +30)

        Returns:
            SpiderResult with NPV changes for each parameter
        """
        if variations is None:
            variations = [-30, -20, -10, 0, 10, 20, 30]

        # Calculate base case NPV
        base_params = {p.name: p.base_value for p in parameters}
        base_npv = self.npv_calculator(base_params)

        # Calculate NPV for each parameter variation
        npv_changes = {}
        max_sensitivity = 0
        min_sensitivity = float('inf')
        most_sensitive = ""
        least_sensitive = ""

        for param in parameters:
            changes = []
            for var_pct in variations:
                # Vary only this parameter
                test_params = base_params.copy()
                test_params[param.name] = param.base_value * (1 + var_pct / 100)

                # Calculate NPV and percentage change from base
                test_npv = self.npv_calculator(test_params)
                pct_change = ((test_npv - base_npv) / abs(base_npv)) * 100 if base_npv != 0 else 0
                changes.append(pct_change)

            npv_changes[param.name] = changes

            # Track most/least sensitive (use range of NPV changes)
            sensitivity = max(changes) - min(changes)
            if sensitivity > max_sensitivity:
                max_sensitivity = sensitivity
                most_sensitive = param.name
            if sensitivity < min_sensitivity:
                min_sensitivity = sensitivity
                least_sensitive = param.name

        return SpiderResult(
            parameters=[p.name for p in parameters],
            variations=variations,
            npv_changes=npv_changes,
            base_npv=base_npv,
            most_sensitive=most_sensitive,
            least_sensitive=least_sensitive
        )

    def create_spider_chart(
        self,
        result: SpiderResult,
        title: str = "NPV Sensitivity Spider Diagram",
        show_legend: bool = True
    ) -> go.Figure:
        """
        Create interactive spider/radar chart.

        Args:
            result: SpiderResult from analyze()
            title: Chart title
            show_legend: Whether to show parameter legend

        Returns:
            Plotly Figure object
        """
        fig = go.Figure()

        # Color palette for parameters
        colors = [
            '#1f77b4', '#ff7f0e', '#2ca02c', '#d62728',
            '#9467bd', '#8c564b', '#e377c2', '#7f7f7f'
        ]

        for i, param in enumerate(result.parameters):
            changes = result.npv_changes[param]

            # Close the spider by repeating first point
            r_values = changes + [changes[0]]
            theta_values = [f"{v:+.0f}%" for v in result.variations] + [f"{result.variations[0]:+.0f}%"]

            fig.add_trace(go.Scatterpolar(
                r=r_values,
                theta=theta_values,
                fill='toself',
                fillcolor=f'rgba{tuple(list(int(colors[i % len(colors)].lstrip("#")[j:j+2], 16) for j in (0, 2, 4)) + [0.1])}',
                line=dict(color=colors[i % len(colors)], width=2),
                name=param.replace("_", " ").title()
            ))

        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    title="NPV Change (%)",
                    ticksuffix="%"
                ),
                angularaxis=dict(
                    direction="clockwise",
                    rotation=90
                )
            ),
            showlegend=show_legend,
            title=dict(text=title, x=0.5),
            height=600,
            width=700
        )

        return fig
```

### SensitivitySurfaceAnalyzer

```python
# ABOUTME: Creates 2D sensitivity surfaces (contour/heatmaps) for two-variable analysis
# ABOUTME: Shows NPV as function of two parameters simultaneously

@dataclass
class SurfaceResult:
    """Results from 2D surface analysis."""
    param1_name: str
    param1_values: np.ndarray
    param2_name: str
    param2_values: np.ndarray
    npv_surface: np.ndarray  # 2D array of NPV values
    base_npv: float
    breakeven_contour: Optional[List[Tuple[float, float]]] = None


class SensitivitySurfaceAnalyzer:
    """
    Generates 2D sensitivity surfaces showing NPV as function of two parameters.

    Creates contour plots and heatmaps that reveal interaction effects
    between parameters and identify breakeven combinations.

    Usage:
        analyzer = SensitivitySurfaceAnalyzer(npv_calculator)
        result = analyzer.analyze(param1, param2, resolution=20)
        fig = analyzer.create_contour_plot(result)
    """

    def __init__(self, npv_calculator: Callable[[Dict[str, float]], float]):
        """
        Initialize analyzer with NPV calculation function.

        Args:
            npv_calculator: Function that takes parameter dict and returns NPV
        """
        self.npv_calculator = npv_calculator
        self.base_params: Dict[str, float] = {}

    def set_base_parameters(self, params: Dict[str, float]):
        """Set base case parameters for analysis."""
        self.base_params = params.copy()

    def analyze(
        self,
        param1: SensitivityParameter,
        param2: SensitivityParameter,
        resolution: int = 20,
        find_breakeven: bool = True
    ) -> SurfaceResult:
        """
        Generate 2D sensitivity surface.

        Args:
            param1: First parameter (x-axis)
            param2: Second parameter (y-axis)
            resolution: Number of points per axis
            find_breakeven: Whether to find NPV=0 contour

        Returns:
            SurfaceResult with NPV surface data
        """
        # Generate parameter grids
        p1_values = np.array(param1.get_values())
        p2_values = np.array(param2.get_values())

        # If variations don't give enough points, interpolate
        if len(p1_values) < resolution:
            p1_values = np.linspace(p1_values.min(), p1_values.max(), resolution)
        if len(p2_values) < resolution:
            p2_values = np.linspace(p2_values.min(), p2_values.max(), resolution)

        # Calculate NPV for each combination
        npv_surface = np.zeros((len(p2_values), len(p1_values)))

        for i, p2_val in enumerate(p2_values):
            for j, p1_val in enumerate(p1_values):
                test_params = self.base_params.copy()
                test_params[param1.name] = p1_val
                test_params[param2.name] = p2_val
                npv_surface[i, j] = self.npv_calculator(test_params)

        # Calculate base NPV
        base_npv = self.npv_calculator(self.base_params)

        # Find breakeven contour if requested
        breakeven_contour = None
        if find_breakeven:
            breakeven_contour = self._find_breakeven_contour(
                p1_values, p2_values, npv_surface
            )

        return SurfaceResult(
            param1_name=param1.name,
            param1_values=p1_values,
            param2_name=param2.name,
            param2_values=p2_values,
            npv_surface=npv_surface,
            base_npv=base_npv,
            breakeven_contour=breakeven_contour
        )

    def _find_breakeven_contour(
        self,
        x_values: np.ndarray,
        y_values: np.ndarray,
        z_surface: np.ndarray
    ) -> List[Tuple[float, float]]:
        """Find points where NPV = 0 using linear interpolation."""
        from scipy import ndimage

        # Find zero-crossing contour
        contour_points = []

        # Check horizontal edges
        for i in range(len(y_values)):
            for j in range(len(x_values) - 1):
                z1, z2 = z_surface[i, j], z_surface[i, j + 1]
                if z1 * z2 < 0:  # Sign change
                    # Linear interpolation
                    t = z1 / (z1 - z2)
                    x_cross = x_values[j] + t * (x_values[j + 1] - x_values[j])
                    contour_points.append((x_cross, y_values[i]))

        # Check vertical edges
        for i in range(len(y_values) - 1):
            for j in range(len(x_values)):
                z1, z2 = z_surface[i, j], z_surface[i + 1, j]
                if z1 * z2 < 0:  # Sign change
                    t = z1 / (z1 - z2)
                    y_cross = y_values[i] + t * (y_values[i + 1] - y_values[i])
                    contour_points.append((x_values[j], y_cross))

        return contour_points

    def create_contour_plot(
        self,
        result: SurfaceResult,
        title: str = "NPV Sensitivity Surface",
        show_breakeven: bool = True,
        colorscale: str = "RdYlGn"
    ) -> go.Figure:
        """
        Create interactive contour plot.

        Args:
            result: SurfaceResult from analyze()
            title: Chart title
            show_breakeven: Highlight NPV=0 contour
            colorscale: Plotly colorscale name

        Returns:
            Plotly Figure object
        """
        fig = go.Figure()

        # Add contour surface
        fig.add_trace(go.Contour(
            z=result.npv_surface,
            x=result.param1_values,
            y=result.param2_values,
            colorscale=colorscale,
            contours=dict(
                showlabels=True,
                labelfont=dict(size=10, color='white')
            ),
            colorbar=dict(title="NPV (MM$)"),
            hovertemplate=(
                f"{result.param1_name}: %{{x:.2f}}<br>"
                f"{result.param2_name}: %{{y:.2f}}<br>"
                "NPV: %{z:.2f} MM$<extra></extra>"
            )
        ))

        # Add breakeven contour if available
        if show_breakeven and result.breakeven_contour:
            x_be = [p[0] for p in result.breakeven_contour]
            y_be = [p[1] for p in result.breakeven_contour]
            fig.add_trace(go.Scatter(
                x=x_be,
                y=y_be,
                mode='markers',
                marker=dict(color='black', size=4, symbol='x'),
                name='Breakeven (NPV=0)',
                hovertemplate=(
                    f"{result.param1_name}: %{{x:.2f}}<br>"
                    f"{result.param2_name}: %{{y:.2f}}<br>"
                    "NPV: ~0<extra></extra>"
                )
            ))

        # Add base case marker
        if result.param1_name in self.base_params and result.param2_name in self.base_params:
            fig.add_trace(go.Scatter(
                x=[self.base_params[result.param1_name]],
                y=[self.base_params[result.param2_name]],
                mode='markers',
                marker=dict(color='blue', size=15, symbol='star'),
                name=f'Base Case (NPV={result.base_npv:.1f})',
            ))

        fig.update_layout(
            title=dict(text=title, x=0.5),
            xaxis_title=result.param1_name.replace("_", " ").title(),
            yaxis_title=result.param2_name.replace("_", " ").title(),
            height=600,
            width=800
        )

        return fig

    def create_heatmap(
        self,
        result: SurfaceResult,
        title: str = "NPV Sensitivity Heatmap",
        colorscale: str = "RdYlGn"
    ) -> go.Figure:
        """Create heatmap version of sensitivity surface."""
        fig = go.Figure()

        fig.add_trace(go.Heatmap(
            z=result.npv_surface,
            x=result.param1_values,
            y=result.param2_values,
            colorscale=colorscale,
            colorbar=dict(title="NPV (MM$)"),
            hovertemplate=(
                f"{result.param1_name}: %{{x:.2f}}<br>"
                f"{result.param2_name}: %{{y:.2f}}<br>"
                "NPV: %{z:.2f} MM$<extra></extra>"
            )
        ))

        fig.update_layout(
            title=dict(text=title, x=0.5),
            xaxis_title=result.param1_name.replace("_", " ").title(),
            yaxis_title=result.param2_name.replace("_", " ").title(),
            height=600,
            width=800
        )

        return fig
```

### BreakevenAnalyzer

```python
# ABOUTME: Calculates and visualizes breakeven prices for oil, gas, and costs
# ABOUTME: Supports multi-commodity breakeven analysis and sensitivity to other parameters

@dataclass
class BreakevenResult:
    """Results from breakeven analysis."""
    parameter_name: str
    breakeven_value: Optional[float]
    unit: str
    base_value: float
    base_npv: float
    sensitivity_curve: List[Tuple[float, float]]  # [(param_value, npv), ...]
    margin_at_base: float  # % above/below breakeven


class BreakevenAnalyzer:
    """
    Calculates breakeven prices and costs for investment decisions.

    Finds the parameter value where NPV equals zero, indicating the
    minimum/maximum acceptable value for project viability.

    Usage:
        analyzer = BreakevenAnalyzer(npv_calculator)
        result = analyzer.find_breakeven("oil_price", base_value=70, range_pct=0.5)
        fig = analyzer.create_breakeven_chart([oil_result, gas_result])
    """

    def __init__(self, npv_calculator: Callable[[Dict[str, float]], float]):
        """Initialize with NPV calculator function."""
        self.npv_calculator = npv_calculator
        self.base_params: Dict[str, float] = {}

    def set_base_parameters(self, params: Dict[str, float]):
        """Set base case parameters."""
        self.base_params = params.copy()

    def find_breakeven(
        self,
        param_name: str,
        base_value: float,
        range_pct: float = 0.5,
        resolution: int = 50,
        unit: str = ""
    ) -> BreakevenResult:
        """
        Find breakeven value for a parameter using bisection.

        Args:
            param_name: Parameter to find breakeven for
            base_value: Base case value
            range_pct: Search range as fraction of base value
            resolution: Points for sensitivity curve
            unit: Display unit

        Returns:
            BreakevenResult with breakeven value and sensitivity data
        """
        # Calculate base NPV
        base_npv = self.npv_calculator(self.base_params)

        # Generate sensitivity curve
        min_val = base_value * (1 - range_pct)
        max_val = base_value * (1 + range_pct)
        test_values = np.linspace(min_val, max_val, resolution)

        sensitivity_curve = []
        for val in test_values:
            test_params = self.base_params.copy()
            test_params[param_name] = val
            npv = self.npv_calculator(test_params)
            sensitivity_curve.append((val, npv))

        # Find breakeven using bisection
        breakeven_value = self._bisection_search(
            param_name, min_val, max_val, tolerance=0.01
        )

        # Calculate margin
        if breakeven_value is not None:
            margin = ((base_value - breakeven_value) / breakeven_value) * 100
        else:
            margin = float('inf') if base_npv > 0 else float('-inf')

        return BreakevenResult(
            parameter_name=param_name,
            breakeven_value=breakeven_value,
            unit=unit,
            base_value=base_value,
            base_npv=base_npv,
            sensitivity_curve=sensitivity_curve,
            margin_at_base=margin
        )

    def _bisection_search(
        self,
        param_name: str,
        low: float,
        high: float,
        tolerance: float = 0.01,
        max_iterations: int = 50
    ) -> Optional[float]:
        """Find breakeven using bisection method."""
        # Check if breakeven exists in range
        test_low = self.base_params.copy()
        test_low[param_name] = low
        npv_low = self.npv_calculator(test_low)

        test_high = self.base_params.copy()
        test_high[param_name] = high
        npv_high = self.npv_calculator(test_high)

        if npv_low * npv_high > 0:
            # No sign change, breakeven not in range
            return None

        for _ in range(max_iterations):
            mid = (low + high) / 2
            test_mid = self.base_params.copy()
            test_mid[param_name] = mid
            npv_mid = self.npv_calculator(test_mid)

            if abs(npv_mid) < tolerance or (high - low) / 2 < tolerance:
                return mid

            if npv_mid * npv_low < 0:
                high = mid
                npv_high = npv_mid
            else:
                low = mid
                npv_low = npv_mid

        return (low + high) / 2

    def create_breakeven_chart(
        self,
        results: List[BreakevenResult],
        title: str = "Breakeven Analysis"
    ) -> go.Figure:
        """
        Create multi-parameter breakeven chart.

        Args:
            results: List of BreakevenResult objects
            title: Chart title

        Returns:
            Plotly Figure with breakeven visualization
        """
        fig = make_subplots(
            rows=len(results), cols=1,
            subplot_titles=[r.parameter_name.replace("_", " ").title() for r in results],
            vertical_spacing=0.12
        )

        colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728']

        for i, result in enumerate(results):
            row = i + 1
            x_vals = [p[0] for p in result.sensitivity_curve]
            y_vals = [p[1] for p in result.sensitivity_curve]

            # NPV curve
            fig.add_trace(
                go.Scatter(
                    x=x_vals, y=y_vals,
                    mode='lines',
                    line=dict(color=colors[i % len(colors)], width=2),
                    name=f'{result.parameter_name} Sensitivity',
                    showlegend=True
                ),
                row=row, col=1
            )

            # Zero line
            fig.add_hline(y=0, line_dash="dash", line_color="gray", row=row, col=1)

            # Breakeven marker
            if result.breakeven_value is not None:
                fig.add_trace(
                    go.Scatter(
                        x=[result.breakeven_value], y=[0],
                        mode='markers+text',
                        marker=dict(color='red', size=12, symbol='x'),
                        text=[f'BE: {result.breakeven_value:.2f}{result.unit}'],
                        textposition='top center',
                        name=f'Breakeven',
                        showlegend=(i == 0)
                    ),
                    row=row, col=1
                )

            # Base case marker
            fig.add_trace(
                go.Scatter(
                    x=[result.base_value], y=[result.base_npv],
                    mode='markers',
                    marker=dict(color='green', size=12, symbol='star'),
                    name=f'Base Case',
                    showlegend=(i == 0)
                ),
                row=row, col=1
            )

            # Update axes
            fig.update_xaxes(title_text=f"{result.parameter_name} ({result.unit})", row=row, col=1)
            fig.update_yaxes(title_text="NPV (MM$)", row=row, col=1)

        fig.update_layout(
            title=dict(text=title, x=0.5),
            height=300 * len(results),
            showlegend=True
        )

        return fig
```

### ScenarioMatrixAnalyzer

```python
# ABOUTME: Creates scenario comparison matrices for management presentations
# ABOUTME: Supports low/mid/high scenarios with customizable probability weighting

@dataclass
class ScenarioDefinition:
    """Definition of a single scenario."""
    name: str
    parameters: Dict[str, float]
    probability: float = 0.0  # For expected value calculation
    color: str = "#1f77b4"


@dataclass
class ScenarioMatrixResult:
    """Results from scenario matrix analysis."""
    scenarios: List[ScenarioDefinition]
    npv_values: Dict[str, float]  # scenario_name -> NPV
    irr_values: Dict[str, float]  # scenario_name -> IRR
    payback_values: Dict[str, float]  # scenario_name -> payback
    expected_npv: float  # Probability-weighted NPV
    best_scenario: str
    worst_scenario: str


class ScenarioMatrixAnalyzer:
    """
    Creates scenario comparison matrices for investment decisions.

    Compares multiple predefined scenarios (e.g., Low/Mid/High cases)
    and calculates probability-weighted expected values.

    Usage:
        analyzer = ScenarioMatrixAnalyzer(npv_calculator, irr_calculator)
        scenarios = [low_case, mid_case, high_case]
        result = analyzer.analyze(scenarios)
        fig = analyzer.create_comparison_chart(result)
    """

    def __init__(
        self,
        npv_calculator: Callable[[Dict[str, float]], float],
        irr_calculator: Optional[Callable[[Dict[str, float]], float]] = None,
        payback_calculator: Optional[Callable[[Dict[str, float]], float]] = None
    ):
        """
        Initialize with metric calculators.

        Args:
            npv_calculator: Function to calculate NPV
            irr_calculator: Optional function to calculate IRR
            payback_calculator: Optional function to calculate payback period
        """
        self.npv_calculator = npv_calculator
        self.irr_calculator = irr_calculator
        self.payback_calculator = payback_calculator

    def analyze(self, scenarios: List[ScenarioDefinition]) -> ScenarioMatrixResult:
        """
        Analyze all scenarios and compare results.

        Args:
            scenarios: List of scenario definitions

        Returns:
            ScenarioMatrixResult with comparison data
        """
        npv_values = {}
        irr_values = {}
        payback_values = {}

        for scenario in scenarios:
            # Calculate NPV
            npv = self.npv_calculator(scenario.parameters)
            npv_values[scenario.name] = npv

            # Calculate IRR if available
            if self.irr_calculator:
                try:
                    irr = self.irr_calculator(scenario.parameters)
                    irr_values[scenario.name] = irr
                except:
                    irr_values[scenario.name] = None

            # Calculate payback if available
            if self.payback_calculator:
                try:
                    payback = self.payback_calculator(scenario.parameters)
                    payback_values[scenario.name] = payback
                except:
                    payback_values[scenario.name] = None

        # Calculate expected NPV
        total_prob = sum(s.probability for s in scenarios)
        if total_prob > 0:
            expected_npv = sum(
                s.probability * npv_values[s.name] / total_prob
                for s in scenarios
            )
        else:
            expected_npv = sum(npv_values.values()) / len(npv_values)

        # Find best/worst scenarios
        best_scenario = max(npv_values, key=npv_values.get)
        worst_scenario = min(npv_values, key=npv_values.get)

        return ScenarioMatrixResult(
            scenarios=scenarios,
            npv_values=npv_values,
            irr_values=irr_values,
            payback_values=payback_values,
            expected_npv=expected_npv,
            best_scenario=best_scenario,
            worst_scenario=worst_scenario
        )

    def create_comparison_chart(
        self,
        result: ScenarioMatrixResult,
        title: str = "Scenario Comparison"
    ) -> go.Figure:
        """
        Create scenario comparison bar chart.

        Args:
            result: ScenarioMatrixResult from analyze()
            title: Chart title

        Returns:
            Plotly Figure with scenario comparison
        """
        scenarios = [s.name for s in result.scenarios]
        npvs = [result.npv_values[s] for s in scenarios]
        colors = [s.color for s in result.scenarios]

        fig = go.Figure()

        # NPV bars
        fig.add_trace(go.Bar(
            x=scenarios,
            y=npvs,
            marker_color=colors,
            text=[f'${npv:.1f}M' for npv in npvs],
            textposition='outside',
            name='NPV'
        ))

        # Expected value line
        fig.add_hline(
            y=result.expected_npv,
            line_dash="dash",
            line_color="black",
            annotation_text=f"Expected: ${result.expected_npv:.1f}M",
            annotation_position="right"
        )

        # Zero line
        fig.add_hline(y=0, line_color="gray", line_width=1)

        fig.update_layout(
            title=dict(text=title, x=0.5),
            xaxis_title="Scenario",
            yaxis_title="NPV (MM$)",
            height=500,
            showlegend=False
        )

        return fig

    def create_matrix_table(
        self,
        result: ScenarioMatrixResult
    ) -> go.Figure:
        """
        Create scenario matrix as formatted table.

        Returns:
            Plotly Figure with table visualization
        """
        scenarios = [s.name for s in result.scenarios]

        # Build table data
        headers = ['Metric'] + scenarios

        npv_row = ['NPV (MM$)'] + [f'{result.npv_values[s]:.1f}' for s in scenarios]

        rows = [npv_row]

        if result.irr_values:
            irr_row = ['IRR (%)'] + [
                f'{result.irr_values[s]*100:.1f}' if result.irr_values.get(s) else 'N/A'
                for s in scenarios
            ]
            rows.append(irr_row)

        if result.payback_values:
            payback_row = ['Payback (yrs)'] + [
                f'{result.payback_values[s]:.1f}' if result.payback_values.get(s) else 'N/A'
                for s in scenarios
            ]
            rows.append(payback_row)

        prob_row = ['Probability'] + [f'{s.probability*100:.0f}%' for s in result.scenarios]
        rows.append(prob_row)

        # Create table
        fig = go.Figure(data=[go.Table(
            header=dict(
                values=headers,
                fill_color='#1f77b4',
                font=dict(color='white', size=12),
                align='center'
            ),
            cells=dict(
                values=[[row[i] for row in rows] for i in range(len(headers))],
                fill_color=[['white', '#f0f0f0'] * (len(rows) // 2 + 1)][:len(rows)],
                align='center'
            )
        )])

        fig.update_layout(
            title=dict(text="Scenario Matrix", x=0.5),
            height=200 + 40 * len(rows)
        )

        return fig
```

### DecisionTreeAnalyzer

```python
# ABOUTME: Creates decision tree analysis for staged investments
# ABOUTME: Calculates expected value considering probabilities and decision points

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Union
import plotly.graph_objects as go


@dataclass
class DecisionNode:
    """A decision or chance node in the tree."""
    name: str
    node_type: str  # "decision", "chance", "terminal"
    value: Optional[float] = None  # For terminal nodes
    probability: float = 1.0  # For chance nodes
    children: List['DecisionNode'] = field(default_factory=list)
    investment: float = 0.0  # Investment required at this node
    expected_value: float = 0.0  # Calculated expected value


class DecisionTreeAnalyzer:
    """
    Performs decision tree analysis for staged investment decisions.

    Useful for analyzing:
    - Drill/don't drill decisions
    - Appraisal well outcomes
    - Development staging (Phase 1, Phase 2, etc.)
    - Farmout vs. operate decisions

    Usage:
        analyzer = DecisionTreeAnalyzer()
        tree = analyzer.build_drill_decision_tree(
            drill_cost=10, success_prob=0.3,
            success_npv=100, failure_npv=-10
        )
        result = analyzer.evaluate(tree)
        fig = analyzer.visualize(tree)
    """

    def build_drill_decision_tree(
        self,
        drill_cost: float,
        success_prob: float,
        success_npv: float,
        failure_npv: float,
        farmout_npv: float = 0
    ) -> DecisionNode:
        """
        Build standard drill/farmout/don't drill decision tree.

        Args:
            drill_cost: Cost to drill (MM$)
            success_prob: Probability of success (0-1)
            success_npv: NPV if successful (MM$)
            failure_npv: NPV if dry hole (MM$, usually negative)
            farmout_npv: NPV if farmout (MM$)

        Returns:
            Root DecisionNode of tree
        """
        # Success terminal node
        success = DecisionNode(
            name="Success",
            node_type="terminal",
            value=success_npv,
            probability=success_prob
        )

        # Failure terminal node
        failure = DecisionNode(
            name="Dry Hole",
            node_type="terminal",
            value=failure_npv,
            probability=1 - success_prob
        )

        # Drill chance node
        drill_outcome = DecisionNode(
            name="Drill Outcome",
            node_type="chance",
            children=[success, failure],
            investment=drill_cost
        )

        # Farmout terminal
        farmout = DecisionNode(
            name="Farmout",
            node_type="terminal",
            value=farmout_npv
        )

        # Don't drill terminal
        no_drill = DecisionNode(
            name="Don't Drill",
            node_type="terminal",
            value=0
        )

        # Root decision node
        root = DecisionNode(
            name="Investment Decision",
            node_type="decision",
            children=[drill_outcome, farmout, no_drill]
        )

        return root

    def evaluate(self, node: DecisionNode) -> float:
        """
        Evaluate decision tree using backward induction.

        Args:
            node: Root node of tree

        Returns:
            Expected value at root node
        """
        if node.node_type == "terminal":
            node.expected_value = node.value or 0
            return node.expected_value

        # Recursively evaluate children
        for child in node.children:
            self.evaluate(child)

        if node.node_type == "chance":
            # Expected value = sum of prob * value
            ev = sum(c.probability * c.expected_value for c in node.children)
            node.expected_value = ev - node.investment

        elif node.node_type == "decision":
            # Optimal decision = max expected value
            node.expected_value = max(c.expected_value for c in node.children)

        return node.expected_value

    def get_optimal_path(self, node: DecisionNode) -> List[str]:
        """Get the optimal decision path from root."""
        path = [node.name]

        if node.node_type == "terminal":
            return path

        if node.node_type == "decision":
            # Find child with max expected value
            best_child = max(node.children, key=lambda c: c.expected_value)
            path.extend(self.get_optimal_path(best_child))

        elif node.node_type == "chance":
            # For chance nodes, show expected outcome
            for child in node.children:
                path.append(f"  {child.name} (p={child.probability:.0%})")

        return path

    def visualize(
        self,
        root: DecisionNode,
        title: str = "Decision Tree Analysis"
    ) -> go.Figure:
        """
        Create decision tree visualization using Sankey diagram.

        Args:
            root: Root node of evaluated tree
            title: Chart title

        Returns:
            Plotly Figure with decision tree
        """
        # Collect all nodes and links
        nodes = []
        links = []
        node_index = {}

        def add_node(node: DecisionNode, depth: int = 0):
            if node.name not in node_index:
                idx = len(nodes)
                node_index[node.name] = idx

                # Color by node type
                if node.node_type == "decision":
                    color = "#1f77b4"  # Blue
                elif node.node_type == "chance":
                    color = "#ff7f0e"  # Orange
                else:  # terminal
                    color = "#2ca02c" if (node.value or 0) > 0 else "#d62728"

                # Label with expected value
                if node.node_type == "terminal":
                    label = f"{node.name}<br>${node.value:.1f}M"
                else:
                    label = f"{node.name}<br>EV: ${node.expected_value:.1f}M"

                nodes.append({
                    'label': label,
                    'color': color,
                    'depth': depth
                })

            return node_index[node.name]

        def process_tree(node: DecisionNode, depth: int = 0):
            source_idx = add_node(node, depth)

            for child in node.children:
                target_idx = add_node(child, depth + 1)

                # Link value is the flow "magnitude"
                value = abs(child.expected_value) if child.expected_value else 1

                # Label for link
                if child.probability < 1:
                    label = f"{child.probability:.0%}"
                else:
                    label = ""

                links.append({
                    'source': source_idx,
                    'target': target_idx,
                    'value': max(value, 0.1),  # Minimum for visibility
                    'label': label
                })

                process_tree(child, depth + 1)

        process_tree(root)

        fig = go.Figure(data=[go.Sankey(
            node=dict(
                pad=15,
                thickness=20,
                line=dict(color="black", width=0.5),
                label=[n['label'] for n in nodes],
                color=[n['color'] for n in nodes]
            ),
            link=dict(
                source=[l['source'] for l in links],
                target=[l['target'] for l in links],
                value=[l['value'] for l in links],
                label=[l['label'] for l in links]
            )
        )])

        fig.update_layout(
            title=dict(text=title, x=0.5),
            height=500,
            font_size=10
        )

        return fig
```

### SensitivityDashboard

```python
# ABOUTME: Combines all sensitivity analyses into comprehensive dashboard
# ABOUTME: Creates executive-ready reports with multiple visualization types

from typing import Dict, List, Optional, Callable
import plotly.graph_objects as go
from plotly.subplots import make_subplots


class SensitivityDashboard:
    """
    Creates comprehensive sensitivity analysis dashboard.

    Combines spider diagrams, contour plots, tornado charts, and
    breakeven analysis into a single executive summary.

    Usage:
        dashboard = SensitivityDashboard(
            npv_calculator=calc_npv,
            base_params=base_case
        )
        dashboard.add_spider_analysis(params)
        dashboard.add_surface_analysis(oil_price, gas_price)
        dashboard.add_breakeven_analysis(['oil_price', 'gas_price'])
        fig = dashboard.create_dashboard()
    """

    def __init__(
        self,
        npv_calculator: Callable[[Dict[str, float]], float],
        base_params: Dict[str, float],
        irr_calculator: Optional[Callable[[Dict[str, float]], float]] = None
    ):
        """
        Initialize dashboard with calculators.

        Args:
            npv_calculator: Function to calculate NPV
            base_params: Base case parameters
            irr_calculator: Optional IRR calculator
        """
        self.npv_calculator = npv_calculator
        self.base_params = base_params.copy()
        self.irr_calculator = irr_calculator

        self.spider_result: Optional[SpiderResult] = None
        self.surface_results: List[SurfaceResult] = []
        self.breakeven_results: List[BreakevenResult] = []
        self.scenario_result: Optional[ScenarioMatrixResult] = None

    def add_spider_analysis(self, parameters: List[SensitivityParameter]):
        """Add spider diagram analysis."""
        analyzer = SpiderDiagramAnalyzer(self.npv_calculator)
        self.spider_result = analyzer.analyze(parameters)

    def add_surface_analysis(
        self,
        param1: SensitivityParameter,
        param2: SensitivityParameter,
        resolution: int = 15
    ):
        """Add 2D surface analysis."""
        analyzer = SensitivitySurfaceAnalyzer(self.npv_calculator)
        analyzer.set_base_parameters(self.base_params)
        result = analyzer.analyze(param1, param2, resolution)
        self.surface_results.append(result)

    def add_breakeven_analysis(
        self,
        param_names: List[str],
        range_pct: float = 0.5
    ):
        """Add breakeven analysis for parameters."""
        analyzer = BreakevenAnalyzer(self.npv_calculator)
        analyzer.set_base_parameters(self.base_params)

        for param in param_names:
            if param in self.base_params:
                result = analyzer.find_breakeven(
                    param, self.base_params[param], range_pct
                )
                self.breakeven_results.append(result)

    def add_scenario_analysis(self, scenarios: List[ScenarioDefinition]):
        """Add scenario comparison."""
        analyzer = ScenarioMatrixAnalyzer(
            self.npv_calculator, self.irr_calculator
        )
        self.scenario_result = analyzer.analyze(scenarios)

    def create_dashboard(
        self,
        title: str = "Economic Sensitivity Dashboard"
    ) -> go.Figure:
        """
        Create comprehensive dashboard with all analyses.

        Returns:
            Plotly Figure with multi-panel dashboard
        """
        # Determine layout based on available analyses
        panels = []
        if self.spider_result:
            panels.append("spider")
        if self.surface_results:
            panels.append("surface")
        if self.breakeven_results:
            panels.append("breakeven")
        if self.scenario_result:
            panels.append("scenarios")

        n_panels = len(panels)
        if n_panels == 0:
            raise ValueError("No analyses added to dashboard")

        # Create subplot layout
        if n_panels <= 2:
            rows, cols = 1, n_panels
        else:
            rows, cols = 2, 2

        # Define subplot specs
        specs = []
        subplot_titles = []

        for i in range(rows):
            row_specs = []
            for j in range(cols):
                idx = i * cols + j
                if idx < n_panels:
                    panel = panels[idx]
                    if panel == "spider":
                        row_specs.append({"type": "polar"})
                        subplot_titles.append("Parameter Sensitivity")
                    elif panel == "surface":
                        row_specs.append({"type": "contour"})
                        subplot_titles.append("NPV Surface")
                    else:
                        row_specs.append({"type": "xy"})
                        subplot_titles.append(panel.title())
                else:
                    row_specs.append(None)
            specs.append(row_specs)

        fig = make_subplots(
            rows=rows, cols=cols,
            specs=specs,
            subplot_titles=subplot_titles
        )

        # Add each panel
        panel_idx = 0
        for i in range(rows):
            for j in range(cols):
                if panel_idx >= n_panels:
                    break

                panel = panels[panel_idx]
                row, col = i + 1, j + 1

                if panel == "spider" and self.spider_result:
                    self._add_spider_to_subplot(fig, row, col)
                elif panel == "surface" and self.surface_results:
                    self._add_surface_to_subplot(fig, row, col)
                elif panel == "breakeven" and self.breakeven_results:
                    self._add_breakeven_to_subplot(fig, row, col)
                elif panel == "scenarios" and self.scenario_result:
                    self._add_scenarios_to_subplot(fig, row, col)

                panel_idx += 1

        fig.update_layout(
            title=dict(text=title, x=0.5),
            height=400 * rows,
            width=500 * cols,
            showlegend=True
        )

        return fig

    def _add_spider_to_subplot(self, fig: go.Figure, row: int, col: int):
        """Add spider diagram to subplot."""
        result = self.spider_result
        colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728']

        for i, param in enumerate(result.parameters[:4]):  # Limit to 4 for clarity
            changes = result.npv_changes[param]
            r_values = changes + [changes[0]]
            theta_values = [f"{v:+.0f}%" for v in result.variations] + [f"{result.variations[0]:+.0f}%"]

            fig.add_trace(
                go.Scatterpolar(
                    r=r_values,
                    theta=theta_values,
                    name=param.replace("_", " ").title(),
                    line=dict(color=colors[i])
                ),
                row=row, col=col
            )

    def _add_surface_to_subplot(self, fig: go.Figure, row: int, col: int):
        """Add surface contour to subplot."""
        result = self.surface_results[0]

        fig.add_trace(
            go.Contour(
                z=result.npv_surface,
                x=result.param1_values,
                y=result.param2_values,
                colorscale="RdYlGn",
                showscale=True
            ),
            row=row, col=col
        )

    def _add_breakeven_to_subplot(self, fig: go.Figure, row: int, col: int):
        """Add breakeven analysis to subplot."""
        result = self.breakeven_results[0]
        x_vals = [p[0] for p in result.sensitivity_curve]
        y_vals = [p[1] for p in result.sensitivity_curve]

        fig.add_trace(
            go.Scatter(x=x_vals, y=y_vals, mode='lines', name='NPV Curve'),
            row=row, col=col
        )

        if result.breakeven_value:
            fig.add_trace(
                go.Scatter(
                    x=[result.breakeven_value], y=[0],
                    mode='markers',
                    marker=dict(size=10, color='red', symbol='x'),
                    name='Breakeven'
                ),
                row=row, col=col
            )

    def _add_scenarios_to_subplot(self, fig: go.Figure, row: int, col: int):
        """Add scenario comparison to subplot."""
        result = self.scenario_result
        names = [s.name for s in result.scenarios]
        npvs = [result.npv_values[n] for n in names]

        fig.add_trace(
            go.Bar(x=names, y=npvs, name='NPV by Scenario'),
            row=row, col=col
        )

    def export_html(self, filepath: str, title: str = "Sensitivity Dashboard"):
        """Export dashboard to standalone HTML file."""
        fig = self.create_dashboard(title)
        fig.write_html(filepath, include_plotlyjs=True)
        return filepath
```

## YAML Configuration

```yaml
# sensitivity_config.yaml
meta:
  mode: sensitivity_analysis
  output_format: html_dashboard

analysis:
  base_case:
    oil_price: 70.0          # $/bbl
    gas_price: 3.50          # $/mcf
    capex: 500.0             # MM$
    opex_per_boe: 15.0       # $/boe
    discount_rate: 0.10      # 10%
    working_interest: 0.80   # 80%

  spider_diagram:
    enabled: true
    parameters:
      - name: oil_price
        display_name: "Oil Price"
        variations: [-30, -20, -10, 0, 10, 20, 30]
      - name: gas_price
        display_name: "Gas Price"
        variations: [-30, -20, -10, 0, 10, 20, 30]
      - name: capex
        display_name: "CAPEX"
        variations: [-20, -10, 0, 10, 20, 30, 40]
      - name: opex_per_boe
        display_name: "OPEX"
        variations: [-30, -20, -10, 0, 10, 20, 30]

  surface_analysis:
    enabled: true
    param1: oil_price
    param2: gas_price
    resolution: 20
    find_breakeven: true

  breakeven:
    enabled: true
    parameters:
      - oil_price
      - gas_price
    range_percent: 0.50

  scenarios:
    enabled: true
    definitions:
      - name: "Low Case"
        probability: 0.25
        oil_price: 55.0
        gas_price: 2.50
        capex: 550.0
      - name: "Mid Case"
        probability: 0.50
        oil_price: 70.0
        gas_price: 3.50
        capex: 500.0
      - name: "High Case"
        probability: 0.25
        oil_price: 90.0
        gas_price: 4.50
        capex: 480.0

output:
  dashboard_path: "reports/sensitivity_dashboard.html"
  include_tables: true
  export_csv: true
```

## CLI Usage

```bash
# Run spider diagram analysis
uv run python -c "
from worldenergydata.economics.sensitivity import SpiderDiagramAnalyzer
# ... analysis code
"

# Generate sensitivity dashboard
uv run python -m worldenergydata.cli sensitivity-dashboard \
    --config config/sensitivity_config.yaml \
    --output reports/sensitivity_dashboard.html

# Quick breakeven analysis
uv run python -c "
from worldenergydata.economics.sensitivity import BreakevenAnalyzer
analyzer = BreakevenAnalyzer(npv_calc)
result = analyzer.find_breakeven('oil_price', 70, range_pct=0.5, unit='\$/bbl')
print(f'Breakeven oil price: \${result.breakeven_value:.2f}/bbl')
"
```

## Example: Complete Sensitivity Analysis

```python
# ABOUTME: Complete example of multi-dimensional sensitivity analysis
# ABOUTME: Shows spider diagram, surface, breakeven, and scenario comparison

from worldenergydata.economics.sensitivity import (
    SensitivityParameter,
    SpiderDiagramAnalyzer,
    SensitivitySurfaceAnalyzer,
    BreakevenAnalyzer,
    ScenarioMatrixAnalyzer,
    ScenarioDefinition,
    SensitivityDashboard,
    ParameterType
)
import numpy as np

# Define NPV calculator (simplified example)
def calculate_npv(params: dict) -> float:
    """Simple NPV calculator for demonstration."""
    oil_price = params.get('oil_price', 70)
    gas_price = params.get('gas_price', 3.5)
    capex = params.get('capex', 500)
    opex_per_boe = params.get('opex_per_boe', 15)
    discount_rate = params.get('discount_rate', 0.10)

    # Simplified: 10-year production profile
    years = np.arange(1, 11)
    oil_production = 5.0 * np.exp(-0.15 * years)  # MMBOE declining
    gas_production = 10.0 * np.exp(-0.12 * years)  # BCF declining

    # Annual cash flows
    revenue = oil_production * oil_price + gas_production * gas_price / 6  # Convert MCF to BOE
    opex = (oil_production + gas_production / 6) * opex_per_boe
    cash_flows = revenue - opex

    # NPV calculation
    discount_factors = 1 / (1 + discount_rate) ** years
    pv = np.sum(cash_flows * discount_factors)
    npv = pv - capex

    return npv

# Base case parameters
base_params = {
    'oil_price': 70.0,
    'gas_price': 3.50,
    'capex': 500.0,
    'opex_per_boe': 15.0,
    'discount_rate': 0.10
}

# Define sensitivity parameters
params = [
    SensitivityParameter(
        name='oil_price',
        display_name='Oil Price',
        base_value=70.0,
        param_type=ParameterType.PERCENTAGE,
        unit='$/bbl',
        color='#1f77b4'
    ),
    SensitivityParameter(
        name='gas_price',
        display_name='Gas Price',
        base_value=3.50,
        param_type=ParameterType.PERCENTAGE,
        unit='$/mcf',
        color='#ff7f0e'
    ),
    SensitivityParameter(
        name='capex',
        display_name='CAPEX',
        base_value=500.0,
        param_type=ParameterType.PERCENTAGE,
        unit='MM$',
        color='#2ca02c'
    ),
    SensitivityParameter(
        name='opex_per_boe',
        display_name='OPEX',
        base_value=15.0,
        param_type=ParameterType.PERCENTAGE,
        unit='$/boe',
        color='#d62728'
    )
]

# Create dashboard
dashboard = SensitivityDashboard(
    npv_calculator=calculate_npv,
    base_params=base_params
)

# Add spider analysis
dashboard.add_spider_analysis(params)

# Add 2D surface (oil vs gas price)
dashboard.add_surface_analysis(params[0], params[1], resolution=20)

# Add breakeven analysis
dashboard.add_breakeven_analysis(['oil_price', 'gas_price'], range_pct=0.5)

# Add scenario comparison
scenarios = [
    ScenarioDefinition(
        name="Low Case",
        parameters={**base_params, 'oil_price': 55, 'gas_price': 2.5},
        probability=0.25,
        color='#d62728'
    ),
    ScenarioDefinition(
        name="Mid Case",
        parameters=base_params,
        probability=0.50,
        color='#ff7f0e'
    ),
    ScenarioDefinition(
        name="High Case",
        parameters={**base_params, 'oil_price': 90, 'gas_price': 4.5},
        probability=0.25,
        color='#2ca02c'
    )
]
dashboard.add_scenario_analysis(scenarios)

# Generate dashboard
fig = dashboard.create_dashboard("Field Development Sensitivity Analysis")
fig.write_html("reports/sensitivity_dashboard.html")
print("Dashboard saved to reports/sensitivity_dashboard.html")

# Individual analyses
print("\n=== Spider Diagram Analysis ===")
spider = SpiderDiagramAnalyzer(calculate_npv)
spider_result = spider.analyze(params)
print(f"Most sensitive parameter: {spider_result.most_sensitive}")
print(f"Least sensitive parameter: {spider_result.least_sensitive}")
print(f"Base NPV: ${spider_result.base_npv:.1f}M")

print("\n=== Breakeven Analysis ===")
be_analyzer = BreakevenAnalyzer(calculate_npv)
be_analyzer.set_base_parameters(base_params)
oil_be = be_analyzer.find_breakeven('oil_price', 70.0, unit='$/bbl')
print(f"Oil breakeven: ${oil_be.breakeven_value:.2f}/bbl")
print(f"Margin at base: {oil_be.margin_at_base:.1f}%")

print("\n=== Scenario Comparison ===")
scenario_analyzer = ScenarioMatrixAnalyzer(calculate_npv)
scenario_result = scenario_analyzer.analyze(scenarios)
print(f"Expected NPV: ${scenario_result.expected_npv:.1f}M")
print(f"Best scenario: {scenario_result.best_scenario}")
print(f"Worst scenario: {scenario_result.worst_scenario}")
```

## Best Practices

### Spider Diagram Analysis
- Limit to 4-6 parameters for readability
- Use same percentage variations for fair comparison
- Highlight most/least sensitive parameters

### 2D Surface Analysis
- Focus on interacting parameters (oil/gas prices, capex/opex)
- Use appropriate resolution (15-25 points per axis)
- Always show breakeven contour and base case marker

### Breakeven Analysis
- Search range should include expected breakeven
- Report margin above/below breakeven for context
- Consider multiple commodities separately

### Scenario Comparison
- Include probability weights for expected value
- Use consistent parameter sets across scenarios
- Show both absolute values and relative changes

### Dashboard Design
- Start with most important analysis (usually spider)
- Keep consistent color coding across panels
- Include summary statistics and key findings
- Export to HTML for stakeholder sharing

## Related Skills

- **npv-analyzer**: Basic NPV and IRR calculations, Monte Carlo simulation
- **production-forecaster**: Decline curve analysis for production inputs
- **hse-risk-analyzer**: Safety data for risk-adjusted economics
- **bsee-data-extractor**: Production data for economic modeling

## Output Formats

| Format | Description | Use Case |
|--------|-------------|----------|
| Interactive HTML | Plotly dashboard | Stakeholder presentations |
| PNG/SVG | Static images | Reports, documents |
| CSV | Raw sensitivity data | Further analysis |
| JSON | Structured results | API integration |
