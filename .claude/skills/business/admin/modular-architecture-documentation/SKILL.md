---
capabilities: []
requires: []
see_also: []
---

# Modular Architecture Documentation Skill

> Version: 1.0.0
> Created: 2026-01-08
> Category: Software Architecture, Documentation, System Design

## Overview

This skill provides a systematic approach to documenting multi-module system architectures, including module boundary definition, CLI command specification, shared component identification, and architecture decision documentation following Agent OS decisions.md patterns.

## When to Use

Use this skill when:
- Documenting modular architecture in tech-stack.md
- Implementing multi-module systems with independent CLI commands
- Defining module boundaries and responsibilities
- Identifying shared vs. module-specific components
- Documenting pyproject.toml entry points for modules
- Recording architecture decisions in decisions.md
- Ensuring module independence and cohesion
- Planning gradual feature adoption (Phase 1: Module A, Phase 2: Module B)

## Skill Components

### 1. Module Definition Framework

**Module Documentation Template:**
```markdown
### Modular Design

Following [DEC-XXX], the system is organized into [N] independent modules:

**Module 1: [Module Name]**
- **Purpose:** [What this module does]
- **Scope:** [What's included in this module]
- **Entry Point:** [Python module path]
- **CLI Command:** `[command-name]`
- **Dependencies:** [External packages specific to this module]
- **Output:** [What this module produces]

**Module 2: [Module Name]**
- **Purpose:** [What this module does]
- **Scope:** [What's included in this module]
- **Entry Point:** [Python module path]
- **CLI Command:** `[command-name]`
- **Dependencies:** [External packages specific to this module]
- **Output:** [What this module produces]

**Shared Components**
- **Configuration Management:** [Shared config handling]
- **Utilities:** [Shared utility functions]
- **Testing Infrastructure:** [Shared test fixtures]
- **Logging Framework:** [Shared logging setup]
```

**Example (3-Module System):**
```markdown
### Modular Design

Following DEC-003 (Modular Architecture, 2025-07-27), the system is organized into three independent modules:

**Module 1: Invoice Automation**
- **Purpose:** Automated invoice generation and delivery
- **Scope:** Template processing, data merging, PDF generation, email delivery
- **Entry Point:** `aceengineer_admin.invoice:main`
- **CLI Command:** `invoice-gen`
- **Dependencies:** python-docx, jinja2, plotly (for invoice charts)
- **Output:** PDF invoices in /reports/invoices/

**Module 2: Tax Preparation**
- **Purpose:** Financial data aggregation and tax form data compilation
- **Scope:** Expense categorization, revenue aggregation, supporting document organization
- **Entry Point:** `aceengineer_admin.tax_prep:main`
- **CLI Command:** `tax-prep`
- **Dependencies:** pandas, openpyxl (for financial data processing)
- **Output:** Tax preparation reports in /reports/tax-prep/

**Module 3: Tax Filing**
- **Purpose:** Tax form generation and filing preparation
- **Scope:** Form 1120 generation, Schedule K-1, filing deadline tracking, submission prep
- **Entry Point:** `aceengineer_admin.tax_file:main`
- **CLI Command:** `tax-file`
- **Dependencies:** pypdf, reportlab (for PDF form filling)
- **Output:** Completed tax forms in /reports/tax-filing/

**Shared Components**
- **Configuration Management:** YAML-based config (pyyaml)
- **Utilities:** PDF processing, date handling (python-dateutil)
- **Testing Infrastructure:** pytest, pytest-cov, test fixtures
- **Logging Framework:** loguru with structured logging
```

### 2. CLI Command Documentation

**CLI Command Documentation Template:**
```markdown
### CLI Interface

Each module provides a dedicated CLI command configured in pyproject.toml:

**Module 1 Commands:**
```bash
[command-name] [subcommand] [options]

# Basic usage
[command-name] --required-arg VALUE

# Common operations
[command-name] --operation1 --flag
[command-name] --operation2 --output-path PATH

# Advanced usage
[command-name] --all --validate --dry-run
```

**Module 2 Commands:**
[Similar structure]

**Module 3 Commands:**
[Similar structure]

**Common Flags:**
- `--help, -h` - Show help message
- `--verbose, -v` - Verbose output
- `--dry-run` - Preview without executing
- `--config PATH` - Custom configuration file
```

**Example (3-Module CLI):**
```markdown
### CLI Interface

Each module provides a dedicated CLI command configured in pyproject.toml:

**Invoice Automation Commands:**
```bash
invoice-gen [options]

# Generate invoice for single client
invoice-gen --client ACMA --month 2025-01 --template monthly

# Generate invoices for all clients
invoice-gen --all-clients --month 2025-01

# Email delivery
invoice-gen --client RII --month 2025-01 --email

# Preview without generating
invoice-gen --client ACMA --month 2025-01 --dry-run
```

**Tax Preparation Commands:**
```bash
tax-prep [options]

# Federal tax preparation
tax-prep --year 2024 --type federal

# State tax preparation
tax-prep --year 2024 --type state --state TX

# Generate expense report
tax-prep --year 2024 --expense-report --validate

# Full preparation with validation
tax-prep --year 2024 --all --validate
```

**Tax Filing Commands:**
```bash
tax-file [options]

# Generate Form 1120
tax-file --year 2024 --form 1120

# Generate Schedule K-1 for all shareholders
tax-file --year 2024 --form k1 --shareholder all

# Generate all forms with validation
tax-file --year 2024 --all --validate

# Filing deadline reminder
tax-file --check-deadlines --year 2024
```

**Common Flags:**
- `--help, -h` - Show help message and exit
- `--verbose, -v` - Verbose output with progress details
- `--dry-run` - Preview operation without executing
- `--config PATH` - Use custom configuration file
- `--validate` - Validate data before processing
```

### 3. pyproject.toml Entry Points

**Entry Points Configuration:**
```toml
[project.scripts]
# Module 1
module1-command = "package.module1:main"

# Module 2
module2-command = "package.module2:main"

# Module 3
module3-command = "package.module3:main"
```

**Example:**
```toml
[project.scripts]
# Module 1: Invoice Automation
invoice-gen = "aceengineer_admin.invoice:main"

# Module 2: Tax Preparation
tax-prep = "aceengineer_admin.tax_prep:main"

# Module 3: Tax Filing
tax-file = "aceengineer_admin.tax_file:main"
```

**Main Function Pattern:**
```python
# src/aceengineer_admin/invoice/__main__.py
import click
from pathlib import Path

@click.command()
@click.option('--client', type=str, help='Client name')
@click.option('--month', type=str, help='Invoice month (YYYY-MM)')
@click.option('--template', type=str, default='monthly', help='Invoice template')
@click.option('--email', is_flag=True, help='Email invoice after generation')
@click.option('--dry-run', is_flag=True, help='Preview without generating')
def main(client: str, month: str, template: str, email: bool, dry_run: bool):
    """Generate client invoices with automated data population."""
    if dry_run:
        click.echo(f"Would generate invoice for {client} ({month}) using {template} template")
        return

    # Implementation
    click.echo(f"Generating invoice for {client}...")
    # ... invoice generation logic

if __name__ == '__main__':
    main()
```

### 4. Module Independence Validation

**Independence Checklist:**
```markdown
### Module Independence Validation

For each module, verify:

**Can Run Standalone:**
- [ ] Module has its own CLI command
- [ ] Module can be executed without other modules
- [ ] Module has dedicated configuration section
- [ ] Module's dependencies are clearly defined
- [ ] Module produces independent output

**Clear Boundaries:**
- [ ] Module responsibilities are well-defined
- [ ] No circular dependencies between modules
- [ ] Shared components are in separate directory
- [ ] Module-specific code is in module directory
- [ ] Clear data flow between modules (if any)

**Testing Independence:**
- [ ] Module has its own test suite
- [ ] Tests can run without other modules
- [ ] Mock external dependencies (other modules)
- [ ] Test coverage meets standards (80%+ overall, 95%+ critical)

**Documentation Completeness:**
- [ ] Module purpose documented
- [ ] CLI commands documented with examples
- [ ] Configuration options explained
- [ ] Input/output formats specified
- [ ] Dependencies listed
```

### 5. Architecture Decision Documentation

**Decision Template (decisions.md):**
```markdown
## [DATE]: [Decision Title]

**ID:** DEC-[NUMBER]
**Status:** [Proposed/Accepted/Rejected/Superseded]
**Category:** [Technical/Product/Process/Architecture]
**Related Specs:** [@.agent-os/specs/spec-name/] (if applicable)

### Decision

[Clear statement of what was decided and why modular architecture was chosen]

### Context

[Why this decision was needed: problems solved, requirements addressed]

### Modular Approach

**Module Structure:**
1. **Module A:** [Purpose, scope, CLI command]
2. **Module B:** [Purpose, scope, CLI command]
3. **Module C:** [Purpose, scope, CLI command]

**Shared Components:** [What's shared across modules]

**Independence Rationale:** [Why modules are independent]

### Alternatives Considered

**Alternative 1: Monolithic System**
- Pros: Simpler initial implementation
- Cons: Harder to test, deploy, and maintain; all-or-nothing adoption

**Alternative 2: Microservices**
- Pros: Maximum independence, scalability
- Cons: Over-engineering for local Python scripts, deployment complexity

**Alternative 3: Selected - Independent Modules with Shared Components**
- Pros: Gradual adoption (use only what you need), independent testing, clear boundaries
- Cons: Slightly more setup complexity
- **Rationale:** Best fit for Python CLI tools with gradual feature rollout

### Consequences

**Positive:**
- Users can adopt modules gradually (Phase 1: Invoices, Phase 2: Tax Prep, Phase 3: Filing)
- Independent testing and development
- Clear separation of concerns
- Easy to extend with new modules

**Negative:**
- More initial project structure setup
- Need to maintain shared components carefully
- Slightly more complex dependency management

### Implementation Notes

**pyproject.toml Configuration:**
```toml
[project.scripts]
module-a-cmd = "package.module_a:main"
module-b-cmd = "package.module_b:main"
module-c-cmd = "package.module_c:main"
```

**Directory Structure:**
```
src/package/
├── module_a/          # Independent module A
├── module_b/          # Independent module B
├── module_c/          # Independent module C
└── shared/            # Shared components
    ├── config.py
    ├── utils.py
    └── logging.py
```
```

## Templates

### Tech-Stack.md Modular Architecture Section

```markdown
## Modular Architecture

### Overview

Following [DEC-XXX] (Modular Architecture Decision, [DATE]), the system is organized into [N] independent modules to support gradual feature adoption and independent development cycles.

### Module Structure

**Module 1: [Name]**
- **Purpose:** [What it does]
- **Scope:** [What's included]
- **Entry Point:** [Python module path]
- **CLI Command:** `[command]`
- **Dependencies:** [Specific packages]
- **Output:** [Where files are saved]
- **Adoption Phase:** [Phase N (Weeks X-Y)]

**Module 2: [Name]**
[Similar structure]

**Module 3: [Name]**
[Similar structure]

**Shared Components**
- **Configuration:** [Config management approach]
- **Utilities:** [Shared utility functions]
- **Data Models:** [Common data structures]
- **Testing:** [Shared test fixtures]
- **Logging:** [Shared logging setup]

### Module Independence

Each module:
- Can be used independently
- Has its own CLI command
- Produces standalone outputs
- Has dedicated configuration section
- Has independent test suite

### Gradual Adoption Path

**Phase 1:** [Module 1] - [Timeline]
**Phase 2:** [Module 2] - [Timeline]
**Phase 3:** [Module 3] - [Timeline]

Users can adopt modules in any order based on business needs.

### CLI Commands

```bash
# Module 1
[module1-cmd] [options]

# Module 2
[module2-cmd] [options]

# Module 3
[module3-cmd] [options]
```

### Directory Organization

```
src/[package]/
├── module_1/          # Independent module 1
│   ├── __init__.py
│   ├── __main__.py    # CLI entry point
│   ├── core.py        # Core logic
│   └── config.py      # Module config
├── module_2/          # Independent module 2
│   └── ...
├── module_3/          # Independent module 3
│   └── ...
└── shared/            # Shared components
    ├── __init__.py
    ├── config.py      # Shared config
    ├── utils.py       # Shared utilities
    └── logging.py     # Shared logging
```

### Testing Strategy

- **Unit Tests:** 80% coverage minimum per module
- **Integration Tests:** Cross-module workflows
- **CLI Tests:** Command-line interface validation
- **Independence Tests:** Each module testable in isolation
```

### Architecture Decision Template (decisions.md)

```markdown
## [YYYY-MM-DD]: Modular Architecture for [System Name]

**ID:** DEC-[XXX]
**Status:** Accepted
**Category:** Architecture
**Related Specs:** N/A

### Decision

Implement a modular architecture with [N] independent modules ([list names]) rather than a monolithic system, enabling gradual feature adoption and independent development cycles.

### Context

[Describe the problem:]
- Users need flexibility to adopt features incrementally
- Different features have different development timelines
- System complexity requires clear separation of concerns
- Need independent testing and deployment of features

### Modular Approach

**Module Structure:**
1. **Module A:** [Purpose] - CLI: `[command]`
2. **Module B:** [Purpose] - CLI: `[command]`
3. **Module C:** [Purpose] - CLI: `[command]`

**Shared Components:**
- Configuration management
- Utility functions
- Logging framework
- Testing infrastructure

**Independence Characteristics:**
- Each module has dedicated CLI command
- Modules can run without others
- Clear module boundaries with no circular dependencies
- Independent test suites

### Alternatives Considered

**1. Monolithic System**
- Pros: Simpler initial structure, single entry point
- Cons: All-or-nothing adoption, harder to test components, tight coupling
- **Why Rejected:** Doesn't support gradual adoption

**2. Microservices Architecture**
- Pros: Maximum independence, horizontal scaling
- Cons: Over-engineering for Python CLI, deployment complexity, network overhead
- **Why Rejected:** Too complex for local automation tools

**3. Plugin Architecture**
- Pros: Dynamic loading, extensibility
- Cons: More complex than needed, harder to debug
- **Why Rejected:** Unnecessary complexity for fixed set of modules

**4. Independent Modules with Shared Components (Selected)**
- Pros: Gradual adoption, independent testing, clear boundaries, appropriate complexity
- Cons: More initial setup, need coordination for shared components
- **Why Selected:** Best balance of flexibility and simplicity

### Consequences

**Positive:**
- **Gradual Adoption:** Users adopt Module A first, then B, then C based on needs
- **Independent Development:** Teams can work on modules independently
- **Clear Testing:** Each module has dedicated test suite
- **Flexible Deployment:** Deploy module updates independently
- **Reduced Risk:** Issues in one module don't affect others

**Negative:**
- **Setup Complexity:** More initial project structure required
- **Shared Component Management:** Need discipline to keep shared code minimal
- **Dependency Coordination:** Must manage shared dependencies carefully
- **Documentation Overhead:** Each module needs documentation

**Mitigation:**
- Use clear naming conventions for modules
- Minimize shared components (only truly shared code)
- Document module boundaries clearly
- Establish testing standards per module

### Implementation

**pyproject.toml:**
```toml
[project.scripts]
module-a = "package.module_a:main"
module-b = "package.module_b:main"
module-c = "package.module_c:main"
```

**Directory Structure:**
```
src/package/
├── module_a/          # Independent module A
├── module_b/          # Independent module B
├── module_c/          # Independent module C
└── shared/            # Minimal shared components
```

**Testing:**
- Each module: 80% coverage minimum
- Critical paths: 95% coverage
- Integration tests for cross-module workflows

### References

- tech-stack.md: Modular Architecture section
- roadmap.md: Phase 1 (Module A), Phase 2 (Module B), Phase 3 (Module C)
```

## Examples

### Example: 3-Module Invoice/Tax System

**tech-stack.md:**
```markdown
## Modular Architecture

### Overview

Following DEC-003 (Modular Architecture Decision, 2025-07-27), the system is organized into three independent modules to support gradual feature adoption and independent development cycles.

### Module Structure

**Module 1: Invoice Automation**
- **Purpose:** Automated invoice generation and delivery
- **Scope:** Template processing, data merging, PDF generation, email delivery
- **Entry Point:** `aceengineer_admin.invoice:main`
- **CLI Command:** `invoice-gen`
- **Dependencies:** python-docx, jinja2, plotly (invoice charts)
- **Output:** PDF invoices in /reports/invoices/
- **Adoption Phase:** Phase 1 (Weeks 1-2) - 80% time savings

**Module 2: Tax Preparation**
- **Purpose:** Financial data aggregation and tax form data compilation
- **Scope:** Expense categorization, revenue aggregation, document organization
- **Entry Point:** `aceengineer_admin.tax_prep:main`
- **CLI Command:** `tax-prep`
- **Dependencies:** pandas, openpyxl (financial processing)
- **Output:** Tax prep reports in /reports/tax-prep/
- **Adoption Phase:** Phase 2 (Weeks 3-4) - Eliminates manual categorization

**Module 3: Tax Filing**
- **Purpose:** Tax form generation and filing preparation
- **Scope:** Form 1120, Schedule K-1, deadline tracking, submission prep
- **Entry Point:** `aceengineer_admin.tax_file:main`
- **CLI Command:** `tax-file`
- **Dependencies:** pypdf, reportlab (form filling)
- **Output:** Tax forms in /reports/tax-filing/
- **Adoption Phase:** Phase 3 (Weeks 5-8) - Streamlined compliance

**Shared Components**
- **Configuration:** YAML-based settings (pyyaml)
- **Utilities:** PDF processing, date handling
- **Testing:** pytest, test fixtures
- **Logging:** loguru with structured logging

### Module Independence

Each module:
- Can be used independently (invoice-gen works without tax-prep)
- Has its own CLI command
- Produces standalone outputs
- Has dedicated configuration section
- Has independent test suite

### Gradual Adoption Path

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

### CLI Commands

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

### Directory Organization

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
│   ├── __main__.py
│   ├── categorizer.py # Expense categorization
│   ├── aggregator.py  # Data aggregation
│   └── config.py
├── tax_file/          # Module 3: Tax Filing
│   ├── __init__.py
│   ├── __main__.py
│   ├── form_1120.py   # Form 1120 generation
│   ├── form_k1.py     # Schedule K-1 generation
│   └── config.py
└── shared/            # Shared components
    ├── __init__.py
    ├── config.py      # Global config management
    ├── pdf_utils.py   # PDF processing utilities
    ├── date_utils.py  # Date handling utilities
    └── logging.py     # Logging setup
```

### Testing Strategy

- **Unit Tests:** 80% coverage minimum per module, 95% for critical modules
- **Integration Tests:** Cross-module workflows (tax prep → tax filing)
- **CLI Tests:** Command-line interface validation
- **Independence Tests:** Each module testable in isolation with mocks
```

**decisions.md:**
```markdown
## 2025-07-27: Modular Architecture for Business Automation

**ID:** DEC-003
**Status:** Accepted
**Category:** Architecture
**Related Specs:** N/A

### Decision

Implement a modular architecture with three independent modules (Invoice Automation, Tax Preparation, Tax Filing) rather than a monolithic business automation system, enabling gradual feature adoption aligned with user needs.

### Context

Small engineering firms need flexibility to adopt automation features incrementally:
- Not all firms need all features simultaneously
- Budget constraints limit initial investment
- Different features have different priorities (invoice automation urgent, tax filing seasonal)
- Need to prove value before full system adoption

### Modular Approach

**Module Structure:**
1. **Invoice Automation:** `invoice-gen` - Immediate 80% time savings, highest ROI
2. **Tax Preparation:** `tax-prep` - Eliminate manual categorization, quarterly benefit
3. **Tax Filing:** `tax-file` - Annual compliance automation, seasonal use

**Shared Components:**
- Configuration management (YAML)
- PDF utilities (pypdf)
- Logging framework (loguru)
- Testing infrastructure (pytest)

**Independence:**
- Each module has CLI command
- No circular dependencies
- Can run without others
- Dedicated test suites

### Alternatives Considered

**1. Monolithic All-in-One System**
- Pros: Single unified interface, simpler initial architecture
- Cons: All-or-nothing adoption, $25K+ perceived investment, harder to justify ROI
- **Why Rejected:** Firms want proof-of-value before full investment

**2. Microservices**
- Pros: Maximum independence, cloud deployment ready
- Cons: Over-engineering for local Python scripts, network complexity
- **Why Rejected:** Unnecessary complexity for desktop automation

**3. Plugin Architecture**
- Pros: Dynamic module loading, third-party extensions
- Cons: Complex for fixed feature set, harder debugging
- **Why Rejected:** No need for third-party plugins

**4. Independent Modules with Shared Components (Selected)**
- Pros: Gradual adoption, prove ROI per module, appropriate complexity
- Cons: Slightly more project structure
- **Why Selected:** Perfect fit for incremental value delivery

### Consequences

**Positive:**
- **Gradual Adoption:** Firms adopt invoice automation first ($1,950/year value), then expand
- **Risk Mitigation:** Prove value module-by-module before full investment
- **Independent Development:** Each module can evolve independently
- **Clear Testing:** 80% coverage per module, 95% for critical invoice generation
- **Flexible Pricing:** Could charge per module if productized

**Negative:**
- **More Setup:** Three module directories vs. one
- **Shared Component Discipline:** Must minimize shared code to avoid coupling
- **Documentation:** Each module needs user guide

**Mitigation:**
- Clear documentation per module
- Minimal shared components (only config, logging, PDF utils)
- Module-specific configuration sections

### Implementation

**pyproject.toml:**
```toml
[project.scripts]
invoice-gen = "aceengineer_admin.invoice:main"
tax-prep = "aceengineer_admin.tax_prep:main"
tax-file = "aceengineer_admin.tax_file:main"
```

**Directory Structure:**
```
src/aceengineer_admin/
├── invoice/           # Module 1
├── tax_prep/          # Module 2
├── tax_file/          # Module 3
└── shared/            # Minimal shared code
```

**Testing:**
- Invoice module: 95% coverage (critical for revenue)
- Tax modules: 80% coverage (seasonal use)
- Integration tests for cross-module workflows

### References

- tech-stack.md: Modular Architecture section
- roadmap.md: Phase 1 (Invoice), Phase 2 (Tax Prep), Phase 3 (Filing)
- mission.md: Implementation Approach with phased rollout
```

## Best Practices

### Module Naming
- **Use domain names, not technical terms:**
  - ✅ `invoice`, `tax_prep`, `tax_file`
  - ❌ `module1`, `processor`, `generator`

- **Keep names short and memorable:**
  - ✅ `invoice-gen` (CLI command)
  - ❌ `invoice_generation_automation_tool`

### Module Boundaries
- **One module = one CLI command = one purpose**
- **Clear inputs/outputs per module**
- **No circular dependencies between modules**
- **Minimize shared components** (only truly shared code)

### CLI Command Design
- **Consistent flag naming across modules:**
  - `--help`, `--verbose`, `--dry-run`, `--config`
- **Intuitive command names reflecting actions:**
  - `invoice-gen`, `tax-prep`, `tax-file`
- **Comprehensive help text with examples**

### Documentation Standards
- **Document in tech-stack.md:** Module structure, CLI commands, adoption path
- **Record in decisions.md:** Why modular, alternatives considered, consequences
- **Update roadmap.md:** Phased implementation per module
- **Maintain README:** Quick start per module

### Testing Independence
- **Each module has test directory:**
  ```
  tests/
  ├── invoice/
  ├── tax_prep/
  ├── tax_file/
  └── shared/
  ```
- **Mock other modules in tests** (don't depend on them)
- **80% coverage per module, 95% for critical**

## Related Skills

- **Product Documentation Modernization** - For documenting architecture in tech-stack.md
- **Technology Stack Modernization** - For pyproject.toml configuration
- **Workspace-Hub Standards Compliance** - For ensuring architectural compliance

## References

### Architecture Patterns
- [Clean Architecture](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)
- [Modular Monolith](https://www.kamilgrzybek.com/blog/posts/modular-monolith-primer)
- [Python Application Layouts](https://realpython.com/python-application-layouts/)

### CLI Design
- [Click Documentation](https://click.palletsprojects.com/)
- [CLI Best Practices](https://clig.dev/)

### Agent OS Resources
- Agent OS Documentation: mission.md, tech-stack.md, roadmap.md, decisions.md
- Agent OS Decision Template: decisions.md format

## Success Criteria

✅ **Modular Architecture Documented When:**
- [ ] Module structure section in tech-stack.md
- [ ] Each module has clear purpose, scope, CLI command
- [ ] Shared components identified and justified
- [ ] CLI commands documented with examples
- [ ] pyproject.toml entry points configured
- [ ] Module independence verified (can run standalone)
- [ ] Architecture decision recorded in decisions.md
- [ ] Testing strategy defined per module
- [ ] Adoption path documented (Phase 1, 2, 3)
- [ ] Directory structure reflects modular organization

---

## Version History

- **1.0.0** (2026-01-08): Initial release - comprehensive modular architecture documentation skill
