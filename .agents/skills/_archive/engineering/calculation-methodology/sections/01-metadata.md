# 01 — Metadata

## Purpose

Establish document control, revision history, and approval workflow for the
calculation. This section ensures traceability and identifies who authored,
checked, and approved the document.

## Schema Fields

```yaml
metadata:
  title: string            # descriptive calculation title
  doc_id: string           # unique document identifier
  revision: string         # revision code (e.g., "A", "0", "P1")
  date: string             # issue date (ISO 8601)
  author: string           # originator name (scalar, not a list)
  status: enum             # draft | reviewed | approved
  reviewer: string         # optional — independent reviewer name
  project: string          # optional — project name or number
  change_log:              # optional — revision history
    - rev: string
      date: string
      description: string
```

> **Renderer Mapping Note:** The methodology guidance recommends tracking
> multiple authors with roles (originator, checker, approver) and structured
> project objects. The renderer accepts only a single `author` scalar and
> optional `reviewer` scalar. Document additional signatories in the
> `change_log` descriptions or the verification section (12).

## Required Content

- Document identifier (`doc_id`) following project naming convention
- Author name
- Revision code and date
- Status field set to `draft` at creation

## Quality Checklist

- [ ] `doc_id` is unique within the project
- [ ] `change_log` entries include a description of changes (not just "updated")
- [ ] Checker and approver roles recorded in section 12 (verification)
- [ ] Date format is consistent (ISO 8601 preferred)
- [ ] Status is one of: `draft`, `reviewed`, `approved`

## Example Snippet

```yaml
metadata:
  title: "Pipeline Wall Thickness — 12-inch Export Line"
  doc_id: "PRJ-CALC-001"
  revision: "A"
  date: "2026-03-15"
  author: "J. Smith"
  status: draft
  project: "Subsea Tieback Development"
  change_log:
    - rev: "A"
      date: "2026-03-15"
      description: "Initial issue for internal review"
```

## Common Mistakes

- Missing revision history — every revision must have a change description
- Checker listed as the same person who originated the calculation
- Status left as `draft` on a document issued for construction
- Using `doc_number` instead of `doc_id` (renderer requires `doc_id`)
- Providing `authors` as a list instead of `author` as a scalar string
