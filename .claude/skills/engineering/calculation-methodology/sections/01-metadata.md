# 01 — Metadata

## Purpose

Establish document control, revision history, and approval workflow for the
calculation. This section ensures traceability and identifies who authored,
checked, and approved the document.

## Schema Fields

```yaml
metadata:
  doc_number: string       # unique document identifier
  title: string            # descriptive calculation title
  revision: string         # revision code (e.g., "A", "0", "P1")
  status: enum             # draft | issued_for_review | issued_for_use
  date: date               # issue date (ISO 8601)
  project:
    name: string
    number: string
  authors:
    - name: string
      role: string         # originator | checker | approver
      date: date
      signature: string    # name or digital signature ref
  revision_history:
    - rev: string
      date: date
      description: string
      by: string
```

## Required Content

- Document number following project naming convention
- At least one author with originator role
- Revision code and date
- Project name and number
- Status field set to `draft` at creation

## Quality Checklist

- [ ] Document number is unique within the project
- [ ] Revision history includes a description of changes (not just "updated")
- [ ] Checker and approver roles are distinct from originator
- [ ] Date format is consistent (ISO 8601 preferred)
- [ ] Status reflects the actual review state

## Example Snippet

```yaml
metadata:
  doc_number: "PRJ-CALC-001"
  title: "Pipeline Wall Thickness — 12-inch Export Line"
  revision: "A"
  status: draft
  date: 2026-03-15
  project:
    name: "Subsea Tieback Development"
    number: "PRJ-2026-042"
  authors:
    - name: "J. Smith"
      role: originator
      date: 2026-03-15
  revision_history:
    - rev: "A"
      date: 2026-03-15
      description: "Initial issue for internal review"
      by: "J. Smith"
```

## Common Mistakes

- Missing revision history — every revision must have a change description
- Checker listed as the same person who originated the calculation
- Status left as `draft` on a document issued for construction
- No project number, making the calculation untraceable to a scope of work
