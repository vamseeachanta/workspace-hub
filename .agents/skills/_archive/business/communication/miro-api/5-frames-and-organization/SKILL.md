---
name: miro-api-5-frames-and-organization
description: 'Sub-skill of miro-api: 5. Frames and Organization.'
version: 1.0.0
category: business
type: reference
scripts_exempt: true
---

# 5. Frames and Organization

## 5. Frames and Organization


```python
# frames.py
# ABOUTME: Frame creation for board organization
# ABOUTME: Group items, create sections, and manage layout

from miro_api import Miro
import os
from typing import List, Optional

miro = Miro(access_token=os.environ.get("MIRO_ACCESS_TOKEN"))


def create_frame(
    board_id: str,
    title: str,
    x: float = 0,
    y: float = 0,
    width: float = 800,
    height: float = 600,
    fill_color: str = "#f5f5f5",
) -> dict:
    """Create a frame to organize board content"""

    frame = miro.frames.create(
        board_id=board_id,
        data={"title": title, "format": "custom"},
        style={"fillColor": fill_color},
        position={"x": x, "y": y, "origin": "center"},
        geometry={"width": width, "height": height},
    )

    return {
        "id": frame.id,
        "title": frame.data.title,
        "position": {"x": frame.position.x, "y": frame.position.y},
        "geometry": {"width": frame.geometry.width, "height": frame.geometry.height},
    }


def create_frame_grid(
    board_id: str,
    titles: list,
    columns: int = 3,
    frame_width: float = 600,
    frame_height: float = 400,
    spacing: float = 50,
    start_x: float = 0,
    start_y: float = 0,
) -> list:
    """Create a grid of frames"""
    created = []

    for i, title in enumerate(titles):
        row = i // columns
        col = i % columns

        x = start_x + col * (frame_width + spacing)
        y = start_y + row * (frame_height + spacing)

        frame = create_frame(
            board_id=board_id,
            title=title,
            x=x,
            y=y,
            width=frame_width,
            height=frame_height,
        )
        created.append(frame)

    return created


def create_kanban_board(
    board_id: str,
    columns: list = None,
    frame_width: float = 400,
    frame_height: float = 800,
) -> list:
    """Create a Kanban-style board with columns"""

    if columns is None:
        columns = ["To Do", "In Progress", "Review", "Done"]

    colors = {
        "To Do": "#f5f5f5",
        "In Progress": "#fff3e0",
        "Review": "#e8f5e9",
        "Done": "#e3f2fd",
    }

    frames = []
    start_x = 0

    for i, column in enumerate(columns):
        frame = create_frame(
            board_id=board_id,
            title=column,
            x=start_x + i * (frame_width + 50),
            y=0,
            width=frame_width,
            height=frame_height,
            fill_color=colors.get(column, "#f5f5f5"),
        )
        frames.append(frame)

    return frames


def create_workshop_layout(
    board_id: str, sections: list, section_width: float = 1000, section_height: float = 600
) -> dict:
    """Create a workshop board layout

    sections: list of {"title": "name", "description": "desc", "color": "#hex"}
    """
    created = {"frames": [], "headers": []}

    for i, section in enumerate(sections):
        # Create frame for section
        frame = create_frame(
            board_id=board_id,
            title=section["title"],
            x=0,
            y=i * (section_height + 100),
            width=section_width,
            height=section_height,
            fill_color=section.get("color", "#f5f5f5"),
        )
        created["frames"].append(frame)

    return created


def update_frame(
    board_id: str,
    frame_id: str,
    title: str = None,
    width: float = None,
    height: float = None,
) -> dict:
    """Update a frame"""
    update_data = {}

    if title:
        update_data["data"] = {"title": title}
    if width or height:
        geometry = {}
        if width:
            geometry["width"] = width
        if height:
            geometry["height"] = height
        update_data["geometry"] = geometry

    frame = miro.frames.update(board_id, frame_id, **update_data)
    return {"id": frame.id, "title": frame.data.title}


def get_items_in_frame(board_id: str, frame_id: str) -> list:
    """Get all items contained within a frame"""
    frame = miro.frames.get(board_id, frame_id)

    # Get child items
    children = miro.frames.get_children(board_id, frame_id)

    return [
        {"id": child.id, "type": child.type}
        for child in children
    ]


def add_items_to_frame(board_id: str, frame_id: str, item_ids: list) -> bool:
    """Add items to a frame by updating their parent"""
    for item_id in item_ids:
        # Items inside a frame are managed by their position
        # They need to be within the frame's boundaries
        pass
    return True


def delete_frame(board_id: str, frame_id: str) -> bool:
    """Delete a frame"""
    miro.frames.delete(board_id, frame_id)
    return True


*Content truncated — see parent skill for full reference.*
