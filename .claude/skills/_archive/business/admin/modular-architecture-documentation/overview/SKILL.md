---
name: modular-architecture-documentation-overview
description: 'Sub-skill of modular-architecture-documentation: Overview (+6).'
version: 1.0.0
category: business
type: reference
scripts_exempt: true
---

# Overview (+6)

## Overview


Following DEC-003 (Modular Architecture Decision, 2025-07-27), the system is organized into three independent modules to support gradual feature adoption and independent development cycles.

## Module Structure


**Module 1: Invoice Automation**
- **Purpose:** Automated invoice generation and delivery
- **Scope:** Template processing, data merging, PDF generation, email delivery
- **Entry Point:** `aceengineer_admin.invoice:main`
- **CLI Command:** `invoice-gen`
- **Dependencies:** python-docx, jinja2, plotly (invoice charts)
- **Output:** PDF invoices in /reports/invoices/
- **Adoption Phase:** Phase 1 (Weeks 1-2) - 80% time savings

**Module 2: Tax Preparation**

*See sub-skills for full details.*

## Module Independence


Each module:
- Can be used independently (invoice-gen works without tax-prep)
- Has its own CLI command
- Produces standalone outputs
- Has dedicated configuration section
- Has independent test suite

## Gradual Adoption Path


**Phase 1:** Invoice Automation (Weeks 1-2)
- Immediate 80% time savings on monthly billing
- No dependency on other modules

**Phase 2:** Tax Preparation (Weeks 3-4)
- Eliminate manual expense categorization
- Can be adopted without invoice automation

**Phase 3:** Tax Filing (Weeks 5-8)
- Streamlined annual compliance
- Works with tax prep module or standalone

Users can adopt modules in any order based on business priorities.

## CLI Commands


```bash
# Module 1: Invoice Automation
invoice-gen --client ACMA --month 2025-01 --template monthly
invoice-gen --all-clients --month 2025-01 --email

# Module 2: Tax Preparation
tax-prep --year 2024 --type federal
tax-prep --year 2024 --expense-report --validate

# Module 3: Tax Filing
tax-file --year 2024 --form 1120
tax-file --year 2024 --form k1 --shareholder all
```

## Directory Organization


```
src/aceengineer_admin/
├── invoice/           # Module 1: Invoice Automation
│   ├── __init__.py
│   ├── __main__.py    # CLI entry point
│   ├── generator.py   # Invoice generation logic
│   ├── templates.py   # Template processing
│   └── config.py      # Invoice config
├── tax_prep/          # Module 2: Tax Preparation
│   ├── __init__.py

*See sub-skills for full details.*

## Testing Strategy


- **Unit Tests:** 80% coverage minimum per module, 95% for critical modules
- **Integration Tests:** Cross-module workflows (tax prep → tax filing)
- **CLI Tests:** Command-line interface validation
- **Independence Tests:** Each module testable in isolation with mocks
```

**decisions.md:**
```markdown
