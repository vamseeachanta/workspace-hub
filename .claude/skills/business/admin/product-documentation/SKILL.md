---
capabilities: []
requires: []
see_also: []
---

# Product Documentation Modernization Skill

> Version: 1.0.0
> Created: 2026-01-08
> Category: Documentation, Product Management, Standards Compliance

## Overview

This skill provides a systematic approach to reviewing and modernizing Agent OS product documentation (mission.md, tech-stack.md, roadmap.md) to ensure quantifiable value propositions, workspace-hub standards compliance, and engineering-specific differentiation.

## When to Use

Use this skill when:
- Initializing Agent OS product documentation for new repositories
- Reviewing existing product documentation for improvements
- Ensuring compliance with workspace-hub standards (UV, Plotly, file organization)
- Adding quantifiable metrics and success criteria to product documents
- Modernizing technology stacks to current best practices
- Documenting modular architecture decisions

## Skill Components

### 1. Mission Document Review & Enhancement

**Checklist for mission.md:**

**Pitch Section:**
- [ ] Includes quantifiable claim (e.g., "reduces overhead by 70%")
- [ ] Clearly states target users and specific pain point
- [ ] Explains value proposition in one sentence
- [ ] Uses active, benefit-focused language

**User Personas:**
- [ ] Includes age range and role
- [ ] Defines business context (number of projects, team size, etc.)
- [ ] Lists specific, measurable pain points with time/cost impacts
- [ ] States concrete goals with success criteria

**Example:**
```markdown
**Business Administrator** (28-45 years old)
- **Role:** Administrative Manager or Business Operations Coordinator
- **Context:** Day-to-day management of business finances, invoicing, and compliance for 3-7 concurrent engineering projects
- **Pain Points:**
  - Spending 6-8 hours/week on invoice generation across multiple clients
  - Manual expense categorization from credit card statements (2-3 hours/week)
  - Annual tax preparation requires 20-30 hours of document organization
- **Goals:**
  - Reduce administrative time by 70% to focus on business development
  - Achieve 100% on-time invoice delivery (currently 75%)
```

**Key Features:**
- [ ] Each feature includes impact metrics or time savings
- [ ] Features grouped by category (Core, Collaboration, Integration)
- [ ] Features written from user benefit perspective, not technical implementation

**Success Metrics Section (Required):**
- [ ] Efficiency Gains: Specific time reductions (e.g., 85% reduction in invoice time)
- [ ] Business Impact: Dollar savings (e.g., $15K-25K annually)
- [ ] Adoption Success: Timeline and satisfaction metrics
- [ ] All metrics are measurable and achievable

**Implementation Approach Section (Required):**
- [ ] Phased approach with clear timelines
- [ ] Each phase shows immediate value delivery
- [ ] Zero business disruption strategy
- [ ] Manual override availability

### 2. Tech Stack Modernization

**Checklist for tech-stack.md:**

**Core Technologies:**
- [ ] Uses UV package manager (workspace-hub standard) - NOT Conda/Poetry
- [ ] Python 3.11+ specified with modern type hints
- [ ] All dependencies use current major versions (e.g., Pandas 2.0+, not 1.x)
- [ ] Deprecated libraries replaced (e.g., pypdf instead of PyPDF2)

**Visualization Standards:**
- [ ] Plotly MANDATORY for all visualizations
- [ ] Explicit note: "All visualizations MUST be interactive (Plotly)"
- [ ] NO Matplotlib, seaborn, or static image exports
- [ ] Kaleido for static exports FROM interactive Plotly charts only

**Modular Architecture:**
- [ ] Reflects decisions.md modular design (e.g., DEC-003)
- [ ] Each module has clear CLI command (e.g., `invoice-gen`, `tax-prep`)
- [ ] Shared components explicitly listed
- [ ] Module boundaries clearly defined

**Complete Dependencies:**
- [ ] Full pyproject.toml configuration included
- [ ] All categories covered: data processing, document generation, visualization, email, automation, logging, CLI, testing
- [ ] Development dependencies separated (`[project.optional-dependencies]`)
- [ ] Entry point scripts defined (`[project.scripts]`)

**CLI Interface:**
- [ ] Click or Typer framework specified
- [ ] Command examples for each module
- [ ] Option documentation included
- [ ] Usage patterns demonstrated

**Testing Strategy:**
- [ ] Coverage requirements specified (minimum 80%, critical modules 95%)
- [ ] Test structure documented (unit/, integration/, performance/)
- [ ] Testing commands provided

**Development Environment:**
- [ ] UV installation instructions
- [ ] Virtual environment creation steps
- [ ] Cross-platform support (Windows/macOS/Linux)
- [ ] Editor recommendations

### 3. Standards Compliance Verification

**Workspace-Hub Standards:**

**UV Package Manager:**
```bash
# ✅ Correct
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip install -e .

# ❌ Wrong
conda create -n myenv
pip install -r requirements.txt
```

**Interactive Visualizations:**
```python
# ✅ Correct - Plotly interactive
import plotly.express as px
fig = px.scatter(df, x='time', y='value')
fig.write_html('../reports/analysis.html')

# ❌ Wrong - Matplotlib static
import matplotlib.pyplot as plt
plt.scatter(df['time'], df['value'])
plt.savefig('plot.png')
```

**File Organization:**
- [ ] Reports in `/reports/` directory
- [ ] Data in `/data/` (raw/, processed/, results/)
- [ ] No files saved to root folder
- [ ] Module-based source organization in `/src/`

**CSV Data Import:**
- [ ] Uses relative paths from report location
- [ ] No hardcoded absolute paths
- [ ] Standardized data directory structure

### 4. Quantification Framework

**Adding Metrics to Documents:**

**Time Savings Calculation:**
```
Before: 15 minutes per invoice × 10 invoices/month = 150 minutes/month
After: 2 minutes per invoice × 10 invoices/month = 20 minutes/month
Reduction: 130 minutes/month = 87% time savings
```

**Cost Savings Calculation:**
```
Hourly rate: $75/hour
Time saved: 130 minutes/month × 12 months = 1,560 minutes/year = 26 hours/year
Value: 26 hours × $75 = $1,950/year per use case

Total across 3 use cases: ~$5,850/year
Add accountant fee reduction: $2,000-5,000/year
Total: $15,000-25,000/year
```

**Adoption Timeline:**
```
Week 1-2: Initial setup and first automated invoice
Week 3-4: Expense tracking automation
Week 5-8: Full tax preparation integration
Result: 8 weeks to full adoption
```

### 5. Engineering-Specific Differentiation

**For Engineering Firms:**
- [ ] Project-based billing emphasized
- [ ] Technical hours tracking mentioned
- [ ] Multi-client parallel project management
- [ ] Engineering service-specific expense categories (certifications, software licenses, standards)
- [ ] Professional engineering compliance tracking

**Example Differentiator:**
```markdown
### Engineering Project Financial Tracking

Unlike generic accounting systems, we provide project-based billing with technical hours tracking, multi-client parallel project management, and engineering service-specific expense categorization (design software, certifications, industry standards). This results in accurate project profitability analysis and improved resource allocation for engineering teams.
```

## Implementation Process

### Step 1: Read Current Documentation
```bash
# Read all three product documents
cat .agent-os/product/mission.md
cat .agent-os/product/tech-stack.md
cat .agent-os/product/decisions.md
```

### Step 2: Review Against Standards
- Compare against workspace-hub standards
- Check for deprecated technologies
- Verify quantifiable metrics exist
- Ensure modular architecture documented

### Step 3: Suggest Improvements
- Organize suggestions by category
- Prioritize based on impact
- Provide specific examples
- Include rationale for each change

### Step 4: Implement Changes
- Use Edit operations for precision
- Update version numbers and dates
- Maintain document structure
- Cross-reference with decisions.md

### Step 5: Validate Compliance
- Verify UV package manager used
- Confirm Plotly for all visualizations
- Check modular architecture alignment
- Ensure quantifiable metrics included

## Templates

### Mission.md Success Metrics Template
```markdown
## Success Metrics

### Efficiency Gains
- **[Feature]:** [%] reduction in time ([before] → [after])
- **[Feature]:** [%] reduction in [metric] ([before] → [after])

### Business Impact
- **Cost Savings:** $[amount] annually ([breakdown])
- **Revenue Protection:** $[amount] in [area]
- **Risk Reduction:** [%] accuracy improvement

### Adoption Success
- **Time to First Value:** [timeframe]
- **Full System Adoption:** [timeframe]
- **User Satisfaction:** [measurable outcome]
```

### Tech-Stack.md pyproject.toml Template
```toml
[project]
name = "project-name"
version = "1.0.0"
description = "Brief description"
requires-python = ">=3.11"
dependencies = [
    # Data Processing
    "pandas>=2.0.0",
    "numpy>=1.24.0",

    # Visualization (Interactive Only)
    "plotly>=5.14.0",
    "kaleido>=0.2.1",

    # CLI Development
    "click>=8.1.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.4.0",
    "pytest-cov>=4.1.0",
    "ruff>=0.1.0",
]

[project.scripts]
module-name = "package.module:main"
```

## Example Usage

### Review Mission Document
```python
# In Claude Code or AI agent
"Review the mission.md file and suggest improvements following the Product Documentation Modernization skill. Focus on adding quantifiable metrics and engineering-specific value propositions."
```

### Modernize Tech Stack
```python
# In Claude Code or AI agent
"Review tech-stack.md for compliance with workspace-hub standards. Replace Conda with UV, ensure Plotly is mandatory, and add complete pyproject.toml configuration."
```

## Success Criteria

Documentation is successfully modernized when:

**Mission.md:**
- [ ] Includes 3+ quantifiable efficiency gains
- [ ] Contains dollar-value business impact metrics
- [ ] Has complete Success Metrics section
- [ ] Includes Implementation Approach section
- [ ] Features engineering-specific differentiation

**Tech-stack.md:**
- [ ] Uses UV package manager (not Conda)
- [ ] Plotly mandatory with explicit note
- [ ] Complete pyproject.toml included
- [ ] Modular architecture documented
- [ ] CLI commands for all modules
- [ ] Testing strategy with coverage requirements
- [ ] Development environment setup included

**Both Documents:**
- [ ] Version updated (e.g., 1.0.0 → 2.0.0)
- [ ] Date updated to current
- [ ] Cross-referenced with decisions.md
- [ ] No deprecated technologies
- [ ] No workspace-hub standard violations

## Related Skills

- **File Organization Skill** - For organizing documentation and code files
- **Standards Compliance Skill** - For verifying workspace-hub standards
- **Quantification Skill** - For calculating time and cost savings
- **Agent OS Initialization Skill** - For setting up new repositories

## References

- Workspace-Hub Standards: `@/mnt/github/workspace-hub/docs/modules/standards/`
- Agent OS Instructions: `@~/.agent-os/instructions/`
- UV Package Manager: https://github.com/astral-sh/uv
- Plotly Documentation: https://plotly.com/python/

---

## Version History

- **1.0.0** (2026-01-08): Initial skill creation based on aceengineer-admin mission.md and tech-stack.md modernization work
