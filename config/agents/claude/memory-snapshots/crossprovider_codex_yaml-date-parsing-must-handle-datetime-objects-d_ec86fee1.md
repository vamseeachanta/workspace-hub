---
name: crossprovider codex yaml-date-parsing-must-handle-datetime-objects-d
description: YAML date parsing must handle datetime objects, date objects, and ISO strings
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [parsing, data-formats, edge-cases]
---

YAML deserializers return datetime objects; standalone date objects and ISO strings also appear in multi-format systems. Date parsing must try all three (datetime.date(), date isinstance, strptime with multiple formats) with None fallback.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
