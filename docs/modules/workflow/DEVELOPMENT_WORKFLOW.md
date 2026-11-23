# Development Workflow Plan

> Standardized development workflow for workspace-hub and all repositories
>
> Version: 1.0.0
> Last Updated: 2025-10-22

## Overview

This document defines the standard development workflow to be used across all repositories in workspace-hub. The workflow emphasizes:
- User-controlled requirements (`user_prompt.md`)
- YAML-based configuration
- Pseudocode review before implementation
- Test-Driven Development (TDD)
- Bash-based execution for efficiency
- Modular code organization

## Workflow Phases

### Phase 1: User Requirements (user_prompt.md)

**Purpose:** Capture user requirements in a single source of truth

**Process:**
1. User creates or updates `user_prompt.md` in repository root
2. File contains natural language description of feature/requirement
3. **Only the user edits this file** - AI/tools read but don't modify
4. Version controlled for requirement tracking

**Template Location:** `templates/user_prompt.md`

**Example:**
```markdown
# User Prompt

## Objective
Implement data analysis pipeline for CSV files

## Requirements
- Load CSV from relative path
- Generate interactive HTML report with Plotly
- Calculate summary statistics
- Export results to JSON

## Constraints
- Must handle files up to 100MB
- Response time < 5 seconds
- Interactive plots only (no static images)
```

---

### Phase 2: YAML Input File Preparation

**Purpose:** Transform requirements into structured, machine-readable configuration

**Process:**
1. AI/tool reads `user_prompt.md`
2. Generates YAML input file in `config/input/`
3. YAML contains all parameters, settings, and specifications
4. User reviews and approves YAML

**YAML Structure:**
```yaml
# config/input/feature-name-YYYYMMDD.yaml

metadata:
  feature: "data-analysis-pipeline"
  created: "2025-10-22"
  status: "draft"
  author: "user"

requirements:
  input:
    - type: "csv"
    - path_type: "relative"
    - max_size_mb: 100

  processing:
    - calculate_statistics: true
    - statistics_types: ["mean", "median", "std", "quantiles"]

  output:
    - format: "html"
    - visualization: "plotly"
    - interactive: true
    - export_json: true

  constraints:
    - max_response_time_sec: 5
    - memory_limit_mb: 512

modules:
  - data_loader
  - statistics_calculator
  - visualization_generator
  - report_builder

tests:
  - test_csv_loading
  - test_statistics_calculation
  - test_report_generation
  - test_performance_constraint

execution:
  entry_point: "src/pipelines/data_analysis_pipeline.py"
  bash_command: "python src/pipelines/data_analysis_pipeline.py --config config/input/feature-name-YYYYMMDD.yaml"
```

**Template Location:** `templates/input_config.yaml`

---

### Phase 3: Pseudocode Review

**Purpose:** Design algorithm and logic before writing code

**Process:**
1. AI generates pseudocode from YAML specification
2. Pseudocode saved to `docs/pseudocode/feature-name.md`
3. User reviews logic, algorithm, and approach
4. User approves or requests modifications
5. **No code written until pseudocode approved**

**Pseudocode Template:**
```markdown
# Pseudocode: Data Analysis Pipeline

## Module: DataLoader

```
FUNCTION load_csv(file_path):
  VALIDATE file_path is relative
  CHECK file_size <= 100MB
  TRY:
    data = read_csv(file_path)
    RETURN data
  CATCH error:
    LOG error
    RAISE DataLoadError
```

## Module: StatisticsCalculator

```
FUNCTION calculate_statistics(data):
  statistics = {}
  statistics['mean'] = CALCULATE_MEAN(data)
  statistics['median'] = CALCULATE_MEDIAN(data)
  statistics['std'] = CALCULATE_STD(data)
  statistics['quantiles'] = CALCULATE_QUANTILES(data, [0.25, 0.5, 0.75])
  RETURN statistics
```

## Integration Flow

```
MAIN FUNCTION run_pipeline(config_file):
  1. LOAD configuration FROM config_file
  2. data = DataLoader.load_csv(config.input.path)
  3. stats = StatisticsCalculator.calculate_statistics(data)
  4. report = ReportBuilder.generate_html(data, stats, config.output)
  5. IF config.output.export_json:
       EXPORT stats TO json_file
  6. RETURN report_path
```

## Error Handling

```
- File not found → Raise FileNotFoundError
- File too large → Raise FileSizeError
- Invalid CSV format → Raise ValidationError
- Timeout exceeded → Raise TimeoutError
```

## Performance Optimization

```
- Use chunking for large files
- Lazy loading for visualization
- Cache intermediate results
- Parallel processing where applicable
```
```

**User Review Checklist:**
- [ ] Algorithm logic is correct
- [ ] Edge cases are handled
- [ ] Performance considerations addressed
- [ ] Error handling is comprehensive
- [ ] Module organization is appropriate

---

### Phase 4: Test-Driven Development (TDD)

**Purpose:** Write tests before implementation to ensure quality

**Process:**
1. Write failing tests based on pseudocode
2. Tests stored in `tests/`
3. Run tests to confirm they fail
4. Implement code to make tests pass
5. Refactor while keeping tests green
6. All tests executed via bash scripts

**TDD Cycle:**
```
1. RED   → Write failing test
2. GREEN → Write minimal code to pass
3. REFACTOR → Improve code quality
4. REPEAT
```

**Test Structure:**
```bash
tests/
├── unit/
│   ├── test_data_loader.py
│   ├── test_statistics_calculator.py
│   └── test_report_builder.py
├── integration/
│   └── test_pipeline_integration.py
├── performance/
│   └── test_performance_constraints.py
└── run_tests.sh
```

**Bash Test Runner:**
```bash
#!/bin/bash
# tests/run_tests.sh

echo "Running TDD test suite..."

# Unit tests
echo "Unit tests..."
pytest tests/unit/ -v

# Integration tests
echo "Integration tests..."
pytest tests/integration/ -v

# Performance tests
echo "Performance tests..."
pytest tests/performance/ -v --durations=10

# Coverage report
echo "Coverage report..."
pytest --cov=src --cov-report=html --cov-report=term

echo "All tests completed."
```

---

### Phase 5: Code Implementation

**Purpose:** Implement code following TDD and pseudocode

**Process:**
1. Create modules in `src/` directory
2. Follow pseudocode design exactly
3. Keep tests passing at all times
4. Code reviews via gate-pass system
5. Integrate into appropriate module structure

**Code Organization:**
```
src/
├── modules/
│   ├── data_loader/
│   │   ├── __init__.py
│   │   ├── csv_loader.py
│   │   └── validators.py
│   ├── statistics/
│   │   ├── __init__.py
│   │   ├── calculator.py
│   │   └── aggregators.py
│   └── visualization/
│       ├── __init__.py
│       ├── plotly_generator.py
│       └── html_builder.py
├── pipelines/
│   └── data_analysis_pipeline.py
└── utils/
    ├── config_loader.py
    └── error_handlers.py
```

**Module Template:**
```python
# src/modules/data_loader/csv_loader.py
"""
ABOUTME: CSV file loading and validation module
ABOUTME: Handles CSV import with size and format validation
"""

import pandas as pd
from pathlib import Path
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)


class CSVLoader:
    """Load and validate CSV files."""

    def __init__(self, max_size_mb: int = 100):
        """
        Initialize CSV loader.

        Args:
            max_size_mb: Maximum file size in megabytes
        """
        self.max_size_mb = max_size_mb

    def load(self, file_path: str) -> pd.DataFrame:
        """
        Load CSV file with validation.

        Args:
            file_path: Relative path to CSV file

        Returns:
            DataFrame with loaded data

        Raises:
            FileNotFoundError: File doesn't exist
            FileSizeError: File exceeds size limit
            ValidationError: Invalid CSV format
        """
        # Implementation following pseudocode
        path = Path(file_path)

        # Validation
        if not path.exists():
            raise FileNotFoundError(f"CSV file not found: {file_path}")

        if path.stat().st_size > self.max_size_mb * 1024 * 1024:
            raise FileSizeError(f"File exceeds {self.max_size_mb}MB limit")

        # Load data
        try:
            data = pd.read_csv(path)
            logger.info(f"Loaded CSV: {file_path} ({len(data)} rows)")
            return data
        except Exception as e:
            logger.error(f"Failed to load CSV: {e}")
            raise ValidationError(f"Invalid CSV format: {e}")
```

---

### Phase 6: Bash-Based Execution

**Purpose:** Execute all operations via bash for efficiency and simplicity

**Process:**
1. All features exposed via bash commands
2. YAML input file drives execution
3. No complex tool chains - direct execution
4. Shortest path from input to output

**Execution Script:**
```bash
#!/bin/bash
# scripts/run_pipeline.sh

set -e

CONFIG_FILE="$1"
OUTPUT_DIR="${2:-./reports}"

if [ -z "$CONFIG_FILE" ]; then
    echo "Usage: ./scripts/run_pipeline.sh <config.yaml> [output_dir]"
    exit 1
fi

echo "Running data analysis pipeline..."
echo "Config: $CONFIG_FILE"
echo "Output: $OUTPUT_DIR"

# Direct execution - shortest route
python src/pipelines/data_analysis_pipeline.py \
    --config "$CONFIG_FILE" \
    --output "$OUTPUT_DIR" \
    --verbose

echo "Pipeline completed successfully!"
echo "Report: $OUTPUT_DIR/report.html"
```

**Usage:**
```bash
# Single command execution
./scripts/run_pipeline.sh config/input/feature-name.yaml

# With custom output
./scripts/run_pipeline.sh config/input/feature-name.yaml ./custom_output

# Run tests
./tests/run_tests.sh

# Full workflow
./scripts/workflow.sh config/input/feature-name.yaml
```

---

## Complete Workflow Example

### Step-by-Step Process

**1. User Creates Requirement**
```bash
# User edits user_prompt.md
vim user_prompt.md
```

**2. Generate YAML Configuration**
```bash
# AI generates YAML from user_prompt.md
./scripts/generate_config.sh user_prompt.md > config/input/my-feature.yaml

# User reviews YAML
vim config/input/my-feature.yaml
```

**3. Generate and Review Pseudocode**
```bash
# AI generates pseudocode from YAML
./scripts/generate_pseudocode.sh config/input/my-feature.yaml > docs/pseudocode/my-feature.md

# User reviews pseudocode
vim docs/pseudocode/my-feature.md

# User approves
echo "approved" > docs/pseudocode/my-feature.approved
```

**4. TDD Implementation**
```bash
# Write failing tests
vim tests/unit/test_my_feature.py

# Run tests (should fail)
./tests/run_tests.sh

# Implement code
vim src/modules/my_feature/implementation.py

# Run tests (should pass)
./tests/run_tests.sh

# Refactor and keep tests green
./tests/run_tests.sh --watch
```

**5. Integration**
```bash
# Integrate into codebase
git add src/modules/my_feature/
git add tests/unit/test_my_feature.py

# Run full test suite
./tests/run_tests.sh --all

# Execute feature
./scripts/run_feature.sh config/input/my-feature.yaml
```

---

## Automation Script

**Full Workflow Automation:**
```bash
#!/bin/bash
# scripts/workflow.sh - Complete development workflow automation

set -e

USER_PROMPT="user_prompt.md"
FEATURE_NAME="$1"

if [ -z "$FEATURE_NAME" ]; then
    echo "Usage: ./scripts/workflow.sh <feature-name>"
    exit 1
fi

echo "========================================="
echo "Development Workflow: $FEATURE_NAME"
echo "========================================="
echo ""

# Phase 1: Read user prompt
if [ ! -f "$USER_PROMPT" ]; then
    echo "Error: $USER_PROMPT not found"
    exit 1
fi

# Phase 2: Generate YAML configuration
echo "Phase 2: Generating YAML configuration..."
./scripts/generate_config.sh "$USER_PROMPT" > "config/input/$FEATURE_NAME.yaml"
echo "✓ YAML configuration created"
echo ""

# Phase 3: Generate pseudocode
echo "Phase 3: Generating pseudocode..."
./scripts/generate_pseudocode.sh "config/input/$FEATURE_NAME.yaml" > "docs/pseudocode/$FEATURE_NAME.md"
echo "✓ Pseudocode generated"
echo ""

# Wait for user approval
echo "Please review pseudocode: docs/pseudocode/$FEATURE_NAME.md"
echo "Press ENTER when approved, or Ctrl+C to abort..."
read

# Phase 4-5: TDD implementation (manual)
echo "Phase 4-5: TDD Implementation"
echo "1. Write tests in tests/unit/test_$FEATURE_NAME.py"
echo "2. Implement in src/modules/$FEATURE_NAME/"
echo "3. Run: ./tests/run_tests.sh"
echo ""

# Phase 6: Execution
echo "Phase 6: Execution"
echo "Run: ./scripts/run_feature.sh config/input/$FEATURE_NAME.yaml"
echo ""

echo "Workflow setup complete!"
```

---

## Directory Structure

```
repository/
├── user_prompt.md                    # User requirements (user-edited only)
├── config/
│   └── input/                        # YAML configuration files
│       ├── feature-1.yaml
│       └── feature-2.yaml
├── docs/
│   ├── DEVELOPMENT_WORKFLOW.md       # This document
│   └── pseudocode/                   # Pseudocode for review
│       ├── feature-1.md
│       └── feature-1.approved
├── src/
│   ├── modules/                      # Modular code
│   │   ├── data_loader/
│   │   ├── statistics/
│   │   └── visualization/
│   ├── pipelines/                    # Integration pipelines
│   └── utils/                        # Utilities
├── tests/
│   ├── unit/                         # Unit tests
│   ├── integration/                  # Integration tests
│   ├── performance/                  # Performance tests
│   └── run_tests.sh                  # Bash test runner
├── scripts/
│   ├── workflow.sh                   # Full workflow automation
│   ├── generate_config.sh            # YAML generation
│   ├── generate_pseudocode.sh        # Pseudocode generation
│   ├── run_feature.sh                # Feature execution
│   └── run_pipeline.sh               # Pipeline execution
└── templates/
    ├── user_prompt.md                # User prompt template
    ├── input_config.yaml             # YAML config template
    └── pseudocode.md                 # Pseudocode template
```

---

## Integration with Existing Systems

### Agent OS Integration
- Workflow phases align with SPARC methodology
- Use `.agent-os/specs/` for feature specifications
- Gate-pass reviews at each phase
- Standards from `.agent-os/standards/`

### Factory.ai Integration
- YAML configs used as droid input
- Pseudocode generation via Claude/OpenAI
- TDD implementation assisted by droids
- Bash execution maintained throughout

### AI Orchestration
- Agent selection via `modules/automation/agent_orchestrator.sh`
- Gate-pass reviews via `modules/automation/gate_pass_review.sh`
- Capability registry updated with workflow agents

---

## Best Practices

### User Prompt (user_prompt.md)
- ✅ Clear, specific requirements
- ✅ Constraints and limitations defined
- ✅ Success criteria explicit
- ❌ No implementation details
- ❌ No technical specifications

### YAML Configuration
- ✅ All parameters explicit
- ✅ Nested structure for organization
- ✅ Comments for complex settings
- ✅ Validation schema defined
- ❌ No hardcoded paths
- ❌ No secrets in files

### Pseudocode
- ✅ Language-agnostic
- ✅ Clear logic flow
- ✅ Error handling explicit
- ✅ Performance considerations noted
- ❌ No actual code syntax
- ❌ No implementation details

### TDD
- ✅ Tests written first
- ✅ Small, focused tests
- ✅ One assertion per test
- ✅ Fast execution
- ❌ No mocking real data
- ❌ No skipping failing tests

### Bash Execution
- ✅ Single command entry point
- ✅ YAML input file
- ✅ Error handling
- ✅ Logging and output
- ❌ No complex tool chains
- ❌ No unnecessary dependencies

---

## Quick Reference

### Commands Cheatsheet

```bash
# 1. Create requirement
vim user_prompt.md

# 2. Generate YAML config
./scripts/generate_config.sh user_prompt.md > config/input/my-feature.yaml

# 3. Generate pseudocode
./scripts/generate_pseudocode.sh config/input/my-feature.yaml > docs/pseudocode/my-feature.md

# 4. Write tests (TDD)
vim tests/unit/test_my_feature.py
./tests/run_tests.sh

# 5. Implement code
vim src/modules/my_feature/implementation.py
./tests/run_tests.sh

# 6. Execute
./scripts/run_feature.sh config/input/my-feature.yaml

# Full workflow
./scripts/workflow.sh my-feature
```

---

## Support

- **Workflow Questions:** See this document
- **Agent OS Integration:** `.agent-os/product/`
- **Factory.ai Usage:** `docs/modules/automation/FACTORY_AI_*.md`
- **Testing Standards:** `.agent-os/standards/best-practices.md`

---

**This workflow ensures quality, maintainability, and efficiency across all repositories! 🚀**
