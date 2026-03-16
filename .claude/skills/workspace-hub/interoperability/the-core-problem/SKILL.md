---
name: interoperability-the-core-problem
description: 'Sub-skill of interoperability: The Core Problem.'
version: 1.0.0
category: workspace-hub
type: reference
scripts_exempt: true
---

# The Core Problem

## The Core Problem


Windows editors (Notepad, VSCode with wrong settings) save files as:
- UTF-16 LE (Notepad default) — crashes any parser that assumes UTF-8
- CRLF line endings — breaks bash heredocs, YAML parsers, and diffs
- UTF-8 with BOM (`\xef\xbb\xbf`) — breaks strict UTF-8 parsers

These failures are **silent** — a file arrives via `git pull`, looks fine in
a text editor, and then crashes a script hours later. Catch before the fact,
not after.
