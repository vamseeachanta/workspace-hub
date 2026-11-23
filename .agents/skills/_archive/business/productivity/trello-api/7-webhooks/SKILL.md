---
name: trello-api-7-webhooks
description: 'Sub-skill of trello-api: 7. Webhooks.'
version: 1.0.0
category: business
type: reference
scripts_exempt: true
---

# 7. Webhooks

## 7. Webhooks


**REST API - Webhooks:**
```bash
# Create webhook
curl -s -X POST "https://api.trello.com/1/webhooks" \
    -d "key=$TRELLO_API_KEY" \
    -d "token=$TRELLO_TOKEN" \
    -d "callbackURL=https://your-server.com/webhook/trello" \
    -d "idModel=BOARD_ID" \
    -d "description=Board events webhook" | jq

# List webhooks
curl -s "https://api.trello.com/1/tokens/$TRELLO_TOKEN/webhooks?key=$TRELLO_API_KEY" | jq

# Get webhook details
curl -s "https://api.trello.com/1/webhooks/WEBHOOK_ID?key=$TRELLO_API_KEY&token=$TRELLO_TOKEN" | jq

# Update webhook
curl -s -X PUT "https://api.trello.com/1/webhooks/WEBHOOK_ID" \
    -d "key=$TRELLO_API_KEY" \
    -d "token=$TRELLO_TOKEN" \
    -d "callbackURL=https://new-server.com/webhook/trello" | jq

# Delete webhook
curl -s -X DELETE "https://api.trello.com/1/webhooks/WEBHOOK_ID?key=$TRELLO_API_KEY&token=$TRELLO_TOKEN"
```

**Webhook Handler Example:**
```python
from flask import Flask, request, jsonify
import json

app = Flask(__name__)

@app.route("/webhook/trello", methods=["HEAD", "POST"])
def trello_webhook():
    # HEAD request is for webhook verification
    if request.method == "HEAD":
        return "", 200

    # Process webhook payload
    data = request.json

    action = data.get("action", {})
    action_type = action.get("type")

    print(f"Received Trello webhook: {action_type}")

    # Handle different action types
    if action_type == "createCard":
        handle_card_created(action)
    elif action_type == "updateCard":
        handle_card_updated(action)
    elif action_type == "moveCardToBoard":
        handle_card_moved(action)
    elif action_type == "addMemberToCard":
        handle_member_assigned(action)
    elif action_type == "commentCard":
        handle_comment_added(action)
    elif action_type == "updateCheckItemStateOnCard":
        handle_checklist_item_updated(action)

    return jsonify({"status": "ok"})


def handle_card_created(action):
    card_data = action.get("data", {}).get("card", {})
    print(f"Card created: {card_data.get('name')}")


def handle_card_updated(action):
    card_data = action.get("data", {}).get("card", {})
    old_data = action.get("data", {}).get("old", {})
    print(f"Card updated: {card_data.get('name')}")

    # Check if moved to different list
    if "idList" in old_data:
        list_after = action.get("data", {}).get("listAfter", {})
        list_before = action.get("data", {}).get("listBefore", {})
        print(f"  Moved from '{list_before.get('name')}' to '{list_after.get('name')}'")


def handle_card_moved(action):
    card_data = action.get("data", {}).get("card", {})
    print(f"Card moved to different board: {card_data.get('name')}")


def handle_member_assigned(action):
    card_data = action.get("data", {}).get("card", {})
    member_data = action.get("data", {}).get("member", {})
    print(f"Member {member_data.get('username')} assigned to: {card_data.get('name')}")


def handle_comment_added(action):
    card_data = action.get("data", {}).get("card", {})
    text = action.get("data", {}).get("text", "")
    print(f"Comment on {card_data.get('name')}: {text[:100]}")


def handle_checklist_item_updated(action):
    card_data = action.get("data", {}).get("card", {})
    item = action.get("data", {}).get("checkItem", {})
    state = item.get("state")
    print(f"Checklist item '{item.get('name')}' marked {state}")


if __name__ == "__main__":
    app.run(port=5000)
```

**Webhook Events:**
```python
# Common Trello webhook action types
WEBHOOK_ACTIONS = {
    # Board events
    "updateBoard": "Board settings changed",
    "addMemberToBoard": "Member added to board",
    "removeMemberFromBoard": "Member removed from board",

    # List events
    "createList": "List created",
    "updateList": "List updated (renamed, moved, archived)",
    "moveListToBoard": "List moved to different board",

    # Card events
    "createCard": "Card created",
    "updateCard": "Card updated (name, desc, due date, position, list)",
    "deleteCard": "Card deleted",
    "moveCardToBoard": "Card moved to different board",
    "copyCard": "Card copied",
    "convertToCardFromCheckItem": "Checklist item converted to card",

    # Card member events
    "addMemberToCard": "Member assigned to card",
    "removeMemberFromCard": "Member removed from card",

    # Card label events
    "addLabelToCard": "Label added to card",
    "removeLabelFromCard": "Label removed from card",

    # Card attachment events
    "addAttachmentToCard": "Attachment added",
    "deleteAttachmentFromCard": "Attachment deleted",

    # Comment events
    "commentCard": "Comment added to card",
    "updateComment": "Comment updated",
    "deleteComment": "Comment deleted",

    # Checklist events
    "addChecklistToCard": "Checklist added to card",
    "removeChecklistFromCard": "Checklist removed",
    "updateChecklist": "Checklist updated",
    "updateCheckItemStateOnCard": "Checklist item checked/unchecked",
    "createCheckItem": "Checklist item created",
    "deleteCheckItem": "Checklist item deleted",
}
```
