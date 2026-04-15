---

name: expense-tracking
version: "1.0.0"
category: business
description: "Track, categorize, and analyze business expenses including credit card statement import and monthly expense reports."
type: reference
tags: [finance, expenses, credit-card, reporting, bookkeeping]
related_skills:
- tax-preparation
- invoice-automation
scripts_exempt: true
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

## Locating the Latest AceEngineer Expense Workbook Across Machines

Use this when the user asks for the latest workbook and mentions network machines such as `home-win`, `aceengineer-va`, or the Mac portable machine.

### Recommended retrieval order

1. Check the local repo copy first:
   - `aceengineer-admin/Sabitha/<year>/EXPENSES Jan <year>-Dec<year> ...`
   - Search both `*.xlsx` and `*.ods`
2. Compare mtimes before assuming the newest year/file:
   - local repo can already contain the newest workbook even if remote access fails
3. Test live network reachability before attempting access:
   - Windows/home-win: ping + port 445 (SMB)
   - Mac portable: resolve hostname via mDNS/avahi, then test ping + port 22
4. Treat documented IPs as hints, not ground truth:
   - hostname/IP mappings can drift
   - prefer fresh resolution over stale notes
5. If the newest workbook is `.ods`, convert/export a values-only `.xlsx` copy for downstream users who expect Excel

### Important operational findings

- `home-win` may be reachable on LAN with SMB open, but stored SMB credentials can be stale; verify authentication before promising remote retrieval.
- The portable Mac may resolve on the LAN via mDNS even when the documented IP is stale; use `avahi-resolve`/hostname resolution rather than relying only on old registry values.
- A machine can respond to ping while still having SSH/File Sharing disabled; verify service ports explicitly.
- For AceEngineer expense files, the newest artifact may be `.ods` rather than `.xlsx`.

### ODS handling pattern

When the newest workbook is an ODS file and the user needs an Excel workbook:

1. Read ODS sheets programmatically with `odfpy`
2. Preserve sheet names and cell text values
3. Write a values-only `.xlsx` copy with `openpyxl`
4. Tell the user clearly that formulas/formatting may not be preserved in the exported copy

### Verification checklist

- Confirm exact source path of the newest workbook
- Report whether it was local or remotely retrieved
- Extract headline totals the user likely cares about:
  - total revenue
  - total expenses
  - net income
  - any major line items already populated
- State any access limitations explicitly if remote machines were unreachable or auth failed
