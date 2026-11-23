#!/bin/bash

# ABOUTME: Install data-validation-reporter skill to a repository
# ABOUTME: Usage: ./install_to_repo.sh <repo-path>

set -euo pipefail

REPO_PATH="${1:-.}"
SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if [ ! -d "$REPO_PATH" ]; then
    echo "Error: Repository path not found: $REPO_PATH"
    exit 1
fi

echo "========================================"
echo "Installing data-validation-reporter"
echo "========================================"
echo "Target repository: $REPO_PATH"
echo ""

# Create directory structure
echo "Creating directory structure..."
mkdir -p "$REPO_PATH/src/validators"
mkdir -p "$REPO_PATH/config/validation"
mkdir -p "$REPO_PATH/examples"

# Copy validator template
echo "Installing validator module..."
cp "$SKILL_DIR/validator_template.py" "$REPO_PATH/src/validators/data_validator.py"

# Create __init__.py
cat > "$REPO_PATH/src/validators/__init__.py" << 'EOF'
"""
Data Validators Module

Provides data validation utilities with quality scoring and interactive reporting.
"""

from .data_validator import DataValidator

__all__ = ['DataValidator']
EOF

# Copy configuration template
echo "Installing configuration..."
cp "$SKILL_DIR/config_template.yaml" "$REPO_PATH/config/validation/validation_config.yaml"

# Copy examples
echo "Installing examples..."
cp "$SKILL_DIR/example_usage.py" "$REPO_PATH/examples/validation_examples.py"

# Create README
cat > "$REPO_PATH/src/validators/README.md" << 'EOF'
# Data Validators Module

## Overview

Data validation utilities with quality scoring and interactive reporting.

**Installed from**: workspace-hub skill `data-validation-reporter`
**Source**: `skills/workspace-hub/data-validation-reporter/`

## Quick Start

```python
from src.validators import DataValidator
import pandas as pd
from pathlib import Path

# Initialize
validator = DataValidator(config_path=Path("config/validation/validation_config.yaml"))

# Validate
df = pd.read_csv("data/your_data.csv")
results = validator.validate_dataframe(
    df=df,
    required_fields=["id", "name"],
    unique_field="id"
)

# Generate report
validator.generate_interactive_report(
    results,
    Path("reports/validation/report.html")
)
```

## Features

- Quality scoring (0-100 scale)
- Missing data analysis
- Type validation
- Duplicate detection
- Interactive Plotly dashboards
- YAML configuration

## Examples

Run the examples:
```bash
python examples/validation_examples.py
```

## Documentation

- Full skill docs: workspace-hub/skills/data-validation-reporter/SKILL.md
- Configuration: config/validation/validation_config.yaml

## Dependencies

Required (add to your dependency file):
- pandas>=1.5.0
- plotly>=5.14.0
- pyyaml>=6.0
EOF

echo ""
echo "========================================"
echo "✅ Installation Complete"
echo "========================================"
echo ""
echo "Installed components:"
echo "  ✅ src/validators/data_validator.py"
echo "  ✅ src/validators/__init__.py"
echo "  ✅ src/validators/README.md"
echo "  ✅ config/validation/validation_config.yaml"
echo "  ✅ examples/validation_examples.py"
echo ""
echo "Next steps:"
echo "  1. Add dependencies: pandas, plotly, pyyaml"
echo "  2. Customize: config/validation/validation_config.yaml"
echo "  3. Test: python examples/validation_examples.py"
echo "  4. Commit changes to repository"
echo ""
