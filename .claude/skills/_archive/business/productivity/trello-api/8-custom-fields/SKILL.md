---
name: trello-api-8-custom-fields
description: 'Sub-skill of trello-api: 8. Custom Fields.'
version: 1.0.0
category: business
type: reference
scripts_exempt: true
---

# 8. Custom Fields

## 8. Custom Fields


**REST API - Custom Fields:**
```bash
# Get custom fields on board
curl -s "https://api.trello.com/1/boards/BOARD_ID/customFields?key=$TRELLO_API_KEY&token=$TRELLO_TOKEN" | jq

# Create custom field
curl -s -X POST "https://api.trello.com/1/customFields" \
    -d "key=$TRELLO_API_KEY" \
    -d "token=$TRELLO_TOKEN" \
    -d "idModel=BOARD_ID" \
    -d "modelType=board" \
    -d "name=Priority Score" \
    -d "type=number" \
    -d "pos=top" | jq

# Field types: number, text, date, checkbox, list

# Create dropdown custom field
curl -s -X POST "https://api.trello.com/1/customFields" \
    -H "Content-Type: application/json" \
    -d '{
        "key": "'$TRELLO_API_KEY'",
        "token": "'$TRELLO_TOKEN'",
        "idModel": "BOARD_ID",
        "modelType": "board",
        "name": "Status",
        "type": "list",
        "pos": "bottom",
        "options": [
            {"value": {"text": "Not Started"}, "pos": 1},
            {"value": {"text": "In Progress"}, "pos": 2},
            {"value": {"text": "Completed"}, "pos": 3}
        ]
    }' | jq

# Set custom field value on card
curl -s -X PUT "https://api.trello.com/1/cards/CARD_ID/customField/FIELD_ID/item" \
    -H "Content-Type: application/json" \
    -d '{
        "key": "'$TRELLO_API_KEY'",
        "token": "'$TRELLO_TOKEN'",
        "value": {"number": "85"}
    }' | jq

# For dropdown, use idValue
curl -s -X PUT "https://api.trello.com/1/cards/CARD_ID/customField/FIELD_ID/item" \
    -H "Content-Type: application/json" \
    -d '{
        "key": "'$TRELLO_API_KEY'",
        "token": "'$TRELLO_TOKEN'",
        "idValue": "OPTION_ID"
    }' | jq

# Get custom field values for card
curl -s "https://api.trello.com/1/cards/CARD_ID/customFieldItems?key=$TRELLO_API_KEY&token=$TRELLO_TOKEN" | jq
```

**Python Custom Fields:**
```python
import requests
import os

API_KEY = os.environ["TRELLO_API_KEY"]
TOKEN = os.environ["TRELLO_TOKEN"]

def get_custom_fields(board_id):
    """Get all custom fields for a board."""
    url = f"https://api.trello.com/1/boards/{board_id}/customFields"
    response = requests.get(url, params={"key": API_KEY, "token": TOKEN})
    return response.json()


def set_custom_field_value(card_id, field_id, value, field_type="text"):
    """Set custom field value on a card."""
    url = f"https://api.trello.com/1/cards/{card_id}/customField/{field_id}/item"

    # Build value based on type
    if field_type == "number":
        data = {"value": {"number": str(value)}}
    elif field_type == "text":
        data = {"value": {"text": value}}
    elif field_type == "checkbox":
        data = {"value": {"checked": str(value).lower()}}
    elif field_type == "date":
        data = {"value": {"date": value}}  # ISO format
    elif field_type == "list":
        data = {"idValue": value}  # Option ID for dropdown
    else:
        data = {"value": {"text": str(value)}}

    response = requests.put(
        url,
        json={**data, "key": API_KEY, "token": TOKEN}
    )
    return response.json()


def get_card_custom_fields(card_id):
    """Get all custom field values for a card."""
    url = f"https://api.trello.com/1/cards/{card_id}/customFieldItems"
    response = requests.get(url, params={"key": API_KEY, "token": TOKEN})
    return response.json()


# Example usage
fields = get_custom_fields("BOARD_ID")
for field in fields:
    print(f"Field: {field['name']} (Type: {field['type']})")

# Set a numeric field
set_custom_field_value("CARD_ID", "FIELD_ID", 95, "number")

# Get field values
values = get_card_custom_fields("CARD_ID")
for value in values:
    print(f"Field {value['idCustomField']}: {value.get('value', value.get('idValue'))}")
```
