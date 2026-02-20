---
name: invoice-automation
version: "1.0.0"
category: business
description: "Automate invoice generation for engineering consulting services using YAML configuration and Word document templates."
---

# Invoice Automation

Generate professional invoices for engineering consulting clients using YAML configuration.

---

## Description

This skill automates invoice generation for AceEngineer's engineering consulting services. It reads client billing data from YAML configurations and generates Word document invoices using templates.

## Trigger Conditions

Activate when the user mentions:
- Invoice generation or creation
- Client billing or billing cycles
- Monthly invoices for clients (ACMA, RII, Doris, SeaNation)
- Engineering consulting fees

## Core Capabilities

1. **Client Invoice Generation**: Generate invoices from YAML billing configurations
2. **Template-Based Output**: Use python-docx to create professional Word documents
3. **Multi-Client Support**: Handle multiple clients with different billing rates and terms
4. **Due Date Calculation**: Automatically calculate payment due dates

## Usage Examples

```bash
# Generate invoices for a specific month
aceengineer invoice generate --month 2025-01

# Generate invoice for specific client
aceengineer invoice generate --month 2025-01 --client ACMA

# Preview without generating files
aceengineer invoice generate --month 2025-01 --dry-run
```

## Configuration Structure

```yaml
# config/invoice_config.yaml
client:
  name: "ACMA Engineering"
  contact: "John Smith"
  address: "123 Client Street"

billing:
  rate: 150.00
  currency: "USD"
  payment_terms_days: 30

services:
  - description: "Engineering consultation"
    hours: 40
    rate: 150.00
```

## Output

- Word document invoices (.docx)
- Invoice tracking spreadsheet
- PDF export (optional)

## Dependencies

- pandas: Data processing
- python-docx: Word document generation
- openpyxl: Excel file handling
- pyyaml: Configuration parsing

## Related Files

- `aceengineer_admin/invoice/`: Invoice module source
- `aceengineer_admin/cli.py`: CLI commands
- `templates/invoices/`: Invoice templates
- `invoices/`: Generated invoice output

## Workflow

1. Load client billing configuration from YAML
2. Calculate billing amounts and due dates
3. Populate invoice template with data
4. Generate Word document with professional formatting
5. Update invoice tracking spreadsheet
6. Optionally export to PDF
