---
name: miro-api-3-shapes-and-drawing
description: 'Sub-skill of miro-api: 3. Shapes and Drawing.'
version: 1.0.0
category: business
type: reference
scripts_exempt: true
---

# 3. Shapes and Drawing

## 3. Shapes and Drawing


```python
# shapes.py
# ABOUTME: Shape creation and manipulation
# ABOUTME: Rectangles, circles, lines, and custom shapes

from miro_api import Miro
import os

miro = Miro(access_token=os.environ.get("MIRO_ACCESS_TOKEN"))


def create_shape(
    board_id: str,
    shape_type: str,
    content: str = "",
    x: float = 0,
    y: float = 0,
    width: float = 200,
    height: float = 100,
    fill_color: str = "#ffffff",
    border_color: str = "#000000",
    border_width: int = 2,
) -> dict:
    """Create a shape on the board

    Shape types: rectangle, circle, triangle, rhombus, parallelogram,
                 trapezoid, pentagon, hexagon, octagon, wedge_round_rectangle_callout,
                 round_rectangle, star, flow_chart_process, flow_chart_decision,
                 flow_chart_terminator, flow_chart_data, flow_chart_document
    """

    shape = miro.shapes.create(
        board_id=board_id,
        data={"content": content, "shape": shape_type},
        style={
            "fillColor": fill_color,
            "borderColor": border_color,
            "borderWidth": str(border_width),
            "borderStyle": "normal",
            "fontFamily": "arial",
            "fontSize": "14",
            "textAlign": "center",
            "textAlignVertical": "middle",
        },
        position={"x": x, "y": y, "origin": "center"},
        geometry={"width": width, "height": height},
    )

    return {
        "id": shape.id,
        "type": shape.data.shape,
        "position": {"x": shape.position.x, "y": shape.position.y},
    }


def create_rectangle(
    board_id: str,
    content: str = "",
    x: float = 0,
    y: float = 0,
    width: float = 200,
    height: float = 100,
    fill_color: str = "#ffffff",
) -> dict:
    """Create a rectangle"""
    return create_shape(
        board_id=board_id,
        shape_type="rectangle",
        content=content,
        x=x,
        y=y,
        width=width,
        height=height,
        fill_color=fill_color,
    )


def create_circle(
    board_id: str,
    content: str = "",
    x: float = 0,
    y: float = 0,
    diameter: float = 100,
    fill_color: str = "#ffffff",
) -> dict:
    """Create a circle"""
    return create_shape(
        board_id=board_id,
        shape_type="circle",
        content=content,
        x=x,
        y=y,
        width=diameter,
        height=diameter,
        fill_color=fill_color,
    )


def create_flowchart_shape(
    board_id: str,
    shape_type: str,
    content: str = "",
    x: float = 0,
    y: float = 0,
    width: float = 150,
    height: float = 80,
) -> dict:
    """Create a flowchart shape

    Types: flow_chart_process, flow_chart_decision, flow_chart_terminator,
           flow_chart_data, flow_chart_document, flow_chart_predefined_process,
           flow_chart_manual_input, flow_chart_display, flow_chart_preparation
    """

    colors = {
        "flow_chart_process": "#e3f2fd",
        "flow_chart_decision": "#fff3e0",
        "flow_chart_terminator": "#f3e5f5",
        "flow_chart_data": "#e8f5e9",
        "flow_chart_document": "#fce4ec",
    }

    return create_shape(
        board_id=board_id,
        shape_type=shape_type,
        content=content,
        x=x,
        y=y,
        width=width,
        height=height,
        fill_color=colors.get(shape_type, "#ffffff"),
    )


def create_flowchart(board_id: str, steps: list, start_x: float = 0, start_y: float = 0) -> list:
    """Create a flowchart from a list of steps

    Each step: {"type": "process|decision|terminator", "content": "text"}
    """
    created = []
    current_y = start_y

    for step in steps:
        shape_type = f"flow_chart_{step.get('type', 'process')}"
        height = 100 if step.get("type") == "decision" else 80

        shape = create_flowchart_shape(
            board_id=board_id,
            shape_type=shape_type,
            content=step["content"],
            x=start_x,
            y=current_y,
            height=height,
        )
        created.append(shape)

        current_y += height + 80  # Add spacing for connectors

    return created


def update_shape(
    board_id: str,
    shape_id: str,
    content: str = None,
    fill_color: str = None,
    x: float = None,
    y: float = None,
) -> dict:
    """Update a shape"""
    update_data = {}

    if content is not None:
        update_data["data"] = {"content": content}
    if fill_color:
        update_data["style"] = {"fillColor": fill_color}
    if x is not None or y is not None:
        position = {}
        if x is not None:
            position["x"] = x
        if y is not None:
            position["y"] = y
        update_data["position"] = position


*Content truncated — see parent skill for full reference.*
