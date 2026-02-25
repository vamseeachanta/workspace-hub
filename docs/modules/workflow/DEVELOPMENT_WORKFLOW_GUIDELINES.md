# Development Workflow Guidelines

> **Workspace Hub** - Centralized Multi-Repository Development Standards
>
> Version: 1.0.0
> Last Updated: 2025-10-22
> Applies to: All 26 repositories in workspace-hub

## Overview

This document defines the mandatory development workflow for all repositories in workspace-hub. Each repository maintains its own domain and style based on mission and objectives, but all follow these consistent guidelines driven by workspace-hub standards.

## Table of Contents

1. [User Prompt Management](#user-prompt-management)
2. [YAML Configuration](#yaml-configuration)
3. [Pseudocode Review Process](#pseudocode-review-process)
4. [Test-Driven Development](#test-driven-development)
5. [Execution System](#execution-system)
6. [Logging Framework](#logging-framework)
7. [Multi-Repository Consistency](#multi-repository-consistency)
8. [Repository Structure](#repository-structure)
9. [Workflow Phases](#workflow-phases)

---

## 1. User Prompt Management

### File Structure

```
.agent-os/
├── user_prompt.md              # Single immutable file - NEVER MODIFIED
├── user_prompt_changelog.md    # Tracks all requirement changes
└── specs/
    └── [spec-name]/
        ├── spec.md
        ├── changelog.md
        └── sub-specs/
```

### Rules

**USER_PROMPT.MD**
- **Status:** Immutable - never updated after creation
- **Purpose:** Original user requirements and specifications
- **Location:** `.agent-os/user_prompt.md`
- **Format:** Markdown with clear sections

**CHANGELOG MECHANISM**
- **File:** `.agent-os/user_prompt_changelog.md`
- **Required:** Yes
- **Updates:** Document all requirement changes with:
  - Date (YYYY-MM-DD)
  - Change description
  - Reason for change
  - Impact assessment
  - Approval status

### Changelog Template

```markdown
# User Prompt Changelog

## [YYYY-MM-DD] - Change Description

**Category:** [Feature|Bugfix|Architecture|Requirements]
**Impact:** [High|Medium|Low]
**Status:** [Proposed|Approved|Implemented]

### Original Requirement
[Quote from user_prompt.md]

### Changed Requirement
[New requirement details]

### Rationale
[Why this change was needed]

### Affected Components
- Component 1
- Component 2

### Approval
- **Approver:** [Name]
- **Date:** [YYYY-MM-DD]
- **Notes:** [Additional context]
```

---

## 2. YAML Configuration

### Configuration Level

**REQUIREMENT:** Comprehensive YAML configurations

All modules MUST include:
- Input parameters
- Output specifications
- Execution parameters (memory limits, timeouts, resource requirements)
- Logging configuration
- Error handling strategies
- Performance thresholds

### YAML Structure

```yaml
# Module Configuration Template
module:
  name: module-name
  version: "1.0.0"
  description: "Comprehensive module description"

execution:
  memory_limit_mb: 2048
  timeout_seconds: 300
  max_retries: 3
  parallel: true
  max_workers: 4

inputs:
  required:
    - name: input_file
      type: string
      description: "Input data file path"
      validation: "file_exists"
    - name: threshold
      type: float
      description: "Analysis threshold"
      validation: "range(0, 1)"

  optional:
    - name: output_format
      type: string
      default: "csv"
      choices: ["csv", "json", "parquet"]

outputs:
  primary:
    - name: results
      type: dataframe
      format: "csv"
      path: "results/{{module}}_{{timestamp}}.csv"

  secondary:
    - name: logs
      type: text
      path: "logs/{{module}}_{{timestamp}}.log"

logging:
  level: DEBUG  # DEBUG, INFO, WARNING, ERROR, CRITICAL
  format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
  handlers:
    - console: true
    - file: "logs/{{module}}.log"
    - rotating_file:
        max_bytes: 10485760  # 10MB
        backup_count: 5

performance:
  benchmarks:
    - metric: execution_time
      threshold_seconds: 60
      action_on_exceed: log_warning
    - metric: memory_usage
      threshold_mb: 1024
      action_on_exceed: raise_error

error_handling:
  strategy: fail_fast  # fail_fast, continue_with_warnings, retry
  on_error:
    - log_error
    - save_partial_results
    - notify_user

validation:
  pre_execution:
    - check_inputs_exist
    - validate_parameter_ranges
    - verify_resource_availability
  post_execution:
    - verify_outputs_created
    - validate_result_integrity
    - check_performance_thresholds
```

### YAML Validation

**REQUIREMENT:** Validate YAML before proceeding to pseudocode

**Validation Rules:**
1. Schema validation against JSON Schema
2. Required fields present
3. Type checking
4. Range validation
5. File path existence
6. Dependency verification

**Validation Script Location:**
- `modules/automation/validate_yaml.py`
- Integrated into workflow as pre-execution hook

---

## 3. Pseudocode Review Process

### Approval Recording

**METHOD:** Approval log file system

**Location:** `.agent-os/specs/[spec-name]/approval_log.md`

**Format:**
```markdown
# Approval Log - [Spec Name]

## Pseudocode Version 1.0
- **Date:** 2025-10-22
- **Approver:** [Name]
- **Status:** APPROVED
- **Notes:** Initial pseudocode approved

## Pseudocode Version 1.1
- **Date:** 2025-10-23
- **Approver:** [Name]
- **Status:** APPROVED
- **Changes:** Updated algorithm for edge cases
- **Requires Re-Testing:** Yes
```

### Pseudocode Change Process

**REQUIREMENT:** Changes require re-approval

**Workflow:**
1. Developer proposes changes to pseudocode
2. Generate diff/comparison report
3. Submit for approval
4. Upon approval, update version number
5. Log approval in approval_log.md
6. Proceed with implementation

### Diff/Comparison Tool

**REQUIREMENT:** Yes

**Tool:** `modules/automation/pseudocode_diff.py`

**Features:**
- Side-by-side comparison
- Highlighted changes
- Impact analysis
- Affected components identification
- Test coverage impact assessment

**Usage:**
```bash
python modules/automation/pseudocode_diff.py \
  --original .agent-os/specs/feature-x/pseudocode_v1.0.md \
  --updated .agent-os/specs/feature-x/pseudocode_v1.1.md \
  --output .agent-os/specs/feature-x/diff_report_v1.0_to_v1.1.html
```

---

## 4. Test-Driven Development (TDD)

### Test Framework Selection

**REQUIREMENT:** Choose appropriate framework for language/domain

**Frameworks by Language:**
- **Python:** pytest (default), unittest (legacy)
- **JavaScript/TypeScript:** Jest, Mocha, Vitest
- **Bash:** bats-core
- **Ruby:** RSpec

**Selection Criteria:**
- Ecosystem compatibility
- Team familiarity
- Feature requirements (mocking, async, parallel execution)

### Test Coverage Requirements

**MINIMUM:** 80%

**TARGET:** 90%+

**Measurement:**
- Line coverage
- Branch coverage
- Function coverage
- Integration coverage

**Tools:**
- Python: pytest-cov, coverage.py
- JavaScript: Istanbul, c8
- Reports: HTML + JSON formats

### Performance Tests

**REQUIREMENT:** Run on every commit

**Test Types:**
1. **Unit Performance Tests**
   - Individual function execution time
   - Memory usage per function
   - Resource utilization

2. **Integration Performance Tests**
   - End-to-end workflow timing
   - Throughput measurements
   - Scalability tests

3. **Regression Tests**
   - Compare against baseline
   - Alert on >10% degradation
   - Auto-fail on >25% degradation

**Configuration:**
```yaml
performance_tests:
  enabled: true
  run_frequency: on_commit

  benchmarks:
    - name: data_processing
      baseline_seconds: 5.0
      warning_threshold_percent: 110  # 10% slower
      fail_threshold_percent: 125     # 25% slower

  reporting:
    generate_charts: true
    compare_to_baseline: true
    save_history: true
    history_retention_days: 90
```

---

## 5. Execution System

### Entry Point Structure

**REQUIREMENT:** YML file + Python run args (digitalmodel repo pattern)

**Architecture:**
```
module/
├── config/
│   ├── module_config.yml       # Comprehensive configuration
│   └── execution_profiles/
│       ├── development.yml
│       ├── testing.yml
│       └── production.yml
├── src/
│   └── module_name/
│       ├── __main__.py         # Entry point with argparse
│       ├── __init__.py
│       └── core.py
└── tests/
    └── test_module.py
```

### Execution Methods

**Method 1: Direct Module Execution**
```bash
python -m module_name --config config/module_config.yml --profile development
```

**Method 2: CLI Script**
```bash
./scripts/run_module.sh --module module_name --config config.yml
```

**Method 3: YAML-Driven Batch Execution**
```bash
python -m automation.batch_runner --batch-config configs/batch_execution.yml
```

### Python Argument Parser Template

```python
# __main__.py
import argparse
import yaml
import logging
from pathlib import Path

def main():
    parser = argparse.ArgumentParser(
        description="Module execution with YAML configuration"
    )

    # Required arguments
    parser.add_argument(
        "--config",
        type=Path,
        required=True,
        help="Path to YAML configuration file"
    )

    # Optional arguments
    parser.add_argument(
        "--profile",
        type=str,
        choices=["development", "testing", "production"],
        default="development",
        help="Execution profile"
    )

    parser.add_argument(
        "--log-level",
        type=str,
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        default="INFO",
        help="Logging level (overrides config)"
    )

    parser.add_argument(
        "--output-dir",
        type=Path,
        help="Output directory (overrides config)"
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate configuration without execution"
    )

    args = parser.parse_args()

    # Load and validate configuration
    config = load_and_validate_config(args.config, args.profile)

    # Setup logging
    setup_logging(
        level=args.log_level or config.get("logging", {}).get("level"),
        config=config
    )

    # Execute module
    if args.dry_run:
        validate_execution_plan(config)
    else:
        execute_module(config, args)

if __name__ == "__main__":
    main()
```

### Error Handling Strategy

**REQUIREMENT:** Fail fast

**Implementation:**
1. **Validation Failures:** Immediate exit with code 1
2. **Runtime Errors:** No automatic recovery, log and exit
3. **Resource Issues:** Detect early, fail before processing
4. **Data Issues:** Validate inputs, fail on corruption

**Error Exit Codes:**
```python
EXIT_CODES = {
    0: "SUCCESS",
    1: "VALIDATION_ERROR",
    2: "CONFIGURATION_ERROR",
    3: "INPUT_ERROR",
    4: "EXECUTION_ERROR",
    5: "OUTPUT_ERROR",
    6: "RESOURCE_ERROR",
    7: "TIMEOUT_ERROR"
}
```

---

## 6. Logging Framework

### Logging Levels

**REQUIREMENT:** Support all levels (DEBUG, INFO, WARNING, ERROR, CRITICAL)

**Usage Guidelines:**

| Level | Use Case | Examples |
|-------|----------|----------|
| DEBUG | Development, troubleshooting | Variable values, function entry/exit, detailed state |
| INFO | Normal operation, key events | Process start/end, major milestones, configuration loaded |
| WARNING | Unexpected but handled situations | Deprecated features, recoverable errors, performance issues |
| ERROR | Errors requiring intervention | Failed operations, invalid data, exceptions |
| CRITICAL | System failure, immediate action | Unrecoverable errors, data corruption, service down |

### Logging Configuration

```yaml
logging:
  version: 1
  disable_existing_loggers: false

  formatters:
    standard:
      format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
      datefmt: "%Y-%m-%d %H:%M:%S"

    detailed:
      format: "%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(funcName)s() - %(message)s"

    json:
      format: '{"timestamp": "%(asctime)s", "name": "%(name)s", "level": "%(levelname)s", "message": "%(message)s"}'

  handlers:
    console:
      class: logging.StreamHandler
      level: INFO
      formatter: standard
      stream: ext://sys.stdout

    file:
      class: logging.handlers.RotatingFileHandler
      level: DEBUG
      formatter: detailed
      filename: logs/module.log
      maxBytes: 10485760  # 10MB
      backupCount: 5
      encoding: utf-8

    error_file:
      class: logging.handlers.RotatingFileHandler
      level: ERROR
      formatter: detailed
      filename: logs/errors.log
      maxBytes: 10485760
      backupCount: 10

  loggers:
    module_name:
      level: DEBUG
      handlers: [console, file, error_file]
      propagate: false

  root:
    level: INFO
    handlers: [console, file]
```

### Structured Logging

**REQUIREMENT:** Use structured logging for automated analysis

```python
import structlog

logger = structlog.get_logger()

# Structured log with context
logger.info(
    "data_processing_complete",
    module="data_analysis",
    records_processed=1000,
    execution_time_seconds=5.2,
    memory_usage_mb=128,
    status="success"
)
```

---

## 7. Multi-Repository Consistency

### Workflow Application

**REQUIREMENT:** Identical workflow across all 26 repositories, adapted per repo type

**Repository Types:**
1. **Python Analysis:** Data analysis, scientific computing, engineering calculations
2. **Web Applications:** React, Node.js, full-stack applications
3. **Engineering:** Specialized engineering calculations and simulations

### Adaptation Guidelines

**Common Elements (All Repos):**
- User prompt management (immutable user_prompt.md + changelog)
- YAML configuration standards
- Approval log system
- TDD requirements (80%+ coverage)
- Fail-fast error handling
- Multi-level logging

**Type-Specific Adaptations:**

| Element | Python Analysis | Web App | Engineering |
|---------|----------------|---------|-------------|
| Test Framework | pytest | Jest/Vitest | pytest |
| Entry Point | `__main__.py` + CLI | npm scripts | `__main__.py` |
| Config Format | YAML | JSON/YAML | YAML |
| Performance Tests | Data processing speed | API response time | Calculation accuracy |
| Dependencies | requirements.txt, uv | package.json | requirements.txt, conda env |

### Shared Configuration Management

**REQUIREMENT:** Each repo has own configs, style maintained by workspace-hub guidelines

**Structure:**
```
workspace-hub/
├── docs/
│   ├── DEVELOPMENT_WORKFLOW_GUIDELINES.md  # This document
│   ├── YAML_SCHEMA_STANDARDS.md
│   ├── TESTING_STANDARDS.md
│   └── LOGGING_STANDARDS.md
└── templates/
    ├── python_analysis/
    │   ├── config_template.yml
    │   ├── __main__template.py
    │   └── test_template.py
    ├── web_app/
    │   ├── config_template.json
    │   ├── jest.config.js
    │   └── test_template.ts
    └── engineering/
        ├── config_template.yml
        ├── __main__template.py
        └── test_template.py
```

**Config Propagation:**
```bash
# Update all repos with latest standards
./modules/automation/propagate_standards.sh --type python_analysis --repos all

# Update specific repo
./modules/automation/propagate_standards.sh --repo worldenergydata --dry-run
```

---

## 8. Repository Structure

### Standard Directory Layout

```
repository/
├── .agent-os/
│   ├── user_prompt.md               # Immutable original requirements
│   ├── user_prompt_changelog.md     # Requirement change tracking
│   ├── product/
│   │   ├── mission.md
│   │   ├── tech-stack.md
│   │   ├── roadmap.md
│   │   └── decisions.md
│   └── specs/
│       └── [spec-name]/
│           ├── spec.md
│           ├── approval_log.md
│           ├── changelog.md
│           ├── pseudocode.md
│           └── sub-specs/
├── src/
│   └── module_name/
│       ├── __init__.py
│       ├── __main__.py
│       ├── core.py
│       └── config/
│           ├── default.yml
│           └── profiles/
├── tests/
│   ├── unit/
│   ├── integration/
│   └── performance/
├── docs/
│   ├── user_guide.md
│   ├── api_documentation.md
│   └── architecture.md
├── scripts/
│   ├── run_module.sh
│   └── validate_config.py
├── data/
│   ├── raw/
│   ├── processed/
│   └── results/
├── logs/
│   └── .gitkeep
├── reports/
│   └── .gitkeep
└── config/
    └── execution_profiles/
```

---

## 9. Workflow Phases

### Phase 1: Specification

**Inputs:**
- `user_prompt.md` (immutable)
- Stakeholder requirements
- Business context

**Outputs:**
- `.agent-os/specs/[spec-name]/spec.md`
- Initial YAML configuration
- Approval log initialized

**Activities:**
1. Create immutable user_prompt.md
2. Document requirements in spec.md
3. Create comprehensive YAML configuration
4. Validate YAML schema
5. Initialize approval log

### Phase 2: Pseudocode

**Inputs:**
- Approved specification
- YAML configuration

**Outputs:**
- `pseudocode.md`
- Algorithm design
- Data flow diagrams

**Activities:**
1. Design algorithms
2. Document pseudocode
3. Create approval log entry
4. Get approval before proceeding

### Phase 3: Architecture

**Inputs:**
- Approved pseudocode
- Technical constraints

**Outputs:**
- Architecture documentation
- Component diagrams
- Interface specifications

**Activities:**
1. Design system architecture
2. Define components and interfaces
3. Document in spec sub-specs
4. Update YAML with architecture details

### Phase 4: Refinement (TDD Implementation)

**Inputs:**
- Approved architecture
- YAML configuration
- Pseudocode

**Outputs:**
- Implemented code
- Passing tests (80%+ coverage)
- Performance benchmarks

**TDD Workflow:**
```bash
# 1. Write failing tests
pytest tests/test_module.py  # Should fail

# 2. Implement minimum code to pass
# Edit src/module_name/core.py

# 3. Run tests
pytest tests/test_module.py  # Should pass

# 4. Refactor while keeping tests green
# Improve code quality

# 5. Run full test suite + performance tests
pytest tests/ --cov --cov-report=html
pytest tests/performance/

# 6. Verify coverage ≥ 80%
# 7. Commit with tests passing
```

### Phase 5: Completion

**Inputs:**
- Implemented and tested code
- Documentation

**Outputs:**
- Production-ready code
- Complete documentation
- Deployment artifacts

**Activities:**
1. Final integration testing
2. Documentation review
3. Performance validation
4. Security audit
5. Deployment preparation

---

## 10. Approval Workflow

### Approval Levels

| Phase | Approver | Required Artifacts |
|-------|----------|-------------------|
| Specification | Product Owner | spec.md, YAML config |
| Pseudocode | Technical Lead | pseudocode.md, approval_log.md |
| Architecture | Architect | architecture docs, component designs |
| Implementation | Code Reviewer | Code + tests (80%+ coverage) |
| Deployment | DevOps Lead | Deployment checklist, performance benchmarks |

### Approval Log Entry Template

```markdown
## [Phase Name] - Version X.Y
**Date:** YYYY-MM-DD HH:MM:SS
**Approver:** [Name/Role]
**Status:** [PROPOSED|APPROVED|REJECTED|NEEDS_REVISION]

### Changes from Previous Version
- Change 1
- Change 2

### Review Comments
[Detailed feedback]

### Conditions/Requirements
- Condition 1
- Condition 2

### Approval Decision
[APPROVED|REJECTED|NEEDS_REVISION]

**Signature:** [Digital signature or approval commit SHA]
```

---

## 11. Quality Gates

### Pre-Commit Checks

**Mandatory Checks:**
1. ✅ YAML validation passes
2. ✅ All tests pass
3. ✅ Code coverage ≥ 80%
4. ✅ No linting errors
5. ✅ No security vulnerabilities
6. ✅ Performance benchmarks within thresholds
7. ✅ Documentation updated

**Implementation:**
```bash
# .git/hooks/pre-commit
#!/bin/bash

echo "Running pre-commit checks..."

# 1. YAML validation
python modules/automation/validate_yaml.py config/*.yml || exit 1

# 2. Run tests
pytest tests/ --cov --cov-fail-under=80 || exit 1

# 3. Lint
flake8 src/ || exit 1
black --check src/ || exit 1

# 4. Security scan
bandit -r src/ || exit 1

# 5. Performance tests
pytest tests/performance/ || exit 1

echo "✅ All pre-commit checks passed"
```

### Continuous Integration

**CI Pipeline Stages:**
```yaml
# .github/workflows/ci.yml
stages:
  - validate:
      - yaml_validation
      - schema_validation

  - test:
      - unit_tests
      - integration_tests
      - performance_tests
      - coverage_report (minimum 80%)

  - quality:
      - linting
      - security_scan
      - code_complexity_analysis

  - deploy:
      - build_artifacts
      - deploy_to_staging
      - smoke_tests
```

---

## 12. Templates and Tools

### Available Templates

**Location:** `/mnt/github/workspace-hub/templates/`

1. **Module Configuration:** `config_template.yml`
2. **Python Entry Point:** `__main__template.py`
3. **Test Template:** `test_template.py`
4. **Approval Log:** `approval_log_template.md`
5. **Changelog:** `changelog_template.md`
6. **Pseudocode:** `pseudocode_template.md`

### Automation Tools

**Location:** `/mnt/github/workspace-hub/modules/automation/`

| Tool | Purpose | Usage |
|------|---------|-------|
| `validate_yaml.py` | YAML schema validation | `python validate_yaml.py config.yml` |
| `pseudocode_diff.py` | Generate pseudocode diffs | `python pseudocode_diff.py v1.md v2.md` |
| `approval_tracker.py` | Track approval status | `python approval_tracker.py --spec feature-x` |
| `coverage_enforcer.py` | Enforce test coverage | `python coverage_enforcer.py --min 80` |
| `propagate_standards.sh` | Update repo standards | `./propagate_standards.sh --repo name` |

---

## 13. Example Workflow

### Complete Feature Development Example

```bash
# Step 1: Create specification
cd .agent-os/specs/
mkdir new-feature
cd new-feature/

# Create immutable user prompt
cat > ../../user_prompt.md << EOF
# User Requirements
[Requirements details - NEVER MODIFIED]
EOF

# Create spec
cat > spec.md << EOF
# Feature Specification
[Detailed specification]
EOF

# Step 2: Create YAML configuration
cat > config.yml << EOF
module:
  name: new-feature
execution:
  memory_limit_mb: 2048
  timeout_seconds: 300
# ... (comprehensive config)
EOF

# Step 3: Validate YAML
python /mnt/github/workspace-hub/modules/automation/validate_yaml.py config.yml

# Step 4: Write pseudocode
cat > pseudocode.md << EOF
# Pseudocode - New Feature
[Algorithm design]
EOF

# Step 5: Request approval
python /mnt/github/workspace-hub/modules/automation/approval_tracker.py \
  --spec new-feature \
  --phase pseudocode \
  --submit

# Step 6: After approval, implement with TDD
cd ../../../

# Write failing test
cat > tests/test_new_feature.py << EOF
def test_new_feature():
    result = new_feature_function()
    assert result == expected_value
EOF

# Run test (should fail)
pytest tests/test_new_feature.py

# Implement feature
# Edit src/module/new_feature.py

# Run test (should pass)
pytest tests/test_new_feature.py

# Run full test suite with coverage
pytest tests/ --cov --cov-report=html --cov-fail-under=80

# Step 7: Run performance tests
pytest tests/performance/test_new_feature_performance.py

# Step 8: Update changelog
cat >> .agent-os/user_prompt_changelog.md << EOF
## [2025-10-22] - New Feature Implementation
**Status:** Implemented
**Coverage:** 85%
**Performance:** Within thresholds
EOF

# Step 9: Commit
git add .
git commit -m "feat: implement new feature with 85% test coverage"
```

---

## 14. Compliance Checklist

Before deployment, verify:

- [ ] user_prompt.md exists and is immutable
- [ ] user_prompt_changelog.md documents all changes
- [ ] YAML configuration is comprehensive and validated
- [ ] Execution parameters (memory, timeout) are specified
- [ ] Approval log has all required entries
- [ ] Pseudocode changes are documented and re-approved
- [ ] Test coverage ≥ 80%
- [ ] Performance tests run on every commit
- [ ] All tests pass
- [ ] Fail-fast error handling implemented
- [ ] Multi-level logging (DEBUG, INFO, WARNING, ERROR, CRITICAL) configured
- [ ] Repository follows workspace-hub guidelines
- [ ] Documentation is complete and up-to-date

---

## 15. Support and Resources

**Documentation:**
- This Guide: `/mnt/github/workspace-hub/docs/workflow/DEVELOPMENT_WORKFLOW_GUIDELINES.md`
- YAML Standards: `/mnt/github/workspace-hub/docs/YAML_SCHEMA_STANDARDS.md`
- Testing Standards: `/mnt/github/workspace-hub/docs/TESTING_STANDARDS.md`
- Logging Standards: `/mnt/github/workspace-hub/docs/LOGGING_STANDARDS.md`

**Templates:**
- `/mnt/github/workspace-hub/templates/`

**Tools:**
- `/mnt/github/workspace-hub/modules/automation/`

**Reference Implementation:**
- `/mnt/github/workspace-hub/digitalmodel/` (Python analysis repository example)

**Questions or Issues:**
- Create issue in workspace-hub repository
- Contact technical lead
- Review workspace-hub mission and roadmap

---

**This document is maintained by the workspace-hub technical team and applies to all 26 repositories. Each repository adapts these guidelines to its specific domain while maintaining consistency across the workspace.**

**Last Review:** 2025-10-22
**Next Review:** 2025-11-22
**Version:** 1.0.0
