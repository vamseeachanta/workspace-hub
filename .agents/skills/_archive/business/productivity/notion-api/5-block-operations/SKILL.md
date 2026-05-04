---
name: notion-api-5-block-operations
description: 'Sub-skill of notion-api: 5. Block Operations.'
version: 1.0.0
category: business
type: reference
scripts_exempt: true
---

# 5. Block Operations

## 5. Block Operations


**Block Types:**
```python
# Paragraph
{
    "type": "paragraph",
    "paragraph": {
        "rich_text": [{"type": "text", "text": {"content": "Text content"}}]
    }
}

# Headings
{
    "type": "heading_1",
    "heading_1": {
        "rich_text": [{"type": "text", "text": {"content": "Heading 1"}}]
    }
}
# Also: heading_2, heading_3

# Bulleted list
{
    "type": "bulleted_list_item",
    "bulleted_list_item": {
        "rich_text": [{"type": "text", "text": {"content": "List item"}}]
    }
}

# Numbered list
{
    "type": "numbered_list_item",
    "numbered_list_item": {
        "rich_text": [{"type": "text", "text": {"content": "Item 1"}}]
    }
}

# To-do
{
    "type": "to_do",
    "to_do": {
        "rich_text": [{"type": "text", "text": {"content": "Task"}}],
        "checked": False
    }
}

# Toggle
{
    "type": "toggle",
    "toggle": {
        "rich_text": [{"type": "text", "text": {"content": "Toggle header"}}],
        "children": []  # Nested blocks
    }
}

# Code block
{
    "type": "code",
    "code": {
        "rich_text": [{"type": "text", "text": {"content": "print('hello')"}}],
        "language": "python"
    }
}

# Quote
{
    "type": "quote",
    "quote": {
        "rich_text": [{"type": "text", "text": {"content": "Quote text"}}]
    }
}

# Callout
{
    "type": "callout",
    "callout": {
        "rich_text": [{"type": "text", "text": {"content": "Important note"}}],
        "icon": {"emoji": "💡"}
    }
}

# Divider
{
    "type": "divider",
    "divider": {}
}

# Table of contents
{
    "type": "table_of_contents",
    "table_of_contents": {}
}
```

**Python - Block Operations:**
```python
# Get page blocks (children)
blocks = notion.blocks.children.list(block_id="page-id")
for block in blocks["results"]:
    print(f"Block type: {block['type']}")

# Append blocks to page
notion.blocks.children.append(
    block_id="page-id",
    children=[
        {
            "object": "block",
            "type": "heading_2",
            "heading_2": {
                "rich_text": [{"type": "text", "text": {"content": "New Section"}}]
            }
        },
        {
            "object": "block",
            "type": "paragraph",
            "paragraph": {
                "rich_text": [
                    {"type": "text", "text": {"content": "Some "}},
                    {"type": "text", "text": {"content": "bold"}, "annotations": {"bold": True}},
                    {"type": "text", "text": {"content": " text."}}
                ]
            }
        },
        {
            "object": "block",
            "type": "bulleted_list_item",
            "bulleted_list_item": {
                "rich_text": [{"type": "text", "text": {"content": "First item"}}]
            }
        },
        {
            "object": "block",
            "type": "bulleted_list_item",
            "bulleted_list_item": {
                "rich_text": [{"type": "text", "text": {"content": "Second item"}}]
            }
        }
    ]
)

# Update block
notion.blocks.update(
    block_id="block-id",
    paragraph={
        "rich_text": [{"type": "text", "text": {"content": "Updated content"}}]
    }
)

# Delete block
notion.blocks.delete(block_id="block-id")

# Get all blocks recursively
def get_all_blocks(block_id):
    """Recursively get all blocks"""
    all_blocks = []
    has_more = True
    start_cursor = None

    while has_more:
        response = notion.blocks.children.list(
            block_id=block_id,
            start_cursor=start_cursor,
            page_size=100
        )
        for block in response["results"]:
            all_blocks.append(block)
            if block.get("has_children"):
                children = get_all_blocks(block["id"])
                all_blocks.extend(children)
        has_more = response["has_more"]
        start_cursor = response.get("next_cursor")

    return all_blocks

all_blocks = get_all_blocks("page-id")
print(f"Total blocks: {len(all_blocks)}")
```
