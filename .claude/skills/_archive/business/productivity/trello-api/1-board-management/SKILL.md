---
name: trello-api-1-board-management
description: 'Sub-skill of trello-api: 1. Board Management.'
version: 1.0.0
category: business
type: reference
scripts_exempt: true
---

# 1. Board Management

## 1. Board Management


**REST API - Boards:**
```bash
# List all boards
curl -s "https://api.trello.com/1/members/me/boards?key=$TRELLO_API_KEY&token=$TRELLO_TOKEN" | jq '.[].name'

# Get specific board
curl -s "https://api.trello.com/1/boards/BOARD_ID?key=$TRELLO_API_KEY&token=$TRELLO_TOKEN" | jq

# Get board with lists and cards
curl -s "https://api.trello.com/1/boards/BOARD_ID?lists=all&cards=all&key=$TRELLO_API_KEY&token=$TRELLO_TOKEN" | jq

# Create board
curl -s -X POST "https://api.trello.com/1/boards" \
    -d "key=$TRELLO_API_KEY" \
    -d "token=$TRELLO_TOKEN" \
    -d "name=Project Alpha" \
    -d "desc=Main project board" \
    -d "defaultLists=false" \
    -d "prefs_permissionLevel=private" | jq

# Create board from template
curl -s -X POST "https://api.trello.com/1/boards" \
    -d "key=$TRELLO_API_KEY" \
    -d "token=$TRELLO_TOKEN" \
    -d "name=New Project" \
    -d "idBoardSource=TEMPLATE_BOARD_ID" | jq

# Update board
curl -s -X PUT "https://api.trello.com/1/boards/BOARD_ID" \
    -d "key=$TRELLO_API_KEY" \
    -d "token=$TRELLO_TOKEN" \
    -d "name=Project Alpha - Updated" \
    -d "desc=Updated description" | jq

# Close (archive) board
curl -s -X PUT "https://api.trello.com/1/boards/BOARD_ID/closed" \
    -d "key=$TRELLO_API_KEY" \
    -d "token=$TRELLO_TOKEN" \
    -d "value=true" | jq

# Delete board permanently
curl -s -X DELETE "https://api.trello.com/1/boards/BOARD_ID?key=$TRELLO_API_KEY&token=$TRELLO_TOKEN"
```

**Python SDK - Boards:**
```python
from trello import TrelloClient
import os

client = TrelloClient(
    api_key=os.environ["TRELLO_API_KEY"],
    token=os.environ["TRELLO_TOKEN"]
)

# List all boards
boards = client.list_boards()
for board in boards:
    print(f"{board.name} (ID: {board.id})")

# Get specific board
board = client.get_board("BOARD_ID")
print(f"Board: {board.name}")
print(f"URL: {board.url}")

# Create new board
new_board = client.add_board(
    board_name="Development Sprint",
    source_board=None,  # Or source board for template
    permission_level="private"  # "private", "org", "public"
)
print(f"Created board: {new_board.id}")

# Get board lists
lists = board.list_lists()
for lst in lists:
    print(f"  List: {lst.name}")

# Get all cards on board
cards = board.get_cards()
for card in cards:
    print(f"  Card: {card.name}")

# Get board members
members = board.get_members()
for member in members:
    print(f"  Member: {member.full_name}")

# Close board
board.close()

# Reopen board
board.open()
```
