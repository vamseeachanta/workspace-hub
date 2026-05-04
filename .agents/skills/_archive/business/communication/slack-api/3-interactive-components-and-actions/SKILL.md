---
name: slack-api-3-interactive-components-and-actions
description: 'Sub-skill of slack-api: 3. Interactive Components and Actions.'
version: 1.0.0
category: business
type: reference
scripts_exempt: true
---

# 3. Interactive Components and Actions

## 3. Interactive Components and Actions


```python
# interactive.py
# ABOUTME: Handle interactive components like buttons, selects, modals
# ABOUTME: Implements approval workflows with state management

from slack_bolt import App
from datetime import datetime
import json
import os

app = App(token=os.environ.get("SLACK_BOT_TOKEN"))

# In-memory storage (use database in production)
approval_requests = {}

@app.action("approve_request")
def handle_approve(ack, body, client, logger):
    """Handle approval button click"""
    ack()

    user = body['user']['id']
    request_id = body['actions'][0]['value']
    channel = body['channel']['id']
    message_ts = body['message']['ts']

    # Update the message to show approval
    updated_blocks = body['message']['blocks'].copy()

    # Remove action buttons
    updated_blocks = [b for b in updated_blocks if b.get('type') != 'actions']

    # Add approval status
    updated_blocks.append({
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": f":white_check_mark: *Approved* by <@{user}> at {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        }
    })

    # Update the original message
    client.chat_update(
        channel=channel,
        ts=message_ts,
        blocks=updated_blocks,
        text="Request approved"
    )

    # Store approval
    approval_requests[request_id] = {
        "status": "approved",
        "approved_by": user,
        "timestamp": datetime.now().isoformat()
    }

    logger.info(f"Request {request_id} approved by {user}")

@app.action("reject_request")
def handle_reject(ack, body, client, respond):
    """Handle rejection with reason modal"""
    ack()

    request_id = body['actions'][0]['value']
    trigger_id = body['trigger_id']

    # Open modal for rejection reason
    client.views_open(
        trigger_id=trigger_id,
        view={
            "type": "modal",
            "callback_id": f"reject_modal_{request_id}",
            "title": {
                "type": "plain_text",
                "text": "Reject Request"
            },
            "submit": {
                "type": "plain_text",
                "text": "Reject"
            },
            "close": {
                "type": "plain_text",
                "text": "Cancel"
            },
            "blocks": [
                {
                    "type": "input",
                    "block_id": "reason_block",
                    "element": {
                        "type": "plain_text_input",
                        "action_id": "rejection_reason",
                        "multiline": True,
                        "placeholder": {
                            "type": "plain_text",
                            "text": "Enter reason for rejection..."
                        }
                    },
                    "label": {
                        "type": "plain_text",
                        "text": "Rejection Reason"
                    }
                }
            ],
            "private_metadata": json.dumps({
                "channel": body['channel']['id'],
                "message_ts": body['message']['ts'],
                "request_id": request_id
            })
        }
    )

@app.view_submission("reject_modal_.*")
def handle_reject_submission(ack, body, client, view, logger):
    """Handle rejection modal submission"""
    ack()

    # Get values from modal
    reason = view['state']['values']['reason_block']['rejection_reason']['value']
    metadata = json.loads(view['private_metadata'])
    user = body['user']['id']

    channel = metadata['channel']
    message_ts = metadata['message_ts']
    request_id = metadata['request_id']

    # Update original message
    client.chat_postMessage(
        channel=channel,
        thread_ts=message_ts,
        text=f":x: *Rejected* by <@{user}>\n*Reason:* {reason}"
    )

    # Update the original message blocks
    original_message = client.conversations_history(
        channel=channel,
        latest=message_ts,
        inclusive=True,
        limit=1
    )

    if original_message['messages']:
        updated_blocks = original_message['messages'][0].get('blocks', [])
        updated_blocks = [b for b in updated_blocks if b.get('type') != 'actions']
        updated_blocks.append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f":x: *Rejected* by <@{user}>"
            }
        })

        client.chat_update(
            channel=channel,
            ts=message_ts,
            blocks=updated_blocks,
            text="Request rejected"
        )

    logger.info(f"Request {request_id} rejected by {user}: {reason}")

@app.action("poll_vote")
def handle_poll_vote(ack, body, logger):
    """Handle poll vote selection"""
    ack()
    selected = body['actions'][0]['selected_option']['value']
    logger.info(f"Poll vote: {selected}")

@app.action("submit_vote")
def handle_submit_vote(ack, body, client, respond):
    """Handle poll submission"""
    ack()

    user = body['user']['id']

    # Get selected option from state
    state = body.get('state', {}).get('values', {})
    selected = None

    for block_id, block_values in state.items():
        for action_id, action_value in block_values.items():
            if action_value.get('selected_option'):
                selected = action_value['selected_option']

    if selected:
        respond(

*Content truncated — see parent skill for full reference.*
