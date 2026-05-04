---
name: todoist-api-8-webhooks
description: 'Sub-skill of todoist-api: 8. Webhooks.'
version: 1.0.0
category: business
type: reference
scripts_exempt: true
---

# 8. Webhooks

## 8. Webhooks


**Webhook Setup:**
```python
from flask import Flask, request, jsonify
import hashlib
import hmac
import os

app = Flask(__name__)
TODOIST_CLIENT_SECRET = os.environ["TODOIST_CLIENT_SECRET"]

def verify_webhook(payload, signature):
    """Verify webhook signature"""
    computed = hmac.new(
        TODOIST_CLIENT_SECRET.encode(),
        payload,
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(computed, signature)

@app.route("/webhook/todoist", methods=["POST"])
def todoist_webhook():
    # Verify signature
    signature = request.headers.get("X-Todoist-Hmac-SHA256", "")
    if not verify_webhook(request.data, signature):
        return jsonify({"error": "Invalid signature"}), 401

    # Parse event
    event = request.json
    event_name = event.get("event_name")
    event_data = event.get("event_data", {})

    print(f"Received event: {event_name}")

    # Handle different event types
    if event_name == "item:added":
        handle_task_added(event_data)
    elif event_name == "item:completed":
        handle_task_completed(event_data)
    elif event_name == "item:updated":
        handle_task_updated(event_data)
    elif event_name == "item:deleted":
        handle_task_deleted(event_data)
    elif event_name == "project:added":
        handle_project_added(event_data)

    return jsonify({"status": "ok"})

def handle_task_added(data):
    print(f"New task: {data.get('content')}")
    # Add your logic here

def handle_task_completed(data):
    print(f"Task completed: {data.get('content')}")
    # Add your logic here

def handle_task_updated(data):
    print(f"Task updated: {data.get('content')}")
    # Add your logic here

def handle_task_deleted(data):
    print(f"Task deleted: {data.get('id')}")
    # Add your logic here

def handle_project_added(data):
    print(f"New project: {data.get('name')}")
    # Add your logic here

if __name__ == "__main__":
    app.run(port=5000)
```

**Webhook Events:**
```python
# Available webhook events
WEBHOOK_EVENTS = {
    # Task events
    "item:added": "Task created",
    "item:updated": "Task updated",
    "item:deleted": "Task deleted",
    "item:completed": "Task completed",
    "item:uncompleted": "Task reopened",

    # Project events
    "project:added": "Project created",
    "project:updated": "Project updated",
    "project:deleted": "Project deleted",
    "project:archived": "Project archived",
    "project:unarchived": "Project unarchived",

    # Note/Comment events
    "note:added": "Comment added",
    "note:updated": "Comment updated",
    "note:deleted": "Comment deleted",

    # Label events
    "label:added": "Label created",
    "label:updated": "Label updated",
    "label:deleted": "Label deleted",

    # Section events
    "section:added": "Section created",
    "section:updated": "Section updated",
    "section:deleted": "Section deleted",

    # Reminder events
    "reminder:fired": "Reminder triggered",
}
```
