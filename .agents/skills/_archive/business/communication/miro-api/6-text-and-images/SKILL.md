---
name: miro-api-6-text-and-images
description: 'Sub-skill of miro-api: 6. Text and Images.'
version: 1.0.0
category: business
type: reference
scripts_exempt: true
---

# 6. Text and Images

## 6. Text and Images


```python
# text_images.py
# ABOUTME: Text elements and image handling
# ABOUTME: Create text boxes, embed images, and manage media

from miro_api import Miro
import os
import requests
from io import BytesIO

miro = Miro(access_token=os.environ.get("MIRO_ACCESS_TOKEN"))


def create_text(
    board_id: str,
    content: str,
    x: float = 0,
    y: float = 0,
    width: float = 200,
    font_size: int = 14,
    font_family: str = "arial",
    text_align: str = "left",
    color: str = "#000000",
) -> dict:
    """Create a text element"""

    text = miro.texts.create(
        board_id=board_id,
        data={"content": content},
        style={
            "color": color,
            "fillOpacity": "1.0",
            "fontFamily": font_family,
            "fontSize": str(font_size),
            "textAlign": text_align,
        },
        position={"x": x, "y": y, "origin": "center"},
        geometry={"width": width},
    )

    return {
        "id": text.id,
        "content": text.data.content,
        "position": {"x": text.position.x, "y": text.position.y},
    }


def create_heading(
    board_id: str,
    content: str,
    x: float = 0,
    y: float = 0,
    level: int = 1,
) -> dict:
    """Create a heading text element"""

    font_sizes = {1: 36, 2: 28, 3: 22, 4: 18}
    font_size = font_sizes.get(level, 14)

    return create_text(
        board_id=board_id,
        content=f"<strong>{content}</strong>",
        x=x,
        y=y,
        width=500,
        font_size=font_size,
    )


def create_bullet_list(
    board_id: str,
    items: list,
    x: float = 0,
    y: float = 0,
) -> dict:
    """Create a bulleted list"""

    content = "<ul>" + "".join(f"<li>{item}</li>" for item in items) + "</ul>"

    return create_text(
        board_id=board_id,
        content=content,
        x=x,
        y=y,
        width=400,
    )


def upload_image_from_url(
    board_id: str,
    image_url: str,
    x: float = 0,
    y: float = 0,
    width: float = None,
    title: str = None,
) -> dict:
    """Create an image from a URL"""

    image_data = {"url": image_url}
    if title:
        image_data["title"] = title

    geometry = {}
    if width:
        geometry["width"] = width

    image = miro.images.create(
        board_id=board_id,
        data=image_data,
        position={"x": x, "y": y, "origin": "center"},
        geometry=geometry if geometry else None,
    )

    return {
        "id": image.id,
        "position": {"x": image.position.x, "y": image.position.y},
    }


def upload_image_from_file(
    board_id: str,
    file_path: str,
    x: float = 0,
    y: float = 0,
    width: float = None,
) -> dict:
    """Upload an image from a local file"""

    with open(file_path, "rb") as f:
        image_data = f.read()

    # Use the image upload endpoint
    headers = {
        "Authorization": f"Bearer {os.environ.get('MIRO_ACCESS_TOKEN')}",
    }

    files = {"resource": (os.path.basename(file_path), image_data)}
    data = {"position": f'{{"x": {x}, "y": {y}, "origin": "center"}}'}

    if width:
        data["geometry"] = f'{{"width": {width}}}'

    response = requests.post(
        f"https://api.miro.com/v2/boards/{board_id}/images",
        headers=headers,
        files=files,
        data=data,
    )
    response.raise_for_status()

    return response.json()


def create_embed(
    board_id: str,
    url: str,
    x: float = 0,
    y: float = 0,
    width: float = 400,
    height: float = 300,
    mode: str = "modal",
) -> dict:
    """Create an embedded content (web page, video, etc.)

    Modes: inline, modal
    """

    embed = miro.embeds.create(
        board_id=board_id,
        data={"url": url, "mode": mode},
        position={"x": x, "y": y, "origin": "center"},
        geometry={"width": width, "height": height},
    )

    return {
        "id": embed.id,
        "url": embed.data.url,
        "position": {"x": embed.position.x, "y": embed.position.y},
    }


def create_document_section(
    board_id: str,
    title: str,

*Content truncated — see parent skill for full reference.*
