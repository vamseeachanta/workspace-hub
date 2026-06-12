---
name: crossprovider hermes subprocess-exporter-tests-assert-tool-remaps-jso
description: Subprocess exporter tests: assert tool remaps, JSONL structure, rerun skip, shim usage
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [subprocess-testing, behavioral-assertions, session-export]
---

For session exporters (Hermes, Codex, Gemini), behavioral assertions that fire: (1) tool remaps (terminal→Bash, patch→Edit, session_search→Grep, skills_list→ToolSearch), (2) JSONL output structure and record counts, (3) rerun skip via .last-export-ts mtime, (4) python-resolver PATH shim actually invoked. Verify with fake uv/python shims in temp home/repo. Minimal fixture: 1 session JSON + 1-2 tool calls to cover normalizations.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
