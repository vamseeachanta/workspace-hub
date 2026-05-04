---
name: docx-templates-5-image-insertion
description: 'Sub-skill of docx-templates: 5. Image Insertion.'
version: 1.0.0
category: data
type: reference
scripts_exempt: true
---

# 5. Image Insertion

## 5. Image Insertion


**Adding Images to Templates:**
```python
"""
Insert images into templates with proper sizing.
"""
from docxtpl import DocxTemplate, InlineImage
from docx.shared import Mm, Inches, Cm
from pathlib import Path
from typing import Optional, Union
from io import BytesIO
import requests

def add_image_to_template(
    template_path: str,
    output_path: str,
    image_path: str,
    context: dict,
    width: Optional[Union[Mm, Inches, Cm]] = None,
    height: Optional[Union[Mm, Inches, Cm]] = None
) -> None:
    """
    Add an image to a template.

    Template syntax:
        {{ image }}

    Args:
        template_path: Path to template
        output_path: Path for output
        image_path: Path to image file
        context: Additional context data
        width: Image width (optional)
        height: Image height (optional)
    """
    template = DocxTemplate(template_path)

    # Create InlineImage
    image = InlineImage(
        template,
        image_path,
        width=width,
        height=height
    )

    # Add image to context
    context["image"] = image

    template.render(context)
    template.save(output_path)


def add_image_from_url(
    template: DocxTemplate,
    url: str,
    width: Optional[Mm] = None
) -> InlineImage:
    """
    Create InlineImage from URL.

    Args:
        template: DocxTemplate instance
        url: Image URL
        width: Desired width

    Returns:
        InlineImage object
    """
    response = requests.get(url)
    response.raise_for_status()

    image_stream = BytesIO(response.content)

    return InlineImage(
        template,
        image_stream,
        width=width
    )


def render_document_with_images(
    template_path: str,
    output_path: str,
    data: dict,
    images: dict
) -> None:
    """
    Render document with multiple images.

    Template:
        Company Logo: {{ logo }}

        Product Images:
        {% for product in products %}
        {{ product.name }}: {{ product.image }}
        {% endfor %}
    """
    template = DocxTemplate(template_path)

    # Process images
    context = data.copy()

    for key, image_info in images.items():
        if isinstance(image_info, str):
            # Simple path
            context[key] = InlineImage(template, image_info, width=Mm(50))
        elif isinstance(image_info, dict):
            # Dict with path and dimensions
            context[key] = InlineImage(
                template,
                image_info["path"],
                width=image_info.get("width"),
                height=image_info.get("height")
            )

    template.render(context)
    template.save(output_path)


class ImageHandler:
    """
    Handle images for template rendering.
    """

    def __init__(self, template: DocxTemplate):
        self.template = template
        self._images: dict = {}

    def add_image(
        self,
        key: str,
        source: Union[str, BytesIO],
        width: Optional[int] = None,
        height: Optional[int] = None,
        unit: str = "mm"
    ) -> 'ImageHandler':
        """
        Add an image to the handler.

        Args:
            key: Context key for the image
            source: File path or BytesIO stream
            width: Width in specified units
            height: Height in specified units
            unit: Unit type ('mm', 'inches', 'cm')
        """
        # Convert units
        if unit == "mm":
            w = Mm(width) if width else None
            h = Mm(height) if height else None
        elif unit == "inches":
            w = Inches(width) if width else None
            h = Inches(height) if height else None
        elif unit == "cm":
            w = Cm(width) if width else None
            h = Cm(height) if height else None
        else:
            w = h = None

        self._images[key] = InlineImage(
            self.template,
            source,
            width=w,
            height=h
        )

        return self

    def add_image_from_url(
        self,
        key: str,
        url: str,
        width: int = 50,
        unit: str = "mm"
    ) -> 'ImageHandler':
        """Add image from URL."""
        response = requests.get(url)
        response.raise_for_status()

        image_stream = BytesIO(response.content)

        return self.add_image(key, image_stream, width=width, unit=unit)

    def get_context(self) -> dict:
        """Get images as context dictionary."""

*Content truncated — see parent skill for full reference.*
