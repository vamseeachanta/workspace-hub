---
name: docx-templates-template-variables-not-rendering
description: 'Sub-skill of docx-templates: Template Variables Not Rendering (+2).'
version: 1.0.0
category: data
type: reference
scripts_exempt: true
---

# Template Variables Not Rendering (+2)

## Template Variables Not Rendering


```python
# Problem: Variables appear as {{ variable }} in output
# Solution: Check variable syntax and context keys

def diagnose_template(template_path: str, context: dict):
    """Diagnose template rendering issues."""
    template = DocxTemplate(template_path)

    # Get expected variables
    expected = template.get_undeclared_template_variables()
    print(f"Template expects: {expected}")

    # Check context
    provided = set(context.keys())
    print(f"Context provides: {provided}")

    # Find mismatches
    missing = expected - provided
    if missing:
        print(f"MISSING: {missing}")
```


## Loop Not Iterating


```python
# Problem: Loop content not appearing
# Solution: Verify loop syntax and data structure

# CORRECT loop syntax in template:
# {%tr for item in items %}
#   {{ item.name }}
# {%tr endfor %}

# Ensure data is a list
context = {
    "items": [
        {"name": "Item 1"},  # Must be dict or object
        {"name": "Item 2"}
    ]
}
```


## Image Not Appearing


```python
# Problem: Image placeholder shows error
# Solution: Verify image path and format

from pathlib import Path

def validate_image(image_path: str) -> bool:
    """Validate image file."""
    path = Path(image_path)

    if not path.exists():
        print(f"Image not found: {image_path}")
        return False

    valid_extensions = {'.png', '.jpg', '.jpeg', '.gif', '.bmp'}
    if path.suffix.lower() not in valid_extensions:
        print(f"Invalid format: {path.suffix}")
        return False

    return True
```
