---
name: modular-architecture-documentation-1-module-definition-framework
description: 'Sub-skill of modular-architecture-documentation: 1. Module Definition
  Framework (+9).'
version: 1.0.0
category: business
type: reference
scripts_exempt: true
---

# 1. Module Definition Framework (+9)

## 1. Module Definition Framework


**Module Documentation Template:**
```markdown

## Modular Design


Following [DEC-XXX], the system is organized into [N] independent modules:

**Module 1: [Module Name]**
- **Purpose:** [What this module does]
- **Scope:** [What's included in this module]
- **Entry Point:** [Python module path]
- **CLI Command:** `[command-name]`
- **Dependencies:** [External packages specific to this module]
- **Output:** [What this module produces]


*See sub-skills for full details.*

## Modular Design


Following DEC-003 (Modular Architecture, 2025-07-27), the system is organized into three independent modules:

**Module 1: Invoice Automation**
- **Purpose:** Automated invoice generation and delivery
- **Scope:** Template processing, data merging, PDF generation, email delivery
- **Entry Point:** `aceengineer_admin.invoice:main`
- **CLI Command:** `invoice-gen`
- **Dependencies:** python-docx, jinja2, plotly (for invoice charts)
- **Output:** PDF invoices in /reports/invoices/


*See sub-skills for full details.*

## 2. CLI Command Documentation


**CLI Command Documentation Template:**
```markdown

## CLI Interface


Each module provides a dedicated CLI command configured in pyproject.toml:

**Module 1 Commands:**
```bash
[command-name] [subcommand] [options]

# Basic usage
[command-name] --required-arg VALUE

# Common operations

*See sub-skills for full details.*

## CLI Interface


Each module provides a dedicated CLI command configured in pyproject.toml:

**Invoice Automation Commands:**
```bash
invoice-gen [options]

# Generate invoice for single client
invoice-gen --client ACMA --month 2025-01 --template monthly

# Generate invoices for all clients

*See sub-skills for full details.*

## 3. pyproject.toml Entry Points


**Entry Points Configuration:**
```toml
[project.scripts]
# Module 1
module1-command = "package.module1:main"

# Module 2
module2-command = "package.module2:main"

# Module 3

*See sub-skills for full details.*

## 4. Module Independence Validation


**Independence Checklist:**
```markdown

## Module Independence Validation


For each module, verify:

**Can Run Standalone:**
- [ ] Module has its own CLI command
- [ ] Module can be executed without other modules
- [ ] Module has dedicated configuration section
- [ ] Module's dependencies are clearly defined
- [ ] Module produces independent output

**Clear Boundaries:**

*See sub-skills for full details.*

## 5. Architecture Decision Documentation


**Decision Template (decisions.md):**
```markdown
