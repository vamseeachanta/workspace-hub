---
name: pandoc-2-image-management
description: 'Sub-skill of pandoc: 2. Image Management (+2).'
version: 1.0.0
category: development
type: reference
scripts_exempt: true
---

# 2. Image Management (+2)

## 2. Image Management


```markdown
<!-- Recommended image syntax -->

![Image caption](images/diagram.png){width=80%}

<!-- With cross-reference -->
![System architecture](images/arch.png){#fig:arch width=100%}

See @fig:arch for the overview.


*See sub-skills for full details.*

## 3. Code Block Best Practices


````markdown
<!-- Named code blocks with line numbers -->
```python {.numberLines startFrom="1"}
def process_data(data: list) -> dict:
    """Process input data and return results."""
    results = {}
    for item in data:
        results[item.id] = transform(item)
    return results
```

*See sub-skills for full details.*

## 4. Table Formatting


```markdown
<!-- Simple table -->
| Column 1 | Column 2 | Column 3 |
|----------|----------|----------|
| Data 1   | Data 2   | Data 3   |
| Data 4   | Data 5   | Data 6   |

<!-- Table with caption and reference -->
| Metric | Value | Unit |
|--------|-------|------|

*See sub-skills for full details.*
