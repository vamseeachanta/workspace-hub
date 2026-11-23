---
name: python-docx-common-issues
description: 'Sub-skill of python-docx: Common Issues.'
version: 1.0.0
category: data
type: reference
scripts_exempt: true
---

# Common Issues

## Common Issues


#### 1. Font Not Appearing Correctly

```python
# Problem: Font doesn't display in Word
# Solution: Use fonts available on target system

# Check available fonts
def get_available_fonts():
    """List fonts that should work cross-platform."""
    return [
        'Arial', 'Calibri', 'Times New Roman',
        'Georgia', 'Verdana', 'Tahoma',
        'Consolas', 'Courier New'
    ]

# Use fallback fonts
def set_font_with_fallback(run, preferred_font, fallback='Arial'):
    run.font.name = preferred_font
    # Set East Asian font as fallback
    run._element.rPr.rFonts.set(qn('w:eastAsia'), fallback)
```

#### 2. Table Width Issues

```python
# Problem: Table columns not sized correctly
# Solution: Explicitly set column widths

def set_column_widths(table, widths):
    """Set explicit column widths for table."""
    for row in table.rows:
        for idx, (cell, width) in enumerate(zip(row.cells, widths)):
            cell.width = width

# Usage
widths = [Inches(1), Inches(3), Inches(2)]
set_column_widths(table, widths)
```

#### 3. Image Not Displaying

```python
# Problem: Image doesn't appear in document
# Solution: Verify image path and format

from pathlib import Path
from PIL import Image

def validate_and_add_image(doc, image_path, width=None):
    """Validate image before adding to document."""
    path = Path(image_path)

    if not path.exists():
        raise FileNotFoundError(f"Image not found: {image_path}")

    # Check format
    supported_formats = {'.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff'}
    if path.suffix.lower() not in supported_formats:
        raise ValueError(f"Unsupported format: {path.suffix}")

    # Validate image can be opened
    try:
        with Image.open(image_path) as img:
            img.verify()
    except Exception as e:
        raise ValueError(f"Invalid image file: {e}")

    # Add to document
    if width:
        doc.add_picture(str(image_path), width=Inches(width))
    else:
        doc.add_picture(str(image_path))
```

#### 4. Style Not Applied

```python
# Problem: Custom style not appearing
# Solution: Ensure style exists before using

def safe_apply_style(paragraph, style_name, doc):
    """Apply style with fallback if not found."""
    try:
        paragraph.style = style_name
    except KeyError:
        # Style doesn't exist, create it or use default
        if style_name not in [s.name for s in doc.styles]:
            # Create minimal style
            from docx.enum.style import WD_STYLE_TYPE
            doc.styles.add_style(style_name, WD_STYLE_TYPE.PARAGRAPH)
        paragraph.style = style_name
```
