---
name: crossprovider gemini python-3-8-safe-iso-8601-datetime-parsing-with-z
description: Python 3.8+ safe ISO 8601 datetime parsing with Z suffix
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [python, datetime, compatibility]
---

Normalize Z suffix via `.replace('Z', '+00:00')` before calling `datetime.fromisoformat()` for cross-version compatibility (Python 3.11+ handles Z natively; this pattern works on 3.8+). Use UTC-aware datetime objects for timestamp comparisons to avoid timezone-aware/naive mixing.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
