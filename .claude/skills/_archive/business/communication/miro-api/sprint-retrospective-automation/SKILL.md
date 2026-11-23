---
name: miro-api-sprint-retrospective-automation
description: 'Sub-skill of miro-api: Sprint Retrospective Automation.'
version: 1.0.0
category: business
type: reference
scripts_exempt: true
---

# Sprint Retrospective Automation

## Sprint Retrospective Automation


```python
# retro_automation.py
# ABOUTME: Automated sprint retrospective board creation
# ABOUTME: Creates templated retro board with categories

from miro_api import Miro
import os
from datetime import datetime

miro = Miro(access_token=os.environ.get("MIRO_ACCESS_TOKEN"))


def create_retrospective_board(
    sprint_number: int,
    team_name: str,
    team_id: str = None,
) -> dict:
    """Create a complete retrospective board for a sprint"""

    team_id = team_id or os.environ.get("MIRO_TEAM_ID")

    # Create board
    board_name = f"Sprint {sprint_number} Retrospective - {team_name}"
    board = miro.boards.create(
        name=board_name,
        description=f"Retrospective for Sprint {sprint_number}",
        team_id=team_id,
    )
    board_id = board.id

    # Create frames for categories
    categories = [
        {"title": "What Went Well", "color": "#c8e6c9", "x": 0},
        {"title": "What Could Be Improved", "color": "#ffcdd2", "x": 700},
        {"title": "Action Items", "color": "#bbdefb", "x": 1400},
    ]

    frames = []
    for cat in categories:
        frame = miro.frames.create(
            board_id=board_id,
            data={"title": cat["title"], "format": "custom"},
            style={"fillColor": cat["color"]},
            position={"x": cat["x"], "y": 0, "origin": "center"},
            geometry={"width": 600, "height": 800},
        )
        frames.append({"id": frame.id, "title": cat["title"]})

        # Add placeholder stickies
        for i in range(3):
            miro.sticky_notes.create(
                board_id=board_id,
                data={"content": "Add your thoughts here..."},
                style={"fillColor": cat["color"]},
                position={
                    "x": cat["x"],
                    "y": -200 + (i * 150),
                    "origin": "center",
                },
            )

    # Create header
    miro.texts.create(
        board_id=board_id,
        data={
            "content": f"<strong>Sprint {sprint_number} Retrospective</strong><br>{datetime.now().strftime('%B %d, %Y')}"
        },
        style={"fontSize": "36", "textAlign": "center"},
        position={"x": 700, "y": -500, "origin": "center"},
        geometry={"width": 800},
    )

    # Add voting instructions
    miro.texts.create(
        board_id=board_id,
        data={
            "content": "Instructions:<br>1. Add sticky notes to each category<br>2. Vote on items using dots<br>3. Discuss top voted items<br>4. Create action items"
        },
        style={"fontSize": "14"},
        position={"x": -400, "y": 0, "origin": "center"},
        geometry={"width": 300},
    )

    return {
        "board_id": board_id,
        "view_link": board.view_link,
        "frames": frames,
    }


def create_sprint_planning_board(
    sprint_number: int,
    team_name: str,
    stories: list,
) -> dict:
    """Create a sprint planning board with user stories"""

    board = miro.boards.create(
        name=f"Sprint {sprint_number} Planning - {team_name}",
        description=f"Planning board for Sprint {sprint_number}",
        team_id=os.environ.get("MIRO_TEAM_ID"),
    )
    board_id = board.id

    # Create Kanban columns
    columns = ["Backlog", "To Do", "In Progress", "Review", "Done"]
    col_width = 350
    col_height = 1000

    for i, col in enumerate(columns):
        miro.frames.create(
            board_id=board_id,
            data={"title": col, "format": "custom"},
            style={"fillColor": "#f5f5f5"},
            position={"x": i * (col_width + 30), "y": 0, "origin": "center"},
            geometry={"width": col_width, "height": col_height},
        )

    # Add stories to backlog
    for j, story in enumerate(stories):
        miro.cards.create(
            board_id=board_id,
            data={
                "title": story.get("title", "User Story"),
                "description": story.get("description", ""),
            },
            position={"x": 0, "y": -300 + (j * 150), "origin": "center"},
            geometry={"width": 300, "height": 120},
        )

    return {"board_id": board_id, "view_link": board.view_link}


if __name__ == "__main__":
    # Create retrospective board
    retro = create_retrospective_board(sprint_number=15, team_name="Platform Team")
    print(f"Retro board: {retro['view_link']}")

    # Create planning board
    stories = [
        {"title": "As a user, I want to login with SSO", "description": "Implement SSO authentication"},
        {"title": "As a user, I want dark mode", "description": "Add dark mode support"},
    ]
    planning = create_sprint_planning_board(sprint_number=16, team_name="Platform Team", stories=stories)
    print(f"Planning board: {planning['view_link']}")
```
