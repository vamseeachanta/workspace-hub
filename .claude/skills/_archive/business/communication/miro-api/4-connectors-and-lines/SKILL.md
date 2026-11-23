---
name: miro-api-4-connectors-and-lines
description: 'Sub-skill of miro-api: 4. Connectors and Lines.'
version: 1.0.0
category: business
type: reference
scripts_exempt: true
---

# 4. Connectors and Lines

## 4. Connectors and Lines


```python
# connectors.py
# ABOUTME: Connector and line creation
# ABOUTME: Connect shapes, create arrows, and diagram flows

from miro_api import Miro
import os

miro = Miro(access_token=os.environ.get("MIRO_ACCESS_TOKEN"))


def create_connector(
    board_id: str,
    start_item_id: str,
    end_item_id: str,
    start_position: str = "right",
    end_position: str = "left",
    stroke_color: str = "#000000",
    stroke_width: int = 2,
    stroke_style: str = "normal",
    start_cap: str = "none",
    end_cap: str = "stealth",
    caption: str = None,
) -> dict:
    """Create a connector between two items

    Positions: top, right, bottom, left, auto
    Caps: none, stealth, rounded_stealth, diamond, diamond_filled, oval, oval_filled,
          arrow, triangle, triangle_filled, erd_one, erd_many, erd_one_or_many, erd_only_one,
          erd_zero_or_one, erd_zero_or_many
    Stroke styles: normal, dashed, dotted
    """

    connector_data = {
        "startItem": {"id": start_item_id, "position": {"x": start_position}},
        "endItem": {"id": end_item_id, "position": {"x": end_position}},
    }

    connector_style = {
        "strokeColor": stroke_color,
        "strokeWidth": str(stroke_width),
        "strokeStyle": stroke_style,
        "startStrokeCap": start_cap,
        "endStrokeCap": end_cap,
    }

    if caption:
        connector_data["captions"] = [{"content": caption, "position": "50%"}]

    connector = miro.connectors.create(
        board_id=board_id,
        data=connector_data,
        style=connector_style,
    )

    return {
        "id": connector.id,
        "start_item": connector.start_item.id,
        "end_item": connector.end_item.id,
    }


def create_line(
    board_id: str,
    start_x: float,
    start_y: float,
    end_x: float,
    end_y: float,
    stroke_color: str = "#000000",
    stroke_width: int = 2,
    end_cap: str = "none",
) -> dict:
    """Create a standalone line"""

    # For lines without connected items, we use absolute coordinates
    connector = miro.connectors.create(
        board_id=board_id,
        data={
            "startItem": {"position": {"x": start_x, "y": start_y}},
            "endItem": {"position": {"x": end_x, "y": end_y}},
        },
        style={
            "strokeColor": stroke_color,
            "strokeWidth": str(stroke_width),
            "startStrokeCap": "none",
            "endStrokeCap": end_cap,
        },
    )

    return {"id": connector.id}


def connect_flowchart_shapes(board_id: str, shape_ids: list, labels: list = None) -> list:
    """Connect a list of shapes in sequence"""
    created = []

    for i in range(len(shape_ids) - 1):
        label = labels[i] if labels and i < len(labels) else None

        connector = create_connector(
            board_id=board_id,
            start_item_id=shape_ids[i],
            end_item_id=shape_ids[i + 1],
            start_position="bottom",
            end_position="top",
            end_cap="stealth",
            caption=label,
        )
        created.append(connector)

    return created


def create_decision_branches(
    board_id: str,
    decision_shape_id: str,
    yes_shape_id: str,
    no_shape_id: str,
) -> list:
    """Create Yes/No branches from a decision diamond"""

    yes_connector = create_connector(
        board_id=board_id,
        start_item_id=decision_shape_id,
        end_item_id=yes_shape_id,
        start_position="bottom",
        end_position="top",
        end_cap="stealth",
        caption="Yes",
        stroke_color="#4caf50",
    )

    no_connector = create_connector(
        board_id=board_id,
        start_item_id=decision_shape_id,
        end_item_id=no_shape_id,
        start_position="right",
        end_position="left",
        end_cap="stealth",
        caption="No",
        stroke_color="#f44336",
    )

    return [yes_connector, no_connector]


def create_erd_relationship(
    board_id: str,
    entity1_id: str,
    entity2_id: str,
    cardinality_start: str = "erd_one",
    cardinality_end: str = "erd_many",
    label: str = None,
) -> dict:
    """Create an ERD relationship line

    Cardinalities: erd_one, erd_many, erd_one_or_many, erd_only_one,
                   erd_zero_or_one, erd_zero_or_many
    """

    return create_connector(
        board_id=board_id,
        start_item_id=entity1_id,
        end_item_id=entity2_id,
        start_cap=cardinality_start,
        end_cap=cardinality_end,
        caption=label,
    )


def update_connector(
    board_id: str,
    connector_id: str,
    stroke_color: str = None,
    caption: str = None,
) -> dict:
    """Update a connector"""
    update_data = {}

    if stroke_color:
        update_data["style"] = {"strokeColor": stroke_color}
    if caption:
        update_data["captions"] = [{"content": caption, "position": "50%"}]


*Content truncated — see parent skill for full reference.*
