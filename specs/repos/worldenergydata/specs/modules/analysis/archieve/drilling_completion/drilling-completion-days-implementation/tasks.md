# Spec Tasks

These are the tasks to be completed for the spec detailed in @specs/modules/analysis/drilling-completion-days-implementation/spec.md

> Created: 2025-07-30
> Status: Ready for Implementation

## Tasks

- [x] 1. Create YAML Configuration and Test Infrastructure
  - [x] 1.1 Create drilling_completion_days_config.yml with bsee_custom basename
  - [x] 1.2 Configure binary file paths pointing to data/modules/bsee/bin/war
  - [x] 1.3 Create a test 'drilling_completion_days_test.py' same like legacy test , only the input yaml file name will be different ,'tests\modules\bsee\analysis\legacy\drilling_n_completion_days_test.py'.
  - [x] 1.4 Verify configuration loads properly through engine

- [x] 2. Convert to Wrapper Class
  - [x] 2.1 Convert to new wrapper class without modifying code logic in src/worldenergydata/modules/bsee/analysis/custom_scripts/Roy/july/extract_drilling_and_completion_days.py
  - [x] 2.2 Implement router method that integrates with custom router file
  - [x] 2.3 Configure binary file paths from YAML configuration

- [x] 3. Enhance Custom Router Integration
  - [x] 3.1 Add drilling_n_completion_days routing condition to custom_router.py
  - [x] 3.2 Import and instantiate the new framework wrapper class
  - [x] 3.3 Verify routing works with existing custom analysis patterns
  - [x] 3.4 run test to see if output excel file is generated.
