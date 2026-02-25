#!/bin/bash

# ABOUTME: Development workflow for Python data analysis repositories
# ABOUTME: Orchestrates user_prompt.md → YAML config → pseudocode → TDD → execution

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Configuration
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
USER_PROMPT="$REPO_ROOT/.agent-os/user_prompt.md"
USER_PROMPT_CHANGELOG="$REPO_ROOT/.agent-os/user_prompt_changelog.md"
CONFIG_DIR="$REPO_ROOT/config"
PSEUDOCODE_DIR="$REPO_ROOT/.agent-os/pseudocode"
SCRIPTS_DIR="$REPO_ROOT/scripts"
SPECS_DIR="$REPO_ROOT/.agent-os/specs"

# Parse arguments
SPEC_NAME="$1"
AUTO_MODE=false

if [ -z "$SPEC_NAME" ]; then
    echo "Usage: $0 <spec-name> [--auto]"
    echo ""
    echo "Example: $0 marine-structural-analysis"
    echo ""
    echo "Options:"
    echo "  --auto    Skip approval prompts (use with caution)"
    exit 1
fi

if [ "$2" = "--auto" ]; then
    AUTO_MODE=true
fi

# Utility function to wait for approval
wait_for_approval() {
    local message="$1"

    if [ "$AUTO_MODE" = true ]; then
        echo -e "${YELLOW}[AUTO MODE] $message${NC}"
        return 0
    fi

    echo ""
    echo -e "${YELLOW}$message${NC}"
    echo -e "${YELLOW}Press ENTER to continue, or Ctrl+C to abort...${NC}"
    read
}

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Python Analysis Workflow: $SPEC_NAME${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Phase 1: Read user prompt
echo -e "${BLUE}Phase 1: User Requirements${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

if [ ! -f "$USER_PROMPT" ]; then
    echo -e "${RED}✗ $USER_PROMPT not found${NC}"
    echo ""
    echo -e "${YELLOW}Please create user_prompt.md with your requirements.${NC}"
    echo -e "${YELLOW}Location: $USER_PROMPT${NC}"
    exit 1
fi

echo -e "${GREEN}✓ User prompt found: $USER_PROMPT${NC}"
echo ""

# Create changelog if it doesn't exist
if [ ! -f "$USER_PROMPT_CHANGELOG" ]; then
    cat > "$USER_PROMPT_CHANGELOG" << 'EOF'
# User Prompt Changelog

> **Purpose:** Track all changes and updates to requirements
> **Original:** `.agent-os/user_prompt.md` (immutable)

## Changelog Entries

EOF
    echo -e "${GREEN}✓ Created changelog: $USER_PROMPT_CHANGELOG${NC}"
fi

# Phase 2: Generate YAML configuration
echo -e "${BLUE}Phase 2: YAML Configuration${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

SPEC_DIR="$SPECS_DIR/$SPEC_NAME"
CONFIG_FILE="$SPEC_DIR/config.yaml"

# Create spec directory
mkdir -p "$SPEC_DIR"

echo -e "${YELLOW}Generating YAML configuration...${NC}"
echo ""

cat > "$CONFIG_FILE" << EOF
module:
  name: $SPEC_NAME
  version: "1.0.0"
  description: "Data analysis module for $SPEC_NAME"
  type: python_analysis

execution:
  memory_limit_mb: 4096
  timeout_seconds: 1800
  max_retries: 3
  parallel: true
  max_workers: 4

inputs:
  required:
    - name: data_file
      type: string
      description: "Path to input data file (CSV/Excel)"
      validation: "file_exists"

    - name: analysis_type
      type: string
      description: "Type of analysis to perform"
      choices: ["structural", "statistical", "performance", "comparative"]

  optional:
    - name: output_format
      type: string
      default: "html"
      choices: ["html", "pdf", "json", "csv"]

    - name: plot_style
      type: string
      default: "plotly"
      choices: ["plotly", "bokeh", "altair"]

outputs:
  primary:
    - name: analysis_report
      type: file
      format: html
      path: "reports/{module}/analysis_report.html"

    - name: processed_data
      type: file
      format: csv
      path: "data/processed/{module}/processed_data.csv"

  secondary:
    - name: visualizations
      type: directory
      path: "reports/{module}/plots/"

    - name: summary_statistics
      type: file
      format: json
      path: "data/results/{module}/summary_stats.json"

logging:
  level: INFO
  format: "%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s"
  handlers:
    console:
      enabled: true
      level: INFO
    file:
      enabled: true
      path: "logs/{module}.log"
      level: DEBUG
      max_bytes: 10485760
      backup_count: 5

performance:
  benchmarks:
    - metric: execution_time
      threshold_seconds: 300
      action_on_exceed: log_warning

    - metric: memory_usage
      threshold_mb: 2048
      action_on_exceed: log_warning

error_handling:
  strategy: fail_fast
  on_error:
    - log_error
    - save_partial_results
    - cleanup_resources

validation:
  pre_execution:
    - check_input_files_exist
    - validate_config_schema
    - verify_output_directories

  post_execution:
    - verify_output_files_created
    - check_minimum_data_rows
    - validate_report_generated
EOF

echo -e "${GREEN}✓ YAML configuration created: $CONFIG_FILE${NC}"
echo ""

# Validate YAML
if [ -f "$REPO_ROOT/modules/automation/validate_yaml.py" ]; then
    echo -e "${YELLOW}Validating YAML configuration...${NC}"
    if python "$REPO_ROOT/modules/automation/validate_yaml.py" "$CONFIG_FILE"; then
        echo -e "${GREEN}✓ YAML validation passed${NC}"
    else
        echo -e "${RED}✗ YAML validation failed${NC}"
        exit 1
    fi
    echo ""
fi

wait_for_approval "Review YAML configuration and approve to continue"

# Phase 3: Initialize approval tracker
echo -e "${BLUE}Phase 3: Approval Tracking${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

if [ -f "$REPO_ROOT/modules/automation/approval_tracker.py" ]; then
    python "$REPO_ROOT/modules/automation/approval_tracker.py" \
        --spec "$SPEC_NAME" \
        --workspace "$REPO_ROOT" \
        create

    echo ""
fi

# Phase 4: Generate pseudocode
echo -e "${BLUE}Phase 4: Pseudocode Generation${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

PSEUDOCODE_FILE="$SPEC_DIR/pseudocode_v1.0.md"

echo -e "${YELLOW}Generating pseudocode from YAML configuration...${NC}"
echo ""

cat > "$PSEUDOCODE_FILE" << 'PSEUDOEOF'
# Pseudocode Specification

## Module Overview

```
MODULE data_analysis_pipeline
  PURPOSE: Process and analyze data according to configuration
  INPUTS: data_file, analysis_type, output_format
  OUTPUTS: analysis_report, processed_data, visualizations
END MODULE
```

## Main Workflow

```
FUNCTION main(config_path)
  # 1. Load and validate configuration
  config = load_yaml_config(config_path)
  VALIDATE config AGAINST schema
  IF validation_fails THEN
    LOG ERROR "Invalid configuration"
    FAIL_FAST
  END IF

  # 2. Setup logging
  logger = setup_logging(config.logging)
  LOG INFO "Starting analysis pipeline"

  # 3. Pre-execution validation
  FOR EACH validator IN config.validation.pre_execution
    CALL validator()
  END FOR

  # 4. Load and process data
  START_TIMER "data_loading"
  data = load_data(config.inputs.data_file)
  LOG INFO "Loaded {data.rows} rows of data"
  STOP_TIMER "data_loading"

  # 5. Perform analysis
  START_TIMER "analysis"
  results = perform_analysis(data, config.inputs.analysis_type)
  STOP_TIMER "analysis"

  # 6. Generate outputs
  START_TIMER "output_generation"

  # Create reports directory
  ENSURE_DIRECTORY_EXISTS(config.outputs.primary[0].path)

  # Generate HTML report with interactive plots
  report = generate_interactive_report(
    data=results,
    plot_library=config.inputs.plot_style,
    output_path=config.outputs.primary[0].path
  )

  # Save processed data
  SAVE_CSV(results.processed_data, config.outputs.primary[1].path)

  # Save visualizations
  FOR EACH plot IN results.plots
    SAVE_PLOT(plot, config.outputs.secondary[0].path)
  END FOR

  # Generate summary statistics
  stats = calculate_summary_statistics(results)
  SAVE_JSON(stats, config.outputs.secondary[1].path)

  STOP_TIMER "output_generation"

  # 7. Post-execution validation
  FOR EACH validator IN config.validation.post_execution
    CALL validator()
  END FOR

  # 8. Performance logging
  LOG_PERFORMANCE_METRICS()

  LOG INFO "Analysis pipeline completed successfully"
  RETURN success_status
END FUNCTION
```

## Data Loading

```
FUNCTION load_data(file_path)
  LOG DEBUG "Loading data from {file_path}"

  # Detect file format
  format = detect_file_format(file_path)

  IF format == "csv" THEN
    data = read_csv(file_path)
  ELSE IF format == "excel" THEN
    data = read_excel(file_path)
  ELSE
    RAISE ValueError("Unsupported file format: {format}")
  END IF

  # Validate data structure
  VALIDATE data HAS required_columns
  VALIDATE data.rows > 0

  LOG INFO "Loaded {data.rows} rows, {data.columns} columns"
  RETURN data
END FUNCTION
```

## Analysis Functions

```
FUNCTION perform_analysis(data, analysis_type)
  LOG INFO "Performing {analysis_type} analysis"

  CASE analysis_type OF
    "structural":
      results = perform_structural_analysis(data)
    "statistical":
      results = perform_statistical_analysis(data)
    "performance":
      results = perform_performance_analysis(data)
    "comparative":
      results = perform_comparative_analysis(data)
    DEFAULT:
      RAISE ValueError("Unknown analysis type: {analysis_type}")
  END CASE

  RETURN results
END FUNCTION

FUNCTION perform_structural_analysis(data)
  # Initialize results container
  results = new AnalysisResults()

  # Calculate structural metrics
  results.metrics = calculate_structural_metrics(data)

  # Generate visualizations
  results.plots = [
    create_scatter_plot(data),
    create_distribution_plot(data),
    create_correlation_heatmap(data)
  ]

  # Store processed data
  results.processed_data = data.cleaned_and_transformed()

  RETURN results
END FUNCTION
```

## Report Generation

```
FUNCTION generate_interactive_report(data, plot_library, output_path)
  LOG INFO "Generating interactive HTML report"

  # Create HTML structure
  html = HTMLDocument()

  # Add header and metadata
  html.add_header("Analysis Report")
  html.add_metadata(timestamp=NOW(), version="1.0")

  # Add summary section
  html.add_section("Summary", data.summary_text)

  # Add interactive visualizations
  FOR EACH plot IN data.plots
    IF plot_library == "plotly" THEN
      interactive_plot = convert_to_plotly(plot)
    ELSE IF plot_library == "bokeh" THEN
      interactive_plot = convert_to_bokeh(plot)
    ELSE IF plot_library == "altair" THEN
      interactive_plot = convert_to_altair(plot)
    END IF

    html.add_plot(interactive_plot)
  END FOR

  # Add data tables
  html.add_data_table(data.processed_data.head(50))

  # Add CSS styling
  html.add_css(load_report_styles())

  # Write to file
  WRITE_FILE(output_path, html.render())

  LOG INFO "Report saved to {output_path}"
  RETURN output_path
END FUNCTION
```

## Error Handling

```
FUNCTION handle_execution_error(error, config)
  # Log error with full context
  LOG ERROR "Execution failed: {error}" WITH_STACKTRACE

  # Follow error handling strategy
  IF config.error_handling.strategy == "fail_fast" THEN
    # Save partial results if available
    IF partial_results_exist THEN
      SAVE_PARTIAL_RESULTS()
    END IF

    # Cleanup resources
    CLEANUP_RESOURCES()

    # Exit with error code
    EXIT 1
  END IF
END FUNCTION
```

## Performance Monitoring

```
FUNCTION check_performance_thresholds(metrics, config)
  FOR EACH benchmark IN config.performance.benchmarks
    IF benchmark.metric == "execution_time" THEN
      IF metrics.execution_time > benchmark.threshold_seconds THEN
        PERFORM benchmark.action_on_exceed
      END IF
    ELSE IF benchmark.metric == "memory_usage" THEN
      IF metrics.memory_mb > benchmark.threshold_mb THEN
        PERFORM benchmark.action_on_exceed
      END IF
    END IF
  END FOR
END FUNCTION
```

## Test Coverage Requirements

```
TESTS REQUIRED:
  Unit Tests:
    - test_load_data_csv()
    - test_load_data_excel()
    - test_load_data_invalid_format()
    - test_perform_structural_analysis()
    - test_perform_statistical_analysis()
    - test_generate_report()
    - test_handle_missing_data()
    - test_validate_configuration()

  Integration Tests:
    - test_end_to_end_pipeline()
    - test_pipeline_with_real_data()
    - test_error_recovery()

  Performance Tests:
    - test_large_dataset_processing()  # 10,000+ rows
    - test_memory_efficiency()
    - test_execution_time()  # Must complete < 300s

  Target Coverage: 80%+ (aiming for 90%)
END TESTS
```
PSEUDOEOF

echo -e "${GREEN}✓ Pseudocode generated: $PSEUDOCODE_FILE${NC}"
echo ""

wait_for_approval "Review pseudocode and approve to continue"

# Submit for approval
if [ -f "$REPO_ROOT/modules/automation/approval_tracker.py" ]; then
    echo -e "${YELLOW}Recording approval...${NC}"
    python "$REPO_ROOT/modules/automation/approval_tracker.py" \
        --spec "$SPEC_NAME" \
        --workspace "$REPO_ROOT" \
        submit \
        --phase pseudocode \
        --version "1.0" \
        --approver "$USER" \
        --status APPROVED \
        --changes "Initial pseudocode specification" \
        --comments "Pseudocode follows YAML configuration and includes all required components"
    echo ""
fi

# Phase 5: TDD Implementation Guidance
echo -e "${BLUE}Phase 5: TDD Implementation${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

echo -e "${YELLOW}Implementation Instructions:${NC}"
echo ""
echo -e "${BLUE}1. Create test directory structure:${NC}"
echo -e "   ${YELLOW}mkdir -p tests/{unit,integration,performance}${NC}"
echo ""
echo -e "${BLUE}2. Create module structure:${NC}"
echo -e "   ${YELLOW}mkdir -p src/modules/$SPEC_NAME${NC}"
echo -e "   ${YELLOW}touch src/modules/$SPEC_NAME/__init__.py${NC}"
echo -e "   ${YELLOW}touch src/modules/$SPEC_NAME/__main__.py${NC}"
echo ""
echo -e "${BLUE}3. Write tests FIRST (following pseudocode):${NC}"
echo -e "   ${YELLOW}vim tests/unit/test_${SPEC_NAME}.py${NC}"
echo ""
echo -e "${BLUE}4. Run tests (should fail initially):${NC}"
echo -e "   ${YELLOW}pytest tests/unit/ -v${NC}"
echo ""
echo -e "${BLUE}5. Implement code to pass tests:${NC}"
echo -e "   ${YELLOW}vim src/modules/$SPEC_NAME/pipeline.py${NC}"
echo ""
echo -e "${BLUE}6. Run tests again (should pass):${NC}"
echo -e "   ${YELLOW}pytest tests/ --cov=src --cov-report=html${NC}"
echo ""
echo -e "${BLUE}7. Verify 80%+ coverage:${NC}"
echo -e "   ${YELLOW}pytest --cov=src --cov-report=term --cov-fail-under=80${NC}"
echo ""

wait_for_approval "Press ENTER when implementation is complete..."

# Phase 6: Create execution script
echo -e "${BLUE}Phase 6: Execution Script${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

EXEC_SCRIPT="$SCRIPTS_DIR/run_${SPEC_NAME}.sh"
mkdir -p "$SCRIPTS_DIR"

cat > "$EXEC_SCRIPT" << 'EXECEOF'
#!/bin/bash

# ABOUTME: Execution script for data analysis pipeline
# ABOUTME: Runs module with YAML configuration

set -e

CONFIG_FILE="$1"
OUTPUT_DIR="${2:-./reports}"

if [ -z "$CONFIG_FILE" ]; then
    echo "Usage: $0 <config.yaml> [output_dir]"
    echo ""
    echo "Example:"
    echo "  $0 config/marine_analysis.yaml reports/marine"
    exit 1
fi

if [ ! -f "$CONFIG_FILE" ]; then
    echo "ERROR: Config file not found: $CONFIG_FILE"
    exit 1
fi

echo "Running data analysis pipeline..."
echo "Config: $CONFIG_FILE"
echo "Output: $OUTPUT_DIR"
echo ""

# Execute via Python module
python -m src.modules.MODULE_NAME \
    --config "$CONFIG_FILE" \
    --output "$OUTPUT_DIR" \
    --verbose

EXIT_CODE=$?

if [ $EXIT_CODE -eq 0 ]; then
    echo ""
    echo "Pipeline completed successfully!"
    echo "Reports: $OUTPUT_DIR/"
else
    echo ""
    echo "Pipeline failed with exit code: $EXIT_CODE"
    exit $EXIT_CODE
fi
EXECEOF

# Replace MODULE_NAME placeholder
sed -i "s/MODULE_NAME/$SPEC_NAME/g" "$EXEC_SCRIPT"
chmod +x "$EXEC_SCRIPT"

echo -e "${GREEN}✓ Execution script created: $EXEC_SCRIPT${NC}"
echo ""

# Final summary
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Workflow Complete!${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

echo -e "${GREEN}✓ All phases completed successfully${NC}"
echo ""

echo -e "${BLUE}Created Files:${NC}"
echo -e "  • User Prompt: ${YELLOW}$USER_PROMPT${NC}"
echo -e "  • Changelog: ${YELLOW}$USER_PROMPT_CHANGELOG${NC}"
echo -e "  • YAML Config: ${YELLOW}$CONFIG_FILE${NC}"
echo -e "  • Pseudocode: ${YELLOW}$PSEUDOCODE_FILE${NC}"
echo -e "  • Execution Script: ${YELLOW}$EXEC_SCRIPT${NC}"
if [ -f "$SPEC_DIR/approval_log.md" ]; then
    echo -e "  • Approval Log: ${YELLOW}$SPEC_DIR/approval_log.md${NC}"
fi
echo ""

echo -e "${BLUE}Next Steps:${NC}"
echo -e "  1. Verify tests in ${YELLOW}tests/${NC}"
echo -e "  2. Run execution script:"
echo -e "     ${YELLOW}$EXEC_SCRIPT $CONFIG_FILE${NC}"
echo -e "  3. Review HTML report in ${YELLOW}reports/${SPEC_NAME}/${NC}"
echo ""

echo -e "${GREEN}Python analysis workflow completed! 🚀${NC}"
