---
name: python-pptx-common-issues
description: 'Sub-skill of python-pptx: Common Issues.'
version: 1.0.0
category: data
type: reference
scripts_exempt: true
---

# Common Issues

## Common Issues


#### 1. Layout Not Found

```python
# Problem: Slide layout index out of range
# Solution: Check available layouts

prs = Presentation()
for i, layout in enumerate(prs.slide_layouts):
    print(f"{i}: {layout.name}")

# Common layouts:
# 0: Title Slide
# 1: Title and Content
# 5: Title Only
# 6: Blank
```

#### 2. Text Overflow

```python
# Problem: Text doesn't fit in shape
# Solution: Adjust font size or enable auto-fit

tf = shape.text_frame
tf.auto_size = True  # Enable auto-sizing
# Or manually adjust
tf.paragraphs[0].font.size = Pt(10)
```

#### 3. Chart Not Displaying

```python
# Problem: Chart appears empty
# Solution: Verify data structure

# DO: Ensure categories and series match
chart_data = CategoryChartData()
chart_data.categories = ['A', 'B', 'C']  # Must have values
chart_data.add_series('Series 1', (1, 2, 3))  # Same length
```
