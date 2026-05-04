---
name: docx-templates-1-basic-template-rendering
description: 'Sub-skill of docx-templates: 1. Basic Template Rendering.'
version: 1.0.0
category: data
type: reference
scripts_exempt: true
---

# 1. Basic Template Rendering

## 1. Basic Template Rendering


**Simple Variable Substitution:**
```python
"""
Basic template rendering with variable substitution.
"""
from docxtpl import DocxTemplate
from typing import Dict, Any
from pathlib import Path

def render_simple_template(
    template_path: str,
    output_path: str,
    context: Dict[str, Any]
) -> None:
    """
    Render a template with simple variable substitution.

    Args:
        template_path: Path to .docx template
        output_path: Path for output document
        context: Dictionary of values to substitute

    Template syntax:
        {{ variable_name }} - Simple variable
        {{ object.property }} - Nested property
    """
    # Load template
    template = DocxTemplate(template_path)

    # Render with context
    template.render(context)

    # Save output
    template.save(output_path)
    print(f"Document saved to {output_path}")


def create_sample_letter(output_path: str) -> None:
    """Create a sample letter using template rendering."""

    # First, create a simple template (normally you'd have this prepared)
    # Template content would have: {{ recipient_name }}, {{ date }}, etc.

    context = {
        "recipient_name": "John Smith",
        "recipient_title": "Director of Operations",
        "company_name": "Acme Corporation",
        "street_address": "123 Business Ave",
        "city_state_zip": "New York, NY 10001",
        "date": "January 17, 2026",
        "subject": "Project Proposal",
        "salutation": "Dear Mr. Smith",
        "body_paragraph_1": """
            We are pleased to submit our proposal for the infrastructure
            upgrade project. Our team has extensive experience in similar
            projects and we are confident we can deliver exceptional results.
        """.strip(),
        "body_paragraph_2": """
            The attached documents outline our approach, timeline, and
            budget estimates. We would welcome the opportunity to discuss
            this proposal at your convenience.
        """.strip(),
        "closing": "Sincerely",
        "sender_name": "Jane Doe",
        "sender_title": "Project Manager"
    }

    # Render template
    render_simple_template("letter_template.docx", output_path, context)


# Example context for a business report
report_context = {
    "report_title": "Q4 2025 Performance Report",
    "prepared_by": "Analytics Team",
    "date": "January 15, 2026",
    "executive_summary": "Strong performance across all metrics...",
    "total_revenue": "$2,450,000",
    "growth_rate": "15.3%",
    "customer_count": "1,250",
    "key_achievements": [
        "Launched new product line",
        "Expanded to 3 new markets",
        "Achieved ISO certification"
    ]
}
```

**Nested Object Access:**
```python
"""
Access nested objects and complex data structures in templates.
"""
from docxtpl import DocxTemplate
from dataclasses import dataclass, asdict
from typing import List, Dict, Optional
from datetime import date

@dataclass
class Address:
    """Address data structure."""
    street: str
    city: str
    state: str
    zip_code: str
    country: str = "USA"

    @property
    def full_address(self) -> str:
        return f"{self.street}\n{self.city}, {self.state} {self.zip_code}"


@dataclass
class Contact:
    """Contact information."""
    name: str
    email: str
    phone: str
    title: Optional[str] = None


@dataclass
class Company:
    """Company data structure."""
    name: str
    address: Address
    contacts: List[Contact]
    industry: str
    website: str

    def to_dict(self) -> Dict:
        """Convert to dictionary for template rendering."""
        return {
            "name": self.name,
            "address": asdict(self.address),
            "contacts": [asdict(c) for c in self.contacts],
            "industry": self.industry,
            "website": self.website
        }


def render_with_nested_data(
    template_path: str,
    output_path: str,
    company: Company
) -> None:
    """
    Render template with nested data structures.

    Template syntax for nested access:
        {{ company.name }}
        {{ company.address.street }}
        {{ company.contacts[0].email }}
    """
    template = DocxTemplate(template_path)

    context = {
        "company": company.to_dict(),
        "generated_date": date.today().strftime("%B %d, %Y")
    }

    template.render(context)
    template.save(output_path)


# Example usage
company = Company(
    name="TechCorp Industries",
    address=Address(
        street="456 Innovation Blvd",
        city="San Francisco",
        state="CA",
        zip_code="94105"
    ),
    contacts=[
        Contact(
            name="Alice Johnson",
            email="alice@techcorp.com",
            phone="555-0101",
            title="CEO"
        ),
        Contact(
            name="Bob Williams",
            email="bob@techcorp.com",

*Content truncated — see parent skill for full reference.*
