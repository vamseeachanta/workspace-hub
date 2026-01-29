# Testing Skill Learner

This file tests the post-commit skill learning hook.

The hook should analyze this commit and:
- Detect patterns used
- Calculate reusability score
- Recommend skill actions
- Update learning log

Created: Tue Jan  7 06:45:00 CST 2026

## Test Content

This is a larger test file to trigger the skill learning hook.
The hook only analyzes commits with >50 lines changed.

### Sample Code Patterns

Here's some Python code to test pattern detection:

```python
import plotly.graph_objects as go
import pandas as pd
import yaml
import logging

logger = logging.getLogger(__name__)

def load_config(config_file):
    """Load YAML configuration."""
    with open(config_file, 'r') as f:
        return yaml.safe_load(f)

def load_data(csv_file):
    """Load CSV data with validation."""
    logger.info(f"Loading data from {csv_file}")
    df = pd.read_csv(csv_file)

    # Validate data
    required_columns = ['date', 'value', 'category']
    for col in required_columns:
        if col not in df.columns:
            raise ValueError(f"Missing required column: {col}")

    return df

def calculate_npv(cash_flows, discount_rate):
    """Calculate Net Present Value."""
    import numpy as np
    return np.npv(discount_rate, cash_flows)

def create_visualization(df, config):
    """Create interactive Plotly visualization."""
    fig = go.Figure()

    for category in df['category'].unique():
        subset = df[df['category'] == category]
        fig.add_trace(go.Scatter(
            x=subset['date'],
            y=subset['value'],
            name=category,
            mode='lines+markers'
        ))

    fig.update_layout(
        title=config.get('title', 'Data Visualization'),
        xaxis_title='Date',
        yaxis_title='Value',
        hovermode='x unified'
    )

    return fig

def main():
    """Main execution function."""
    # Load configuration
    config = load_config('config/input/analysis.yaml')

    # Load data
    df = load_data(config['data']['csv_file'])

    # Create visualization
    fig = create_visualization(df, config['visualization'])

    # Save HTML report
    output_path = config['output']['path']
    fig.write_html(output_path)
    logger.info(f"Report saved to {output_path}")

if __name__ == '__main__':
    main()
```

### Expected Patterns Detected

The skill-learner should detect:
1. **plotly_viz** - Plotly visualization usage
2. **pandas_processing** - Pandas data handling
3. **yaml_config** - YAML configuration loading
4. **financial_calc** - NPV calculation
5. **data_validation** - Data validation logic
6. **bash_execution** - Main function pattern

### Expected Reusability Score

Based on patterns:
- Plotly: +25 points
- Pandas: +15 points
- YAML: +10 points
- NPV/Financial: +30 points
- Validation: +15 points
- Total: ~95/100

### Expected Recommendation

**CREATE NEW SKILL** - High reusability score indicates strong candidate for new skill.

Possible skill name: `data-analysis-visualizer` or `financial-data-reporter`
