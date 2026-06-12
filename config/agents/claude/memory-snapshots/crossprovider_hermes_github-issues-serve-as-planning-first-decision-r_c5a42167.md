---
name: crossprovider hermes github-issues-serve-as-planning-first-decision-r
description: GitHub issues serve as planning-first decision records before filesystem moves
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [github, process, safety]
---

Use GitHub issues (#2754–#2758 pattern) as planning records and decision gates before any clone/delete/relocate/sync operations. Avoids unplanned mutations and provides audit trail. Issues remain in planning state (status:needs-plan, status:plan-approved labels) until approval flow completes.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
