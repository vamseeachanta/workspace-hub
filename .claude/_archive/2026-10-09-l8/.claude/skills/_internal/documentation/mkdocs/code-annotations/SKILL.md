---
name: mkdocs-code-annotations
description: 'Sub-skill of mkdocs: Code Annotations.'
version: 1.0.0
category: _internal
type: reference
scripts_exempt: true
---

# Code Annotations

## Code Annotations


```python
def calculate_area(radius: float) -> float:  # (1)!
    """Calculate the area of a circle."""
    import math  # (2)!
    return math.pi * radius ** 2  # (3)!
```

1. Type hints improve code readability
2. Import inside function for demonstration
3. Uses the formula: A = pi * r^2
