---
name: dash-3-layout-components
description: 'Sub-skill of dash: 3. Layout Components.'
version: 1.0.0
category: data-analysis
type: reference
scripts_exempt: true
---

# 3. Layout Components

## 3. Layout Components


**HTML Components:**
```python
from dash import html

# Text elements
layout = html.Div([
    html.H1("Main Title"),
    html.H2("Subtitle"),
    html.H3("Section Header"),
    html.P("Paragraph text with ", html.Strong("bold"), " and ", html.Em("italic")),
    html.Hr(),  # Horizontal rule
    html.Br(),  # Line break

    # Lists
    html.Ul([
        html.Li("Item 1"),
        html.Li("Item 2"),
        html.Li("Item 3")
    ]),

    # Links
    html.A("Click here", href="https://example.com", target="_blank"),

    # Images
    html.Img(src="/assets/logo.png", style={"width": "200px"}),

    # Tables
    html.Table([
        html.Thead([
            html.Tr([html.Th("Name"), html.Th("Value")])
        ]),
        html.Tbody([
            html.Tr([html.Td("Item 1"), html.Td("100")]),
            html.Tr([html.Td("Item 2"), html.Td("200")])
        ])
    ])
])
```

**Core Components (dcc):**
```python
from dash import dcc

# Input components
components = html.Div([
    # Dropdown
    dcc.Dropdown(
        id="dropdown",
        options=[
            {"label": "Option A", "value": "a"},
            {"label": "Option B", "value": "b"},
            {"label": "Option C", "value": "c", "disabled": True}
        ],
        value="a",
        multi=False,
        clearable=True,
        searchable=True,
        placeholder="Select..."
    ),

    # Multi-select dropdown
    dcc.Dropdown(
        id="multi-dropdown",
        options=[{"label": f"Option {i}", "value": i} for i in range(10)],
        value=[1, 2, 3],
        multi=True
    ),

    # Slider
    dcc.Slider(
        id="slider",
        min=0,
        max=100,
        step=5,
        value=50,
        marks={0: "0", 25: "25", 50: "50", 75: "75", 100: "100"}
    ),

    # Range slider
    dcc.RangeSlider(
        id="range-slider",
        min=0,
        max=100,
        step=1,
        value=[20, 80],
        marks={i: str(i) for i in range(0, 101, 20)}
    ),

    # Input
    dcc.Input(
        id="text-input",
        type="text",
        placeholder="Enter text...",
        debounce=True  # Wait for typing to stop
    ),

    # Textarea
    dcc.Textarea(
        id="textarea",
        placeholder="Enter longer text...",
        style={"width": "100%", "height": "100px"}
    ),

    # Checklist
    dcc.Checklist(
        id="checklist",
        options=[
            {"label": "Option 1", "value": "1"},
            {"label": "Option 2", "value": "2"},
            {"label": "Option 3", "value": "3"}
        ],
        value=["1"],
        inline=True
    ),

    # Radio items
    dcc.RadioItems(
        id="radio",
        options=[
            {"label": "Small", "value": "s"},
            {"label": "Medium", "value": "m"},
            {"label": "Large", "value": "l"}
        ],
        value="m",
        inline=True
    ),

    # Date picker
    dcc.DatePickerSingle(
        id="date-picker",
        date="2025-01-01",
        display_format="YYYY-MM-DD"
    ),

    # Date range picker
    dcc.DatePickerRange(
        id="date-range",
        start_date="2025-01-01",
        end_date="2025-12-31",
        display_format="YYYY-MM-DD"
    ),

    # Upload
    dcc.Upload(
        id="upload",
        children=html.Div(["Drag and Drop or ", html.A("Select Files")]),
        style={
            "width": "100%",
            "height": "60px",
            "lineHeight": "60px",
            "borderWidth": "1px",
            "borderStyle": "dashed",
            "borderRadius": "5px",
            "textAlign": "center"
        }
    ),

    # Tabs
    dcc.Tabs(id="tabs", value="tab-1", children=[
        dcc.Tab(label="Tab 1", value="tab-1"),
        dcc.Tab(label="Tab 2", value="tab-2")
    ]),

    # Loading indicator
    dcc.Loading(
        id="loading",
        type="default",  # default, graph, cube, circle, dot
        children=html.Div(id="loading-output")
    ),

    # Interval (for periodic updates)
    dcc.Interval(
        id="interval-component",
        interval=1000,  # milliseconds
        n_intervals=0
    ),

    # Store (client-side data storage)
    dcc.Store(id="data-store", storage_type="session"),  # memory, session, local

    # Graph
    dcc.Graph(
        id="graph",
        config={

*Content truncated — see parent skill for full reference.*
