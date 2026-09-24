---
name: crossprovider gemini verify-active-content-before-removing-suspect-di
description: Verify active content before removing suspect directories
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [cleanup, risk, filesystem-archaeology]
---

Directories with sparse commits may still be active (monitoring-dashboard: 59-file Express app; coordination: Python library with Pydantic schemas). Check tracked status, inbound refs, and recent content before flagging for removal.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
