---
name: tax-preparation
version: "1.0.0"
category: business
description: "Automate preparation of corporate tax documents including federal Form 1120, Texas franchise tax, and CPA review packages."
---

# Tax Preparation

Prepare corporate tax documents and supporting materials for AceEngineer Inc.

---

## Description

This skill automates the preparation of corporate tax documents including federal Form 1120, Texas franchise tax, and supporting documentation for CPA review.

## Trigger Conditions

Activate when the user mentions:
- Tax preparation or tax documents
- Corporate tax forms (1120)
- Texas franchise tax
- Tax year preparation
- Tax filing package

## Core Capabilities

1. **Expense Categorization**: Automatically categorize expenses for tax purposes
2. **Income Summarization**: Aggregate revenue by client and category
3. **Form Data Preparation**: Prepare data for Form 1120 fields
4. **Supporting Documentation**: Compile supporting schedules and documentation
5. **CPA Package Generation**: Create organized package for CPA review

## Usage Examples

```bash
# Prepare tax documents for a year
aceengineer tax prepare --year 2024

# Generate draft forms only
aceengineer tax prepare --year 2024 --draft

# Create filing package with checklist
aceengineer tax file --year 2024

# Generate checklist only
aceengineer tax file --year 2024 --checklist-only
```

## Tax Categories

### Deductible Expenses
- Professional services and consulting fees
- Office supplies and equipment
- Software and technology
- Travel and transportation
- Professional development and training
- Insurance premiums
- Bank fees and charges

### Revenue Categories
- Engineering consulting services
- Design review fees
- Technical support services

## Output Structure

```
tax_output/
├── 2024/
│   ├── income_summary.xlsx
│   ├── expense_summary.xlsx
│   ├── form_1120_data.xlsx
│   ├── texas_franchise_data.xlsx
│   ├── supporting_schedules/
│   └── cpa_package/
│       ├── checklist.md
│       ├── instructions.pdf
│       └── all_documents.zip
```

## Dependencies

- pandas: Financial data processing
- openpyxl: Excel report generation
- PyPDF2: PDF document handling
- reportlab: PDF generation

## Related Files

- `aceengineer_admin/tax/`: Tax module source
- `aceengineer_admin/cli.py`: CLI commands
- `tax_data/`: Historical tax data
- `tax_output/`: Generated tax documents

## Workflow

1. Load expense and revenue data for tax year
2. Categorize transactions for tax purposes
3. Calculate totals and prepare form data
4. Generate summary reports in Excel
5. Compile supporting documentation
6. Create CPA review package with checklist
