# Marketing Materials Generation System

## Overview

This directory contains a **generic, reusable system** for generating professional marketing brochures for repository modules. The system is designed to work across multiple repositories (worldenergydata, digitalmodel, and others) using YAML-based configuration.

## System Architecture

```
specs/modules/marketing/
├── README.md                              # This file
├── master_spec.md                         # Generic template specification (repo-agnostic)
├── marketing_config_schema.yaml           # Configuration schema/template
├── worldenergydata_marketing_config.yaml  # WorldEnergyData-specific config
└── [future configs for other repos]       # Add more as needed
```

## Quick Start

### 1. Review the Configuration

The WorldEnergyData configuration is ready to use:

```yaml
# File: worldenergydata_marketing_config.yaml
repository:
  name: "WorldEnergyData"
  description: "Comprehensive Python data library for energy assets..."

statistics:
  module_count: 4
  python_files: 816
  test_count: 258
  test_functions: 2777
  years_experience: 3
```

### 2. Generate Brochures

The configuration defines modules in tiers:

**Tier 1 (Core):**
- BSEE Data Integration
- Marine Safety Incident Analysis
- Wind Energy Data Integration

**Tier 2 (Advanced):**
- Economic Evaluation (NPV Analysis)
- Field-Specific Analysis
- Well Production Dashboard

**Tier 3 (Integration):**
- Web Scraping Infrastructure
- FDAS (Field Data Analysis System)

### 3. Target Audiences

All brochures target:
- Energy data analysts and researchers
- Energy consultants
- Petroleum engineers
- Financial analysts (NPV/economic modeling)

## Repository Statistics

Current worldenergydata metrics (auto-discovered):

- **816** Python files
- **258** test files
- **2,777** individual test functions
- **63** CSV data files
- **3** years of development (started Dec 2022)
- **4** main modules with comprehensive capabilities

## Key Features

### 1. **Repository-Agnostic Design**

The same `master_spec.md` works for any repository by using template variables:

```markdown
# {{MODULE_NAME}}
## {{MODULE_TAGLINE}}

### About {{REPO_NAME}}
{{REPO_DESCRIPTION}}

**Repository Highlights:**
- {{YEARS_EXPERIENCE}} years of development
- {{MODULE_COUNT}} comprehensive modules
- {{TEST_COUNT}} rigorous tests
```

### 2. **Flexible Target Audiences**

Configure multiple audiences with different technical levels:

```yaml
audiences:
  primary:
    - name: "Energy Data Analysts"
      technical_level: "Analyst/Researcher"
    - name: "Petroleum Engineers"
      technical_level: "Engineer"
```

### 3. **Module Tier Organization**

Prioritize brochure creation by organizing modules into tiers:

- **Tier 1**: Core capabilities (highest priority)
- **Tier 2**: Advanced features
- **Tier 3**: Integration tools
- **Tier 4**: Experimental/emerging

### 4. **Standards Emphasis Flexibility**

Different repos emphasize different things:

**WorldEnergyData:**
```yaml
standards_emphasis:
  type: "data_sources"
  primary_focus: "Single source of truth for public energy data"
  items:
    - name: "BSEE"
    - name: "SODIR"
    - name: "Public Databases"
```

**DigitalModel** (example):
```yaml
standards_emphasis:
  type: "compliance_standards"
  primary_focus: "Industry standards compliance"
  items:
    - name: "DNV-RP-C203"
    - name: "API RP 2A"
    - name: "ISO 19901"
```

## Usage for WorldEnergyData

### Step 1: Review Configuration

```bash
# Review worldenergydata-specific config
cat worldenergydata_marketing_config.yaml
```

### Step 2: Generate Brochures (Future)

```bash
# When automation is implemented
python generate_brochures.py --config worldenergydata_marketing_config.yaml --module "BSEE Data Integration"
```

### Step 3: Review and Approve

1. Review generated markdown
2. Validate technical accuracy
3. Generate PDF
4. Final approval

## Usage for Other Repositories

### To Use with DigitalModel or Another Repo:

1. **Copy the schema:**
   ```bash
   cp marketing_config_schema.yaml digitalmodel_marketing_config.yaml
   ```

2. **Customize for your repo:**
   ```yaml
   repository:
     name: "DigitalModel"
     description: "Engineering asset lifecycle management..."

   statistics:
     module_count: 15  # Update with actual count
     python_files: 704
     # ... etc

   modules:
     tier_1_core:
       - name: "Fatigue Analysis"
         path: "src/digitalmodel/modules/fatigue"
         # ... etc
   ```

3. **Generate brochures** using the same master_spec.md template

## Configuration Guide

### Required Sections

1. **repository** - Name, description, URLs
2. **audiences** - Target audience definitions
3. **statistics** - Repo metrics (auto-discoverable)
4. **standards_emphasis** - What to highlight
5. **modules** - Organized by tier
6. **contact** - Contact information

### Customizable Elements

- Industry focus (Energy vs. Engineering vs. Other)
- Technical level per audience
- Module capabilities and priorities
- Branding (colors, fonts, logos)
- Output formats and tools

## File Naming Convention

Generated files follow this pattern:

- **Markdown:** `marketing_brochure_<module_name>.md`
- **PDF:** `marketing_brochure_<module_name>.pdf`
- **Location:** `reports/modules/marketing/`

## Automation Workflow (Planned)

```python
# Pseudocode for future automation
config = load_yaml("worldenergydata_marketing_config.yaml")

for module in config['modules']['tier_1_core']:
    # Extract capabilities from module code
    capabilities = analyze_module(module['path'])

    # Generate brochure with template
    brochure = generate_brochure(
        module=module,
        template="master_spec.md",
        config=config
    )

    # Generate PDF
    generate_pdf(brochure, pandoc_template)
```

## Benefits of This Approach

### ✅ Reusability
- Same template works across all repos
- Consistent branding and structure
- Reduce duplication of effort

### ✅ Maintainability
- Single master spec to update
- YAML configs are easy to modify
- Clear separation of content and presentation

### ✅ Scalability
- Add new repos easily
- Add new modules with minimal effort
- Batch generate multiple brochures

### ✅ Flexibility
- Customize per repository
- Multiple target audiences
- Configurable technical levels

## Next Steps

1. **Review configurations** - Validate worldenergydata_marketing_config.yaml
2. **Implement generator** - Build Python script to automate brochure generation
3. **Generate first brochure** - Start with "BSEE Data Integration" module
4. **Create templates** - Design pandoc PDF templates
5. **Batch generate** - Create all tier 1 module brochures

## Questions or Issues?

Contact: vamsee.achanta@aceengineer.com

## Version History

- **v1.0.0** (2025-01-23) - Initial generic template system
  - Created master_spec.md as repo-agnostic template
  - Created marketing_config_schema.yaml
  - Created worldenergydata_marketing_config.yaml with repository statistics
  - Documented 4 main modules across 3 tiers
  - Configured for 4 target audience types
