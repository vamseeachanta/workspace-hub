---
name: crossprovider codex dedupe-before-write-augment-in-place-don-t-overw
description: Dedupe-before-write: augment in-place, don't overwrite
metadata:
  type: reference
  source: codex
  bridged: 2026-05-28
  tags: [dedupe-workflow, page-creation, augment-in-place, preventive]
---

Before creating any page, grep target domain's standards/ + sources/ for existing code_id match. If found, augment with missing sections/tables rather than overwrite wholesale or create a duplicate. Example: AWS_A5.10 existed; session added as variant source instead.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
