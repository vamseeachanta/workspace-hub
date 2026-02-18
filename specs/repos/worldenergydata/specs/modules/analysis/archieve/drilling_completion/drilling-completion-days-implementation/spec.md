# Spec Requirements Document

> Spec: Drilling and Completion Days Integration
> Created: 2025-07-30
> Status: Planning

## User Prompt

> This spec was initiated based on the following user request:

```
I need to create a spec for implementing drilling and completion days functionality into the worldenergydata codebase. 

**Spec Description:**
Convert the plain script "extract_drilling_and_completion_days.py" into a proper class-based implementation that integrates with the worldenergydata framework. The implementation should:

1. Convert the existing plain script into a class-based structure
2. Use pickle .bin files instead of CSV files from "data\modules\bsee\bin\war" path
3. Keep the lease input file "tests\modules\bsee\analysis\leases.csv" intact
4. Create a condition in "src\worldenergydata\modules\bsee\custom_router.py"
5. Create test file and YAML configuration in "tests\modules\bsee\analysis" folder
6. Use basename "bsee_custom" in the YAML configuration for the engine
7. Generate output .xlsx file format without errors

**Technical Requirements:**
- The plain script currently processes BSEE WAR data to calculate drilling and completion days for wells
- It loads lease data, processes various WAR data files, and outputs an Excel file with drilling/completion analysis
- The class implementation should maintain all existing functionality while integrating with the framework's architecture
- Must use the existing engine workflow pattern with YAML configuration

**Expected Output:**
- Excel file containing drilling and completion days analysis by API well number
- Integration with existing test framework
- Proper router configuration for the custom workflow
```

## Overview

Integrate the existing drilling and completion days analysis script into the worldenergydata framework by converting the plain script into class-based implementation into a properly integrated custom router workflow that processes BSEE WAR data using pickle binary files and produces Excel analysis output.

## User Stories

### Framework Integration Story

As an energy data analyst, I want to run drilling and completion days analysis through the standard worldenergydata engine workflow, so that I can leverage the framework's configuration management, logging, and file handling capabilities.

The analyst configures a YAML file with lease data input and WAR binary file paths, runs the analysis through the engine, and receives standardized logging output and organized results in the configured output directory.

### Binary Data Processing Story

As a developer maintaining the codebase, I want the analysis to use pickle binary files from the established data directory structure, so that processing is faster and data formats are consistent with the framework standards.

The system reads WAR data from `data\modules\bsee\bin\war` pickle files (main, prop, remarks, boreholes) instead of CSV files, maintaining the same analysis logic but with improved performance and consistency.

### Custom Router Configuration Story

As a system administrator, I want the drilling days analysis to be configurable through the custom router system, so that multiple analysis types can be managed through a single entry point.

The custom router checks for a `drilling_n_completion_days` flag in the configuration and routes to the appropriate analysis class, enabling extensible custom analysis capabilities.

## Spec Scope

1. **Custom Router Enhancement** - Add drilling and completion days routing logic to the existing CustomRouter class
2. **Configuration Integration** - Create YAML configuration files that work with the engine's basename "bsee_custom" routing
3. **Binary File Processing** - Modify existing class to use pickle .bin files from the standard data directory structure
4. **Test Framework Integration** - Create comprehensive test files following the established testing patterns
5. **Excel Output Generation** - Ensure error-free Excel file output with drilling and completion days analysis by API

## Out of Scope

- Modification of the core drilling and completion days calculation logic
- Changes to the existing lease input file format or location
- Integration with other analysis types beyond drilling and completion days
- Database storage of results (output remains file-based)

## Expected Deliverable

1. Converted class script with router method and other functionality
2. Enhanced CustomRouter class with drilling days routing capability
3. YAML configuration file for testing and production use
4. Test file that validates the complete workflow from configuration to Excel output
5. Excel file output containing accurate drilling and completion days analysis by API well number

## Spec Documentation

- Tasks: @specs/modules/analysis/drilling-completion-days-implementation/tasks.md
- Technical Specification: @specs/modules/analysis/drilling-completion-days-implementation/sub-specs/technical-spec.md
- Tests Specification: @specs/modules/analysis/drilling-completion-days-implementation/sub-specs/tests.md