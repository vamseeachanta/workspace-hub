---
name: windmill-7-approval-flows
description: 'Sub-skill of windmill: 7. Approval Flows.'
version: 1.0.0
category: operations
type: reference
scripts_exempt: true
---

# 7. Approval Flows

## 7. Approval Flows


```python
# scripts/approvals/expense_approval.py
"""
Expense approval workflow with multi-level approvals.
"""

import wmill
from typing import Optional
from enum import Enum


class ApprovalLevel(Enum):
    AUTO = "auto"
    MANAGER = "manager"
    DIRECTOR = "director"
    EXECUTIVE = "executive"


def main(
    expense_id: str,
    amount: float,
    category: str,
    description: str,
    requestor_email: str,
    receipts: Optional[list] = None,
):
    """
    Process expense approval request.

    Args:
        expense_id: Unique expense ID
        amount: Expense amount in USD
        category: Expense category
        description: Expense description
        requestor_email: Email of person requesting expense
        receipts: List of receipt file URLs

    Returns:
        Approval request status and next steps
    """
    # Determine approval level based on amount and category
    approval_level = determine_approval_level(amount, category)

    # Get approvers for this level
    approvers = get_approvers(approval_level, requestor_email)

    if approval_level == ApprovalLevel.AUTO:
        # Auto-approve small expenses
        return {
            "expense_id": expense_id,
            "status": "approved",
            "approval_level": approval_level.value,
            "auto_approved": True,
            "message": f"Expense auto-approved (amount: ${amount:.2f})"
        }

    # Create approval request in database
    db = wmill.get_resource("u/admin/expenses_db")
    approval_id = create_approval_request(
        db,
        expense_id=expense_id,
        amount=amount,
        category=category,
        description=description,
        requestor=requestor_email,
        approvers=approvers,
        level=approval_level.value
    )

    # Send notification to approvers
    slack = wmill.get_resource("u/admin/slack_webhook")
    send_approval_notification(
        slack,
        expense_id=expense_id,
        amount=amount,
        category=category,
        description=description,
        requestor=requestor_email,
        approvers=approvers,
        approval_link=f"https://windmill.example.com/approvals/{approval_id}"
    )

    # Return approval URL for Windmill's built-in approval step
    return {
        "expense_id": expense_id,
        "approval_id": approval_id,
        "status": "pending_approval",
        "approval_level": approval_level.value,
        "approvers": approvers,
        "resume_url": wmill.get_resume_url(),  # For approval continuation
        "message": f"Expense pending {approval_level.value} approval"
    }


def determine_approval_level(amount: float, category: str) -> ApprovalLevel:
    """Determine required approval level based on business rules."""
    # Category-specific rules
    high_scrutiny_categories = ["travel", "equipment", "consulting"]

    if amount <= 100:
        return ApprovalLevel.AUTO
    elif amount <= 1000:
        return ApprovalLevel.MANAGER
    elif amount <= 5000 or category in high_scrutiny_categories:
        return ApprovalLevel.DIRECTOR
    else:
        return ApprovalLevel.EXECUTIVE


def get_approvers(level: ApprovalLevel, requestor: str) -> list:
    """Get list of approvers for given level."""
    approvers_config = wmill.get_variable("u/admin/approvers_config")

    if level == ApprovalLevel.MANAGER:
        # Get requestor's manager
        return approvers_config.get("managers", {}).get(requestor, [])
    elif level == ApprovalLevel.DIRECTOR:
        return approvers_config.get("directors", [])
    elif level == ApprovalLevel.EXECUTIVE:
        return approvers_config.get("executives", [])
    return []


def create_approval_request(db, **kwargs) -> str:
    """Create approval request in database."""
    import psycopg2
    import uuid

    approval_id = str(uuid.uuid4())

    conn = psycopg2.connect(**db)
    try:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO expense_approvals
                (id, expense_id, amount, category, description,
                 requestor, approvers, level, status, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 'pending', NOW())
            """, (
                approval_id,
                kwargs["expense_id"],
                kwargs["amount"],
                kwargs["category"],
                kwargs["description"],
                kwargs["requestor"],
                kwargs["approvers"],
                kwargs["level"]
            ))
            conn.commit()
    finally:
        conn.close()

    return approval_id


def send_approval_notification(slack, **kwargs):
    """Send Slack notification for approval request."""
    import requests

    blocks = [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": "Expense Approval Required"
            }
        },
        {
            "type": "section",
            "fields": [
                {"type": "mrkdwn", "text": f"*Amount:* ${kwargs['amount']:.2f}"},
                {"type": "mrkdwn", "text": f"*Category:* {kwargs['category']}"},
                {"type": "mrkdwn", "text": f"*Requestor:* {kwargs['requestor']}"},
                {"type": "mrkdwn", "text": f"*Description:* {kwargs['description']}"}
            ]
        },
        {
            "type": "actions",
            "elements": [
                {
                    "type": "button",
                    "text": {"type": "plain_text", "text": "Review & Approve"},
                    "url": kwargs["approval_link"],
                    "style": "primary"

*Content truncated — see parent skill for full reference.*
