---
name: docx-templates-2-loops-and-iterations
description: 'Sub-skill of docx-templates: 2. Loops and Iterations.'
version: 1.0.0
category: data
type: reference
scripts_exempt: true
---

# 2. Loops and Iterations

## 2. Loops and Iterations


**Rendering Lists and Tables:**
```python
"""
Use loops to render lists, tables, and repeated content.
"""
from docxtpl import DocxTemplate
from typing import List, Dict, Any
from dataclasses import dataclass
from decimal import Decimal

@dataclass
class LineItem:
    """Invoice line item."""
    description: str
    quantity: int
    unit_price: Decimal
    discount: Decimal = Decimal("0")

    @property
    def subtotal(self) -> Decimal:
        return self.quantity * self.unit_price * (1 - self.discount / 100)


@dataclass
class Invoice:
    """Invoice data structure."""
    invoice_number: str
    date: str
    due_date: str
    client_name: str
    client_address: str
    items: List[LineItem]
    tax_rate: Decimal = Decimal("8.5")
    notes: str = ""

    @property
    def subtotal(self) -> Decimal:
        return sum(item.subtotal for item in self.items)

    @property
    def tax_amount(self) -> Decimal:
        return self.subtotal * self.tax_rate / 100

    @property
    def total(self) -> Decimal:
        return self.subtotal + self.tax_amount

    def to_context(self) -> Dict[str, Any]:
        """Convert to template context."""
        return {
            "invoice_number": self.invoice_number,
            "date": self.date,
            "due_date": self.due_date,
            "client_name": self.client_name,
            "client_address": self.client_address,
            "items": [
                {
                    "description": item.description,
                    "quantity": item.quantity,
                    "unit_price": f"${item.unit_price:.2f}",
                    "discount": f"{item.discount}%" if item.discount else "",
                    "subtotal": f"${item.subtotal:.2f}"
                }
                for item in self.items
            ],
            "subtotal": f"${self.subtotal:.2f}",
            "tax_rate": f"{self.tax_rate}%",
            "tax_amount": f"${self.tax_amount:.2f}",
            "total": f"${self.total:.2f}",
            "notes": self.notes
        }


def render_invoice(
    template_path: str,
    output_path: str,
    invoice: Invoice
) -> None:
    """
    Render invoice template with line items.

    Template syntax for loops:
        {%tr for item in items %}
        {{ item.description }} | {{ item.quantity }} | {{ item.unit_price }}
        {%tr endfor %}

    Note: {%tr %} is for table rows, {%p %} for paragraphs
    """
    template = DocxTemplate(template_path)
    context = invoice.to_context()
    template.render(context)
    template.save(output_path)


def render_list_document(
    template_path: str,
    output_path: str,
    items: List[str],
    title: str
) -> None:
    """
    Render document with bullet list.

    Template syntax for paragraph loops:
        {%p for item in items %}
        - {{ item }}
        {%p endfor %}
    """
    template = DocxTemplate(template_path)

    context = {
        "title": title,
        "items": items,
        "item_count": len(items)
    }

    template.render(context)
    template.save(output_path)


# Example: Create invoice
invoice = Invoice(
    invoice_number="INV-2026-0042",
    date="January 17, 2026",
    due_date="February 16, 2026",
    client_name="Acme Corp",
    client_address="123 Main St\nNew York, NY 10001",
    items=[
        LineItem("Consulting Services", 40, Decimal("150.00")),
        LineItem("Software License", 1, Decimal("500.00")),
        LineItem("Training Session", 8, Decimal("100.00"), Decimal("10")),
    ],
    notes="Payment due within 30 days. Thank you for your business!"
)

# render_invoice("invoice_template.docx", "invoice_output.docx", invoice)


def render_nested_loops(
    template_path: str,
    output_path: str,
    departments: List[Dict]
) -> None:
    """
    Render template with nested loops.

    Template syntax:
        {%p for dept in departments %}
        Department: {{ dept.name }}
        {%p for emp in dept.employees %}
        - {{ emp.name }} ({{ emp.role }})
        {%p endfor %}
        {%p endfor %}
    """
    template = DocxTemplate(template_path)

    context = {
        "company_name": "TechCorp",
        "departments": departments
    }

    template.render(context)
    template.save(output_path)


# Example data for nested loops
departments = [
    {
        "name": "Engineering",
        "head": "Alice Johnson",
        "employees": [
            {"name": "Bob Smith", "role": "Senior Developer"},
            {"name": "Carol White", "role": "Developer"},
            {"name": "David Brown", "role": "QA Engineer"}
        ]
    },
    {
        "name": "Marketing",
        "head": "Eve Davis",
        "employees": [
            {"name": "Frank Miller", "role": "Marketing Manager"},
            {"name": "Grace Lee", "role": "Content Writer"}
        ]
    }

*Content truncated — see parent skill for full reference.*
