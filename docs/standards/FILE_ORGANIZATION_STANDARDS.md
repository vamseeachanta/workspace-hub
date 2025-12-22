# File Organization Standards

> **Purpose**: Define consistent file and folder organization across all 26 repositories
> **AI Responsibility**: AI proposes folder structure, waits for approval before creating
> **Last Updated**: 2025-10-23

## Overview

All repositories follow a **consistent, module-based structure** where AI is responsible for organizing files into appropriate subfolders after the basic structure is established.

## Basic Structure (Human-Defined)

### Top-Level Directories

Every repository MUST have these top-level directories:

```
repository/
├── src/                    # Source code
├── tests/                  # Test files
├── docs/                   # Documentation
├── config/                 # Configuration files
├── scripts/                # Utility scripts
├── examples/               # Example code/data
├── data/                   # Data files
│   ├── raw/               # Raw input data
│   ├── processed/         # Processed data
│   └── results/           # Output results
├── reports/               # Generated reports (HTML, PDF)
├── logs/                  # Log files (gitignored)
└── .agent-os/            # Agent OS workflow files
    ├── specs/            # Specifications
    └── product/          # Product documentation
```

### Module-Based Structure (src/)

Source code follows **domain/module organization**:

```
src/
├── modules/              # Business/domain modules
│   ├── module_name_1/   # First module (domain-driven)
│   │   ├── __init__.py
│   │   ├── core.py      # Core functionality
│   │   ├── utils.py     # Module-specific utilities
│   │   └── config.py    # Module configuration
│   ├── module_name_2/
│   └── shared/          # Shared utilities across modules
├── base_configs/        # Base configuration templates
├── common/              # Common functionality (if needed)
└── __init__.py
```

## AI Folder Organization Responsibility

### When AI Takes Over

**After basic structure is established**, AI is responsible for:

1. **Creating subfolders** as files accumulate
2. **Organizing existing files** into logical groups
3. **Proposing structure changes** when needed
4. **Maintaining consistency** across repositories

### AI Workflow

**Step 1: Recognize Need**
```
Trigger: When 5+ files exist in a single directory without clear organization
Action: AI identifies need for subfolder organization
```

**Step 2: Propose Structure**
```
AI Message: "I notice we have multiple [file_type] files. I propose this structure:

module_name/
├── analysis/          # Analysis-related files
├── visualization/     # Plotting and charts
├── validation/        # Validation and checks
└── io/               # Input/output operations

Should I proceed with this organization?"
```

**Step 3: Wait for Approval**
```
User responds: "Yes" or "No" or suggests alternative
AI only proceeds after explicit approval
```

**Step 4: Execute Organization**
```
AI actions:
1. Create proposed subdirectories
2. Move files to appropriate locations
3. Update imports/references in code
4. Update documentation
5. Commit with clear message
```

### Naming Conventions

#### Module/Domain-Driven (Top Level)

Use **domain names** that reflect business/technical purpose:

**Good examples:**
- `marine_analysis/` (domain: marine engineering)
- `structural_analysis/` (domain: structural engineering)
- `data_processing/` (domain: data operations)
- `authentication/` (domain: user auth)
- `reporting/` (domain: report generation)

**Bad examples:**
- `python_files/` (technical, not domain)
- `new_module/` (temporal context)
- `utils/` (too generic for top level)
- `misc/` (unclear purpose)

#### Subfolder Names (Functional)

Within modules, use **functional names** that describe what files do:

**Good examples:**
```
marine_analysis/
├── loads/              # Load calculations
├── stress/             # Stress analysis
├── buckling/           # Buckling checks
├── fatigue/            # Fatigue analysis
└── validation/         # Result validation
```

**Bad examples:**
```
marine_analysis/
├── files/              # Too generic
├── stuff/              # Meaningless
├── temp/               # Suggests temporary
└── old/                # Temporal context
```

## Folder Depth Limits

**Maximum depth: 5 levels**

```
src/                           # Level 1
└── modules/                   # Level 2
    └── marine_analysis/       # Level 3
        └── stress/            # Level 4
            └── components/    # Level 5 (MAX)
```

**If you need more depth:**
1. Re-evaluate module boundaries
2. Consider splitting into separate modules
3. Use flatter structure with clear naming

## Organization Patterns by File Type

### Python Modules

```
module_name/
├── __init__.py              # Module initialization
├── __main__.py              # CLI entry point
├── core/                    # Core functionality
│   ├── __init__.py
│   ├── calculator.py
│   └── processor.py
├── models/                  # Data models
│   ├── __init__.py
│   └── schema.py
├── utils/                   # Module-specific utilities
│   ├── __init__.py
│   └── helpers.py
├── validation/              # Input validation
│   ├── __init__.py
│   └── validators.py
└── io/                      # Input/output
    ├── __init__.py
    ├── readers.py
    └── writers.py
```

### Test Organization

Mirror source structure:

```
tests/
├── unit/                    # Unit tests
│   └── modules/
│       └── marine_analysis/
│           ├── test_core.py
│           ├── test_stress.py
│           └── test_buckling.py
├── integration/             # Integration tests
│   └── test_pipeline.py
├── verification/            # Verification tests
│   └── test_benchmarks.py
├── fixtures/                # Test fixtures/data
│   └── sample_data.csv
└── conftest.py             # Pytest configuration
```

### Documentation Organization

```
docs/
├── api/                     # API documentation
│   └── marine_analysis.md
├── tutorials/               # Step-by-step guides
│   └── getting_started.md
├── guides/                  # How-to guides
│   └── stress_analysis.md
├── reference/               # Reference material
│   └── standards.md
├── development/             # Development docs
│   └── contributing.md
└── images/                  # Images and diagrams
    └── architecture.png
```

### Configuration Organization

```
config/
├── base/                    # Base configurations
│   ├── logging.yaml
│   └── defaults.yaml
├── modules/                 # Module-specific configs
│   └── marine_analysis/
│       └── config.yaml
├── environments/            # Environment-specific
│   ├── development.yaml
│   ├── staging.yaml
│   └── production.yaml
└── schemas/                 # JSON schemas
    └── module_config_schema.json
```

### Data Organization

```
data/
├── raw/                     # Original, immutable data
│   ├── input_data_v1.csv
│   └── reference_data.csv
├── processed/               # Cleaned, transformed data
│   ├── cleaned_data.csv
│   └── normalized_data.csv
├── results/                 # Analysis outputs
│   ├── stress_results.csv
│   └── summary_stats.csv
└── external/               # External data sources
    └── api_data.json
```

## AI Decision-Making Process

### When to Create Subfolders

**Create subfolders when:**
1. **5+ files** of similar type exist in same directory
2. **Logical grouping** emerges (analysis, validation, etc.)
3. **Module complexity** requires separation
4. **Code duplication** suggests shared functionality
5. **Import paths** become unwieldy

**Example trigger:**
```
Before (needs organization):
src/modules/marine_analysis/
├── stress_calc.py
├── stress_validate.py
├── stress_report.py
├── buckling_calc.py
├── buckling_validate.py
└── buckling_report.py

AI recognizes: Pattern of calc/validate/report for each analysis type
AI proposes: Subfolder structure by analysis type
```

### Proposed Structure Examples

**Example 1: Analysis Module**
```
AI: "I notice 12 files related to structural analysis. I propose:

marine_analysis/
├── stress/              # Stress analysis (4 files)
├── buckling/            # Buckling analysis (4 files)
├── fatigue/             # Fatigue analysis (4 files)
└── shared/              # Shared utilities

Each subfolder will contain:
- calculations.py
- validation.py
- reporting.py

Should I proceed?"
```

**Example 2: Web Application**
```
AI: "The src/ directory has 15 files. I propose:

src/
├── routes/              # API routes (5 files)
├── models/              # Data models (4 files)
├── services/            # Business logic (3 files)
├── middleware/          # Middleware (2 files)
└── utils/               # Utilities (1 file)

Should I organize this way?"
```

**Example 3: Data Pipeline**
```
AI: "The pipeline has grown to 10 files. I suggest:

data_pipeline/
├── ingestion/           # Data ingestion
├── transformation/      # Data transformation
├── validation/          # Quality checks
├── storage/             # Data storage
└── monitoring/          # Pipeline monitoring

Should I create this structure?"
```

## Consistency Rules

### Across All Repositories

1. **Same top-level structure** - All repos use same base directories
2. **Same naming patterns** - Domain-driven → functional → specific
3. **Same depth limits** - Maximum 5 levels
4. **Same organization triggers** - 5+ files → propose organization
5. **Same approval workflow** - Always wait for user confirmation

### Module-Specific Variations

While structure is consistent, **content varies by domain**:

```
Marine Engineering Repo:
src/modules/
├── hull_analysis/
├── stability/
└── propulsion/

Web Application Repo:
src/modules/
├── authentication/
├── user_management/
└── api_gateway/

Data Science Repo:
src/modules/
├── data_cleaning/
├── feature_engineering/
└── modeling/
```

## Migration Strategy

### For Existing Disorganized Repos

**Phase 1: Assessment**
```
AI: "I've analyzed the repository structure. Current state:
- 47 files in src/ (no organization)
- 23 test files in tests/ (no structure)
- Documentation mixed with code

I propose a 3-phase reorganization:

Phase 1: Create base structure
Phase 2: Organize by domain (3 main modules identified)
Phase 3: Create functional subfolders within modules

Should I proceed with Phase 1?"
```

**Phase 2: Incremental Organization**
```
AI: "Phase 1 complete. For Phase 2, I identified these domains:
1. Marine Analysis (15 files)
2. Data Processing (12 files)
3. Reporting (8 files)

Should I organize files into these modules?"
```

**Phase 3: Subfolder Creation**
```
AI: "Within 'Marine Analysis', I see patterns:
- Stress-related files (5)
- Buckling-related files (4)
- Fatigue-related files (3)

Should I create stress/, buckling/, fatigue/ subfolders?"
```

## File Moving Guidelines

### When AI Moves Files

**Always:**
1. **Update imports** in moved files
2. **Update imports** in files that reference moved files
3. **Update documentation** with new paths
4. **Update tests** to reflect new structure
5. **Commit with clear message** explaining moves

**Never:**
1. Move files without updating imports
2. Break existing functionality
3. Move without testing
4. Create orphaned files

### Import Update Examples

**Before move:**
```python
# src/modules/marine_analysis/stress_calculator.py
from validation import validate_input
from utils import format_output
```

**After move to subfolders:**
```python
# src/modules/marine_analysis/stress/calculator.py
from ..validation.validators import validate_input
from ..utils.formatters import format_output
```

### Commit Message Pattern

```
Organize [module_name] into functional subfolders

Created structure:
- [subfolder1]/ - [purpose]
- [subfolder2]/ - [purpose]
- [subfolder3]/ - [purpose]

Changes:
- Moved [N] files to appropriate subfolders
- Updated [M] import statements
- Updated documentation references
- All tests passing

Rationale: [Brief explanation of why organization was needed]
```

## Examples from Real Projects

### Example 1: Marine Structural Analysis

**Before (flat structure):**
```
src/modules/marine_analysis/
├── calculate_stress.py
├── validate_stress.py
├── report_stress.py
├── calculate_buckling.py
├── validate_buckling.py
├── report_buckling.py
├── calculate_fatigue.py
├── validate_fatigue.py
├── report_fatigue.py
├── load_data.py
├── save_results.py
└── utilities.py
```

**After (organized by analysis type):**
```
src/modules/marine_analysis/
├── stress/
│   ├── calculations.py
│   ├── validation.py
│   └── reporting.py
├── buckling/
│   ├── calculations.py
│   ├── validation.py
│   └── reporting.py
├── fatigue/
│   ├── calculations.py
│   ├── validation.py
│   └── reporting.py
├── io/
│   ├── data_loader.py
│   └── result_saver.py
└── utils/
    └── helpers.py
```

### Example 2: Web API

**Before:**
```
src/
├── app.py
├── user_routes.py
├── product_routes.py
├── order_routes.py
├── user_model.py
├── product_model.py
├── order_model.py
├── auth_middleware.py
├── logging_middleware.py
├── validation.py
└── database.py
```

**After:**
```
src/
├── app.py
├── routes/
│   ├── users.py
│   ├── products.py
│   └── orders.py
├── models/
│   ├── user.py
│   ├── product.py
│   └── order.py
├── middleware/
│   ├── auth.py
│   └── logging.py
└── core/
    ├── validation.py
    └── database.py
```

## Anti-Patterns to Avoid

### ❌ Don't Create These

**Overly Generic Names:**
```
src/
├── stuff/
├── misc/
├── other/
└── files/
```

**Technical Instead of Domain:**
```
src/
├── python_files/
├── yaml_configs/
└── json_data/
```

**Temporal Context:**
```
src/
├── old/
├── new/
├── legacy/
└── v2/
```

**Too Deep:**
```
src/
└── modules/
    └── analysis/
        └── structural/
            └── marine/
                └── stress/
                    └── calculations/  # 7 levels - too deep!
```

## Tools and Automation

### File Organization Helper Script

```bash
# scripts/organize_files.sh
# AI can use this to analyze and propose organization

#!/bin/bash
# Analyzes repository structure and suggests organization
find src/ -type f -name "*.py" | awk -F/ '{print NF-1, $0}' | sort -n
```

### Import Update Script

```bash
# scripts/update_imports.sh
# After moving files, update imports automatically

#!/bin/bash
# Updates imports after file moves
# Usage: ./update_imports.sh old_path new_path
```

## Checklist for AI

Before proposing folder organization:

- [ ] Identified 5+ files that could be grouped
- [ ] Recognized clear pattern or domain
- [ ] Verified folder depth won't exceed 5 levels
- [ ] Prepared clear proposal with rationale
- [ ] Ready to update all imports/references
- [ ] Ready to update documentation
- [ ] Have test plan to verify nothing breaks

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2025-10-23 | Initial file organization standards |

## Related Documentation

- `CLAUDE.md` - Core configuration with file organization rules
- `DEVELOPMENT_WORKFLOW_GUIDELINES.md` - Workflow integration
- `INTERACTIVE_MODE_GUIDELINES.md` - Question-asking patterns

---

**Remember**: Good organization emerges naturally. Wait until patterns are clear, then propose structure that reflects actual usage.
