---
name: python-docx-5-image-insertion-and-positioning
description: 'Sub-skill of python-docx: 5. Image Insertion and Positioning.'
version: 1.0.0
category: data
type: reference
scripts_exempt: true
---

# 5. Image Insertion and Positioning

## 5. Image Insertion and Positioning


```python
"""
Insert and position images in Word documents.
"""
from docx import Document
from docx.shared import Inches, Pt, Cm, Emu
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
from pathlib import Path
from io import BytesIO
from typing import Optional, Tuple
import requests

def add_image_from_url(doc: Document, url: str, width: Optional[float] = None) -> None:
    """Add image from URL to document."""
    response = requests.get(url)
    image_stream = BytesIO(response.content)

    if width:
        doc.add_picture(image_stream, width=Inches(width))
    else:
        doc.add_picture(image_stream)


def add_image_with_caption(
    doc: Document,
    image_path: str,
    caption: str,
    width: float = 4.0,
    figure_num: int = 1
) -> None:
    """Add image with centered caption below."""
    # Add image
    para = doc.add_paragraph()
    para.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = para.add_run()
    run.add_picture(image_path, width=Inches(width))

    # Add caption
    caption_para = doc.add_paragraph()
    caption_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
    caption_run = caption_para.add_run(f'Figure {figure_num}: {caption}')
    caption_run.italic = True
    caption_run.font.size = Pt(10)


def add_inline_image(paragraph, image_path: str, width: float = 1.0) -> None:
    """Add image inline with text."""
    run = paragraph.add_run()
    run.add_picture(image_path, width=Inches(width))


def create_document_with_images(output_path: str, sample_image_path: str) -> None:
    """Create document with various image placements."""
    doc = Document()

    doc.add_heading('Image Examples', level=0)

    # Check if sample image exists
    if not Path(sample_image_path).exists():
        # Create a placeholder message if no image
        doc.add_paragraph(
            'Note: Sample image not found. Replace with actual image path.'
        )
        doc.save(output_path)
        return

    # Simple centered image
    doc.add_heading('Centered Image', level=1)
    doc.add_paragraph('The image below is centered on the page:')

    img_para = doc.add_paragraph()
    img_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = img_para.add_run()
    run.add_picture(sample_image_path, width=Inches(4))

    # Image with caption
    doc.add_heading('Image with Caption', level=1)
    doc.add_paragraph('Images can include descriptive captions:')
    add_image_with_caption(
        doc,
        sample_image_path,
        'Sample chart showing quarterly results',
        width=4.0,
        figure_num=1
    )

    # Multiple images in a row (using table)
    doc.add_heading('Multiple Images Side by Side', level=1)
    doc.add_paragraph('Use tables to arrange images side by side:')

    # Create 1x3 table for images
    table = doc.add_table(rows=2, cols=3)

    for i in range(3):
        cell = table.cell(0, i)
        para = cell.paragraphs[0]
        para.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = para.add_run()
        run.add_picture(sample_image_path, width=Inches(1.8))

        # Add caption below each image
        caption_cell = table.cell(1, i)
        caption_cell.paragraphs[0].text = f'Image {i + 1}'
        caption_cell.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER

    # Inline image with text
    doc.add_heading('Inline Images', level=1)
    para = doc.add_paragraph('You can include small images ')
    run = para.add_run()
    run.add_picture(sample_image_path, width=Inches(0.5))
    para.add_run(' inline with your text for icons or small graphics.')

    doc.save(output_path)
    print(f"Document with images saved to {output_path}")


# Usage (provide path to actual image)
# create_document_with_images('image_document.docx', 'sample_chart.png')
```
