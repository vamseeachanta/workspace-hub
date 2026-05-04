---
name: slack-api-4-modals-and-views
description: 'Sub-skill of slack-api: 4. Modals and Views.'
version: 1.0.0
category: business
type: reference
scripts_exempt: true
---

# 4. Modals and Views

## 4. Modals and Views


```python
# modals.py
# ABOUTME: Modal dialogs for complex user input
# ABOUTME: Multi-step workflows with view updates

from slack_bolt import App
import json
import os

app = App(token=os.environ.get("SLACK_BOT_TOKEN"))

@app.command("/create-ticket")
def open_ticket_modal(ack, body, client):
    """Open a modal for ticket creation"""
    ack()

    client.views_open(
        trigger_id=body['trigger_id'],
        view={
            "type": "modal",
            "callback_id": "create_ticket_modal",
            "title": {
                "type": "plain_text",
                "text": "Create Ticket"
            },
            "submit": {
                "type": "plain_text",
                "text": "Create"
            },
            "close": {
                "type": "plain_text",
                "text": "Cancel"
            },
            "blocks": [
                {
                    "type": "input",
                    "block_id": "title_block",
                    "element": {
                        "type": "plain_text_input",
                        "action_id": "title_input",
                        "placeholder": {
                            "type": "plain_text",
                            "text": "Brief description of the issue"
                        }
                    },
                    "label": {
                        "type": "plain_text",
                        "text": "Title"
                    }
                },
                {
                    "type": "input",
                    "block_id": "description_block",
                    "element": {
                        "type": "plain_text_input",
                        "action_id": "description_input",
                        "multiline": True,
                        "placeholder": {
                            "type": "plain_text",
                            "text": "Detailed description..."
                        }
                    },
                    "label": {
                        "type": "plain_text",
                        "text": "Description"
                    }
                },
                {
                    "type": "input",
                    "block_id": "priority_block",
                    "element": {
                        "type": "static_select",
                        "action_id": "priority_select",
                        "placeholder": {
                            "type": "plain_text",
                            "text": "Select priority"
                        },
                        "options": [
                            {
                                "text": {"type": "plain_text", "text": "Low"},
                                "value": "low"
                            },
                            {
                                "text": {"type": "plain_text", "text": "Medium"},
                                "value": "medium"
                            },
                            {
                                "text": {"type": "plain_text", "text": "High"},
                                "value": "high"
                            },
                            {
                                "text": {"type": "plain_text", "text": "Critical"},
                                "value": "critical"
                            }
                        ]
                    },
                    "label": {
                        "type": "plain_text",
                        "text": "Priority"
                    }
                },
                {
                    "type": "input",
                    "block_id": "assignee_block",
                    "element": {
                        "type": "users_select",
                        "action_id": "assignee_select",
                        "placeholder": {
                            "type": "plain_text",
                            "text": "Select assignee"
                        }
                    },
                    "label": {
                        "type": "plain_text",
                        "text": "Assignee"
                    },
                    "optional": True
                },
                {
                    "type": "input",
                    "block_id": "due_date_block",
                    "element": {
                        "type": "datepicker",
                        "action_id": "due_date_picker",
                        "placeholder": {
                            "type": "plain_text",
                            "text": "Select a date"
                        }
                    },
                    "label": {
                        "type": "plain_text",
                        "text": "Due Date"
                    },
                    "optional": True
                }
            ]
        }
    )

@app.view("create_ticket_modal")
def handle_ticket_submission(ack, body, client, view, logger):
    """Handle ticket modal submission"""

    # Extract values
    values = view['state']['values']
    title = values['title_block']['title_input']['value']
    description = values['description_block']['description_input']['value']
    priority = values['priority_block']['priority_select']['selected_option']['value']
    assignee = values['assignee_block']['assignee_select'].get('selected_user')
    due_date = values['due_date_block']['due_date_picker'].get('selected_date')

    user = body['user']['id']

    # Validate input
    errors = {}
    if len(title) < 5:
        errors['title_block'] = "Title must be at least 5 characters"
    if len(description) < 10:
        errors['description_block'] = "Description must be at least 10 characters"

    if errors:
        ack(response_action="errors", errors=errors)
        return

    ack()

    # Create ticket (in real app, save to database/API)
    ticket_id = f"TICKET-{hash(title) % 10000:04d}"

    # Notify in channel
    blocks = [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": f":ticket: New Ticket Created",
                "emoji": True
            }
        },
        {
            "type": "section",
            "fields": [
                {"type": "mrkdwn", "text": f"*ID:*\n`{ticket_id}`"},
                {"type": "mrkdwn", "text": f"*Priority:*\n{priority.title()}"},

*Content truncated — see parent skill for full reference.*
