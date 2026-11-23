---
name: technology-stack-modernization-ex1-complete-modernization
description: 'Sub-skill of technology-stack-modernization: Example 1: Complete Tech
  Stack Modernization (+7).'
version: 1.0.0
category: business
type: reference
scripts_exempt: true
---

# Example 1: Complete Tech Stack Modernization (+7)

## Example 1: Complete Tech Stack Modernization


**Before (tech-stack.md):**
```markdown

## Python Environment

- **Python 3.9+**
- **Conda** - Package and environment management
- **pip** - Python package installer


## Dependencies

- Pandas 1.5.0
- NumPy 1.23.0
- Matplotlib 3.6.0
- PyPDF2 3.0.0


## Development Tools

- Black - Code formatting
- isort - Import sorting
- flake8 - Linting
```

**After (tech-stack.md):**
```markdown

## Python Environment

- **Python 3.11+** - Modern type hints and 10-25% performance improvement
- **UV Package Manager** - Fast, reliable package and environment management (workspace-hub standard)


## Dependencies

- **pandas>=2.0.0** - Data processing with improved performance
- **numpy>=1.24.0** - Numerical computing
- **plotly>=5.14.0** - Interactive visualizations (MANDATORY - workspace-hub standard)
- **pypdf>=3.0.0** - Modern PDF processing (replaces deprecated PyPDF2)

**Note:** All visualizations MUST be interactive (Plotly). No static matplotlib charts per workspace-hub standards.


## Development Tools

- **Ruff** - All-in-one linter, formatter, and import sorter (replaces Black+isort+flake8)
- **mypy** - Static type checking
- **pytest** - Testing framework with coverage reporting
```

**pyproject.toml Changes:**
```toml
# Before
[build-system]
requires = ["setuptools", "wheel"]

# After
[project]
name = "project-name"
version = "1.0.0"
requires-python = ">=3.11"
dependencies = [
    "pandas>=2.0.0",
    "numpy>=1.24.0",
    "plotly>=5.14.0",
    "pypdf>=3.0.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.4.0",
    "pytest-cov>=4.1.0",
    "ruff>=0.1.0",
    "mypy>=1.5.0",
]

[tool.ruff]
line-length = 100
target-version = "py311"
```


## Example 2: Matplotlib → Plotly Migration


**Before:**
```python
# src/analysis/visualizer.py
import matplotlib.pyplot as plt
import pandas as pd

def create_scatter_plot(data_path: str, output_path: str):
    """Create scatter plot of analysis results."""
    df = pd.read_csv(data_path)

    plt.figure(figsize=(10, 6))
    plt.scatter(df['x'], df['y'], alpha=0.5)
    plt.xlabel('X Values')
    plt.ylabel('Y Values')
    plt.title('Analysis Results')
    plt.grid(True)
    plt.savefig(output_path, dpi=300)
    plt.close()
```

**After:**
```python
# src/analysis/visualizer.py
import plotly.express as px
import pandas as pd
from pathlib import Path

def create_scatter_plot(data_path: str, output_path: str):
    """Create interactive scatter plot of analysis results."""
    # Use relative path from report location
    df = pd.read_csv(f"../{data_path}")

    # Create interactive Plotly chart
    fig = px.scatter(
        df,
        x='x',
        y='y',
        title='Analysis Results',
        labels={'x': 'X Values', 'y': 'Y Values'},
        hover_data=['x', 'y']  # Show values on hover
    )

    # Customize layout
    fig.update_layout(
        template='plotly_white',
        hovermode='closest',
        height=600
    )

    # Save as interactive HTML
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    fig.write_html(output_path, include_plotlyjs='cdn')
```

**Benefits:**
- Interactive hover tooltips (show exact values)
- Zoom and pan capabilities
- Export options (PNG, SVG) built-in
- Responsive design (mobile-friendly)
- No separate image files needed
- Workspace-hub compliant
