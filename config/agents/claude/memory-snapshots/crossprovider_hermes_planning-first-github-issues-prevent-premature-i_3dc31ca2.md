---
name: crossprovider hermes planning-first-github-issues-prevent-premature-i
description: Planning-first GitHub issues prevent premature infrastructure moves
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [github-workflow, infrastructure-planning, governance]
---

Issues #2754–#2757 established pattern: GitHub issues as decision records BEFORE any repo relocations/renames. Avoids parallel-session conflicts and uncoordinated moves. Use labels (machine, status:needs-plan, status:plan-approved) to gate infrastructure changes on explicit approval.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
