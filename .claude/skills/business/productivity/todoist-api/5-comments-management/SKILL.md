---
name: todoist-api-5-comments-management
description: 'Sub-skill of todoist-api: 5. Comments Management (+1).'
version: 1.0.0
category: business
type: reference
scripts_exempt: true
---

# 5. Comments Management (+1)

## 5. Comments Management


**REST API - Comments:**
```bash
# Get comments for task
curl -s -X GET "https://api.todoist.com/rest/v2/comments?task_id=TASK_ID" \
    -H "Authorization: Bearer $TODOIST_API_KEY" | jq

# Get comments for project
curl -s -X GET "https://api.todoist.com/rest/v2/comments?project_id=PROJECT_ID" \
    -H "Authorization: Bearer $TODOIST_API_KEY" | jq

# Add comment to task
curl -s -X POST "https://api.todoist.com/rest/v2/comments" \
    -H "Authorization: Bearer $TODOIST_API_KEY" \
    -H "Content-Type: application/json" \
    -d '{
        "task_id": "TASK_ID",
        "content": "This is a comment on the task"
    }' | jq

# Add comment with attachment
curl -s -X POST "https://api.todoist.com/rest/v2/comments" \
    -H "Authorization: Bearer $TODOIST_API_KEY" \
    -H "Content-Type: application/json" \
    -d '{
        "task_id": "TASK_ID",
        "content": "See attached file",
        "attachment": {
            "file_name": "report.pdf",
            "file_type": "application/pdf",
            "file_url": "https://example.com/report.pdf"
        }
    }' | jq

# Update comment
curl -s -X POST "https://api.todoist.com/rest/v2/comments/COMMENT_ID" \
    -H "Authorization: Bearer $TODOIST_API_KEY" \
    -H "Content-Type: application/json" \
    -d '{
        "content": "Updated comment content"
    }' | jq

# Delete comment
curl -s -X DELETE "https://api.todoist.com/rest/v2/comments/COMMENT_ID" \
    -H "Authorization: Bearer $TODOIST_API_KEY"
```

**Python SDK - Comments:**
```python
# Get comments for task
comments = api.get_comments(task_id="1234567890")
for comment in comments:
    print(f"  {comment.posted_at}: {comment.content}")

# Add comment
new_comment = api.add_comment(
    task_id="1234567890",
    content="Added some notes about this task"
)

# Update comment
api.update_comment(
    comment_id=new_comment.id,
    content="Updated notes"
)

# Delete comment
api.delete_comment(comment_id=new_comment.id)
```


## 6. Filters and Queries


**Filter Syntax:**
```bash
# Date filters
"today"                    # Due today
"tomorrow"                 # Due tomorrow
"overdue"                  # Past due date
"next 7 days"              # Due in next week
"no date"                  # No due date set
"Jan 15"                   # Specific date
"before: Jan 20"           # Before date
"after: Jan 10"            # After date

# Priority filters
"p1"                       # Priority 1 (urgent)
"p2"                       # Priority 2 (high)
"p3"                       # Priority 3 (medium)
"p4"                       # Priority 4 (normal)
"(p1 | p2)"               # Priority 1 OR 2

# Label filters
"@work"                    # Has label "work"
"@work & @urgent"          # Has both labels
"@work | @personal"        # Has either label
"!@work"                   # Does NOT have label

# Project filters
"#Work"                    # In project "Work"
"##Work"                   # In project "Work" and sub-projects
"#Work & #Q1"              # In both projects (intersection)

# Search filters
"search: meeting"          # Content contains "meeting"

# Assignee filters
"assigned to: me"          # Assigned to current user
"assigned to: John"        # Assigned to John
"assigned by: me"          # Assigned by current user

# Combined filters
"today & @work"            # Due today with work label
"(today | overdue) & p1"   # Today or overdue AND priority 1
"#Work & !@done"           # In Work project without done label
```

**Python Filter Examples:**
```python
# Get tasks with various filters
today_work = api.get_tasks(filter="today & @work")
urgent = api.get_tasks(filter="(p1 | p2) & (today | overdue)")
project_pending = api.get_tasks(filter="#ProjectAlpha & !@completed")
this_week = api.get_tasks(filter="next 7 days")
no_date = api.get_tasks(filter="no date & @inbox")

# Complex filter
complex_filter = api.get_tasks(
    filter="(today | tomorrow) & (p1 | p2) & (#Work | #Personal) & !@waiting"
)
```
