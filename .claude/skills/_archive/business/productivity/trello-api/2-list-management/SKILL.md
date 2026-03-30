---
name: trello-api-2-list-management
description: 'Sub-skill of trello-api: 2. List Management.'
version: 1.0.0
category: business
type: reference
scripts_exempt: true
---

# 2. List Management

## 2. List Management


**REST API - Lists:**
```bash
# Get lists for board
curl -s "https://api.trello.com/1/boards/BOARD_ID/lists?key=$TRELLO_API_KEY&token=$TRELLO_TOKEN" | jq

# Create list
curl -s -X POST "https://api.trello.com/1/lists" \
    -d "key=$TRELLO_API_KEY" \
    -d "token=$TRELLO_TOKEN" \
    -d "name=In Progress" \
    -d "idBoard=BOARD_ID" \
    -d "pos=bottom" | jq

# Update list name
curl -s -X PUT "https://api.trello.com/1/lists/LIST_ID" \
    -d "key=$TRELLO_API_KEY" \
    -d "token=$TRELLO_TOKEN" \
    -d "name=Currently Working" | jq

# Move list to different position
curl -s -X PUT "https://api.trello.com/1/lists/LIST_ID" \
    -d "key=$TRELLO_API_KEY" \
    -d "token=$TRELLO_TOKEN" \
    -d "pos=top" | jq

# Archive list
curl -s -X PUT "https://api.trello.com/1/lists/LIST_ID/closed" \
    -d "key=$TRELLO_API_KEY" \
    -d "token=$TRELLO_TOKEN" \
    -d "value=true" | jq

# Move all cards in list to another list
curl -s -X POST "https://api.trello.com/1/lists/LIST_ID/moveAllCards" \
    -d "key=$TRELLO_API_KEY" \
    -d "token=$TRELLO_TOKEN" \
    -d "idBoard=BOARD_ID" \
    -d "idList=TARGET_LIST_ID" | jq

# Archive all cards in list
curl -s -X POST "https://api.trello.com/1/lists/LIST_ID/archiveAllCards?key=$TRELLO_API_KEY&token=$TRELLO_TOKEN"
```

**Python SDK - Lists:**
```python
from trello import TrelloClient
import os

client = TrelloClient(
    api_key=os.environ["TRELLO_API_KEY"],
    token=os.environ["TRELLO_TOKEN"]
)

board = client.get_board("BOARD_ID")

# Get all lists
lists = board.list_lists()
for lst in lists:
    print(f"List: {lst.name} (ID: {lst.id})")

# Create new list
new_list = board.add_list(
    name="Backlog",
    pos="bottom"  # "top", "bottom", or position number
)
print(f"Created list: {new_list.id}")

# Get specific list
target_list = board.get_list("LIST_ID")

# Get cards in list
cards = target_list.list_cards()
for card in cards:
    print(f"  Card: {card.name}")

# Rename list
target_list.set_name("New Backlog")

# Change list position
target_list.set_pos("top")

# Archive list
target_list.close()

# Move all cards from one list to another
source_list = board.get_list("SOURCE_LIST_ID")
dest_list = board.get_list("DEST_LIST_ID")

for card in source_list.list_cards():
    card.change_list(dest_list.id)
```
