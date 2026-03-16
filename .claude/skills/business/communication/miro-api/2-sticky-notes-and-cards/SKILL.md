---
name: miro-api-2-sticky-notes-and-cards
description: 'Sub-skill of miro-api: 2. Sticky Notes and Cards.'
version: 1.0.0
category: business
type: reference
scripts_exempt: true
---

# 2. Sticky Notes and Cards

## 2. Sticky Notes and Cards


```python
# sticky_notes.py
# ABOUTME: Sticky note and card creation
# ABOUTME: Create, position, and style sticky notes

from miro_api import Miro
import os

miro = Miro(access_token=os.environ.get("MIRO_ACCESS_TOKEN"))


def create_sticky_note(
    board_id: str,
    content: str,
    x: float = 0,
    y: float = 0,
    color: str = "yellow",
    width: float = 200,
) -> dict:
    """Create a sticky note on a board"""

    # Color mapping
    colors = {
        "yellow": "yellow",
        "green": "green",
        "blue": "blue",
        "pink": "pink",
        "orange": "orange",
        "purple": "violet",
        "gray": "gray",
        "cyan": "cyan",
        "red": "red",
        "light_yellow": "light_yellow",
        "light_green": "light_green",
        "light_blue": "light_blue",
        "light_pink": "light_pink",
    }

    sticky = miro.sticky_notes.create(
        board_id=board_id,
        data={"content": content, "shape": "square"},
        style={"fillColor": colors.get(color, "yellow")},
        position={"x": x, "y": y, "origin": "center"},
        geometry={"width": width},
    )

    return {
        "id": sticky.id,
        "content": sticky.data.content,
        "position": {"x": sticky.position.x, "y": sticky.position.y},
        "color": sticky.style.fill_color,
    }


def create_sticky_grid(
    board_id: str,
    items: list,
    start_x: float = 0,
    start_y: float = 0,
    columns: int = 4,
    spacing: float = 250,
    color: str = "yellow",
) -> list:
    """Create a grid of sticky notes"""
    created = []

    for i, item in enumerate(items):
        row = i // columns
        col = i % columns

        x = start_x + (col * spacing)
        y = start_y + (row * spacing)

        sticky = create_sticky_note(
            board_id=board_id, content=item, x=x, y=y, color=color
        )
        created.append(sticky)

    return created


def create_card(
    board_id: str,
    title: str,
    description: str = "",
    x: float = 0,
    y: float = 0,
    assignee_id: str = None,
    due_date: str = None,
    tags: list = None,
) -> dict:
    """Create a card widget"""

    card_data = {"title": title, "description": description}

    if assignee_id:
        card_data["assigneeId"] = assignee_id
    if due_date:
        card_data["dueDate"] = due_date
    if tags:
        card_data["tagIds"] = tags

    card = miro.cards.create(
        board_id=board_id,
        data=card_data,
        position={"x": x, "y": y, "origin": "center"},
        geometry={"width": 320, "height": 200},
    )

    return {
        "id": card.id,
        "title": card.data.title,
        "position": {"x": card.position.x, "y": card.position.y},
    }


def update_sticky_note(
    board_id: str, sticky_id: str, content: str = None, color: str = None
) -> dict:
    """Update a sticky note"""
    update_data = {}

    if content:
        update_data["data"] = {"content": content}
    if color:
        update_data["style"] = {"fillColor": color}

    sticky = miro.sticky_notes.update(board_id, sticky_id, **update_data)

    return {"id": sticky.id, "content": sticky.data.content}


def delete_sticky_note(board_id: str, sticky_id: str) -> bool:
    """Delete a sticky note"""
    miro.sticky_notes.delete(board_id, sticky_id)
    return True


# Retrospective board example
def create_retro_board(board_id: str) -> dict:
    """Create a retrospective board layout"""

    # Create category headers
    categories = [
        {"title": "What went well", "color": "green", "x": 0},
        {"title": "What to improve", "color": "pink", "x": 500},
        {"title": "Action items", "color": "blue", "x": 1000},
    ]

    created_stickies = {}

    for cat in categories:
        # Create header sticky
        header = create_sticky_note(
            board_id=board_id,
            content=f"<strong>{cat['title']}</strong>",
            x=cat["x"],
            y=-200,
            color=cat["color"],
            width=400,
        )
        created_stickies[cat["title"]] = [header]

        # Create placeholder stickies
        for i in range(3):
            placeholder = create_sticky_note(
                board_id=board_id,
                content="Add your thoughts here...",
                x=cat["x"],
                y=i * 150,
                color=cat["color"],
            )
            created_stickies[cat["title"]].append(placeholder)

    return created_stickies


if __name__ == "__main__":
    board_id = "YOUR_BOARD_ID"

    # Create grid of stickies
    items = ["Task 1", "Task 2", "Task 3", "Task 4", "Task 5", "Task 6"]
    stickies = create_sticky_grid(
        board_id=board_id, items=items, columns=3, color="blue"

*Content truncated — see parent skill for full reference.*
