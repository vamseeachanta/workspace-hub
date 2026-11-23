---
name: notion-api-6-rich-text-formatting
description: 'Sub-skill of notion-api: 6. Rich Text Formatting (+1).'
version: 1.0.0
category: business
type: reference
scripts_exempt: true
---

# 6. Rich Text Formatting (+1)

## 6. Rich Text Formatting


**Rich Text Structure:**
```python
# Basic text
{"type": "text", "text": {"content": "Plain text"}}

# Styled text
{
    "type": "text",
    "text": {"content": "Styled text"},
    "annotations": {
        "bold": True,
        "italic": False,
        "strikethrough": False,
        "underline": False,
        "code": False,
        "color": "red"  # default, gray, brown, orange, yellow, green, blue, purple, pink, red
    }
}

# Link
{
    "type": "text",
    "text": {
        "content": "Click here",
        "link": {"url": "https://example.com"}
    }
}

# Mention user
{
    "type": "mention",
    "mention": {
        "type": "user",
        "user": {"id": "user-id"}
    }
}

# Mention page
{
    "type": "mention",
    "mention": {
        "type": "page",
        "page": {"id": "page-id"}
    }
}

# Mention date
{
    "type": "mention",
    "mention": {
        "type": "date",
        "date": {"start": "2025-01-17"}
    }
}

# Equation
{
    "type": "equation",
    "equation": {"expression": "E = mc^2"}
}
```

**Python - Rich Text Helper:**
```python
def create_rich_text(text, bold=False, italic=False, code=False, color="default", link=None):
    """Helper to create rich text objects"""
    rt = {
        "type": "text",
        "text": {"content": text},
        "annotations": {
            "bold": bold,
            "italic": italic,
            "strikethrough": False,
            "underline": False,
            "code": code,
            "color": color
        }
    }
    if link:
        rt["text"]["link"] = {"url": link}
    return rt

# Usage
paragraph_content = [
    create_rich_text("This is "),
    create_rich_text("bold", bold=True),
    create_rich_text(" and "),
    create_rich_text("italic", italic=True),
    create_rich_text(" text with a "),
    create_rich_text("link", link="https://example.com"),
    create_rich_text(".")
]

notion.blocks.children.append(
    block_id="page-id",
    children=[{
        "type": "paragraph",
        "paragraph": {"rich_text": paragraph_content}
    }]
)
```


## 7. Relations and Rollups


**Create Related Databases:**
```python
# Create Projects database
projects_db = notion.databases.create(
    parent={"type": "page_id", "page_id": "parent-page-id"},
    title=[{"type": "text", "text": {"content": "Projects"}}],
    properties={
        "Name": {"title": {}},
        "Status": {
            "select": {
                "options": [
                    {"name": "Active", "color": "green"},
                    {"name": "Completed", "color": "gray"}
                ]
            }
        }
    }
)

# Create Tasks database with relation to Projects
tasks_db = notion.databases.create(
    parent={"type": "page_id", "page_id": "parent-page-id"},
    title=[{"type": "text", "text": {"content": "Tasks"}}],
    properties={
        "Name": {"title": {}},
        "Status": {
            "select": {
                "options": [
                    {"name": "To Do", "color": "gray"},
                    {"name": "Done", "color": "green"}
                ]
            }
        },
        "Project": {
            "relation": {
                "database_id": projects_db["id"],
                "single_property": {}
            }
        }
    }
)

# Add rollup to Projects for task count
notion.databases.update(
    database_id=projects_db["id"],
    properties={
        "Task Count": {
            "rollup": {
                "relation_property_name": "Tasks",  # This is auto-created
                "rollup_property_name": "Name",
                "function": "count"
            }
        }
    }
)

# Create task linked to project
notion.pages.create(
    parent={"database_id": tasks_db["id"]},
    properties={
        "Name": {"title": [{"text": {"content": "Task 1"}}]},
        "Status": {"select": {"name": "To Do"}},
        "Project": {"relation": [{"id": "project-page-id"}]}
    }
)
```
