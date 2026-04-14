---
name: financial-site-bypass-workflow
description: Workflow for accessing restricted financial sites when browser automation is blocked
version: 1.0.0
source: auto-extracted
extracted: 2026-04-14
metadata:
  tags: ["browser", "finance", "workaround", "data-export"]
---

# Financial Site Bypass Workflow

When Claude-in-Chrome blocks financial domains (Fidelity, brokerages), direct browser automation fails. Instead: (1) Take a screenshot and paste it to Claude for OCR, (2) Manually export CSV/transaction files from the site UI and load them via file path, or (3) Copy/paste table data directly into chat. Store exported files in a local workspace folder and back them up to git. This preserves data access without unblocking security restrictions.