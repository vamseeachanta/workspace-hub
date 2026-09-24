---
name: crossprovider gemini python-3-8-built-in-generic-compatibility
description: Python 3.8 built-in generic compatibility
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [python, type-hints, python-3.8]
---

When using built-in generics like `dict[str, Any]` in Python 3.8 targeting code, add `from __future__ import annotations` to ALL files that use the syntax, not just a subset. This applies consistently across modules in a type-stubs project.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
