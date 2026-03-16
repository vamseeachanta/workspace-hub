---
name: miro-api-1-board-management
description: 'Sub-skill of miro-api: 1. Board Management.'
version: 1.0.0
category: business
type: reference
scripts_exempt: true
---

# 1. Board Management

## 1. Board Management


```python
# boards.py
# ABOUTME: Miro board management operations
# ABOUTME: Create, read, update, delete boards

import os
from miro_api import Miro
from dotenv import load_dotenv

load_dotenv()

# Initialize Miro client
miro = Miro(access_token=os.environ.get("MIRO_ACCESS_TOKEN"))


def create_board(name: str, description: str = "", team_id: str = None) -> dict:
    """Create a new Miro board"""
    team_id = team_id or os.environ.get("MIRO_TEAM_ID")

    board = miro.boards.create(
        name=name,
        description=description,
        team_id=team_id,
        policy={
            "permissionsPolicy": {
                "collaborationToolsStartAccess": "all_editors",
                "copyAccess": "anyone",
                "sharingAccess": "team_members_with_editing_rights",
            },
            "sharingPolicy": {
                "access": "private",
                "inviteToAccountAndBoardLinkAccess": "editor",
                "organizationAccess": "private",
                "teamAccess": "edit",
            },
        },
    )

    return {
        "id": board.id,
        "name": board.name,
        "view_link": board.view_link,
        "created_at": board.created_at,
    }


def get_board(board_id: str) -> dict:
    """Get board details"""
    board = miro.boards.get(board_id)

    return {
        "id": board.id,
        "name": board.name,
        "description": board.description,
        "view_link": board.view_link,
        "created_at": board.created_at,
        "modified_at": board.modified_at,
    }


def list_boards(team_id: str = None, limit: int = 50) -> list:
    """List all boards in a team"""
    team_id = team_id or os.environ.get("MIRO_TEAM_ID")

    boards = miro.boards.get_all(team_id=team_id, limit=limit)

    return [
        {
            "id": board.id,
            "name": board.name,
            "view_link": board.view_link,
        }
        for board in boards
    ]


def update_board(board_id: str, name: str = None, description: str = None) -> dict:
    """Update board properties"""
    update_data = {}
    if name:
        update_data["name"] = name
    if description:
        update_data["description"] = description

    board = miro.boards.update(board_id, **update_data)

    return {"id": board.id, "name": board.name, "description": board.description}


def delete_board(board_id: str) -> bool:
    """Delete a board"""
    miro.boards.delete(board_id)
    return True


def copy_board(board_id: str, new_name: str, team_id: str = None) -> dict:
    """Copy an existing board"""
    team_id = team_id or os.environ.get("MIRO_TEAM_ID")

    board = miro.boards.copy(board_id, name=new_name, team_id=team_id)

    return {
        "id": board.id,
        "name": board.name,
        "view_link": board.view_link,
    }


# Usage example
if __name__ == "__main__":
    # Create a board
    board = create_board(
        name="Sprint Retrospective - Q1 2026",
        description="Team retrospective for Q1 sprint",
    )
    print(f"Created board: {board['view_link']}")

    # List boards
    boards = list_boards(limit=10)
    for b in boards:
        print(f"- {b['name']}: {b['view_link']}")
```
