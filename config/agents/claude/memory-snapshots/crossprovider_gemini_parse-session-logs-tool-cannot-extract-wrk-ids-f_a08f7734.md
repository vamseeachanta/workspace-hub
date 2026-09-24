---
name: crossprovider gemini parse-session-logs-tool-cannot-extract-wrk-ids-f
description: Parse-session-logs tool cannot extract WRK-IDs from JSONL event structure
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [session-log-parsing, tooling-limitation, structured-data-gap]
---

WRK-ID references appear in message content text, not in structured event fields. Current script can extract timestamps and provider refs but fails on WRK-ID association, requiring manual message-content parsing or secondary pass.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
