---
id: CONTEXT-{{ id }}
work_items:
  - {{ wrk_id }}
created_at: {{ created_at }}
source: user_input
---

# Context Document: {{ title }}

## Original Request (Verbatim)

> {{ verbatim_request }}

## Extracted Work Items

| ID | Title | Complexity | Priority |
|----|-------|-----------|----------|
| {{ wrk_id }} | {{ wrk_title }} | {{ complexity }} | {{ priority }} |

## Additional Context

{{ additional_context }}

## Attachments

_None_
