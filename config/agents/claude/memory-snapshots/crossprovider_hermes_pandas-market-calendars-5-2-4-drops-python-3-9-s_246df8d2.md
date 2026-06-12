---
name: crossprovider hermes pandas-market-calendars-5-2-4-drops-python-3-9-s
description: pandas-market-calendars 5.2.4+ drops Python 3.9 support
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [dependency-compatibility, python-versions, ci-blockers]
---

Version 5.2.4 and later use PEP 604 union syntax (|) which is not available in Python 3.9; projects supporting Python 3.9 must pin to 5.1.3 or lower. This causes parse-time ast syntax errors during CI on Python 3.9 runs.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
