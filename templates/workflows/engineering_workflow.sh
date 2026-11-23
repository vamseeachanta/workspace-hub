#!/bin/bash

# ABOUTME: Development workflow for engineering calculation repositories
# ABOUTME: Orchestrates user_prompt.md → YAML config → pseudocode → TDD → validation

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
MODULE_NAME="$1"
AUTO_MODE=false

if [ -z "$MODULE_NAME" ]; then
    echo "Usage: $0 <module-name> [--auto]"
    echo ""
    echo "Example: $0 structural-beam-analysis"
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
echo -e "${BLUE}Engineering Workflow: $MODULE_NAME${NC}"
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

SPEC_DIR="$SPECS_DIR/$MODULE_NAME"
CONFIG_FILE="$SPEC_DIR/config.yaml"

# Create spec directory
mkdir -p "$SPEC_DIR"

echo -e "${YELLOW}Generating YAML configuration...${NC}"
echo ""

cat > "$CONFIG_FILE" << EOF
module:
  name: $MODULE_NAME
  version: "1.0.0"
  description: "Engineering calculation module: $MODULE_NAME"
  type: engineering_calculation
  engineering_discipline: "structural"  # structural, mechanical, electrical, civil

execution:
  memory_limit_mb: 8192
  timeout_seconds: 3600
  max_retries: 2
  numerical_precision: 1e-6
  max_iterations: 10000

inputs:
  required:
    - name: geometry
      type: object
      description: "Geometric parameters of the structure"
      validation: "validate_geometry"
      units:
        length: "meters"
        area: "square_meters"

    - name: material_properties
      type: object
      description: "Material properties for analysis"
      validation: "validate_materials"
      units:
        stress: "pascals"
        strain: "dimensionless"
        modulus: "pascals"

    - name: loads
      type: array
      description: "Applied loads and boundary conditions"
      validation: "validate_loads"
      units:
        force: "newtons"
        moment: "newton_meters"

  optional:
    - name: analysis_type
      type: string
      default: "linear_static"
      choices: ["linear_static", "nonlinear_static", "modal", "dynamic"]

    - name: mesh_density
      type: string
      default: "medium"
      choices: ["coarse", "medium", "fine", "very_fine"]

    - name: solver_method
      type: string
      default: "direct"
      choices: ["direct", "iterative", "hybrid"]

outputs:
  primary:
    - name: analysis_report
      type: file
      format: html
      path: "reports/{module}/analysis_report.html"

    - name: results_data
      type: file
      format: json
      path: "data/results/{module}/results.json"

    - name: calculations_summary
      type: file
      format: csv
      path: "data/results/{module}/summary.csv"

  secondary:
    - name: stress_plots
      type: directory
      path: "reports/{module}/stress_plots/"

    - name: deformation_plots
      type: directory
      path: "reports/{module}/deformation_plots/"

    - name: validation_report
      type: file
      format: html
      path: "reports/{module}/validation.html"

validation:
  engineering_standards:
    - "AISC 360"
    - "ACI 318"
    - "ASCE 7"

  safety_factors:
    - type: "load_factor"
      value: 1.5

    - type: "resistance_factor"
      value: 0.9

  result_checks:
    - name: "stress_limits"
      condition: "max_stress < yield_strength"
      critical: true

    - name: "deflection_limits"
      condition: "max_deflection < L/360"
      critical: true

    - name: "stability_check"
      condition: "buckling_factor > 1.0"
      critical: true

calculations:
  numerical_methods:
    - "finite_element_method"
    - "matrix_structural_analysis"

  convergence_criteria:
    relative_tolerance: 1e-6
    absolute_tolerance: 1e-9
    max_iterations: 10000

  verification:
    - "hand_calculations"
    - "benchmark_problems"
    - "code_compliance"

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
    calculation_log:
      enabled: true
      path: "logs/{module}_calculations.log"
      level: DEBUG

performance:
  benchmarks:
    - metric: calculation_time
      threshold_seconds: 600
      action_on_exceed: log_warning

    - metric: memory_usage
      threshold_mb: 4096
      action_on_exceed: log_warning

    - metric: convergence_iterations
      threshold: 5000
      action_on_exceed: log_warning

error_handling:
  strategy: fail_fast
  on_error:
    - log_error_with_inputs
    - save_intermediate_results
    - generate_error_report
    - cleanup_resources

quality_assurance:
  peer_review_required: true
  independent_verification: true
  documentation_required: true

units:
  system: "SI"  # SI or Imperial
  length: "meters"
  force: "newtons"
  stress: "pascals"
  temperature: "kelvin"
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
        --spec "$MODULE_NAME" \
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
# Pseudocode Specification - Engineering Calculation Module

## Module Overview

```
MODULE engineering_analysis
  PURPOSE: Perform structural engineering calculations and analysis
  STANDARDS: AISC 360, ACI 318, ASCE 7
  UNITS: SI (meters, newtons, pascals)
  PRECISION: 1e-6 (6 decimal places)
END MODULE
```

## Main Analysis Workflow

```
FUNCTION main_analysis(config_path)
  # 1. Load configuration
  config = load_yaml_config(config_path)
  VALIDATE config AGAINST schema

  # 2. Setup logging
  logger = setup_logging(config.logging)
  calculation_logger = setup_calculation_logger()

  LOG INFO "Starting engineering analysis: {config.module.name}"
  LOG_CALCULATION "Analysis initiated with config: {config_path}"

  # 3. Load inputs
  geometry = load_geometry(config.inputs.geometry)
  materials = load_materials(config.inputs.material_properties)
  loads = load_loads(config.inputs.loads)

  # 4. Validate inputs
  VALIDATE_GEOMETRY(geometry)
  VALIDATE_MATERIALS(materials)
  VALIDATE_LOADS(loads)

  LOG INFO "Input validation completed"

  # 5. Perform calculations
  START_TIMER "analysis"

  results = perform_structural_analysis(
    geometry=geometry,
    materials=materials,
    loads=loads,
    analysis_type=config.inputs.analysis_type,
    solver_method=config.inputs.solver_method
  )

  STOP_TIMER "analysis"
  LOG INFO "Analysis completed in {elapsed_time} seconds"

  # 6. Apply safety factors
  results = apply_safety_factors(results, config.validation.safety_factors)

  # 7. Validate results
  validation_passed = validate_results(results, config.validation.result_checks)

  IF NOT validation_passed THEN
    LOG CRITICAL "Results failed validation checks"
    generate_failure_report(results)
    FAIL_FAST
  END IF

  LOG INFO "Results validation passed"

  # 8. Generate outputs
  generate_analysis_report(results, config.outputs.primary[0].path)
  generate_stress_plots(results, config.outputs.secondary[0].path)
  generate_deformation_plots(results, config.outputs.secondary[1].path)
  generate_validation_report(results, config.outputs.secondary[2].path)

  # 9. Save results
  save_results_json(results, config.outputs.primary[1].path)
  save_summary_csv(results, config.outputs.primary[2].path)

  LOG INFO "Engineering analysis completed successfully"

  RETURN results
END FUNCTION
```

## Structural Analysis

```
FUNCTION perform_structural_analysis(geometry, materials, loads, analysis_type, solver_method)
  LOG INFO "Performing {analysis_type} analysis"

  # 1. Build structural model
  model = build_structural_model(geometry, materials)
  LOG_CALCULATION "Model created with {model.nodes} nodes, {model.elements} elements"

  # 2. Apply boundary conditions
  model = apply_boundary_conditions(model, loads.boundary_conditions)

  # 3. Apply loads
  model = apply_loads(model, loads.forces, loads.moments)

  # 4. Assemble system matrices
  LOG INFO "Assembling stiffness matrix..."
  K = assemble_stiffness_matrix(model)  # Global stiffness matrix
  F = assemble_force_vector(model)      # Global force vector

  LOG_CALCULATION "Matrix dimensions: {K.rows} x {K.cols}"

  # 5. Solve system of equations
  LOG INFO "Solving system using {solver_method} method..."

  IF solver_method == "direct" THEN
    displacements = solve_direct(K, F)
  ELSE IF solver_method == "iterative" THEN
    displacements = solve_iterative(K, F, max_iterations=config.max_iterations)
  ELSE
    displacements = solve_hybrid(K, F)
  END IF

  LOG_CALCULATION "Solution converged: max displacement = {MAX(displacements)}"

  # 6. Calculate stresses and strains
  stresses = calculate_stresses(model, displacements)
  strains = calculate_strains(model, displacements)

  LOG_CALCULATION "Max stress: {MAX(stresses)}, Max strain: {MAX(strains)}"

  # 7. Calculate reactions
  reactions = calculate_reactions(model, K, displacements)

  # 8. Compile results
  results = AnalysisResults(
    displacements=displacements,
    stresses=stresses,
    strains=strains,
    reactions=reactions,
    model=model
  )

  RETURN results
END FUNCTION
```

## Matrix Assembly

```
FUNCTION assemble_stiffness_matrix(model)
  # Initialize global stiffness matrix
  n_dof = model.nodes * 6  # 6 DOF per node (3 translations + 3 rotations)
  K_global = ZEROS(n_dof, n_dof)

  LOG DEBUG "Assembling stiffness matrix: {n_dof} DOF"

  # Loop through elements
  FOR EACH element IN model.elements
    # Get element stiffness matrix in local coordinates
    k_local = calculate_element_stiffness(element)

    # Transform to global coordinates
    T = get_transformation_matrix(element)
    k_global = T^T * k_local * T

    # Get element DOF indices
    dof_indices = get_dof_indices(element.nodes)

    # Add to global matrix
    FOR i IN dof_indices
      FOR j IN dof_indices
        K_global[i][j] += k_global[i][j]
      END FOR
    END FOR

    LOG_CALCULATION "Element {element.id}: stiffness added"
  END FOR

  LOG INFO "Stiffness matrix assembled: {K_global.nonzero_count} non-zero entries"

  RETURN K_global
END FUNCTION
```

## Validation Checks

```
FUNCTION validate_results(results, checks)
  all_passed = TRUE
  failed_checks = []

  LOG INFO "Performing {LENGTH(checks)} validation checks"

  FOR EACH check IN checks
    LOG INFO "Checking: {check.name}"

    passed = evaluate_check(results, check.condition)

    IF NOT passed THEN
      IF check.critical THEN
        LOG CRITICAL "CRITICAL CHECK FAILED: {check.name}"
        all_passed = FALSE
        failed_checks.APPEND(check.name)
      ELSE
        LOG WARNING "Check failed (non-critical): {check.name}"
      END IF
    ELSE
      LOG INFO "Check passed: {check.name}"
    END IF

    LOG_CALCULATION "{check.name}: {passed ? 'PASS' : 'FAIL'}"
  END FOR

  IF NOT all_passed THEN
    LOG ERROR "Failed checks: {JOIN(failed_checks, ', ')}"
  END IF

  RETURN all_passed
END FUNCTION

FUNCTION evaluate_check(results, condition)
  # Parse condition
  # Example: "max_stress < yield_strength"

  IF condition CONTAINS "max_stress < yield_strength" THEN
    max_stress = MAX(results.stresses)
    yield_strength = results.model.material.yield_strength

    LOG_CALCULATION "Stress check: {max_stress} Pa < {yield_strength} Pa"

    RETURN max_stress < yield_strength

  ELSE IF condition CONTAINS "max_deflection < L/360" THEN
    max_deflection = MAX(ABS(results.displacements))
    length = results.model.geometry.length
    limit = length / 360

    LOG_CALCULATION "Deflection check: {max_deflection} m < {limit} m"

    RETURN max_deflection < limit

  ELSE IF condition CONTAINS "buckling_factor > 1.0" THEN
    buckling_factor = calculate_buckling_factor(results)

    LOG_CALCULATION "Buckling check: factor = {buckling_factor}"

    RETURN buckling_factor > 1.0
  END IF
END FUNCTION
```

## Report Generation

```
FUNCTION generate_analysis_report(results, output_path)
  LOG INFO "Generating analysis report"

  html = HTMLDocument()

  # Header
  html.add_title("Structural Analysis Report")
  html.add_metadata({
    "Date": NOW(),
    "Analysis Type": results.analysis_type,
    "Standards": "AISC 360, ACI 318"
  })

  # Executive Summary
  html.add_section("Executive Summary", generate_executive_summary(results))

  # Input Parameters
  html.add_section("Input Parameters", format_inputs(results.model))

  # Analysis Results
  html.add_section("Analysis Results", generate_results_section(results))

  # Interactive Stress Plots (using Plotly)
  html.add_plot("Stress Distribution", create_stress_plot(results))
  html.add_plot("Deformation Shape", create_deformation_plot(results))
  html.add_plot("Reaction Forces", create_reactions_plot(results))

  # Validation Results
  html.add_section("Validation Checks", generate_validation_table(results))

  # Detailed Calculations
  html.add_section("Detailed Calculations", generate_calculations_appendix(results))

  # Write report
  WRITE_FILE(output_path, html.render())

  LOG INFO "Report saved: {output_path}"
END FUNCTION
```

## Testing Requirements

```
TESTS REQUIRED:
  Unit Tests:
    - test_load_geometry()
    - test_validate_materials()
    - test_assemble_stiffness_matrix()
    - test_apply_boundary_conditions()
    - test_solve_direct()
    - test_solve_iterative()
    - test_calculate_stresses()
    - test_evaluate_check()

  Integration Tests:
    - test_end_to_end_simple_beam()
    - test_end_to_end_complex_frame()
    - test_validation_checks_integration()

  Verification Tests (against known solutions):
    - test_cantilever_beam_benchmark()
    - test_simply_supported_beam_benchmark()
    - test_fixed_frame_benchmark()
    - compare_to_commercial_software()
    - verify_hand_calculations()

  Performance Tests:
    - test_large_model_performance()  # 10,000+ elements
    - test_convergence_speed()
    - test_memory_efficiency()

  Numerical Accuracy Tests:
    - test_convergence_tolerance()
    - test_numerical_stability()
    - test_ill_conditioned_matrices()

  Target Coverage: 80%+ (engineering modules require high confidence)

  Required Peer Review:
    - Technical review by licensed engineer
    - Independent verification of results
    - Code review for calculation accuracy
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
        --spec "$MODULE_NAME" \
        --workspace "$REPO_ROOT" \
        submit \
        --phase pseudocode \
        --version "1.0" \
        --approver "$USER" \
        --status APPROVED \
        --changes "Initial pseudocode specification" \
        --comments "Pseudocode includes structural analysis algorithms, validation checks, and engineering standards compliance"
    echo ""
fi

# Phase 5: TDD Implementation Guidance
echo -e "${BLUE}Phase 5: TDD Implementation${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

echo -e "${YELLOW}Implementation Instructions:${NC}"
echo ""
echo -e "${BLUE}1. Create test directory structure:${NC}"
echo -e "   ${YELLOW}mkdir -p tests/{unit,integration,verification,benchmarks}${NC}"
echo ""
echo -e "${BLUE}2. Create module structure:${NC}"
echo -e "   ${YELLOW}mkdir -p src/modules/$MODULE_NAME/{analysis,validation,reporting}${NC}"
echo ""
echo -e "${BLUE}3. Write verification tests (known solutions):${NC}"
echo -e "   ${YELLOW}vim tests/verification/test_benchmark_problems.py${NC}"
echo ""
echo -e "${BLUE}4. Write unit tests:${NC}"
echo -e "   ${YELLOW}vim tests/unit/test_${MODULE_NAME}.py${NC}"
echo ""
echo -e "${BLUE}5. Run tests (should fail):${NC}"
echo -e "   ${YELLOW}pytest tests/ -v${NC}"
echo ""
echo -e "${BLUE}6. Implement structural analysis:${NC}"
echo -e "   ${YELLOW}vim src/modules/$MODULE_NAME/analysis/solver.py${NC}"
echo ""
echo -e "${BLUE}7. Run tests incrementally:${NC}"
echo -e "   ${YELLOW}pytest tests/unit/ -v${NC}"
echo -e "   ${YELLOW}pytest tests/verification/ -v${NC}"
echo ""
echo -e "${BLUE}8. Verify 80%+ coverage:${NC}"
echo -e "   ${YELLOW}pytest --cov=src --cov-report=html --cov-fail-under=80${NC}"
echo ""
echo -e "${BLUE}9. Peer review:${NC}"
echo -e "   ${YELLOW}# Request technical review from licensed engineer${NC}"
echo -e "   ${YELLOW}# Independent verification of results${NC}"
echo ""

wait_for_approval "Press ENTER when implementation is complete..."

# Phase 6: Create execution script
echo -e "${BLUE}Phase 6: Execution Script${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

EXEC_SCRIPT="$SCRIPTS_DIR/run_${MODULE_NAME}.sh"
mkdir -p "$SCRIPTS_DIR"

cat > "$EXEC_SCRIPT" << 'EXECEOF'
#!/bin/bash

# ABOUTME: Execution script for engineering calculation module
# ABOUTME: Runs analysis with YAML configuration and generates reports

set -e

CONFIG_FILE="$1"
OUTPUT_DIR="${2:-./reports}"

if [ -z "$CONFIG_FILE" ]; then
    echo "Usage: $0 <config.yaml> [output_dir]"
    echo ""
    echo "Example:"
    echo "  $0 config/beam_analysis.yaml reports/beam"
    exit 1
fi

if [ ! -f "$CONFIG_FILE" ]; then
    echo "ERROR: Config file not found: $CONFIG_FILE"
    exit 1
fi

echo "========================================="
echo "Engineering Analysis Module"
echo "========================================="
echo "Config: $CONFIG_FILE"
echo "Output: $OUTPUT_DIR"
echo ""

# Validate configuration
echo "Validating configuration..."
python modules/automation/validate_yaml.py "$CONFIG_FILE"

if [ $? -ne 0 ]; then
    echo "ERROR: Configuration validation failed"
    exit 1
fi

echo ""
echo "Running analysis..."

# Execute via Python module
python -m src.modules.MODULE_NAME \
    --config "$CONFIG_FILE" \
    --output "$OUTPUT_DIR" \
    --verbose \
    --log-calculations

EXIT_CODE=$?

if [ $EXIT_CODE -eq 0 ]; then
    echo ""
    echo "========================================="
    echo "Analysis completed successfully!"
    echo "========================================="
    echo ""
    echo "Generated files:"
    echo "  • Analysis Report: $OUTPUT_DIR/analysis_report.html"
    echo "  • Results Data: $OUTPUT_DIR/results.json"
    echo "  • Summary: $OUTPUT_DIR/summary.csv"
    echo "  • Validation Report: $OUTPUT_DIR/validation.html"
    echo ""
    echo "Open report: open $OUTPUT_DIR/analysis_report.html"
else
    echo ""
    echo "========================================="
    echo "Analysis failed with exit code: $EXIT_CODE"
    echo "========================================="
    echo ""
    echo "Check logs for details:"
    echo "  • Error log: logs/MODULE_NAME.log"
    echo "  • Calculation log: logs/MODULE_NAME_calculations.log"
    exit $EXIT_CODE
fi
EXECEOF

# Replace MODULE_NAME placeholder
sed -i "s/MODULE_NAME/$MODULE_NAME/g" "$EXEC_SCRIPT"
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
echo -e "  1. Review implementation in ${YELLOW}src/modules/$MODULE_NAME/${NC}"
echo -e "  2. Verify tests and benchmarks: ${YELLOW}pytest tests/ --cov=src${NC}"
echo -e "  3. Request peer review from licensed engineer"
echo -e "  4. Run analysis: ${YELLOW}$EXEC_SCRIPT $CONFIG_FILE${NC}"
echo -e "  5. Review HTML reports in ${YELLOW}reports/${MODULE_NAME}/${NC}"
echo ""

echo -e "${GREEN}Engineering workflow completed! 🚀${NC}"
