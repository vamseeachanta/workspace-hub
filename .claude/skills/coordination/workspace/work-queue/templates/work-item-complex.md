---
id: {{ id }}
title: "{{ title }}"
status: pending
priority: {{ priority }}
complexity: {{ complexity }}
created_at: {{ created_at }}
target_repos:
  - {{ target_repo }}
commit:
spec_ref:
related: []
blocked_by: []
route:
claimed_at:
failure_reason:
attempts: 0
---

# {{ title }}

## What

{{ description }}

## Why

{{ rationale }}

## Detailed Requirements

{{ requirements }}

## Constraints

- {{ constraint_1 }}
- {{ constraint_2 }}

## Architecture Notes

{{ architecture_notes }}

## Open Questions

- [ ] {{ question_1 }}
- [ ] {{ question_2 }}

## Acceptance Criteria

- [ ] {{ criterion_1 }}
- [ ] {{ criterion_2 }}
- [ ] {{ criterion_3 }}

## Implementation Notes

_Populated during processing._

---
*Source: {{ source }}*
