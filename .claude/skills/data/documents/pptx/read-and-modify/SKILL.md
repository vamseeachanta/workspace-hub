---
name: pptx-read-and-modify
description: 'Sub-skill of pptx: Read and Modify (+2).'
version: 1.1.0
category: data
type: reference
scripts_exempt: true
---

# Read and Modify (+2)

## Read and Modify


```python
from pptx import Presentation

prs = Presentation("existing.pptx")

for slide in prs.slides:
    for shape in slide.shapes:
        if shape.has_text_frame:
            for paragraph in shape.text_frame.paragraphs:
                for run in paragraph.runs:
                    if "old text" in run.text:
                        run.text = run.text.replace("old text", "new text")

prs.save("modified.pptx")
```

## Extract Text


```python
from pptx import Presentation

prs = Presentation("presentation.pptx")

for slide_num, slide in enumerate(prs.slides, 1):
    print(f"\n--- Slide {slide_num} ---")
    for shape in slide.shapes:
        if shape.has_text_frame:
            for paragraph in shape.text_frame.paragraphs:
                print(paragraph.text)
```

## Copy Slides


```python
from pptx import Presentation
from copy import deepcopy

prs = Presentation("source.pptx")
# Note: python-pptx doesn't directly support slide copying
# Use slide layouts from the same presentation instead
```
