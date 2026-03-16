---
name: docx-templates-1-template-design
description: 'Sub-skill of docx-templates: 1. Template Design (+2).'
version: 1.0.0
category: data
type: reference
scripts_exempt: true
---

# 1. Template Design (+2)

## 1. Template Design


```python
"""Best practices for template design."""

# DO: Use meaningful variable names
good_context = {
    "customer_name": "John Smith",
    "invoice_date": "2026-01-17",
    "total_amount": "$1,500.00"
}

# DON'T: Use cryptic names
bad_context = {
    "cn": "John Smith",
    "d": "2026-01-17",
    "t": "$1,500.00"
}

# DO: Organize context with nested objects
organized_context = {
    "customer": {
        "name": "John Smith",
        "email": "john@example.com",
        "address": {
            "street": "123 Main St",
            "city": "New York"
        }
    },
    "invoice": {
        "number": "INV-001",
        "date": "2026-01-17",
        "items": [...]
    }
}

# DO: Include computed values
def prepare_context(data: dict) -> dict:
    """Prepare context with computed values."""
    context = data.copy()

    # Add computed fields
    if "items" in context:
        context["item_count"] = len(context["items"])
        context["subtotal"] = sum(i["total"] for i in context["items"])

    # Add display flags
    context["has_discount"] = context.get("discount", 0) > 0

    return context
```


## 2. Error Handling


```python
"""Robust error handling for template rendering."""
from typing import Tuple, Optional

def safe_render(
    template_path: str,
    output_path: str,
    context: dict
) -> Tuple[bool, Optional[str]]:
    """
    Safely render template with error handling.

    Returns:
        Tuple of (success, error_message)
    """
    try:
        # Validate template exists
        if not Path(template_path).exists():
            return False, f"Template not found: {template_path}"

        # Load and render
        template = DocxTemplate(template_path)

        # Check for missing variables
        required_vars = template.get_undeclared_template_variables()
        missing = [v for v in required_vars if v not in context]
        if missing:
            return False, f"Missing variables: {missing}"

        template.render(context)

        # Ensure output directory exists
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)

        template.save(output_path)
        return True, None

    except Exception as e:
        return False, str(e)
```


## 3. Performance Optimization


```python
"""Optimize batch document generation."""

# DO: Use parallel processing for large batches
def optimized_batch_generation(
    template_path: str,
    records: List[Dict],
    output_dir: str,
    batch_size: int = 100
) -> List[str]:
    """Generate documents in optimized batches."""
    from concurrent.futures import ThreadPoolExecutor

    def process_batch(batch_records):
        results = []
        for record in batch_records:
            template = DocxTemplate(template_path)
            template.render(record)
            output_path = Path(output_dir) / f"{record['id']}.docx"
            template.save(str(output_path))
            results.append(str(output_path))
        return results

    # Process in batches
    all_results = []
    batches = [records[i:i+batch_size] for i in range(0, len(records), batch_size)]

    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = [executor.submit(process_batch, b) for b in batches]
        for future in futures:
            all_results.extend(future.result())

    return all_results
```
