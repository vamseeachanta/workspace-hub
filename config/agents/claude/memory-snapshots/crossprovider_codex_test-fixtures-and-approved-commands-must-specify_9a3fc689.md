---
name: crossprovider codex test-fixtures-and-approved-commands-must-specify
description: Test fixtures and approved commands must specify matching dates/parameters
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [testing, fixtures, command-parity, defect-pattern]
---

When tests use fixture dates (e.g., 2026-06-18) but approved commands specify different dates (e.g., --generated-date 2026-06-20), tests pass while real command execution fails. Fixture hardcoding hides parameter drift that breaks the actual approved workflow.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
