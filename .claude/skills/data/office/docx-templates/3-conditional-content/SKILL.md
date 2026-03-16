---
name: docx-templates-3-conditional-content
description: 'Sub-skill of docx-templates: 3. Conditional Content.'
version: 1.0.0
category: data
type: reference
scripts_exempt: true
---

# 3. Conditional Content

## 3. Conditional Content


**If-Else Logic in Templates:**
```python
"""
Use conditionals to include or exclude content based on data.
"""
from docxtpl import DocxTemplate
from typing import Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum

class ContractType(Enum):
    FULL_TIME = "full_time"
    PART_TIME = "part_time"
    CONTRACTOR = "contractor"


class ConfidentialityLevel(Enum):
    STANDARD = "standard"
    HIGH = "high"
    RESTRICTED = "restricted"


@dataclass
class EmployeeContract:
    """Employee contract data."""
    employee_name: str
    position: str
    department: str
    start_date: str
    contract_type: ContractType
    salary: float
    bonus_eligible: bool
    stock_options: Optional[int] = None
    confidentiality_level: ConfidentialityLevel = ConfidentialityLevel.STANDARD
    probation_period_months: int = 3
    remote_work_allowed: bool = False
    relocation_package: bool = False

    def to_context(self) -> Dict[str, Any]:
        """Convert to template context with conditional flags."""
        return {
            "employee_name": self.employee_name,
            "position": self.position,
            "department": self.department,
            "start_date": self.start_date,
            "salary": f"${self.salary:,.2f}",

            # Contract type flags for conditionals
            "is_full_time": self.contract_type == ContractType.FULL_TIME,
            "is_part_time": self.contract_type == ContractType.PART_TIME,
            "is_contractor": self.contract_type == ContractType.CONTRACTOR,
            "contract_type_display": self.contract_type.value.replace("_", " ").title(),

            # Benefit flags
            "bonus_eligible": self.bonus_eligible,
            "has_stock_options": self.stock_options is not None,
            "stock_options": self.stock_options,

            # Additional terms
            "confidentiality_level": self.confidentiality_level.value,
            "is_high_confidentiality": self.confidentiality_level in [
                ConfidentialityLevel.HIGH,
                ConfidentialityLevel.RESTRICTED
            ],
            "probation_period_months": self.probation_period_months,
            "remote_work_allowed": self.remote_work_allowed,
            "relocation_package": self.relocation_package
        }


def render_contract(
    template_path: str,
    output_path: str,
    contract: EmployeeContract
) -> None:
    """
    Render contract with conditional sections.

    Template syntax for conditionals:
        {% if is_full_time %}
        Full-time benefits section...
        {% endif %}

        {% if bonus_eligible %}
        Bonus clause...
        {% else %}
        Standard compensation only.
        {% endif %}

        {% if is_high_confidentiality %}
        Additional NDA requirements...
        {% endif %}
    """
    template = DocxTemplate(template_path)
    context = contract.to_context()
    template.render(context)
    template.save(output_path)


def render_with_conditions(
    template_path: str,
    output_path: str,
    data: Dict[str, Any]
) -> None:
    """
    Render template with various conditional patterns.

    Supported conditional patterns:
        {% if condition %} ... {% endif %}
        {% if condition %} ... {% else %} ... {% endif %}
        {% if condition %} ... {% elif other %} ... {% else %} ... {% endif %}
        {% if value > 100 %} ... {% endif %}
        {% if value in list %} ... {% endif %}
    """
    template = DocxTemplate(template_path)
    template.render(data)
    template.save(output_path)


# Example contract
contract = EmployeeContract(
    employee_name="John Doe",
    position="Senior Software Engineer",
    department="Engineering",
    start_date="February 1, 2026",
    contract_type=ContractType.FULL_TIME,
    salary=150000,
    bonus_eligible=True,
    stock_options=5000,
    confidentiality_level=ConfidentialityLevel.HIGH,
    remote_work_allowed=True
)

# render_contract("contract_template.docx", "john_doe_contract.docx", contract)


def create_conditional_report(
    template_path: str,
    output_path: str,
    performance_data: Dict
) -> None:
    """
    Create report with conditional formatting based on performance.

    Template example:
        Performance Score: {{ score }}

        {% if score >= 90 %}
        OUTSTANDING PERFORMANCE
        {% elif score >= 75 %}
        MEETS EXPECTATIONS
        {% elif score >= 60 %}
        NEEDS IMPROVEMENT
        {% else %}
        PERFORMANCE PLAN REQUIRED
        {% endif %}

        {% if has_warnings %}
        Warnings:
        {%p for warning in warnings %}
        - {{ warning }}
        {%p endfor %}
        {% endif %}
    """
    template = DocxTemplate(template_path)

    # Add computed flags to context
    score = performance_data.get("score", 0)
    context = {
        **performance_data,
        "performance_level": (
            "Outstanding" if score >= 90 else
            "Meets Expectations" if score >= 75 else
            "Needs Improvement" if score >= 60 else
            "Below Expectations"
        ),
        "has_warnings": len(performance_data.get("warnings", [])) > 0
    }

    template.render(context)
    template.save(output_path)
```
