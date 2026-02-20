---
name: expense-tracking
version: "1.0.0"
category: business
description: "Track, categorize, and analyze business expenses including credit card statement import and monthly expense reports."
---

# Expense Tracking

Track, categorize, and analyze business expenses for AceEngineer Inc.

---

## Description

This skill manages expense tracking including credit card statement import, automatic categorization, and expense analysis for engineering consulting operations.

## Trigger Conditions

Activate when the user mentions:
- Expense tracking or expense management
- Credit card statement import
- Expense categorization
- Business expense analysis
- Monthly expense reports

## Core Capabilities

1. **Statement Import**: Import credit card and bank statements
2. **Auto-Categorization**: Automatically categorize expenses by type
3. **Receipt Management**: Link receipts to transactions
4. **Expense Analysis**: Generate expense reports and visualizations
5. **Budget Comparison**: Compare actual vs budgeted expenses

## Usage Examples

```python
# Import credit card statement
from aceengineer_admin.common import import_statement

expenses = import_statement("statements/amex_2025_01.csv")

# Categorize expenses
categorized = categorize_expenses(expenses)

# Generate monthly report
report = generate_expense_report(
    year=2025,
    month=1,
    output_format="html"
)
```

## Expense Categories

### Operating Expenses
- Software subscriptions
- Cloud services
- Communication (phone, internet)
- Professional memberships

### Travel Expenses
- Airfare
- Hotels and lodging
- Ground transportation
- Per diem meals

### Office Expenses
- Office supplies
- Equipment purchases
- Furniture
- Maintenance

### Professional Services
- Legal fees
- Accounting fees
- Consulting fees
- Insurance

## Output Reports

```
reports/
├── monthly_expense_report.html  # Interactive Plotly charts
├── expense_by_category.xlsx
├── vendor_analysis.xlsx
└── budget_variance.xlsx
```

## Configuration

```yaml
# config/expense_config.yaml
categories:
  - name: "Software"
    keywords: ["adobe", "microsoft", "github", "aws"]
  - name: "Travel"
    keywords: ["airline", "hotel", "uber", "lyft"]
  - name: "Office"
    keywords: ["staples", "amazon", "office depot"]

budget:
  software: 500.00
  travel: 2000.00
  office: 300.00
```

## Dependencies

- pandas: Data processing and analysis
- plotly: Interactive expense visualizations
- openpyxl: Excel report generation

## Related Files

- `aceengineer_admin/common/`: Common utilities
- `expense_data/`: Historical expense data
- `statements/`: Imported statements

## Workflow

1. Import credit card/bank statement CSV
2. Parse and clean transaction data
3. Apply auto-categorization rules
4. Flag transactions requiring review
5. Generate expense reports
6. Update expense tracking spreadsheet
