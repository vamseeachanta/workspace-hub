---
name: crossprovider hermes hardcoded-closed-issue-sets-in-validators-create
description: Hardcoded closed-issue sets in validators create hidden false negatives
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [validation, defect-class, closed-issues]
---

llm-wiki #88 review found that hardcoding specific closed issues (e.g., {76,79}) in route validators and generators prevents detection when new issues later close. Instead of hardcoding, validators should dynamically query closed-issue state to avoid false negatives for future closed issues.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
