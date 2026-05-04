---
name: trello-api-3-card-management
description: 'Sub-skill of trello-api: 3. Card Management.'
version: 1.0.0
category: business
type: reference
scripts_exempt: true
---

# 3. Card Management

## 3. Card Management


**REST API - Cards:**
```bash
# Get cards for list
curl -s "https://api.trello.com/1/lists/LIST_ID/cards?key=$TRELLO_API_KEY&token=$TRELLO_TOKEN" | jq

# Get single card
curl -s "https://api.trello.com/1/cards/CARD_ID?key=$TRELLO_API_KEY&token=$TRELLO_TOKEN" | jq

# Create card with all options
curl -s -X POST "https://api.trello.com/1/cards" \
    -d "key=$TRELLO_API_KEY" \
    -d "token=$TRELLO_TOKEN" \
    -d "idList=LIST_ID" \
    -d "name=Implement feature X" \
    -d "desc=Detailed description of the feature" \
    -d "pos=top" \
    -d "due=2025-01-30T12:00:00.000Z" \
    -d "dueComplete=false" \
    -d "idMembers=MEMBER_ID1,MEMBER_ID2" \
    -d "idLabels=LABEL_ID1,LABEL_ID2" | jq

# Update card
curl -s -X PUT "https://api.trello.com/1/cards/CARD_ID" \
    -d "key=$TRELLO_API_KEY" \
    -d "token=$TRELLO_TOKEN" \
    -d "name=Updated card name" \
    -d "desc=Updated description" \
    -d "due=2025-02-15" | jq

# Move card to different list
curl -s -X PUT "https://api.trello.com/1/cards/CARD_ID" \
    -d "key=$TRELLO_API_KEY" \
    -d "token=$TRELLO_TOKEN" \
    -d "idList=NEW_LIST_ID" | jq

# Move card to different board
curl -s -X PUT "https://api.trello.com/1/cards/CARD_ID" \
    -d "key=$TRELLO_API_KEY" \
    -d "token=$TRELLO_TOKEN" \
    -d "idBoard=NEW_BOARD_ID" \
    -d "idList=NEW_LIST_ID" | jq

# Archive card
curl -s -X PUT "https://api.trello.com/1/cards/CARD_ID" \
    -d "key=$TRELLO_API_KEY" \
    -d "token=$TRELLO_TOKEN" \
    -d "closed=true" | jq

# Delete card permanently
curl -s -X DELETE "https://api.trello.com/1/cards/CARD_ID?key=$TRELLO_API_KEY&token=$TRELLO_TOKEN"

# Add comment to card
curl -s -X POST "https://api.trello.com/1/cards/CARD_ID/actions/comments" \
    -d "key=$TRELLO_API_KEY" \
    -d "token=$TRELLO_TOKEN" \
    -d "text=This is a comment on the card" | jq

# Add attachment via URL
curl -s -X POST "https://api.trello.com/1/cards/CARD_ID/attachments" \
    -d "key=$TRELLO_API_KEY" \
    -d "token=$TRELLO_TOKEN" \
    -d "url=https://example.com/file.pdf" \
    -d "name=Important Document" | jq
```

**Python SDK - Cards:**
```python
from trello import TrelloClient
from datetime import datetime, timedelta
import os

client = TrelloClient(
    api_key=os.environ["TRELLO_API_KEY"],
    token=os.environ["TRELLO_TOKEN"]
)

board = client.get_board("BOARD_ID")
target_list = board.get_list("LIST_ID")

# Create card
new_card = target_list.add_card(
    name="Complete API integration",
    desc="Full description of the task with acceptance criteria",
    labels=None,  # Add labels later
    due="2025-02-01",
    source=None,  # Or source card ID to copy from
    position="top"  # "top", "bottom", or number
)
print(f"Created card: {new_card.id}")

# Get card
card = client.get_card("CARD_ID")
print(f"Card: {card.name}")
print(f"Description: {card.description}")
print(f"Due: {card.due_date}")

# Update card properties
card.set_name("Updated: Complete API integration")
card.set_description("Updated description with more details")

# Set due date
due_date = datetime.now() + timedelta(days=7)
card.set_due(due_date)

# Mark due date complete
card.set_due_complete()

# Add label to card
labels = board.get_labels()
for label in labels:
    if label.name == "High Priority":
        card.add_label(label)
        break

# Assign member
members = board.get_members()
for member in members:
    if member.username == "target_user":
        card.add_member(member)
        break

# Add comment
card.comment("This task is now in progress")

# Add checklist
checklist = card.add_checklist(
    title="Implementation Steps",
    items=["Design API", "Write code", "Write tests", "Deploy"]
)

# Move card to different list
done_list = board.get_list("DONE_LIST_ID")
card.change_list(done_list.id)

# Archive card
card.set_closed(True)

# Unarchive card
card.set_closed(False)

# Delete card
card.delete()
```
