---
name: teams-api-2-adaptive-cards
description: 'Sub-skill of teams-api: 2. Adaptive Cards.'
version: 1.0.0
category: business
type: reference
scripts_exempt: true
---

# 2. Adaptive Cards

## 2. Adaptive Cards


```python
# adaptive_cards.py
# ABOUTME: Adaptive Card construction for rich Teams messages
# ABOUTME: Interactive cards with actions and data binding

from typing import Dict, List, Optional, Any
import json

class AdaptiveCardBuilder:
    """Builder for Adaptive Cards"""

    def __init__(self, version: str = "1.4"):
        self.card = {
            "type": "AdaptiveCard",
            "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
            "version": version,
            "body": [],
            "actions": []
        }

    def add_text_block(
        self,
        text: str,
        size: str = "default",
        weight: str = "default",
        color: str = "default",
        wrap: bool = True
    ):
        """Add a text block"""
        self.card["body"].append({
            "type": "TextBlock",
            "text": text,
            "size": size,
            "weight": weight,
            "color": color,
            "wrap": wrap
        })
        return self

    def add_fact_set(self, facts: Dict[str, str]):
        """Add a fact set (key-value pairs)"""
        self.card["body"].append({
            "type": "FactSet",
            "facts": [
                {"title": k, "value": v}
                for k, v in facts.items()
            ]
        })
        return self

    def add_column_set(self, columns: List[Dict]):
        """Add a column set for side-by-side content"""
        self.card["body"].append({
            "type": "ColumnSet",
            "columns": columns
        })
        return self

    def add_image(
        self,
        url: str,
        size: str = "auto",
        alt_text: str = ""
    ):
        """Add an image"""
        self.card["body"].append({
            "type": "Image",
            "url": url,
            "size": size,
            "altText": alt_text
        })
        return self

    def add_action_submit(
        self,
        title: str,
        data: Dict[str, Any],
        style: str = "default"
    ):
        """Add a submit action button"""
        self.card["actions"].append({
            "type": "Action.Submit",
            "title": title,
            "data": data,
            "style": style
        })
        return self

    def add_action_open_url(
        self,
        title: str,
        url: str
    ):
        """Add an open URL action"""
        self.card["actions"].append({
            "type": "Action.OpenUrl",
            "title": title,
            "url": url
        })
        return self

    def add_action_show_card(
        self,
        title: str,
        card: Dict
    ):
        """Add a show card action (nested card)"""
        self.card["actions"].append({
            "type": "Action.ShowCard",
            "title": title,
            "card": card
        })
        return self

    def add_input_text(
        self,
        id: str,
        placeholder: str = "",
        is_multiline: bool = False,
        label: str = ""
    ):
        """Add a text input"""
        input_element = {
            "type": "Input.Text",
            "id": id,
            "placeholder": placeholder,
            "isMultiline": is_multiline
        }
        if label:
            input_element["label"] = label
        self.card["body"].append(input_element)
        return self

    def add_input_choice_set(
        self,
        id: str,
        choices: List[Dict[str, str]],
        is_multi_select: bool = False,
        style: str = "compact",
        label: str = ""
    ):
        """Add a choice set (dropdown/radio)"""
        input_element = {
            "type": "Input.ChoiceSet",
            "id": id,
            "choices": choices,
            "isMultiSelect": is_multi_select,
            "style": style
        }
        if label:
            input_element["label"] = label
        self.card["body"].append(input_element)
        return self

    def add_container(
        self,
        items: List[Dict],
        style: str = "default"
    ):
        """Add a container for grouping elements"""
        self.card["body"].append({
            "type": "Container",
            "items": items,
            "style": style
        })
        return self

    def build(self) -> Dict:
        """Build and return the card"""
        return self.card

    def to_json(self) -> str:
        """Return card as JSON string"""
        return json.dumps(self.card, indent=2)

def create_deployment_card(
    app_name: str,
    environment: str,
    version: str,
    status: str,
    details: Dict[str, str],
    action_url: str
) -> Dict:
    """Create a deployment notification card"""

*Content truncated — see parent skill for full reference.*
