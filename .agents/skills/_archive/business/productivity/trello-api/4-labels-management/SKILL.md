---
name: trello-api-4-labels-management
description: 'Sub-skill of trello-api: 4. Labels Management (+1).'
version: 1.0.0
category: business
type: reference
scripts_exempt: true
---

# 4. Labels Management (+1)

## 4. Labels Management


**REST API - Labels:**
```bash
# Get labels for board
curl -s "https://api.trello.com/1/boards/BOARD_ID/labels?key=$TRELLO_API_KEY&token=$TRELLO_TOKEN" | jq

# Create label
curl -s -X POST "https://api.trello.com/1/labels" \
    -d "key=$TRELLO_API_KEY" \
    -d "token=$TRELLO_TOKEN" \
    -d "name=Bug" \
    -d "color=red" \
    -d "idBoard=BOARD_ID" | jq

# Available colors: yellow, purple, blue, red, green, orange, black, sky, pink, lime

# Update label
curl -s -X PUT "https://api.trello.com/1/labels/LABEL_ID" \
    -d "key=$TRELLO_API_KEY" \
    -d "token=$TRELLO_TOKEN" \
    -d "name=Critical Bug" \
    -d "color=red" | jq

# Delete label
curl -s -X DELETE "https://api.trello.com/1/labels/LABEL_ID?key=$TRELLO_API_KEY&token=$TRELLO_TOKEN"

# Add label to card
curl -s -X POST "https://api.trello.com/1/cards/CARD_ID/idLabels" \
    -d "key=$TRELLO_API_KEY" \
    -d "token=$TRELLO_TOKEN" \
    -d "value=LABEL_ID" | jq

# Remove label from card
curl -s -X DELETE "https://api.trello.com/1/cards/CARD_ID/idLabels/LABEL_ID?key=$TRELLO_API_KEY&token=$TRELLO_TOKEN"
```

**Python SDK - Labels:**
```python
# Get all labels for board
labels = board.get_labels()
for label in labels:
    print(f"Label: {label.name} (Color: {label.color})")

# Create new label
new_label = board.add_label(
    name="Enhancement",
    color="blue"
)

# Add label to card
card.add_label(new_label)

# Remove label from card
card.remove_label(new_label)

# Update label (using API directly)
import requests

requests.put(
    f"https://api.trello.com/1/labels/{label.id}",
    params={
        "key": os.environ["TRELLO_API_KEY"],
        "token": os.environ["TRELLO_TOKEN"],
        "name": "New Name",
        "color": "green"
    }
)
```


## 5. Checklists Management


**REST API - Checklists:**
```bash
# Get checklists on card
curl -s "https://api.trello.com/1/cards/CARD_ID/checklists?key=$TRELLO_API_KEY&token=$TRELLO_TOKEN" | jq

# Create checklist
curl -s -X POST "https://api.trello.com/1/checklists" \
    -d "key=$TRELLO_API_KEY" \
    -d "token=$TRELLO_TOKEN" \
    -d "idCard=CARD_ID" \
    -d "name=Deployment Checklist" | jq

# Add item to checklist
curl -s -X POST "https://api.trello.com/1/checklists/CHECKLIST_ID/checkItems" \
    -d "key=$TRELLO_API_KEY" \
    -d "token=$TRELLO_TOKEN" \
    -d "name=Run tests" \
    -d "pos=bottom" \
    -d "checked=false" | jq

# Update checklist item (mark complete)
curl -s -X PUT "https://api.trello.com/1/cards/CARD_ID/checkItem/CHECKITEM_ID" \
    -d "key=$TRELLO_API_KEY" \
    -d "token=$TRELLO_TOKEN" \
    -d "state=complete" | jq

# Delete checklist
curl -s -X DELETE "https://api.trello.com/1/checklists/CHECKLIST_ID?key=$TRELLO_API_KEY&token=$TRELLO_TOKEN"
```

**Python SDK - Checklists:**
```python
# Get checklists on card
checklists = card.fetch_checklists()
for checklist in checklists:
    print(f"Checklist: {checklist.name}")
    for item in checklist.items:
        status = "[x]" if item["checked"] else "[ ]"
        print(f"  {status} {item['name']}")

# Create checklist with items
checklist = card.add_checklist(
    title="Release Checklist",
    items=[
        "Code review completed",
        "Tests passing",
        "Documentation updated",
        "Changelog updated",
        "Version bumped"
    ]
)

# Check/uncheck item
checklist.set_checklist_item("Code review completed", checked=True)

# Delete checklist item
checklist.delete_checklist_item("Documentation updated")

# Rename checklist
checklist.rename("Pre-Release Checklist")

# Delete checklist
checklist.delete()
```
